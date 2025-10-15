# Utilise une image Python slim
FROM python:3.13-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script et les sources
COPY docker_script_bdd.py /app/
COPY docker_tests_bdd.py /app/
COPY sources/ /app/sources/

# Commande d'execution du script
CMD ["sh", "-c", "python ${SCRIPT_TO_RUN}"]
