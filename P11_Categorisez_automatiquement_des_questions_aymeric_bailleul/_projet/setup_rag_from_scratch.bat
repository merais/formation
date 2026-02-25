@echo off
setlocal enabledelayedexpansion
:: ============================================================
:: P11 - RAG Chatbot Puls-Events
:: Initialisation complete depuis zero
::   1. Telecharge le dataset Open Agenda (si absent)
::   2. Lance le pipeline complet de build du vectorstore
:: Auteur : Aymeric Bailleul
:: Duree estimee : 10-15 minutes (hors telechargement)
:: ============================================================

:: Se placer dans le dossier _projet/
cd /d "%~dp0"

echo.
echo ============================================================
echo  P11 - RAG Chatbot Puls-Events
echo  Initialisation complete depuis zero
echo  Repertoire de travail : %CD%
echo ============================================================
echo.

:: ------------------------------------------------------------
:: PREREQUIS : Verification avant de commencer
:: ------------------------------------------------------------
echo Verification des prerequis systeme...
echo.
set "PREREQ_OK=1"

:: Python 3.11+
set "PYTHON_CMD=python"
set "PYTHON_EXE="
where python >nul 2>&1
if errorlevel 1 (
    echo   [KO] Python introuvable dans le PATH.
    echo        Installez Python 3.11 depuis https://www.python.org/downloads/
    set "PREREQ_OK=0"
) else (
    for /f "tokens=2 delims= " %%V in ('python --version 2^>^&1') do set "PY_VER=%%V"
    for /f "tokens=1,2 delims=." %%A in ("!PY_VER!") do (
        set "PY_MAJOR=%%A"
        set "PY_MINOR=%%B"
    )
    if !PY_MAJOR! lss 3 (
        set "PY_OK=0"
    ) else if !PY_MAJOR! equ 3 if !PY_MINOR! lss 11 (
        set "PY_OK=0"
    ) else (
        set "PY_OK=1"
    )
    if "!PY_OK!"=="0" (
        :: python trop vieux, essayer le Python Launcher Windows
        where py >nul 2>&1
        if not errorlevel 1 (
            py -3.11 --version >nul 2>&1
            if not errorlevel 1 (
                for /f "tokens=2 delims= " %%V in ('py -3.11 --version 2^>^&1') do set "PY_VER=%%V"
                :: Resoudre le chemin absolu pour poetry env use
                for /f "delims=" %%P in ('py -3.11 -c "import sys; print(sys.executable)"') do set "PYTHON_EXE=%%P"
                set "PYTHON_CMD=py -3.11"
                set "PY_OK=1"
                echo   [OK] Python !PY_VER! ^(via py -3.11^)
                echo        Chemin : !PYTHON_EXE!
                echo        Note : 'python' dans le PATH pointe vers une version plus ancienne.
            )
        )
        if "!PY_OK!"=="0" (
            echo   [KO] Python !PY_VER! detecte - version 3.11 minimum requise.
            echo        Si Python 3.11 est installe, verifiez que son dossier est en premier dans le PATH.
            echo        Ou installez Python 3.11 depuis https://www.python.org/downloads/
            set "PREREQ_OK=0"
        )
    ) else (
        echo   [OK] Python !PY_VER!
    )
)

:: Poetry
where poetry >nul 2>&1
if errorlevel 1 (
    echo   [KO] Poetry introuvable dans le PATH.
    echo        Installez Poetry depuis https://python-poetry.org/docs/
    set "PREREQ_OK=0"
) else (
    for /f "tokens=*" %%V in ('poetry --version 2^>^&1') do set "POETRY_VER=%%V"
    echo   [OK] !POETRY_VER!
)

:: Connexion internet (test HTTPS sur pypi.org)
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'https://pypi.org' -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop; exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
    echo   [KO] Impossible d'atteindre https://pypi.org en HTTPS.
    echo        Une connexion internet est requise pour telecharger les dependances.
    echo        Verifiez votre pare-feu, proxy ou connexion reseau.
    set "PREREQ_OK=0"
) else (
    echo   [OK] Connexion internet disponible ^(HTTPS pypi.org OK^)
)

:: Scripts source obligatoires
if not exist "src\build_vectorstore.py" (
    echo   [KO] src\build_vectorstore.py introuvable.
    echo        Le dossier src\ avec tous les scripts Python doit etre present.
    set "PREREQ_OK=0"
) else (
    echo   [OK] Scripts source detectes
)
if not exist "launch_rag_interface.bat" (
    echo   [KO] launch_rag_interface.bat introuvable.
    echo        Recuperez le script depuis le depot et relancez.
    set "PREREQ_OK=0"
)
if not exist "pyproject.toml" (
    echo   [KO] pyproject.toml introuvable.
    echo        Le fichier pyproject.toml doit etre present a la racine du projet.
    set "PREREQ_OK=0"
) else (
    echo   [OK] pyproject.toml detecte
)

echo.
if "!PREREQ_OK!"=="0" (
    echo ARRET : un ou plusieurs prerequis sont manquants.
    echo Corrigez les problemes ci-dessus puis relancez le script.
    echo.
    pause
    exit /b 1
)
echo Tous les prerequis sont satisfaits. Demarrage...
echo.

:: ------------------------------------------------------------
:: VERIFICATION 1 : Environnement virtuel
:: ------------------------------------------------------------
echo [1/5] Verification de l'environnement virtuel...
if not exist ".venv\Scripts\python.exe" (
    echo.
    echo ATTENTION : environnement virtuel introuvable.
    echo.
    set /p "INSTALL_ENV=Voulez-vous l'installer maintenant avec Poetry ? (O/N) : "
    if /i "!INSTALL_ENV!"=="O" (
        echo.
        echo Configuration de Poetry pour creer le .venv dans le projet...
        poetry config virtualenvs.in-project true
        if errorlevel 1 (
            echo ATTENTION : Impossible de configurer virtualenvs.in-project. Continuation...
        )
        if not "!PYTHON_EXE!"=="" (
            echo Specification de l'interpreteur Python pour Poetry : !PYTHON_EXE!
            poetry env use "!PYTHON_EXE!"
            if errorlevel 1 (
                echo.
                echo ERREUR : Impossible de configurer Poetry avec !PYTHON_EXE!
                echo.
                pause
                exit /b 1
            )
        )
        echo Installation des dependances ^(pyproject.toml^)...
        poetry install --no-root
        if errorlevel 1 (
            echo.
            echo ERREUR : L'installation Poetry a echoue.
            echo Causes possibles :
            echo   - Pare-feu ou proxy bloquant l'acces a PyPI en HTTPS
            echo   - Python 3.11 mal configure dans Poetry
            echo   - pyproject.toml invalide
            echo Conseil : relancez en activant les logs : poetry install --no-root -v
            echo.
            pause
            exit /b 1
        )
        echo.
        echo OK - Environnement virtuel installe dans .venv\
    ) else (
        echo.
        echo Installation annulee.
        echo.
        echo Pour installer manuellement l'environnement :
        echo   1. Ouvrez un terminal dans ce dossier ^(_projet^)
        echo   2. Executez : poetry config virtualenvs.in-project true
        echo   3. Executez : poetry install --no-root
        echo   4. Relancez ce script.
        echo.
        echo Si Poetry n'est pas installe : https://python-poetry.org/docs/
        echo.
        pause
        exit /b 1
    )
)
echo       OK - .venv detecte
echo.

:: ------------------------------------------------------------
:: VERIFICATION 2 : Cle API Mistral
:: ------------------------------------------------------------
echo [2/5] Verification du fichier .env...
if not exist ".env" (
    echo.
    echo ATTENTION : fichier .env manquant.
    echo.
    set /p "CREATE_ENV=Voulez-vous creer le fichier .env maintenant ? (O/N) : "
    if /i "!CREATE_ENV!"=="O" (
        echo.
        set /p "API_KEY=Entrez votre MISTRAL_API_KEY : "
        if "!API_KEY!"=="" (
            echo MISTRAL_API_KEY=> .env
            echo.
            echo ATTENTION : fichier .env cree mais la cle est vide.
            echo Le pipeline va continuer mais echouera lors de l'appel a l'API Mistral.
            echo Editez le fichier .env et renseignez votre MISTRAL_API_KEY avant de relancer.
        ) else (
            echo MISTRAL_API_KEY=!API_KEY!> .env
            echo.
            echo OK - Fichier .env cree avec la cle fournie.
        )
    ) else (
        echo.
        echo Creation annulee.
        echo.
        echo Pour creer le fichier .env manuellement :
        echo   1. Creer un fichier nomme ".env" a la racine du projet ^(_projet^)
        echo   2. Y ajouter la ligne : MISTRAL_API_KEY=votre_cle_api_mistral
        echo.
        echo Pour obtenir une cle API Mistral :
        echo   https://console.mistral.ai/ ^> API Keys ^> Create new key
        echo.
        echo   Relancez ce script une fois le fichier .env cree.
        echo.
        pause
        exit /b 1
    )
)
findstr /i "MISTRAL_API_KEY" .env >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERREUR : MISTRAL_API_KEY absente du fichier .env.
    echo Ajoutez la ligne : MISTRAL_API_KEY=votre_cle_api_mistral
    echo.
    pause
    exit /b 1
)
echo       OK - .env et MISTRAL_API_KEY detectes
echo.

:: ------------------------------------------------------------
:: VERIFICATION 3 : Dataset brut Open Agenda (telechargement si absent)
:: ------------------------------------------------------------
echo [3/5] Verification du dataset brut Open Agenda...

set "RAW_DIR=data\raw"
set "RAW_FILE=%RAW_DIR%\evenements-publics-openagenda.parquet"
set "DOWNLOAD_URL=https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/exports/parquet/?lang=fr&timezone=Europe%%2FParis"
set "MIN_SIZE_BYTES=800000000"

if not exist "%RAW_DIR%" (
    echo       Creation du dossier %RAW_DIR%...
    mkdir "%RAW_DIR%"
)

set "NEED_DOWNLOAD=0"
if not exist "%RAW_FILE%" (
    set "NEED_DOWNLOAD=1"
) else (
    for %%A in ("%RAW_FILE%") do set "FILE_SIZE=%%~zA"
    set /a "FILE_MB=!FILE_SIZE! / 1048576"
    if !FILE_SIZE! LSS %MIN_SIZE_BYTES% (
        echo       ATTENTION : Fichier present mais trop petit ^(!FILE_MB! MB^) - probablement corrompu.
        echo       Suppression et re-telechargement...
        del "%RAW_FILE%"
        set "NEED_DOWNLOAD=1"
    ) else (
        echo       OK - Dataset present : %RAW_FILE% ^(!FILE_MB! MB^)
    )
)

if !NEED_DOWNLOAD! EQU 1 (
    echo       Dataset absent ou corrompu. Telechargement depuis Open Agenda...
    echo       URL : %DOWNLOAD_URL%
    echo       Taille attendue : ~905 MB - cela peut prendre plusieurs minutes.
    echo.
    :: curl.exe (Windows 10+) est plus fiable que Invoke-WebRequest pour les gros fichiers binaires
    where curl.exe >nul 2>&1
    if not errorlevel 1 (
        curl.exe -L --progress-bar -o "%RAW_FILE%" "%DOWNLOAD_URL%"
    ) else (
        echo       curl.exe absent, utilisation de WebClient PowerShell...
        powershell -NoProfile -Command ^
            "(New-Object System.Net.WebClient).DownloadFile('%DOWNLOAD_URL%', '%RAW_FILE%'); Write-Host 'Telechargement termine.'"
    )
    if errorlevel 1 (
        echo.
        echo ERREUR : Telechargement echoue.
        echo Verifiez votre connexion internet et relancez le script.
        echo.
        pause
        exit /b 1
    )
    if not exist "%RAW_FILE%" (
        echo.
        echo ERREUR : Le fichier n'a pas ete cree apres telechargement.
        echo.
        pause
        exit /b 1
    )
    echo       OK - Dataset telecharge : %RAW_FILE%
)
echo.

:: ------------------------------------------------------------
:: CREATION des dossiers de sortie si besoin
:: ------------------------------------------------------------
echo [4/5] Preparation des dossiers de sortie...
if not exist "data\processed"   mkdir "data\processed"
if not exist "data\vectorstore" mkdir "data\vectorstore"
if not exist "data\evaluation"  mkdir "data\evaluation"
if not exist "logs\setup"       mkdir "logs\setup"
echo       OK - Dossiers data\processed, data\vectorstore, data\evaluation, logs\setup prets
echo.

:: ------------------------------------------------------------
:: PIPELINE BUILD VECTORSTORE
:: ------------------------------------------------------------
echo [5/5] Lancement du pipeline complet de build du vectorstore...

:: Guard : vectorstore deja present ?
if exist "data\vectorstore\faiss_index.bin" (
    echo.
    echo ATTENTION : un vectorstore existe deja dans data\vectorstore\.
    echo Le relancer va ecraser l'index FAISS existant et consommer des appels API Mistral.
    echo.
    set /p "CONFIRM_REBUILD=Voulez-vous vraiment relancer le pipeline complet ? (O/N) : "
    if /i not "!CONFIRM_REBUILD!"=="O" (
        echo.
        echo Pipeline annule. Le vectorstore existant est conserve.
        echo.
        echo Si vous souhaitez reconstruire le vectorstore plus tard :
        echo   Relancez ce script et repondez O a la question de confirmation.
        echo.
        echo Pour lancer l'interface Streamlit avec le vectorstore actuel :
        echo   Executez launch_rag_interface.bat
        echo.
        pause >nul
        endlocal
        exit /b 0
    )
    echo.
)

echo       Etapes :
echo         1. Nettoyage des donnees       (clean_data.py)
echo         2. Decoupage en chunks         (chunk_texts.py)
echo         3. Vectorisation Mistral       (vectorize_data.py)  ~4 min
echo         4. Creation index FAISS        (create_faiss_index.py)
echo.
echo ============================================================
echo  DEBUT DU PIPELINE  -  %date% %time%
echo ============================================================
echo.

:: Nom du fichier log horodate
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set "DT=%%I"
set "TIMESTAMP=!DT:~0,8!_!DT:~8,6!"
set "LOG_FILE=logs\setup\!TIMESTAMP!_full_install.log"
echo Log : !LOG_FILE!
echo.

:: Timestamp de debut dans le log
echo ============================================================ > "!LOG_FILE!"
echo  SETUP RAG FROM SCRATCH  -  %date% %time% >> "!LOG_FILE!"
echo ============================================================ >> "!LOG_FILE!"

:: Forcer UTF-8 pour eviter UnicodeEncodeError avec les caracteres speciaux
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

:: Lancement du pipeline (sortie visible dans le terminal ET dans le log)
.venv\Scripts\python.exe src\build_vectorstore.py 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -Append -FilePath '!LOG_FILE!'"

set "EXIT_CODE=!ERRORLEVEL!"
echo. >> "!LOG_FILE!"
echo FIN  -  %date% %time% >> "!LOG_FILE!"

echo.
echo ============================================================
echo  FIN DU PIPELINE  -  %date% %time%
echo ============================================================

if !EXIT_CODE! neq 0 (
    echo.
    echo ECHEC - Code erreur : !EXIT_CODE!
    echo Consultez le log complet : !LOG_FILE!
) else (
    echo.
    echo SUCCES - Le vectorstore est pret.
    echo Log complet disponible : !LOG_FILE!
    echo.
    echo Pour lancer l'interface Streamlit :
    echo   Executez le script launch_rag_interface.bat
)

echo.
echo ============================================================
echo  Appuyez sur une touche pour fermer cette fenetre...
echo ============================================================
pause >nul
endlocal
