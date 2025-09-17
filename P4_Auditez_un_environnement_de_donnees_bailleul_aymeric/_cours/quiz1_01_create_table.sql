-- Table pour les biens immobiliers
CREATE TABLE biens_immobiliers (
    id_bien INT PRIMARY KEY,
    valeur_fonciere_actuelle INT,
    no_voie INT,
    bis_ter_quater VARCHAR(10),
    type_de_voie VARCHAR(50),
    code_voie VARCHAR(50),
    voie VARCHAR(255),
    code_postal INT,
    commune VARCHAR(255),
    code_departement INT,
    code_commune INT,
    surface FLOAT,
    type VARCHAR(50),
    nb_pieces INT
);

-- Table pour les transactions
CREATE TABLE transactions (
    date_vente DATE,
    valeur_fonciere FLOAT,
    bien_immobilier INT,
	PRIMARY KEY (date_vente, bien_immobilier),
    FOREIGN KEY (bien_immobilier) REFERENCES biens_immobiliers(id_bien)
);

-- Table pour l'indice INSEE
CREATE TABLE indice_insee (
    date DATE,
    indice_prix_logement FLOAT
);