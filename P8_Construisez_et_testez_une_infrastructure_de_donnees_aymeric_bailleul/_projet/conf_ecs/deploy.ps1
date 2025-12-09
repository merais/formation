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

# Charger les variables depuis le fichier .env
function Get-EnvVariables {
    $envFile = Join-Path (Split-Path $PSScriptRoot -Parent) ".env"
    
    if (-not (Test-Path $envFile)) {
        Write-Error "Fichier .env introuvable à : $envFile"
        return $null
    }
    
    Write-Info "Chargement des variables depuis .env..."
    
    $envVars = @{}
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            $envVars[$key] = $value
        }
    }
    
    return $envVars
}

# Créer les secrets
function New-Secrets {
    param($AccountId, $Region)
    
    Write-Info "`n=== Création des secrets dans Secrets Manager ==="
    
    # Charger les variables du .env
    $envVars = Get-EnvVariables
    if ($null -eq $envVars) {
        Write-Error "Impossible de charger le fichier .env"
        return
    }
    
    # Récupérer les valeurs du .env
    $awsAccessKey = $envVars["AWS_ACCESS_KEY_ID"]
    $awsSecretKeyPlain = $envVars["AWS_SECRET_ACCESS_KEY"]
    $mongoUser = $envVars["MONGODB_ROOT_USER"]
    $mongoPassPlain = $envVars["MONGODB_ROOT_PASSWORD"]
    $expressUser = $envVars["MONGO_EXPRESS_USER"]
    $expressPassPlain = $envVars["MONGO_EXPRESS_PASSWORD"]
    $bucketName = $envVars["S3_BUCKET_NAME"]
    
    Write-Success "✓ Credentials chargés depuis .env"
    Write-Info "  - S3 Bucket: $bucketName"
    Write-Info "  - MongoDB User: $mongoUser"
    Write-Info "  - Mongo Express User: $expressUser"
    
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

# Configurer les credentials AWS Admin pour le déploiement
function Set-AWSAdminCredentials {
    Write-Info "`n=== Configuration des credentials AWS Admin ==="
    
    $envVars = Get-EnvVariables
    if ($null -eq $envVars) {
        Write-Error "Impossible de charger le fichier .env"
        return $false
    }
    
    $adminAccessKey = $envVars["AWS_ADMIN_ACCESS_KEY_ID"]
    $adminSecretKey = $envVars["AWS_ADMIN_SECRET_ACCESS_KEY"]
    
    if ([string]::IsNullOrEmpty($adminAccessKey) -or [string]::IsNullOrEmpty($adminSecretKey)) {
        Write-Error "AWS_ADMIN_ACCESS_KEY_ID ou AWS_ADMIN_SECRET_ACCESS_KEY non trouvé dans .env"
        Write-Error "Veuillez ajouter vos credentials admin dans le fichier .env"
        return $false
    }
    
    $env:AWS_ACCESS_KEY_ID = $adminAccessKey
    $env:AWS_SECRET_ACCESS_KEY = $adminSecretKey
    $env:AWS_DEFAULT_REGION = $Region
    
    Write-Success "✓ Credentials AWS Admin configurés"
    return $true
}

# Script principal
Write-Info "=== Déploiement Weather Pipeline sur AWS ECS ==="
Write-Info "Région: $Region"

if (-not (Test-AWSCli)) {
    exit 1
}

# Configurer les credentials admin
if (-not (Set-AWSAdminCredentials)) {
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
