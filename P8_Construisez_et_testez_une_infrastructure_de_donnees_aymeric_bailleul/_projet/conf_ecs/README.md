# Déploiement sur AWS ECS - Guide Complet

Ce guide vous accompagne étape par étape pour déployer l'infrastructure météorologique sur AWS ECS.

## 📋 Prérequis

- Compte AWS avec droits admin ou permissions sur : ECS, ECR, VPC, IAM, EFS, Secrets Manager, CloudWatch Logs
- AWS CLI installé et configuré (`aws configure`)
- Docker installé localement
- Fichier `.env` configuré dans le dossier `_projet` avec vos credentials AWS admin
- Votre ID de compte AWS (ou utilisez le script automatisé `deploy.ps1`)

## 🚀 Méthode Rapide : Script Automatisé

### Option A : Déploiement Automatique (Recommandé)

Le script `deploy.ps1` automatise tout le processus de déploiement :

```powershell
# Depuis le dossier conf_ecs
.\deploy.ps1 -Region eu-west-1
```

Le script effectue automatiquement :
1. ✅ Création des secrets dans AWS Secrets Manager
2. ✅ Création du cluster ECS
3. ✅ Build et push des images Docker vers ECR
4. ✅ Déploiement du stack VPC CloudFormation
5. ✅ Création de l'EFS avec Access Point
6. ✅ Déploiement des rôles IAM
7. ✅ Enregistrement des Task Definitions
8. ✅ Création des services ECS

**Note :** Le script utilise automatiquement les credentials `AWS_ADMIN_ACCESS_KEY_ID` et `AWS_ADMIN_SECRET_ACCESS_KEY` depuis votre fichier `.env`

---

## 📖 Méthode Manuelle : Étape par Étape

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

### Étape 4 : Créer le VPC (AVANT l'EFS)

⚠️ **IMPORTANT** : Le VPC doit être créé AVANT l'EFS pour obtenir les subnet IDs nécessaires.

Utiliser le fichier CloudFormation `vpc-infrastructure.yaml` (corrigé pour éviter la dépendance circulaire) :

```powershell
aws cloudformation create-stack `
    --stack-name weather-pipeline-vpc `
    --template-body file://vpc-infrastructure.yaml `
    --region $REGION

# Attendre la création complète
aws cloudformation wait stack-create-complete `
    --stack-name weather-pipeline-vpc `
    --region $REGION

# Vérifier les outputs
aws cloudformation describe-stacks `
    --stack-name weather-pipeline-vpc `
    --region $REGION `
    --query 'Stacks[0].Outputs'
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

### Étape 6 : Créer le système de fichiers EFS pour MongoDB

```powershell
# Créer le système de fichiers EFS
$EFS_ID = (aws efs create-file-system `
    --performance-mode generalPurpose `
    --throughput-mode bursting `
    --encrypted `
    --tags Key=Name,Value=weather-pipeline-efs `
    --region $REGION `
    --query 'FileSystemId' `
    --output text)

Write-Host "EFS ID: $EFS_ID"

# Attendre 10 secondes que l'EFS soit disponible
Start-Sleep -Seconds 10
```

### Étape 7 : Créer les mount targets et Access Point EFS

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

# ⚠️ IMPORTANT : Créer un Access Point EFS pour MongoDB (résout l'erreur "No such file or directory")
$AP_ID = (aws efs create-access-point `
    --file-system-id $EFS_ID `
    --posix-user Uid=999,Gid=999 `
    --root-directory "Path=/mongodb,CreationInfo={OwnerUid=999,OwnerGid=999,Permissions=755}" `
    --region $REGION `
    --query 'AccessPointId' `
    --output text)

Write-Host "Access Point ID: $AP_ID"
```

### Étape 8 : Créer le cluster ECS

```powershell
aws ecs create-cluster `
    --cluster-name weather-pipeline-cluster `
    --region $REGION `
    --capacity-providers FARGATE FARGATE_SPOT `
    --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1
```

### Étape 9 : Créer les rôles IAM pour les tâches ECS

⚠️ **IMPORTANT** : Le fichier `iam-roles.yaml` a été corrigé pour inclure les permissions CloudWatch Logs dans le rôle d'exécution.

Utiliser le fichier CloudFormation `iam-roles.yaml` :

```powershell
aws cloudformation create-stack `
    --stack-name weather-pipeline-iam `
    --template-body file://iam-roles.yaml `
    --capabilities CAPABILITY_NAMED_IAM `
    --region $REGION

# Attendre la création complète
aws cloudformation wait stack-create-complete `
    --stack-name weather-pipeline-iam `
    --region $REGION

# Vérifier les rôles créés
aws cloudformation describe-stacks `
    --stack-name weather-pipeline-iam `
    --region $REGION `
    --query 'Stacks[0].Outputs'
```

**Permissions incluses :**
- `WeatherPipelineECSTaskExecutionRole` : Pull images ECR, accès Secrets Manager, **création de log groups CloudWatch**
- `WeatherPipelineECSTaskRole` : Accès S3, CloudWatch Logs, Secrets Manager
- `WeatherPipelineEventBridgeECSRole` : Déclenchement des tâches ECS

### Étape 10 : Préparer et enregistrer les Task Definitions

⚠️ **IMPORTANT** : Les task definitions doivent être mises à jour avec :
- Votre ACCOUNT_ID (343374742393)
- Votre REGION (eu-west-1)
- L'EFS_ID créé à l'étape 6
- L'Access Point ID créé à l'étape 7 (pour MongoDB uniquement)

**Configuration spéciale pour MongoDB :**
La task definition MongoDB doit utiliser l'Access Point EFS au lieu du rootDirectory simple :

```json
"efsVolumeConfiguration": {
  "fileSystemId": "fs-0e949e0f67c2d330d",
  "transitEncryption": "ENABLED",
  "authorizationConfig": {
    "accessPointId": "fsap-VOTRE_ACCESS_POINT_ID",
    "iam": "DISABLED"
  }
}
```

**Enregistrer toutes les task definitions :**

```powershell
# MongoDB (avec Access Point EFS)
aws ecs register-task-definition `
    --cli-input-json file://task-definition-mongodb.json `
    --region $REGION

# Mongo Express
aws ecs register-task-definition `
    --cli-input-json file://task-definition-mongo-express.json `
    --region $REGION

# ETL Pipeline
aws ecs register-task-definition `
    --cli-input-json file://task-definition-etl.json `
    --region $REGION

# MongoDB Importer
aws ecs register-task-definition `
    --cli-input-json file://task-definition-importer.json `
    --region $REGION

# S3 Cleanup
aws ecs register-task-definition `
    --cli-input-json file://task-definition-s3-cleanup.json `
    --region $REGION
```

### Étape 11 : Créer les Services ECS

```powershell
# Récupérer les IDs des sous-réseaux publics et privés
$PUBLIC_SUBNET1 = (aws cloudformation describe-stacks `
    --stack-name weather-pipeline-vpc `
    --query 'Stacks[0].Outputs[?OutputKey==`PublicSubnet1`].OutputValue' `
    --output text `
    --region $REGION)

$PUBLIC_SUBNET2 = (aws cloudformation describe-stacks `
    --stack-name weather-pipeline-vpc `
    --query 'Stacks[0].Outputs[?OutputKey==`PublicSubnet2`].OutputValue' `
    --output text `
    --region $REGION)

$PRIVATE_SUBNET1 = (aws cloudformation describe-stacks `
    --stack-name weather-pipeline-vpc `
    --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnet1`].OutputValue' `
    --output text `
    --region $REGION)

$PRIVATE_SUBNET2 = (aws cloudformation describe-stacks `
    --stack-name weather-pipeline-vpc `
    --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnet2`].OutputValue' `
    --output text `
    --region $REGION)

$ECS_SG = (aws cloudformation describe-stacks `
    --stack-name weather-pipeline-vpc `
    --query 'Stacks[0].Outputs[?OutputKey==`ECSSecurityGroup`].OutputValue' `
    --output text `
    --region $REGION)

# Service MongoDB (sous-réseaux privés, pas d'IP publique)
aws ecs create-service `
    --cluster weather-pipeline-cluster `
    --service-name mongodb `
    --task-definition weather-mongodb `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNET1,$PRIVATE_SUBNET2],securityGroups=[$ECS_SG],assignPublicIp=DISABLED}" `
    --enable-execute-command `
    --region $REGION

# Service Mongo Express (sous-réseaux publics avec IP publique pour accès web)
aws ecs create-service `
    --cluster weather-pipeline-cluster `
    --service-name mongo-express `
    --task-definition weather-mongo-express `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$PUBLIC_SUBNET1,$PUBLIC_SUBNET2],securityGroups=[$ECS_SG],assignPublicIp=ENABLED}" `
    --enable-execute-command `
    --region $REGION

# Service MongoDB Importer (sous-réseaux privés, long-running)
aws ecs create-service `
    --cluster weather-pipeline-cluster `
    --service-name mongodb-importer `
    --task-definition weather-importer `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNET1,$PRIVATE_SUBNET2],securityGroups=[$ECS_SG],assignPublicIp=DISABLED}" `
    --enable-execute-command `
    --region $REGION

# Service S3 Cleanup (sous-réseaux privés, long-running)
aws ecs create-service `
    --cluster weather-pipeline-cluster `
    --service-name s3-cleanup `
    --task-definition weather-s3-cleanup `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNET1,$PRIVATE_SUBNET2],securityGroups=[$ECS_SG],assignPublicIp=DISABLED}" `
    --enable-execute-command `
    --region $REGION
```

**Note importante :** Les services dans les sous-réseaux privés utilisent la NAT Gateway pour accéder à Internet (S3, ECR, Secrets Manager).

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
# Vérifier l'état des services (après 2-3 minutes)
aws ecs describe-services `
    --cluster weather-pipeline-cluster `
    --services mongodb mongo-express mongodb-importer s3-cleanup `
    --region $REGION `
    --query 'services[*].[serviceName,status,runningCount,desiredCount]' `
    --output table

# Vérifier les tâches en cours d'exécution
aws ecs list-tasks `
    --cluster weather-pipeline-cluster `
    --region $REGION

# Voir les événements des services (pour diagnostiquer les problèmes)
aws ecs describe-services `
    --cluster weather-pipeline-cluster `
    --services mongodb `
    --region $REGION `
    --query 'services[0].events[0:5].[createdAt,message]' `
    --output text

# Voir les logs CloudWatch en temps réel
aws logs tail /ecs/weather-mongodb --follow --region $REGION
aws logs tail /ecs/weather-mongo-express --follow --region $REGION
aws logs tail /ecs/weather-importer --follow --region $REGION
aws logs tail /ecs/weather-s3-cleanup --follow --region $REGION
```

**Services attendus :**
- ✅ `mongodb` : 1/1 running
- ✅ `mongo-express` : 1/1 running
- ✅ `mongodb-importer` : 1/1 running (peut prendre 1-2 min après MongoDB)
- ✅ `s3-cleanup` : 1/1 running (peut prendre 1-2 min après MongoDB)

## 📊 Accès à Mongo Express

Pour accéder à Mongo Express, récupérez l'IP publique de la tâche :

```powershell
# Lister les tâches du service mongo-express
$TASK_ARN = (aws ecs list-tasks `
    --cluster weather-pipeline-cluster `
    --service-name mongo-express `
    --query 'taskArns[0]' `
    --output text `
    --region $REGION)

# Récupérer l'ENI (Elastic Network Interface)
$ENI_ID = (aws ecs describe-tasks `
    --cluster weather-pipeline-cluster `
    --tasks $TASK_ARN `
    --region $REGION `
    --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' `
    --output text)

# Récupérer l'IP publique
$PUBLIC_IP = (aws ec2 describe-network-interfaces `
    --network-interface-ids $ENI_ID `
    --region $REGION `
    --query 'NetworkInterfaces[0].Association.PublicIp' `
    --output text)

Write-Host "Mongo Express accessible sur : http://${PUBLIC_IP}:8081"
```

**Identifiants de connexion :** Utilisez les valeurs définies dans le secret `weather-pipeline/mongo-express-credentials`

## 🔧 Corrections et Problèmes Résolus

### Problèmes rencontrés et solutions

1. **❌ Dépendance circulaire VPC CloudFormation**
   - **Problème :** `ECSSecurityGroup` référençait lui-même dans son ingress, créant une dépendance circulaire
   - **Solution :** Extraction de la règle d'auto-référence dans une ressource `AWS::EC2::SecurityGroupIngress` séparée

2. **❌ Permission CloudWatch Logs manquante**
   - **Problème :** `AccessDeniedException: not authorized to perform: logs:CreateLogGroup`
   - **Solution :** Ajout de la politique `CloudWatchLogsAccess` au rôle `ECSTaskExecutionRole` dans `iam-roles.yaml`

3. **❌ EFS mount error "No such file or directory"**
   - **Problème :** MongoDB ne pouvait pas monter `/mongodb` car le répertoire n'existait pas
   - **Solution :** Création d'un **EFS Access Point** avec le répertoire `/mongodb` pré-créé et permissions MongoDB (UID/GID 999)

4. **❌ Secret S3 non trouvé**
   - **Problème :** Format d'ARN incorrect pour les secrets Secrets Manager
   - **Solution :** Utilisation du format `arn:aws:secretsmanager:REGION:ACCOUNT:secret:NAME:KEY::` sans suffixe de version

### Fichiers corrigés

- ✅ `vpc-infrastructure.yaml` : Règle d'ingress séparée pour éviter dépendance circulaire
- ✅ `iam-roles.yaml` : Permissions CloudWatch Logs ajoutées
- ✅ `task-definition-mongodb.json` : Utilisation d'Access Point EFS au lieu de rootDirectory
- ✅ Toutes les task definitions : ARNs corrects (Account ID, Region, awslogs-region)

## 🔄 Mise à jour des services

```powershell
# Builder une nouvelle version de l'image
docker build -t weather-etl:v2 .
docker tag weather-etl:v2 "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/weather-etl:v2"
docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/weather-etl:v2"

# Mettre à jour la task definition (modifier le JSON et ré-enregistrer)
aws ecs register-task-definition --cli-input-json file://task-definition-importer.json

# Forcer le redéploiement du service avec la nouvelle version
aws ecs update-service `
    --cluster weather-pipeline-cluster `
    --service mongodb-importer `
    --force-new-deployment `
    --region $REGION

# Mettre à jour un stack CloudFormation existant
aws cloudformation update-stack `
    --stack-name weather-pipeline-iam `
    --template-body file://iam-roles.yaml `
    --capabilities CAPABILITY_NAMED_IAM `
    --region $REGION
```

## 🧹 Nettoyage (Suppression complète)

⚠️ **ATTENTION** : Cette procédure supprime TOUTE l'infrastructure. Assurez-vous de sauvegarder vos données MongoDB avant !

```powershell
# Étape 1 : Mettre les services à 0 puis les supprimer
aws ecs update-service --cluster weather-pipeline-cluster --service mongodb --desired-count 0 --region $REGION
aws ecs update-service --cluster weather-pipeline-cluster --service mongo-express --desired-count 0 --region $REGION
aws ecs update-service --cluster weather-pipeline-cluster --service mongodb-importer --desired-count 0 --region $REGION
aws ecs update-service --cluster weather-pipeline-cluster --service s3-cleanup --desired-count 0 --region $REGION

# Attendre 30 secondes que les tâches se terminent
Start-Sleep -Seconds 30

# Supprimer les services
aws ecs delete-service --cluster weather-pipeline-cluster --service mongodb --force --region $REGION
aws ecs delete-service --cluster weather-pipeline-cluster --service mongo-express --force --region $REGION
aws ecs delete-service --cluster weather-pipeline-cluster --service mongodb-importer --force --region $REGION
aws ecs delete-service --cluster weather-pipeline-cluster --service s3-cleanup --force --region $REGION

# Étape 2 : Supprimer le cluster ECS
aws ecs delete-cluster --cluster weather-pipeline-cluster --region $REGION

# Étape 3 : Supprimer l'Access Point et les mount targets EFS
# Lister et supprimer les mount targets
$MOUNT_TARGETS = aws efs describe-mount-targets --file-system-id $EFS_ID --region $REGION --query 'MountTargets[*].MountTargetId' --output text
foreach ($MT in $MOUNT_TARGETS.Split()) {
    aws efs delete-mount-target --mount-target-id $MT --region $REGION
}

# Lister et supprimer les access points
$ACCESS_POINTS = aws efs describe-access-points --file-system-id $EFS_ID --region $REGION --query 'AccessPoints[*].AccessPointId' --output text
foreach ($AP in $ACCESS_POINTS.Split()) {
    aws efs delete-access-point --access-point-id $AP --region $REGION
}

# Attendre 30 secondes que les mount targets soient supprimés
Start-Sleep -Seconds 30

# Supprimer le système de fichiers EFS
aws efs delete-file-system --file-system-id $EFS_ID --region $REGION

# Étape 4 : Supprimer les stacks CloudFormation
aws cloudformation delete-stack --stack-name weather-pipeline-iam --region $REGION
aws cloudformation delete-stack --stack-name weather-pipeline-vpc --region $REGION

# Attendre la suppression complète
aws cloudformation wait stack-delete-complete --stack-name weather-pipeline-iam --region $REGION
aws cloudformation wait stack-delete-complete --stack-name weather-pipeline-vpc --region $REGION

# Étape 5 : Supprimer les secrets Secrets Manager
aws secretsmanager delete-secret --secret-id weather-pipeline/aws-credentials --force-delete-without-recovery --region $REGION
aws secretsmanager delete-secret --secret-id weather-pipeline/mongodb-credentials --force-delete-without-recovery --region $REGION
aws secretsmanager delete-secret --secret-id weather-pipeline/mongo-express-credentials --force-delete-without-recovery --region $REGION
aws secretsmanager delete-secret --secret-id weather-pipeline/s3-config --force-delete-without-recovery --region $REGION

# Étape 6 : Supprimer les repositories ECR et leurs images
aws ecr delete-repository --repository-name weather-etl --force --region $REGION
aws ecr delete-repository --repository-name weather-mongodb --force --region $REGION

Write-Host "✅ Nettoyage complet terminé !"
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
