<#
.SYNOPSIS
    Initialisation locale du projet _orchestration (hors Docker).

.DESCRIPTION
    Ce script :
      1. Charge les variables d'environnement depuis .env
      2. Reinitialise la base de donnees via main.py --reset
      3. Valide la connexion dbt

    A executer une seule fois apres le premier `docker compose up -d`.
    Le venv doit deja exister a l'emplacement indique ci-dessous.

.NOTES
    Venv : C:\Users\aymer\.venvs\orchestration (Python 3.12)
    DB   : localhost:5433 / sport_data
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------

$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvRoot   = "C:\Users\aymer\.venvs\orchestration"
$PythonExe  = Join-Path $VenvRoot "Scripts\python.exe"
$DbtExe     = Join-Path $VenvRoot "Scripts\dbt.exe"
$EnvFile    = Join-Path $ScriptDir ".env"

if (-not (Test-Path $PythonExe)) {
    throw "Python introuvable : $PythonExe -- cree le venv avec : python -m venv $VenvRoot"
}

# ---------------------------------------------------------------------------
# Chargement du fichier .env
# ---------------------------------------------------------------------------

Write-Host "Chargement de $EnvFile..."
foreach ($line in Get-Content $EnvFile) {
    $line = $line.Trim()
    if ($line -eq "" -or $line.StartsWith("#")) { continue }
    $parts = $line -split "=", 2
    if ($parts.Count -eq 2) {
        $key   = $parts[0].Trim()
        $value = $parts[1].Trim()
        # $env: propage la variable aux processus enfants (contrairement a SetEnvironmentVariable Process)
        Set-Item -Path "Env:$key" -Value $value
        Write-Host "  $key = $value"
    }
}

# ---------------------------------------------------------------------------
# Etape 1 : reinitialisation de la base de donnees
# ---------------------------------------------------------------------------

Write-Host ""
Write-Host "=== Etape 1/2 : Reinitialisation de sport_data (main.py --reset) ==="
Push-Location $ScriptDir

$resetArgs = @("main.py", "--reset")
if ($args -contains "--skip-api") {
    $resetArgs += "--skip-api"
    Write-Host "Option --skip-api activee : simulation Strava passee."
}

& $PythonExe @resetArgs
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    throw "main.py --reset a echoue (code $LASTEXITCODE)"
}

# ---------------------------------------------------------------------------
# Etape 2 : validation de la connexion dbt
# ---------------------------------------------------------------------------

Write-Host ""
Write-Host "=== Etape 2/2 : Validation dbt debug ==="
& $DbtExe debug `
    --project-dir (Join-Path $ScriptDir "dbt\sport_data") `
    --profiles-dir (Join-Path $ScriptDir "dbt")

if ($LASTEXITCODE -ne 0) {
    Write-Warning "dbt debug a signale une erreur — verifier profiles.yml et la connexion PostgreSQL."
} else {
    Write-Host "dbt OK."
}

Pop-Location

Write-Host ""
Write-Host "Initialisation terminee."
Write-Host "Le flow sport_data_pipeline est pret a etre execute dans Kestra : http://localhost:9000"
