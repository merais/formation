-- biens_immobiliers >> Transformation et chargement des données
--		- Remplacement des , par des .
--		- Suppression des nombres flotant dans la colonne valeur_fonciere_actuelle
--		- Suppression des .0 dans la colonne code_postal
\copy biens_immobiliers FROM 'G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_cours\sources\quiz1\bien_immo.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';');


-- transactions >> Transformation et chargement des données
--		- Suppression des nombres flotant dans la colonne valeur_fonciere
\copy transactions FROM 'G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_cours\sources\quiz1\transactions.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';');


-- biens_immobiliers >> Transformation et chargement des données
--		- Remplacement des , par des .
\copy indice_insee FROM 'G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_cours\sources\quiz1\indice_insee.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';');