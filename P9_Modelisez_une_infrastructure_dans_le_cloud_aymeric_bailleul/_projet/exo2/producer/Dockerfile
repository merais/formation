FROM python:3.11-slim

WORKDIR /app

# Copier les requirements et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script producteur
COPY producer.py .

# Désactiver le buffering Python pour les logs en temps réel
ENV PYTHONUNBUFFERED=1

# Commande pour lancer le producteur avec -u (unbuffered)
CMD ["python", "-u", "producer.py"]
