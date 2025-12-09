# Quick Start - Déploiement AWS ECS

## 🚀 Déploiement rapide (automatisé)

```powershell
cd conf_ecs
.\deploy.ps1 -Region eu-west-1
```

Le script vous demandera interactivement :
- Credentials AWS S3
- Credentials MongoDB
- Credentials Mongo Express  
- Nom du bucket S3

## 📝 Déploiement manuel étape par étape

### 1. Prérequis
```powershell
aws configure
docker --version
```

### 2. Variables
```powershell
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$REGION = "eu-west-1"
```

### 3. Créer les secrets
```powershell
.\deploy.ps1 -Step secrets -Region $REGION
```

### 4. Déployer l'infrastructure
```powershell
.\deploy.ps1 -Step infrastructure -Region $REGION
```

### 5. Créer le cluster ECS
```powershell
aws ecs create-cluster --cluster-name weather-pipeline-cluster --region $REGION
```

### 6. Créer EFS et mount targets
```powershell
$EFS_ID = (aws efs create-file-system --performance-mode generalPurpose --encrypted --region $REGION --query 'FileSystemId' --output text)

# Récupérer subnet IDs depuis CloudFormation
$SUBNET1 = (aws cloudformation describe-stacks --stack-name weather-pipeline-vpc --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnet1`].OutputValue' --output text --region $REGION)
$SUBNET2 = (aws cloudformation describe-stacks --stack-name weather-pipeline-vpc --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnet2`].OutputValue' --output text --region $REGION)
$EFS_SG = (aws cloudformation describe-stacks --stack-name weather-pipeline-vpc --query 'Stacks[0].Outputs[?OutputKey==`EFSSecurityGroup`].OutputValue' --output text --region $REGION)

# Créer mount targets
aws efs create-mount-target --file-system-id $EFS_ID --subnet-id $SUBNET1 --security-groups $EFS_SG --region $REGION
aws efs create-mount-target --file-system-id $EFS_ID --subnet-id $SUBNET2 --security-groups $EFS_SG --region $REGION
```

### 7. Mettre à jour task-definition-mongodb.json
Remplacer `EFS_ID` par la valeur de `$EFS_ID`

### 8. Builder et pousser les images
```powershell
.\deploy.ps1 -Step images -Region $REGION
```

### 9. Enregistrer les task definitions
```powershell
.\deploy.ps1 -Step tasks -Region $REGION
```

### 10. Créer les services
```powershell
# Récupérer les valeurs nécessaires
$SUBNETS = (aws cloudformation describe-stacks --stack-name weather-pipeline-vpc --query 'Stacks[0].Outputs[?contains(OutputKey,`PrivateSubnet`)].OutputValue' --output text --region $REGION) -split '\s+'
$ECS_SG = (aws cloudformation describe-stacks --stack-name weather-pipeline-vpc --query 'Stacks[0].Outputs[?OutputKey==`ECSSecurityGroup`].OutputValue' --output text --region $REGION)

# MongoDB
aws ecs create-service `
    --cluster weather-pipeline-cluster `
    --service-name mongodb `
    --task-definition weather-mongodb `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$($SUBNETS -join ',')],securityGroups=[$ECS_SG],assignPublicIp=DISABLED}" `
    --region $REGION

# Mongo Express
aws ecs create-service `
    --cluster weather-pipeline-cluster `
    --service-name mongo-express `
    --task-definition weather-mongo-express `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$($SUBNETS -join ',')],securityGroups=[$ECS_SG],assignPublicIp=ENABLED}" `
    --region $REGION

# Importer
aws ecs create-service `
    --cluster weather-pipeline-cluster `
    --service-name mongodb-importer `
    --task-definition weather-importer `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$($SUBNETS -join ',')],securityGroups=[$ECS_SG],assignPublicIp=DISABLED}" `
    --region $REGION

# S3 Cleanup
aws ecs create-service `
    --cluster weather-pipeline-cluster `
    --service-name s3-cleanup `
    --task-definition weather-s3-cleanup `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$($SUBNETS -join ',')],securityGroups=[$ECS_SG],assignPublicIp=DISABLED}" `
    --region $REGION
```

## 🔍 Vérification

```powershell
# Status des services
aws ecs describe-services --cluster weather-pipeline-cluster --services mongodb mongo-express mongodb-importer s3-cleanup --region $REGION

# Lister les tâches
aws ecs list-tasks --cluster weather-pipeline-cluster --region $REGION

# Logs
aws logs tail /ecs/weather-mongodb --follow --region $REGION
```

## 🌐 Accès à Mongo Express

```powershell
# Récupérer l'IP publique
$TASK_ARN = (aws ecs list-tasks --cluster weather-pipeline-cluster --service-name mongo-express --query 'taskArns[0]' --output text --region $REGION)
$ENI_ID = (aws ecs describe-tasks --cluster weather-pipeline-cluster --tasks $TASK_ARN --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text --region $REGION)
$PUBLIC_IP = (aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --query 'NetworkInterfaces[0].Association.PublicIp' --output text --region $REGION)

Write-Host "Mongo Express: http://$PUBLIC_IP:8081"
```

## 🧹 Nettoyage

```powershell
# Supprimer les services
aws ecs delete-service --cluster weather-pipeline-cluster --service mongodb --force --region $REGION
aws ecs delete-service --cluster weather-pipeline-cluster --service mongo-express --force --region $REGION
aws ecs delete-service --cluster weather-pipeline-cluster --service mongodb-importer --force --region $REGION
aws ecs delete-service --cluster weather-pipeline-cluster --service s3-cleanup --force --region $REGION

# Attendre que les services soient supprimés
Start-Sleep -Seconds 60

# Supprimer le cluster
aws ecs delete-cluster --cluster weather-pipeline-cluster --region $REGION

# Supprimer les stacks CloudFormation
aws cloudformation delete-stack --stack-name weather-pipeline-iam --region $REGION
aws cloudformation delete-stack --stack-name weather-pipeline-vpc --region $REGION

# Supprimer EFS
aws efs delete-file-system --file-system-id $EFS_ID --region $REGION

# Supprimer les secrets
aws secretsmanager delete-secret --secret-id weather-pipeline/aws-credentials --force-delete-without-recovery --region $REGION
aws secretsmanager delete-secret --secret-id weather-pipeline/mongodb-credentials --force-delete-without-recovery --region $REGION
aws secretsmanager delete-secret --secret-id weather-pipeline/mongo-express-credentials --force-delete-without-recovery --region $REGION
aws secretsmanager delete-secret --secret-id weather-pipeline/s3-config --force-delete-without-recovery --region $REGION
```

## 📚 Fichiers de configuration

- `README.md` : Documentation complète
- `QUICKSTART.md` : Ce fichier (guide rapide)
- `vpc-infrastructure.yaml` : CloudFormation VPC
- `iam-roles.yaml` : CloudFormation IAM
- `task-definition-*.json` : Définitions de tâches ECS
- `Dockerfile.mongodb` : Image MongoDB personnalisée
- `deploy.ps1` : Script de déploiement automatisé
