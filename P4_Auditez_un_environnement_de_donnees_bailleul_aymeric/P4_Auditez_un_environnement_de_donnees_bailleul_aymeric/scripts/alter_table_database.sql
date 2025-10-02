-- ÉTAPE 1 : RETRAIT DES CLÉS ÉTRANGÈRES ET PRIMAIRES
-- Suppression des contraintes de clés étrangères de la table 'vente_detail'
ALTER TABLE vente_detail DROP CONSTRAINT vente_detail_customer_id_fkey;
ALTER TABLE vente_detail DROP CONSTRAINT vente_detail_id_employe_fkey;
ALTER TABLE vente_detail DROP CONSTRAINT vente_detail_ean_fkey;
ALTER TABLE vente_detail DROP CONSTRAINT "vente_detail_Date achat_fkey";
-- Suppression des contraintes de clés primaires
ALTER TABLE produits DROP CONSTRAINT IF EXISTS produits_pkey;
ALTER TABLE clients DROP CONSTRAINT IF EXISTS clients_pkey;
ALTER TABLE employers DROP CONSTRAINT IF EXISTS employers_pkey;
ALTER TABLE vente_detail DROP CONSTRAINT IF EXISTS vente_detail_pkey;

-- ÉTAPE 2 : PRÉPARATION ET AJOUT DES NOUVELLES COLONNES
-- Ajout des nouvelles colonnes pour les clés primaires (`SERIAL`)
ALTER TABLE produits ADD COLUMN id_produit SERIAL;
ALTER TABLE clients ADD COLUMN id_client SERIAL;
ALTER TABLE employers ADD COLUMN id_employe_new SERIAL; -- Temporaire pour éviter un conflit
-- Ajout des nouvelles colonnes pour les clés étrangères
ALTER TABLE vente_detail ADD COLUMN id_client_new INT;
ALTER TABLE vente_detail ADD COLUMN id_employe_new INT;
ALTER TABLE vente_detail ADD COLUMN id_produit_new INT;
-- Ajout des autres colonnes
ALTER TABLE employers ADD COLUMN num_employe VARCHAR(255);
ALTER TABLE calendrier ADD COLUMN day_off BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE calendrier ADD COLUMN is_closed BOOLEAN NOT NULL DEFAULT FALSE;

-- ÉTAPE 3 : MIGRATION DES DONNÉES
-- 1. Sauvegarde des anciennes clés dans les nouvelles colonnes
-- Cela garantit qu'on ne perd pas l'historique des identifiants
UPDATE employers SET num_employe = id_employe;
-- 2. Mise à jour de la table 'vente_detail' avec les nouvelles clés
-- On joint les tables pour trouver les nouvelles valeurs
UPDATE vente_detail
SET
    id_client_new = clients.id_client,
    id_employe_new = employers.id_employe_new,
    id_produit_new = produits.id_produit
FROM
    clients, employers, produits
WHERE
    vente_detail.CUSTOMER_ID = clients.CUSTOMER_ID AND
    vente_detail.id_employe = employers.id_employe AND
    vente_detail.EAN = produits.EAN;

-- ÉTAPE 4 : NETTOYAGE ET FINALISATION
-- 1. Suppression des anciennes colonnes
--ALTER TABLE produits DROP COLUMN EAN;
ALTER TABLE employers DROP COLUMN id_employe;
ALTER TABLE vente_detail DROP COLUMN CUSTOMER_ID;
ALTER TABLE vente_detail DROP COLUMN EAN;
ALTER TABLE vente_detail DROP COLUMN id_employe;
-- 2. Renommage des colonnes temporaires
ALTER TABLE clients RENAME COLUMN CUSTOMER_ID TO num_customer;
ALTER TABLE employers RENAME COLUMN id_employe_new TO id_employe;
ALTER TABLE vente_detail RENAME COLUMN id_client_new TO id_client;
ALTER TABLE vente_detail RENAME COLUMN id_employe_new TO id_employe;
ALTER TABLE vente_detail RENAME COLUMN id_produit_new TO id_produit;
-- 3. Ajout des nouvelles clés primaires et étrangères
ALTER TABLE produits ADD PRIMARY KEY (id_produit);
ALTER TABLE clients ADD PRIMARY KEY (id_client);
ALTER TABLE employers ADD PRIMARY KEY (id_employe);

ALTER TABLE clients
ADD CONSTRAINT fk_clients_calendrier FOREIGN KEY (date_inscription) REFERENCES calendrier (date);

ALTER TABLE employers
ADD CONSTRAINT fk_employers_calendrier FOREIGN KEY (date_debut) REFERENCES calendrier (date);

ALTER TABLE vente_detail
ADD CONSTRAINT fk_vente_detail_clients FOREIGN KEY (id_client) REFERENCES clients (id_client);

ALTER TABLE vente_detail
ADD CONSTRAINT fk_vente_detail_employers FOREIGN KEY (id_employe) REFERENCES employers (id_employe);

ALTER TABLE vente_detail
ADD CONSTRAINT fk_vente_detail_produits FOREIGN KEY (id_produit) REFERENCES produits (id_produit);

ALTER TABLE vente_detail
ADD CONSTRAINT fk_vente_detail_calendrier FOREIGN KEY ("Date achat") REFERENCES calendrier (date);