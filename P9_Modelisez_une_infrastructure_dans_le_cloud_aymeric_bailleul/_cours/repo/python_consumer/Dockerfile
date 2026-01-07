# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy consumer script
COPY consumer.py consumer.py

# Command to run
CMD ["python", "consumer.py"]