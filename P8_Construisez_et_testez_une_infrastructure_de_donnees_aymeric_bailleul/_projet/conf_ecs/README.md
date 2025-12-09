# Déploiement sur AWS ECS - Guide Complet

Ce guide vous accompagne étape par étape pour déployer l'infrastructure météorologique sur AWS ECS.

## 📋 Prérequis

- Compte AWS avec droits admin ou permissions sur : ECS, ECR, VPC, IAM, EFS, Secrets Manager
- AWS CLI installé et configuré (`aws configure`)
- Docker installé localement
- Votre ID de compte AWS (remplacer `ACCOUNT_ID` dans les commandes)

## 🚀 Étapes de déploiement

### Étape 1 : Configuration AWS CLI

```powershell
# Vérifier la configuration AWS
aws sts get-caller-identity

# Noter votre Account ID
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$REGION = "eu-west-1"

Write-Host "Account ID: $ACCOUNT_ID"
Write-Host "Region: $REGION"
```

### Étape 2 : Créer les repositories ECR

```powershell
# Créer le repository pour l'image ETL
aws ecr create-repository `
    --repository-name weather-etl `
    --region $REGION `
    --image-scanning-configuration scanOnPush=true

# Créer le repository pour MongoDB (optionnel, on peut utiliser l'image officielle)
# Mais pour la personnaliser avec init-mongo.js :
aws ecr create-repository `
    --repository-name weather-mongodb `
    --region $REGION `
    --image-scanning-configuration scanOnPush=true
```

### Étape 3 : Stocker les secrets dans AWS Secrets Manager

```powershell
# Créer le secret pour les credentials AWS S3
aws secretsmanager create-secret `
    --name weather-pipeline/aws-credentials `
    --description "AWS S3 credentials for weather pipeline" `
    --secret-string '{
        "AWS_ACCESS_KEY_ID": "VOTRE_ACCESS_KEY",
        "AWS_SECRET_ACCESS_KEY": "VOTRE_SECRET_KEY"
    }' `
    --region $REGION

# Créer le secret pour MongoDB
aws secretsmanager create-secret `
    --name weather-pipeline/mongodb-credentials `
    --description "MongoDB credentials" `
    --secret-string '{
        "MONGODB_ROOT_USER": "admin",
        "MONGODB_ROOT_PASSWORD": "VotreMotDePasseSecurise123!"
    }' `
    --region $REGION

# Créer le secret pour Mongo Express
aws secretsmanager create-secret `
    --name weather-pipeline/mongo-express-credentials `
    --description "Mongo Express web interface credentials" `
    --secret-string '{
        "MONGO_EXPRESS_USER": "admin",
        "MONGO_EXPRESS_PASSWORD": "VotreMotDePasseSecurise456!"
    }' `
    --region $REGION

# Créer le secret pour la configuration S3
aws secretsmanager create-secret `
    --name weather-pipeline/s3-config `
    --description "S3 bucket configuration" `
    --secret-string '{
        "S3_BUCKET_NAME": "votre-bucket-name",
        "S3_PREFIX_SOURCE": "01_raw/",
        "S3_PREFIX_DESTINATION": "02_cleaned/",
        "S3_PREFIX_ARCHIVE": "03_archived/"
    }' `
    --region $REGION
```

### Étape 4 : Créer le système de fichiers EFS pour MongoDB

```powershell
# Créer le système de fichiers EFS
$EFS_ID = (aws efs create-file-system `
    --performance-mode generalPurpose `
    --throughput-mode bursting `
    --encrypted `
    --tags Key=Name,Value=weather-mongodb-data `
    --region $REGION `
    --query 'FileSystemId' `
    --output text)

Write-Host "EFS ID: $EFS_ID"

# Attendre que l'EFS soit disponible
aws efs describe-file-systems --file-system-id $EFS_ID --region $REGION

# Note: Vous devrez créer les mount targets dans l'étape VPC
```

### Étape 5 : Builder et pousser les images Docker vers ECR

```powershell
# Se connecter à ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

# Aller dans le dossier du projet
cd "G:\Mon Drive\_formation_over_git\P8_Construisez_et_testez_une_infrastructure_de_donnees_aymeric_bailleul\_projet"

# Builder l'image ETL
docker build -t weather-etl:latest .

# Tagger l'image pour ECR
docker tag weather-etl:latest "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/weather-etl:latest"

# Pousser vers ECR
docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/weather-etl:latest"

# Builder l'image MongoDB personnalisée (avec init-mongo.js)
docker build -t weather-mongodb:latest -f Dockerfile.mongodb .

# Tagger pour ECR
docker tag weather-mongodb:latest "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/weather-mongodb:latest"

# Pousser vers ECR
docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/weather-mongodb:latest"
```

### Étape 6 : Créer le VPC et les ressources réseau

Utiliser le fichier CloudFormation `vpc-infrastructure.yaml` :

```powershell
aws cloudformation create-stack `
    --stack-name weather-pipeline-vpc `
    --template-body file://conf_ecs/vpc-infrastructure.yaml `
    --region $REGION

# Attendre la création
aws cloudformation wait stack-create-complete `
    --stack-name weather-pipeline-vpc `
    --region $REGION

# Récupérer les outputs
aws cloudformation describe-stacks `
    --stack-name weather-pipeline-vpc `
    --region $REGION `
    --query 'Stacks[0].Outputs'
```

### Étape 7 : Créer les mount targets EFS

```powershell
# Récupérer les subnet IDs depuis le stack VPC
$SUBNET1 = (aws cloudformation describe-stacks `
    --stack-name weather-pipeline-vpc `
    --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnet1`].OutputValue' `
    --output text `
    --region $REGION)

$SUBNET2 = (aws cloudformation describe-stacks `
    --stack-name weather-pipeline-vpc `
    --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnet2`].OutputValue' `
    --output text `
    --region $REGION)

$EFS_SG = (aws cloudformation describe-stacks `
    --stack-name weather-pipeline-vpc `
    --query 'Stacks[0].Outputs[?OutputKey==`EFSSecurityGroup`].OutputValue' `
    --output text `
    --region $REGION)

# Créer les mount targets
aws efs create-mount-target `
    --file-system-id $EFS_ID `
    --subnet-id $SUBNET1 `
    --security-groups $EFS_SG `
    --region $REGION

aws efs create-mount-target `
    --file-system-id $EFS_ID `
    --subnet-id $SUBNET2 `
    --security-groups $EFS_SG `
    --region $REGION
```

### Étape 8 : Créer le cluster ECS

```powershell
aws ecs create-cluster `
    --cluster-name weather-pipeline-cluster `
    --region $REGION `
    --capacity-providers FARGATE FARGATE_SPOT `
    --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1
```

### Étape 9 : Créer le rôle IAM pour les tâches ECS

Utiliser le fichier CloudFormation `iam-roles.yaml` :

```powershell
aws cloudformation create-stack `
    --stack-name weather-pipeline-iam `
    --template-body file://conf_ecs/iam-roles.yaml `
    --capabilities CAPABILITY_NAMED_IAM `
    --region $REGION

# Attendre la création
aws cloudformation wait stack-create-complete `
    --stack-name weather-pipeline-iam `
    --region $REGION
```

### Étape 10 : Créer les Task Definitions

```powershell
# Remplacer les valeurs dans les fichiers JSON
# Éditer les fichiers task-definition-*.json avec vos valeurs :
# - ACCOUNT_ID
# - REGION
# - EFS_ID
# - ARNs des secrets

# Enregistrer la task definition MongoDB
aws ecs register-task-definition `
    --cli-input-json file://conf_ecs/task-definition-mongodb.json `
    --region $REGION

# Enregistrer la task definition Mongo Express
aws ecs register-task-definition `
    --cli-input-json file://conf_ecs/task-definition-mongo-express.json `
    --region $REGION

# Enregistrer la task definition ETL
aws ecs register-task-definition `
    --cli-input-json file://conf_ecs/task-definition-etl.json `
    --region $REGION

# Enregistrer la task definition Importer
aws ecs register-task-definition `
    --cli-input-json file://conf_ecs/task-definition-importer.json `
    --region $REGION

# Enregistrer la task definition S3 Cleanup
aws ecs register-task-definition `
    --cli-input-json file://conf_ecs/task-definition-s3-cleanup.json `
    --region $REGION
```

### Étape 11 : Créer les Services ECS

```powershell
# Récupérer les IDs nécessaires
$SUBNET_IDS = (aws cloudformation describe-stacks `
    --stack-name weather-pipeline-vpc `
    --query 'Stacks[0].Outputs[?contains(OutputKey,`Subnet`)].OutputValue' `
    --output text `
    --region $REGION)

$ECS_SG = (aws cloudformation describe-stacks `
    --stack-name weather-pipeline-vpc `
    --query 'Stacks[0].Outputs[?OutputKey==`ECSSecurityGroup`].OutputValue' `
    --output text `
    --region $REGION)

# Service MongoDB
aws ecs create-service `
    --cluster weather-pipeline-cluster `
    --service-name mongodb `
    --task-definition weather-mongodb `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$ECS_SG],assignPublicIp=DISABLED}" `
    --region $REGION

# Service Mongo Express (avec Load Balancer)
aws ecs create-service `
    --cluster weather-pipeline-cluster `
    --service-name mongo-express `
    --task-definition weather-mongo-express `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$ECS_SG],assignPublicIp=ENABLED}" `
    --region $REGION

# Service Importer (long-running)
aws ecs create-service `
    --cluster weather-pipeline-cluster `
    --service-name mongodb-importer `
    --task-definition weather-importer `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$ECS_SG],assignPublicIp=DISABLED}" `
    --region $REGION

# Service S3 Cleanup (long-running)
aws ecs create-service `
    --cluster weather-pipeline-cluster `
    --service-name s3-cleanup `
    --task-definition weather-s3-cleanup `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$ECS_SG],assignPublicIp=DISABLED}" `
    --region $REGION
```

### Étape 12 : Créer une tâche planifiée pour l'ETL (EventBridge)

```powershell
# Créer une règle EventBridge pour exécuter l'ETL une fois par jour
aws events put-rule `
    --name weather-etl-daily `
    --schedule-expression "cron(0 2 * * ? *)" `
    --state ENABLED `
    --region $REGION

# Ajouter la permission à EventBridge
$TASK_ROLE_ARN = (aws cloudformation describe-stacks `
    --stack-name weather-pipeline-iam `
    --query 'Stacks[0].Outputs[?OutputKey==`ECSTaskRoleArn`].OutputValue' `
    --output text `
    --region $REGION)

# Créer la cible (nécessite un rôle IAM pour EventBridge)
# Voir le fichier eventbridge-rule.json
```

### Étape 13 : Vérification du déploiement

```powershell
# Vérifier les services
aws ecs describe-services `
    --cluster weather-pipeline-cluster `
    --services mongodb mongo-express mongodb-importer s3-cleanup `
    --region $REGION

# Vérifier les tâches en cours
aws ecs list-tasks `
    --cluster weather-pipeline-cluster `
    --region $REGION

# Voir les logs CloudWatch
aws logs tail /ecs/weather-mongodb --follow --region $REGION
aws logs tail /ecs/weather-importer --follow --region $REGION
```

## 📊 Accès à Mongo Express

Pour accéder à Mongo Express, récupérez l'IP publique de la tâche :

```powershell
$TASK_ARN = (aws ecs list-tasks `
    --cluster weather-pipeline-cluster `
    --service-name mongo-express `
    --query 'taskArns[0]' `
    --output text `
    --region $REGION)

aws ecs describe-tasks `
    --cluster weather-pipeline-cluster `
    --tasks $TASK_ARN `
    --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' `
    --output text `
    --region $REGION

# Utiliser l'IP publique : http://IP_PUBLIQUE:8081
```

## 🔄 Mise à jour des services

```powershell
# Builder une nouvelle version de l'image
docker build -t weather-etl:v2 .
docker tag weather-etl:v2 "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/weather-etl:v2"
docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/weather-etl:v2"

# Mettre à jour la task definition (modifier le JSON et ré-enregistrer)
aws ecs register-task-definition --cli-input-json file://conf_ecs/task-definition-importer.json

# Forcer le déploiement du service
aws ecs update-service `
    --cluster weather-pipeline-cluster `
    --service mongodb-importer `
    --force-new-deployment `
    --region $REGION
```

## 🧹 Nettoyage (Suppression)

```powershell
# Supprimer les services
aws ecs delete-service --cluster weather-pipeline-cluster --service mongodb --force --region $REGION
aws ecs delete-service --cluster weather-pipeline-cluster --service mongo-express --force --region $REGION
aws ecs delete-service --cluster weather-pipeline-cluster --service mongodb-importer --force --region $REGION
aws ecs delete-service --cluster weather-pipeline-cluster --service s3-cleanup --force --region $REGION

# Supprimer le cluster
aws ecs delete-cluster --cluster weather-pipeline-cluster --region $REGION

# Supprimer les stacks CloudFormation
aws cloudformation delete-stack --stack-name weather-pipeline-iam --region $REGION
aws cloudformation delete-stack --stack-name weather-pipeline-vpc --region $REGION

# Supprimer l'EFS
aws efs delete-file-system --file-system-id $EFS_ID --region $REGION

# Supprimer les secrets
aws secretsmanager delete-secret --secret-id weather-pipeline/aws-credentials --force-delete-without-recovery --region $REGION
aws secretsmanager delete-secret --secret-id weather-pipeline/mongodb-credentials --force-delete-without-recovery --region $REGION
aws secretsmanager delete-secret --secret-id weather-pipeline/mongo-express-credentials --force-delete-without-recovery --region $REGION
aws secretsmanager delete-secret --secret-id weather-pipeline/s3-config --force-delete-without-recovery --region $REGION

# Supprimer les repositories ECR
aws ecr delete-repository --repository-name weather-etl --force --region $REGION
aws ecr delete-repository --repository-name weather-mongodb --force --region $REGION
```

## 💰 Estimation des coûts

**Estimation mensuelle approximative :**
- ECS Fargate (5 tâches) : ~$50-100/mois
- EFS (10 GB) : ~$3/mois
- Load Balancer (optionnel) : ~$20/mois
- Data Transfer : ~$5-10/mois
- Secrets Manager : ~$2/mois
- **Total : ~$80-135/mois**

## 🔐 Bonnes pratiques de sécurité

1. ✅ Tous les credentials sont dans Secrets Manager
2. ✅ Les services sont dans des sous-réseaux privés
3. ✅ Mongo Express devrait être derrière un Load Balancer avec HTTPS
4. ✅ Utilisez des Security Groups restrictifs
5. ✅ Activez CloudWatch Logs pour le monitoring
6. ✅ Utilisez des IAM roles avec le principe du moindre privilège

## 📚 Ressources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS Fargate Pricing](https://aws.amazon.com/fargate/pricing/)
- [ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
