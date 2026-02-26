@echo off
:: ============================================================
:: P11 - RAG Chatbot Puls-Events
:: Lancement de l'interface Streamlit
:: Auteur : Aymeric Bailleul
:: Usage  : Double-cliquer ou executer depuis n'importe ou
:: ============================================================

:: Se placer dans le dossier _projet/
cd /d "%~dp0"

:: Verifier que le .venv existe
if not exist ".venv\Scripts\streamlit.exe" (
    echo ERREUR : environnement virtuel introuvable.
    echo Verifiez que .venv existe dans le dossier _projet.
    echo Commande d'installation : poetry install
    pause
    exit /b 1
)

:: Verifier que le fichier chat_interface.py existe
if not exist "src\rag\chat_interface.py" (
    echo ERREUR : src\rag\chat_interface.py introuvable.
    pause
    exit /b 1
)

:: Verifier que le fichier .env existe
if not exist ".env" (
    echo ATTENTION : fichier .env manquant.
    echo Creez un fichier .env avec : MISTRAL_API_KEY=votre_cle_api
    pause
    exit /b 1
)

echo ============================================================
echo  P11 - RAG Chatbot Puls-Events
echo  Lancement de l'interface Streamlit...
echo  URL : http://localhost:8501
echo  Pour arreter : Ctrl+C dans cette fenetre
echo ============================================================
echo.

.venv\Scripts\streamlit.exe run src\rag\chat_interface.py

pause
