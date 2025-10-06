# Utilise une image Python slim
FROM python:3.13-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances Python
RUN pip install --no-cache-dir pymongo pandas

# Copier le script et les sources
COPY script_bdd.py /app/
COPY sources/ /app/sources/

# Commande d'execution du script
CMD ["python", "script_bdd.py"]
