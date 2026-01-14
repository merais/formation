FROM eclipse-temurin:11-jre

# Installer Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier les requirements et installer les dépendances
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copier le script consommateur
COPY consumer.py .

# Créer le dossier de sortie
RUN mkdir -p /output

# Commande pour lancer le consommateur
CMD ["python3", "consumer.py"]
