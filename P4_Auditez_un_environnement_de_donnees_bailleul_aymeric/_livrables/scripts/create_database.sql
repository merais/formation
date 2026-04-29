-- Création de la table 'produits'
CREATE TABLE produits (
    EAN BIGINT PRIMARY KEY,
    categorie VARCHAR(255),
    Rayon VARCHAR(255),
    Libelle_produit VARCHAR(255),
    prix FLOAT
);

-- Création de la table 'clients'
CREATE TABLE clients (
    CUSTOMER_ID VARCHAR(255) PRIMARY KEY,
    date_inscription DATE
);

-- Création de la table 'employers'
CREATE TABLE employers (
    id_employe VARCHAR(255) PRIMARY KEY,
    employe VARCHAR(255),
    prenom VARCHAR(255),
    nom VARCHAR(255),
    date_debut DATE,
    hash_mdp VARCHAR(255),
    mail VARCHAR(255)
);

-- Création de la table 'calendrier'
CREATE TABLE calendrier (
    date DATE PRIMARY KEY,
    annee INT,
    mois INT,
    Jour INT,
    mois_nom VARCHAR(255),
    annee_mois VARCHAR(255),
    jour_semaine INT,
    trimestre VARCHAR(255)
);

-- Création de la table 'vente_detail'
CREATE TABLE vente_detail (
    ID_BDD VARCHAR(255) PRIMARY KEY,
    CUSTOMER_ID VARCHAR(255),
    id_employe VARCHAR(255),
    EAN BIGINT,
    "Date achat" DATE,
    "ID ticket" VARCHAR(255),
    FOREIGN KEY (CUSTOMER_ID) REFERENCES clients (CUSTOMER_ID),
    FOREIGN KEY (id_employe) REFERENCES employers (id_employe),
    FOREIGN KEY (EAN) REFERENCES produits (EAN),
    FOREIGN KEY ("Date achat") REFERENCES calendrier (date)
);