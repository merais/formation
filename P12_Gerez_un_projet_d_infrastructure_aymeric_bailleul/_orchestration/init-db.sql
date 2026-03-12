-- init-db.sql
-- Script d'initialisation PostgreSQL execute au premier demarrage du conteneur.
-- Cree la base de donnees 'kestra' utilisee par Kestra pour ses metadonnees internes.
-- La base 'sport_data' est creee par la variable POSTGRES_DB dans docker-compose.yml.

SELECT 'CREATE DATABASE kestra'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'kestra'
)\gexec
