-- ====================================
-- SCRIPT DE CRÉATION DE LA BASE DE DONNÉES IMMOBILIÈRE SQLITE
-- ====================================

-- Suppression des tables si elles existent (pour permettre la ré-exécution)
DROP TABLE IF EXISTS bien;
DROP TABLE IF EXISTS mutation;
DROP TABLE IF EXISTS communes;
DROP TABLE IF EXISTS departement;
DROP TABLE IF EXISTS region;
DROP TABLE IF EXISTS type_local;
DROP TABLE IF EXISTS type_voie;

-- ====================================
-- CRÉATION DES TABLES DE RÉFÉRENCE
-- ====================================

-- Table des régions
CREATE TABLE region (
    code_reg TEXT PRIMARY KEY,
    nom_reg TEXT NOT NULL
);

-- Table des départements
CREATE TABLE departement (
    code_dep TEXT PRIMARY KEY,
    nom_dep TEXT NOT NULL,
    reg_code TEXT,
    FOREIGN KEY (reg_code) REFERENCES region(code_reg)
);

-- Table des communes
CREATE TABLE communes (
    code_com TEXT PRIMARY KEY,
    nom_com TEXT NOT NULL,
    geolocalisation TEXT,
    pop_total INTEGER,
    code_dep TEXT,
    FOREIGN KEY (code_dep) REFERENCES departement(dep_code)
);

-- Table des types de voie
CREATE TABLE type_voie (
    code_type_voie INTEGER PRIMARY KEY,
    type_voie TEXT NOT NULL
);

-- Table des types de local
CREATE TABLE type_local (
    code_type_local INTEGER PRIMARY KEY,
    type_local TEXT NOT NULL
);

-- ====================================
-- CRÉATION DES TABLES PRINCIPALES
-- ====================================

-- Table des mutations
CREATE TABLE mutation (
    id_mutation INTEGER PRIMARY KEY,
    date_mutation TEXT NOT NULL,
    nature_mutation TEXT,
    valeur_fonciere REAL
);

-- Table des biens
CREATE TABLE bien (
    id_bien INTEGER PRIMARY KEY,
    id_mutation INTEGER ,
    addr_num_voie INTEGER,
    addr_suffixe TEXT,
    code_type_voie INTEGER,
    addr_voie TEXT,
    addr_code_postal TEXT,
    code_com TEXT,
    num_plan TEXT,
    code_type_local INTEGER,
    surf_reelle_bati INTEGER,
    nombre_pieces_principales INTEGER,
    surf_terrain INTEGER,
    FOREIGN KEY (id_mutation) REFERENCES mutation(id_mutation),
    FOREIGN KEY (code_com) REFERENCES communes(code_com),
    FOREIGN KEY (code_type_voie) REFERENCES type_voie(code_type_voie),
    FOREIGN KEY (code_type_local) REFERENCES type_local(code_type_local)
);

-- ====================================
-- INSERTION DES DONNÉES DE RÉFÉRENCE
-- ====================================

-- Insertion des types de voie
INSERT INTO type_voie (code_type_voie, type_voie) VALUES
(0, 'RUE'),
(1, 'AV'),
(2, 'ALL'),
(3, 'RTE'),
(4, 'CRS'),
(5, 'CHE'),
(6, 'GR'),
(7, 'LOT'),
(8, '???'),
(9, 'MAIL'),
(10, 'IMP'),
(11, 'RLE'),
(12, 'PL'),
(13, 'ESPA'),
(14, 'MTE'),
(15, 'BD'),
(16, 'CHT'),
(17, 'PTR'),
(18, 'RES'),
(19, 'TRA'),
(20, 'REM'),
(21, 'ESP'),
(22, 'PROM'),
(23, 'COR'),
(24, 'QUAI'),
(25, 'PARC'),
(26, 'ILOT'),
(27, 'HLM'),
(28, 'VOIE'),
(29, 'VALL'),
(30, 'ACH'),
(31, 'PTE'),
(32, 'BRTL'),
(33, 'PTTE'),
(34, 'ESC'),
(35, 'PAS'),
(36, 'RPT'),
(37, 'CD'),
(38, 'VCHE'),
(39, 'VC'),
(40, 'HAM'),
(41, 'MRN'),
(42, 'VAL'),
(43, 'CITE'),
(44, 'FG'),
(45, 'VLA'),
(46, 'COUR'),
(47, 'MAIS'),
(48, 'TSSE'),
(49, 'CR'),
(50, 'CHEM'),
(51, 'SQ'),
(52, 'N'),
(53, 'PASS'),
(54, 'PRV'),
(55, 'COTE'),
(56, 'CLOS'),
(57, 'RPE'),
(58, 'VGE'),
(59, 'DOM'),
(60, 'PLAN'),
(61, 'SEN'),
(62, 'ZAC'),
(63, 'CAMI'),
(64, 'CAE'),
(65, 'CHS'),
(66, 'VEN'),
(67, 'QUA'),
(68, 'GPL'),
(69, 'CASR'),
(70, 'GAL'),
(71, 'VTE'),
(72, 'DSC'),
(73, 'ART'),
(74, 'ROC'),
(75, 'PLA'),
(76, 'CC'),
(77, 'PIST'),
(78, 'VIL'),
(79, 'FRM');

-- Insertion des types de local
INSERT INTO type_local (code_type_local, type_local) VALUES
(1, 'Maison'),
(2, 'Appartement');

-- Insertion des régions
INSERT INTO region (code_reg, nom_reg) VALUES
('0', 'Collectivites d''outre-mer'),
('1', 'Guadeloupe'),
('2', 'Martinique'),
('3', 'Guyane'),
('4', 'La Reunion'),
('6', 'Mayotte'),
('11', 'Ile-de-France'),
('24', 'Centre-Val de Loire'),
('27', 'Bourgogne-Franche-Comte'),
('28', 'Normandie'),
('32', 'Hauts-de-France'),
('44', 'Grand Est'),
('52', 'Pays de la Loire'),
('53', 'Bretagne'),
('75', 'Nouvelle-Aquitaine'),
('76', 'Occitanie'),
('84', 'Auvergne-Rhone-Alpes'),
('93', 'Provence-Alpes-Cote d''Azur'),
('94', 'Corse');

-- ====================================
-- SCRIPT PYTHON POUR L'IMPORTATION DES DONNÉES
-- ====================================

/*
Pour importer les données des fichiers CSV, utilisez le script Python suivant :

import sqlite3
import pandas as pd

# Connexion à la base de données
conn = sqlite3.connect('immobilier.db')
cursor = conn.cursor()

# Exécution du script de création des tables (ce fichier)
with open('create_database.sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()
    cursor.executescript(sql_script)

# Importation des départements
df_dept = pd.read_csv('departement.csv', sep=';', encoding='utf-8')
df_dept.to_sql('departement', conn, if_exists='append', index=False)

# Importation des communes
df_communes = pd.read_csv('communes.csv', sep=';', encoding='utf-8')
df_communes.to_sql('communes', conn, if_exists='append', index=False)

# Importation des mutations
df_mutations = pd.read_csv('mutation.csv', sep=';', encoding='utf-8')
df_mutations.to_sql('mutation', conn, if_exists='append', index=False)

# Importation des biens
df_biens = pd.read_csv('bien.csv', sep=';', encoding='utf-8')
# Remplacer les valeurs vides par NULL
df_biens = df_biens.where(pd.notnull(df_biens), None)
df_biens.to_sql('bien', conn, if_exists='append', index=False)

conn.commit()
conn.close()

print("Base de données créée et données importées avec succès !")
*/

-- ====================================
-- INDEX POUR OPTIMISER LES PERFORMANCES
-- ====================================

CREATE INDEX idx_bien_code_com ON bien(code_com);
CREATE INDEX idx_bien_code_type_local ON bien(code_type_local);
CREATE INDEX idx_bien_id_mutation ON bien(id_mutation);
CREATE INDEX idx_mutation_date ON mutation(date_mutation);
CREATE INDEX idx_mutation_valeur ON mutation(valeur_fonciere);
CREATE INDEX idx_communes_code_dep ON communes(code_dep);

-- ====================================
-- REQUÊTES DE VÉRIFICATION
-- ====================================

-- Vérification du nombre d'enregistrements par table
-- SELECT 'region' as table_name, COUNT(*) as count FROM region
-- UNION ALL
-- SELECT 'departement', COUNT(*) FROM departement  
-- UNION ALL
-- SELECT 'communes', COUNT(*) FROM communes
-- UNION ALL
-- SELECT 'type_voie', COUNT(*) FROM type_voie
-- UNION ALL
-- SELECT 'type_local', COUNT(*) FROM type_local
-- UNION ALL
-- SELECT 'mutation', COUNT(*) FROM mutation
-- UNION ALL
-- SELECT 'bien', COUNT(*) FROM bien;

-- Exemples de requêtes analytiques
-- SELECT 
--     r.nom_reg,
--     d.dep_nom,
--     COUNT(m.id_mutation) as nb_mutations,
--     AVG(m.valeur_fonciere) as prix_moyen
-- FROM mutation m
-- JOIN bien b ON m.id_mutation = b.id_mutation
-- JOIN communes c ON b.code_com = c.code_com
-- JOIN departement d ON c.code_dep = d.dep_code
-- JOIN region r ON d.reg_code = r.code_reg
-- GROUP BY r.nom_reg, d.dep_nom
-- ORDER BY nb_mutations DESC;

-- ====================================
-- FIN DU SCRIPT
-- ====================================