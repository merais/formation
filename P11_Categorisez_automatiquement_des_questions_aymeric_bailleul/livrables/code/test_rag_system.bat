@echo off
setlocal enabledelayedexpansion
:: ============================================================
:: P11 - RAG Chatbot Puls-Events
:: Execution de la suite de tests
::   tests\test_00_environnement.py
::   tests\test_01_preprocessing.py
::   tests\test_02_vectorstore.py
::   tests\test_03_chunking.py
::   tests\test_04_rag_system.py
:: Auteur : Aymeric Bailleul
:: ============================================================

cd /d "%~dp0"

echo.
echo ============================================================
echo  P11 - RAG Chatbot Puls-Events
echo  Suite de tests
echo  Repertoire de travail : %CD%
echo ============================================================
echo.

:: Verifier que le .venv existe
if not exist ".venv\Scripts\python.exe" (
    echo ERREUR : environnement virtuel introuvable.
    echo Lancez setup_rag_from_scratch.bat pour initialiser le projet.
    echo.
    pause
    exit /b 1
)

:: Verifier que le dossier tests existe
if not exist "tests\" (
    echo ERREUR : dossier tests\ introuvable.
    echo.
    pause
    exit /b 1
)

:: Verifier que pytest est disponible
.venv\Scripts\python.exe -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR : pytest introuvable dans le .venv.
    echo Verifiez que les dependances de developpement sont installees :
    echo   poetry install
    echo.
    pause
    exit /b 1
)

:: Creer le dossier de logs si absent
if not exist "logs\tests" mkdir "logs\tests"

:: Nom du fichier log horodate
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set "DT=%%I"
set "TIMESTAMP=!DT:~0,8!_!DT:~8,6!"
set "LOG_FILE=logs\tests\!TIMESTAMP!_full_tests_rag.log"

echo Lancement des tests...
echo Log : %LOG_FILE%
echo.
echo ============================================================
echo  DEBUT DES TESTS  -  %date% %time%
echo ============================================================
echo.

:: Initialiser le log en UTF-8 sans BOM via .NET
powershell -NoProfile -Command "[System.IO.File]::WriteAllText('!LOG_FILE!', \"============================================================`r`n FULL TESTS RAG  -  %date% %time%`r`n============================================================`r`n\", [System.Text.UTF8Encoding]::new($false))"

.venv\Scripts\python.exe -m pytest tests\ -v 2>&1 | powershell -NoProfile -Command "$w = [System.IO.StreamWriter]::new('!LOG_FILE!', $true, [System.Text.UTF8Encoding]::new($false)); try { $input | ForEach-Object { Write-Host $_; $w.WriteLine($_) } } finally { $w.Close() }"

set "EXIT_CODE=!ERRORLEVEL!"

:: Footer UTF-8 via StreamWriter
powershell -NoProfile -Command "$w = [System.IO.StreamWriter]::new('!LOG_FILE!', $true, [System.Text.UTF8Encoding]::new($false)); $w.WriteLine(''); $w.WriteLine('FIN  -  ' + (Get-Date -Format 'dd/MM/yyyy HH:mm:ss,ff')); $w.Close()"

echo.
echo ============================================================
echo  FIN DES TESTS  -  %date% %time%
echo ============================================================

if !EXIT_CODE! neq 0 (
    echo.
    echo ECHEC - Un ou plusieurs tests ont echoue ^(code : !EXIT_CODE!^).
    echo Log : !LOG_FILE!
) else (
    echo.
    echo SUCCES - Tous les tests sont passes.
    echo Log : !LOG_FILE!
)

echo.
pause
endlocal
