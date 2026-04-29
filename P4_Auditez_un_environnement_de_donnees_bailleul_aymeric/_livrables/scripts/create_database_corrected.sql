-- Création de la table 'produits'
CREATE TABLE produits (
    id_produit SERIAL PRIMARY KEY,
	EAN BIGINT,
    categorie VARCHAR(255),
    Rayon VARCHAR(255),
    Libelle_produit VARCHAR(255),
    prix FLOAT
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
    trimestre VARCHAR(255),
	day_off BOOLEAN not null default false
);

-- Création de la table 'clients'
CREATE TABLE clients (
	id_client SERIAL PRIMARY KEY,
    CUSTOMER_ID VARCHAR(255),
    date_inscription DATE,
	FOREIGN KEY (date_inscription) REFERENCES calendrier (date)
);

-- Création de la table 'employers'
CREATE TABLE employers (
	id_employe SERIAL PRIMARY KEY,
    num_employe VARCHAR(255),
    employe VARCHAR(255),
    prenom VARCHAR(255),
    nom VARCHAR(255),
    date_debut DATE,
    hash_mdp VARCHAR(255),
    mail VARCHAR(255),
	FOREIGN KEY (date_debut) REFERENCES calendrier (date)
);

-- Création de la table 'vente_detail'
CREATE TABLE vente_detail (
    ID_BDD VARCHAR(255) PRIMARY KEY,
    id_client INT,
    id_employe INT,
    id_produit INT,
    "Date achat" DATE,
    "ID ticket" VARCHAR(255),
    FOREIGN KEY (id_client) REFERENCES clients (id_client),
    FOREIGN KEY (id_employe) REFERENCES employers (id_employe),
    FOREIGN KEY (id_produit) REFERENCES produits (id_produit),
    FOREIGN KEY ("Date achat") REFERENCES calendrier (date)
);