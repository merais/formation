# Cheatsheet : Connecter PostgreSQL Local à Airbyte (Docker)

Ce guide détaille la procédure pour connecter une base de données PostgreSQL hébergée sur la machine hôte (Windows) à une instance Airbyte tournant dans un conteneur Docker, en utilisant la méthode CDC (Change Data Capture).

## 1. Configuration des fichiers PostgreSQL

Avant de toucher à la base de données, il faut configurer l'instance PostgreSQL pour accepter les connexions externes et activer la réplication logique.

### A. Modifier `postgresql.conf`
*Localisation typique : `C:\Program Files\PostgreSQL\<version>\data\postgresql.conf`*

Modifiez ou ajoutez les lignes suivantes :

```ini
# Écouter sur toutes les interfaces (pour que Docker puisse se connecter)
listen_addresses = '*'

# Activer le niveau de log nécessaire pour le CDC
wal_level = logical

# Nombre minimum de slots et senders (1 suffit pour Airbyte seul)
max_replication_slots = 1
max_wal_senders = 1
```

### B. Modifier `pg_hba.conf`
*Localisation typique : `C:\Program Files\PostgreSQL\<version>\data\pg_hba.conf`*

Ajoutez cette ligne à la fin du fichier pour autoriser l'authentification depuis le réseau Docker :

```text
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    all             all             0.0.0.0/0               scram-sha-256
```
*(Note : Remplacez `scram-sha-256` par `md5` si vous utilisez une vieille version de Postgres).*

### C. Redémarrer le service
Ouvrez l'application "Services" de Windows, trouvez **PostgreSQL**, et faites **Redémarrer**.

---

## 2. Configuration SQL (Remise à zéro & Activation)

Exécutez ce script SQL sur votre base de données cible (ex: `SuperSmartMarket_origine`).
Ce script nettoie toute configuration existante (pour éviter les conflits) et recrée proprement les éléments nécessaires.

**Attention :** Remplacez `votre_utilisateur` par le user utilisé dans Airbyte (ex: `postgres`).

```sql
-- ==========================================
-- 1. NETTOYAGE (Remise à zéro)
-- ==========================================

-- Supprimer le slot de réplication s'il existe déjà
SELECT pg_drop_replication_slot('airbyte_slot') 
WHERE EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'airbyte_slot');

-- Supprimer la publication si elle existe
DROP PUBLICATION IF EXISTS airbyte_publication;

-- ==========================================
-- 2. CRÉATION (Configuration Propre)
-- ==========================================

-- Création du Slot de réplication logique
-- Ce slot retient les logs (WAL) pour Airbyte
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');

-- Création de la Publication pour TOUTES les tables
-- Cela inclut automatiquement les futures tables si besoin
CREATE PUBLICATION airbyte_publication FOR ALL TABLES;

-- ==========================================
-- 3. PERMISSIONS
-- ==========================================

-- Donner le droit de réplication à l'utilisateur
ALTER USER votre_utilisateur REPLICATION;

-- S'assurer qu'il peut lire les tables
GRANT USAGE ON SCHEMA public TO votre_utilisateur;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO votre_utilisateur;
```

---

## 3. Configuration dans Airbyte (UI)

Lors de la création de la **Source** PostgreSQL dans Airbyte :

### Paramètres de Connexion
*   **Host** : `host.docker.internal` (C'est l'adresse magique pour accéder à votre PC depuis Docker).
*   **Port** : `5432`
*   **DB Name** : `SuperSmartMarket_origine`
*   **User/Password** : Vos identifiants.

### Paramètres de Réplication
*   **Replication Method** : `Standard (CDC)`
*   **Replication Slot** : `airbyte_slot`
*   **Publication** : `airbyte_publication`

### Résolution d'erreurs courantes

*   **Error: Expected exactly one replication slot but found 0** :
    *   Signifie que le slot n'a pas été créé manuellement ou qu'Airbyte n'a pas les droits pour le créer. -> Exécutez le script SQL ci-dessus.
*   **Connection refused** :
    *   Vérifiez `listen_addresses = '*'` et le redémarrage du service.
    *   Vérifiez que le pare-feu Windows autorise le port 5432.
    *   Utilisez bien `host.docker.internal` et non `localhost`.
