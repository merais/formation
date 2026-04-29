FROM mysql:8.0

# Copier le script d'initialisation
COPY init.sql /docker-entrypoint-initdb.d/

# S'assurer que le fichier a les bonnes permissions
RUN chmod 644 /docker-entrypoint-initdb.d/init.sql
