# ============================================================================
# Script de création de structure de projet
# Auteur: Aymeric Bailleul
# Date: 2025-11-21
# ============================================================================

# ============================================================================
# CONFIGURATION - Modifier uniquement cette ligne
# ============================================================================
$PROJECT_FOLDER_NAME = "P8_Construisez_et_testez_une_infrastructure_de_donnees_aymeric_bailleul"

# ============================================================================
# NE PAS MODIFIER EN DESSOUS DE CETTE LIGNE
# ============================================================================

Write-Host "`n" -NoNewline
Write-Host ("=" * 100) -ForegroundColor Cyan
Write-Host "SCRIPT DE CREATION DE STRUCTURE DE PROJET" -ForegroundColor Cyan
Write-Host ("=" * 100) -ForegroundColor Cyan

# Récupérer le chemin du script (racine du repo)
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "`nRepertoire du script: $SCRIPT_DIR" -ForegroundColor Yellow

# Chemin complet du dossier projet
$PROJECT_PATH = Join-Path $SCRIPT_DIR $PROJECT_FOLDER_NAME

Write-Host "`nCreation de la structure pour: $PROJECT_FOLDER_NAME" -ForegroundColor Green

# ============================================================================
# Création du dossier principal
# ============================================================================
if (-not (Test-Path $PROJECT_PATH)) {
    New-Item -ItemType Directory -Path $PROJECT_PATH -Force | Out-Null
    Write-Host "  [OK] Dossier principal cree: $PROJECT_FOLDER_NAME" -ForegroundColor Green
} else {
    Write-Host "  [INFO] Dossier principal existe deja: $PROJECT_FOLDER_NAME" -ForegroundColor Yellow
}

# ============================================================================
# Création des sous-dossiers _cours et _projet
# ============================================================================
$COURS_PATH = Join-Path $PROJECT_PATH "_cours"
$PROJET_PATH = Join-Path $PROJECT_PATH "_projet"

foreach ($folder in @($COURS_PATH, $PROJET_PATH)) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        $folderName = Split-Path $folder -Leaf
        Write-Host "  [OK] Sous-dossier cree: $folderName" -ForegroundColor Green
    } else {
        $folderName = Split-Path $folder -Leaf
        Write-Host "  [INFO] Sous-dossier existe deja: $folderName" -ForegroundColor Yellow
    }
}

# ============================================================================
# Création des dossiers data et sources dans _cours
# ============================================================================
Write-Host "`nCreation des dossiers dans _cours:" -ForegroundColor Cyan
$COURS_DATA = Join-Path $COURS_PATH "data"
$COURS_SOURCES = Join-Path $COURS_PATH "sources"

foreach ($folder in @($COURS_DATA, $COURS_SOURCES)) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        $folderName = Split-Path $folder -Leaf
        Write-Host "  [OK] _cours\$folderName cree" -ForegroundColor Green
    } else {
        $folderName = Split-Path $folder -Leaf
        Write-Host "  [INFO] _cours\$folderName existe deja" -ForegroundColor Yellow
    }
}

# ============================================================================
# Création des dossiers data et sources dans _projet
# ============================================================================
Write-Host "`nCreation des dossiers dans _projet:" -ForegroundColor Cyan
$PROJET_DATA = Join-Path $PROJET_PATH "data"
$PROJET_SOURCES = Join-Path $PROJET_PATH "sources"

foreach ($folder in @($PROJET_DATA, $PROJET_SOURCES)) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        $folderName = Split-Path $folder -Leaf
        Write-Host "  [OK] _projet\$folderName cree" -ForegroundColor Green
    } else {
        $folderName = Split-Path $folder -Leaf
        Write-Host "  [INFO] _projet\$folderName existe deja" -ForegroundColor Yellow
    }
}

# ============================================================================
# Récapitulatif
# ============================================================================
Write-Host "`n" -NoNewline
Write-Host ("=" * 100) -ForegroundColor Cyan
Write-Host "STRUCTURE CREEE AVEC SUCCES" -ForegroundColor Green
Write-Host ("=" * 100) -ForegroundColor Cyan

Write-Host "`nArborescence creee:" -ForegroundColor Yellow
Write-Host "  $PROJECT_FOLDER_NAME\" -ForegroundColor White
Write-Host "    _cours\" -ForegroundColor White
Write-Host "      data\" -ForegroundColor Gray
Write-Host "      sources\" -ForegroundColor Gray
Write-Host "    _projet\" -ForegroundColor White
Write-Host "      data\" -ForegroundColor Gray
Write-Host "      sources\" -ForegroundColor Gray

Write-Host "`n"
