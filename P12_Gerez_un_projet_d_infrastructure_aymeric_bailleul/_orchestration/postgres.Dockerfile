FROM postgres:16-alpine

# ─── Script d initialisation SQL bake dans l image ───────────────────────────
# Raison : les bind mounts depuis Google Drive echouent sous Docker Desktop
# WSL2. En copiant init-db.sql dans l image, on garantit que la base 'kestra'
# est creee au premier demarrage meme sans volume preexistant.
COPY init-db.sql /docker-entrypoint-initdb.d/01-init.sql
