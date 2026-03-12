FROM kestra/kestra:latest

USER root

# ─── Dependances systeme ──────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        libpq-dev \
        gcc \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ─── Environnement Python isole dans /opt/venv ───────────────────────────────
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip --quiet \
    && /opt/venv/bin/pip install --quiet \
        psycopg2-binary \
        pandas \
        openpyxl \
        python-dotenv \
        kestra \
        dbt-postgres==1.10.0

# Rendre le venv accessible a tous les utilisateurs
RUN chmod -R a+rx /opt/venv

# ─── Copie des ressources du projet dans l image ─────────────────────────────
# Raison : les bind mounts depuis Google Drive (G:\Mon Drive) echouent
# silencieusement sous Docker Desktop / WSL2. En copiant les fichiers au
# moment du build (Docker CLI lit depuis Windows), on garantit leur presence.
COPY scripts/         /opt/scripts/
COPY dbt/profiles.yml /opt/dbt/profiles.yml
COPY dbt/sport_data/  /opt/dbt/sport_data/
COPY flows/sport_data_pipeline.yml /opt/flows/sport_data_pipeline.yml
RUN chmod -R a+rx /opt/scripts /opt/dbt /opt/flows \
    && mkdir -p /opt/dbt/sport_data/logs /opt/dbt/sport_data/target \
    && chmod -R a+rwx /opt/dbt/sport_data/logs /opt/dbt/sport_data/target

USER kestra

# Mettre le venv en priorite dans le PATH
ENV PATH="/opt/venv/bin:$PATH"
