# Script de gestion du cluster ECS weather-pipeline
# Permet de mettre en pause ou redémarrer le cluster pour optimiser les coûts

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("pause", "resume", "status")]
    [string]$Action
)

# Configuration
$Region = "eu-west-1"
$ClusterName = "weather-pipeline-cluster"
$Services = @("weather-etl", "mongodb-importer", "s3-cleanup", "mongodb", "mongo-express")

# Couleurs
function Write-Info { param($Message) Write-Host $Message -ForegroundColor Cyan }
function Write-Success { param($Message) Write-Host $Message -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host $Message -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host $Message -ForegroundColor Red }

# Vérifier les credentials AWS
if (-not $env:AWS_ACCESS_KEY_ID -or -not $env:AWS_SECRET_ACCESS_KEY) {
    Write-Error "`n❌ Variables d'environnement AWS non configurées"
    Write-Info "`nConfigurer les credentials admin:"
    Write-Host '  $env:AWS_ACCESS_KEY_ID="AKIAU74V2YN4QRLU3TNJ"'
    Write-Host '  $env:AWS_SECRET_ACCESS_KEY="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"'
    Write-Host '  $env:AWS_DEFAULT_REGION="eu-west-1"'
    exit 1
}

switch ($Action) {
    "pause" {
        Write-Warning "`n⏸️  MISE EN PAUSE DU CLUSTER"
        Write-Warning "════════════════════════════════════════════════`n"
        
        foreach ($service in $Services) {
            Write-Info "  ⏸️  Arrêt de $service..."
            aws ecs update-service `
                --cluster $ClusterName `
                --service $service `
                --desired-count 0 `
                --region $Region `
                --output text | Out-Null
            Write-Success "    ✓ $service mis en pause (desired=0)"
        }
        
        Write-Success "`n✅ Cluster mis en pause - Facturation arrêtée"
        Write-Info "`n💡 Pour redémarrer: .\manage_cluster.ps1 resume"
    }
    
    "resume" {
        Write-Info "`n▶️  REDÉMARRAGE DU CLUSTER"
        Write-Info "════════════════════════════════════════════════`n"
        
        foreach ($service in $Services) {
            Write-Info "  ▶️  Démarrage de $service..."
            aws ecs update-service `
                --cluster $ClusterName `
                --service $service `
                --desired-count 1 `
                --region $Region `
                --output text | Out-Null
            Write-Success "    ✓ $service redémarré (desired=1)"
        }
        
        Write-Success "`n✅ Cluster redémarré"
        Write-Warning "`n⏳ Attendre 1-2 minutes pour que tous les services soient opérationnels"
        Write-Info "`n💡 Pour vérifier l'état: .\manage_cluster.ps1 status"
    }
    
    "status" {
        Write-Info "`n📊 ÉTAT DU CLUSTER"
        Write-Info "════════════════════════════════════════════════`n"
        
        $table = aws ecs describe-services `
            --cluster $ClusterName `
            --services $Services `
            --region $Region `
            --query 'services[].[serviceName,status,runningCount,desiredCount]' `
            --output table
        
        Write-Host $table
        
        # Calculer le coût estimé
        $runningTasks = (aws ecs describe-services `
            --cluster $ClusterName `
            --services $Services `
            --region $Region `
            --query 'sum(services[].runningCount)' `
            --output text)
        
        Write-Info "`n💰 Estimation des coûts:"
        if ($runningTasks -eq 0) {
            Write-Success "   ✓ Cluster en pause - Pas de facturation Fargate"
        } else {
            Write-Warning "   ⚠️  $runningTasks tâche(s) en cours"
            Write-Host "   → ~$([math]::Round($runningTasks * 0.04 * 24 * 30, 2)) USD/mois (estimation)"
        }
        
        Write-Info "`n📍 Ressources persistantes (toujours facturées):"
        Write-Host "   • ECR: 2 images (~0.10 USD/mois/GB)"
        Write-Host "   • S3: Bucket p8-weather-data (~0.023 USD/mois/GB)"
        Write-Host "   • CloudWatch Logs: Logs ECS (~0.50 USD/mois/GB)"
        
        Write-Info "`n💡 Commandes:"
        Write-Host "   Pause:  .\manage_cluster.ps1 pause"
        Write-Host "   Resume: .\manage_cluster.ps1 resume"
    }
}
