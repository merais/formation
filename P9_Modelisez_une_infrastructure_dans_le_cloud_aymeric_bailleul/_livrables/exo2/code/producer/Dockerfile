FROM python:3.11-slim

WORKDIR /app

# Copier les requirements et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script producteur
COPY producer.py .

# Commande pour lancer le producteur
CMD ["python", "producer.py"]
