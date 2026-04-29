
\copy calendrier FROM 'G:/My Drive/_formation_over_git/P4_Auditez_un_environnement_de_donnees_bailleul_aymeric/_projet/sources/calendrier.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);
\copy clients FROM 'G:/My Drive/_formation_over_git/P4_Auditez_un_environnement_de_donnees_bailleul_aymeric/_projet/sources/clients.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);
\copy employers FROM 'G:/My Drive/_formation_over_git/P4_Auditez_un_environnement_de_donnees_bailleul_aymeric/_projet/sources/employer.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);
\copy produits FROM 'G:/My Drive/_formation_over_git/P4_Auditez_un_environnement_de_donnees_bailleul_aymeric/_projet/sources/produits.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);
\copy vente_detail FROM 'G:/My Drive/_formation_over_git/P4_Auditez_un_environnement_de_donnees_bailleul_aymeric/_projet/sources/vente_detail.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);