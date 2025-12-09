# Script de déploiement automatisé sur AWS ECS
# Weather Pipeline - Projet P8

param(
    [Parameter(Mandatory=$false)]
    [string]$Region = "eu-west-1",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "secrets", "infrastructure", "images", "tasks", "services")]
    [string]$Step = "all"
)

# Couleurs pour les messages
function Write-Success { param($Message) Write-Host $Message -ForegroundColor Green }
function Write-Info { param($Message) Write-Host $Message -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host $Message -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host $Message -ForegroundColor Red }

# Vérifier AWS CLI
function Test-AWSCli {
    try {
        aws --version | Out-Null
        Write-Success "✓ AWS CLI trouvé"
        return $true
    }
    catch {
        Write-Error "✗ AWS CLI non trouvé. Installez-le depuis https://aws.amazon.com/cli/"
        return $false
    }
}

# Récupérer l'Account ID
function Get-AWSAccountId {
    try {
        $accountId = aws sts get-caller-identity --query Account --output text
        Write-Success "✓ Account ID: $accountId"
        return $accountId
    }
    catch {
        Write-Error "✗ Impossible de récupérer l'Account ID"
        return $null
    }
}

# Créer les secrets
function New-Secrets {
    param($AccountId, $Region)
    
    Write-Info "`n=== Création des secrets dans Secrets Manager ==="
    
    Write-Host "Entrez vos credentials AWS S3:"
    $awsAccessKey = Read-Host "AWS_ACCESS_KEY_ID"
    $awsSecretKey = Read-Host "AWS_SECRET_ACCESS_KEY" -AsSecureString
    $awsSecretKeyPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($awsSecretKey))
    
    Write-Host "`nEntrez vos credentials MongoDB:"
    $mongoUser = Read-Host "MONGODB_ROOT_USER (default: admin)" 
    if ([string]::IsNullOrEmpty($mongoUser)) { $mongoUser = "admin" }
    $mongoPass = Read-Host "MONGODB_ROOT_PASSWORD" -AsSecureString
    $mongoPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($mongoPass))
    
    Write-Host "`nEntrez vos credentials Mongo Express:"
    $expressUser = Read-Host "MONGO_EXPRESS_USER (default: admin)"
    if ([string]::IsNullOrEmpty($expressUser)) { $expressUser = "admin" }
    $expressPass = Read-Host "MONGO_EXPRESS_PASSWORD" -AsSecureString
    $expressPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($expressPass))
    
    Write-Host "`nEntrez votre configuration S3:"
    $bucketName = Read-Host "S3_BUCKET_NAME"
    
    # Créer les secrets
    $secrets = @{
        "weather-pipeline/aws-credentials" = @{
            "AWS_ACCESS_KEY_ID" = $awsAccessKey
            "AWS_SECRET_ACCESS_KEY" = $awsSecretKeyPlain
        }
        "weather-pipeline/mongodb-credentials" = @{
            "MONGODB_ROOT_USER" = $mongoUser
            "MONGODB_ROOT_PASSWORD" = $mongoPassPlain
        }
        "weather-pipeline/mongo-express-credentials" = @{
            "MONGO_EXPRESS_USER" = $expressUser
            "MONGO_EXPRESS_PASSWORD" = $expressPassPlain
        }
        "weather-pipeline/s3-config" = @{
            "S3_BUCKET_NAME" = $bucketName
            "S3_PREFIX_SOURCE" = "01_raw/"
            "S3_PREFIX_DESTINATION" = "02_cleaned/"
            "S3_PREFIX_ARCHIVE" = "03_archived/"
        }
    }
    
    foreach ($secretName in $secrets.Keys) {
        $secretValue = $secrets[$secretName] | ConvertTo-Json -Compress
        try {
            aws secretsmanager create-secret `
                --name $secretName `
                --secret-string $secretValue `
                --region $Region 2>$null
            Write-Success "✓ Secret créé: $secretName"
        }
        catch {
            Write-Warning "! Secret existe déjà: $secretName (ignoré)"
        }
    }
}

# Déployer l'infrastructure CloudFormation
function Deploy-Infrastructure {
    param($Region)
    
    Write-Info "`n=== Déploiement de l'infrastructure VPC ==="
    
    aws cloudformation create-stack `
        --stack-name weather-pipeline-vpc `
        --template-body file://vpc-infrastructure.yaml `
        --region $Region
    
    Write-Info "Attente de la création du stack VPC..."
    aws cloudformation wait stack-create-complete `
        --stack-name weather-pipeline-vpc `
        --region $Region
    
    Write-Success "✓ VPC créé"
    
    Write-Info "`n=== Déploiement des rôles IAM ==="
    
    aws cloudformation create-stack `
        --stack-name weather-pipeline-iam `
        --template-body file://iam-roles.yaml `
        --capabilities CAPABILITY_NAMED_IAM `
        --region $Region
    
    Write-Info "Attente de la création du stack IAM..."
    aws cloudformation wait stack-create-complete `
        --stack-name weather-pipeline-iam `
        --region $Region
    
    Write-Success "✓ Rôles IAM créés"
}

# Builder et pousser les images
function Push-Images {
    param($AccountId, $Region)
    
    Write-Info "`n=== Build et push des images Docker ==="
    
    # Login ECR
    Write-Info "Connexion à ECR..."
    aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$AccountId.dkr.ecr.$Region.amazonaws.com"
    
    # Créer les repositories
    Write-Info "Création des repositories ECR..."
    aws ecr create-repository --repository-name weather-etl --region $Region 2>$null
    aws ecr create-repository --repository-name weather-mongodb --region $Region 2>$null
    
    # Build et push ETL
    Write-Info "Build de l'image weather-etl..."
    docker build -t weather-etl:latest ..
    docker tag weather-etl:latest "$AccountId.dkr.ecr.$Region.amazonaws.com/weather-etl:latest"
    docker push "$AccountId.dkr.ecr.$Region.amazonaws.com/weather-etl:latest"
    Write-Success "✓ Image weather-etl poussée"
    
    # Build et push MongoDB
    Write-Info "Build de l'image weather-mongodb..."
    docker build -t weather-mongodb:latest -f Dockerfile.mongodb ..
    docker tag weather-mongodb:latest "$AccountId.dkr.ecr.$Region.amazonaws.com/weather-mongodb:latest"
    docker push "$AccountId.dkr.ecr.$Region.amazonaws.com/weather-mongodb:latest"
    Write-Success "✓ Image weather-mongodb poussée"
}

# Créer le cluster ECS
function New-ECSCluster {
    param($Region)
    
    Write-Info "`n=== Création du cluster ECS ==="
    
    aws ecs create-cluster `
        --cluster-name weather-pipeline-cluster `
        --region $Region `
        --capacity-providers FARGATE FARGATE_SPOT `
        --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1
    
    Write-Success "✓ Cluster ECS créé"
}

# Remplacer les placeholders dans les fichiers
function Update-TaskDefinitions {
    param($AccountId, $Region)
    
    Write-Info "`n=== Mise à jour des Task Definitions ==="
    
    $files = @(
        "task-definition-mongodb.json",
        "task-definition-mongo-express.json",
        "task-definition-etl.json",
        "task-definition-importer.json",
        "task-definition-s3-cleanup.json"
    )
    
    foreach ($file in $files) {
        $content = Get-Content $file -Raw
        $content = $content -replace "ACCOUNT_ID", $AccountId
        $content = $content -replace "REGION", $Region
        $content | Set-Content "$file.temp"
        Write-Success "✓ Mis à jour: $file"
    }
}

# Enregistrer les Task Definitions
function Register-TaskDefinitions {
    param($Region)
    
    Write-Info "`n=== Enregistrement des Task Definitions ==="
    
    $files = @(
        "task-definition-mongodb.json.temp",
        "task-definition-mongo-express.json.temp",
        "task-definition-etl.json.temp",
        "task-definition-importer.json.temp",
        "task-definition-s3-cleanup.json.temp"
    )
    
    foreach ($file in $files) {
        if (Test-Path $file) {
            aws ecs register-task-definition --cli-input-json file://$file --region $Region
            Write-Success "✓ Enregistré: $file"
        }
    }
}

# Script principal
Write-Info "=== Déploiement Weather Pipeline sur AWS ECS ==="
Write-Info "Région: $Region"

if (-not (Test-AWSCli)) {
    exit 1
}

$accountId = Get-AWSAccountId
if ($null -eq $accountId) {
    exit 1
}

switch ($Step) {
    "all" {
        New-Secrets -AccountId $accountId -Region $Region
        Deploy-Infrastructure -Region $Region
        New-ECSCluster -Region $Region
        Push-Images -AccountId $accountId -Region $Region
        Update-TaskDefinitions -AccountId $accountId -Region $Region
        Register-TaskDefinitions -Region $Region
        Write-Success "`n=== Déploiement terminé ! ==="
    }
    "secrets" {
        New-Secrets -AccountId $accountId -Region $Region
    }
    "infrastructure" {
        Deploy-Infrastructure -Region $Region
    }
    "images" {
        Push-Images -AccountId $accountId -Region $Region
    }
    "tasks" {
        Update-TaskDefinitions -AccountId $accountId -Region $Region
        Register-TaskDefinitions -Region $Region
    }
}

Write-Info "`nPour créer les services ECS, suivez les étapes 11-13 du README.md"
