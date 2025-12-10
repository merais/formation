FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY pyproject.toml poetry.lock* ./

# Installer Poetry
RUN pip install --no-cache-dir poetry==1.8.5

# Configurer Poetry pour ne pas créer de virtualenv
RUN poetry config virtualenvs.create false

# Installer les dépendances (ignorer les erreurs de lock)
RUN poetry install --no-interaction --no-ansi --no-root || pip install boto3 pandas python-dotenv pymongo pytest

# Copier le code source
COPY ABAI_P8_script_01_clean_data.py .
COPY ABAI_P8_script_02_import_to_mongodb.py .
COPY ABAI_P8_script_03_test_mongodb.py .
COPY ABAI_P8_script_04_cleanup_s3.py .
COPY ABAI_P8_script_05_benchmark_mongodb.py .
COPY .env* ./

# Commande par défaut
CMD ["python", "ABAI_P8_script_01_clean_data.py"]
