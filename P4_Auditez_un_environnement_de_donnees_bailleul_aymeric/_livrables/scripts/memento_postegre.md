### MDP postegre user
`Qwerty123++ SQL`

### Création de la bdd a executer dans un terminal
`createdb -U postgres SuperSmartMarket_origine`

### Connextion a la bdd (ici SuperSmartMarket_origine) a executer dans un terminal
`psql -U postgres -d SuperSmartMarket_origine`

### Création des tables dans la bdd (ici SuperSmartMarket_origine) a executer dans un terminal
`psql -U postgres -d SuperSmartMarket_origine -f "G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\create_database.sql"`
`psql -U postgres -d SuperSmartMarket_origine -f "G:\My Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\create_database.sql"`

### Importation des data dans la bdd (ici SuperSmartMarket_origine) a executer dans un terminal
`psql -U postgres -d SuperSmartMarket_origine -f "G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\import_data.sql"`
`psql -U postgres -d SuperSmartMarket_origine -f "G:\My Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\import_data.sql"`

### Création des tables dans la bdd (ici SuperSmartMarket_origine) a executer dans un terminal
`psql -U postgres -d SuperSmartMarket_origine -f "G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\create_table_logs.sql"`
`psql -U postgres -d SuperSmartMarket_origine -f "G:\My Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\create_table_logs.sql"`

### Importation des data dans la bdd (ici SuperSmartMarket_origine) a executer dans un terminal
`psql -U postgres -d SuperSmartMarket_origine -f "G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\import_data_logs.sql"`
`psql -U postgres -d SuperSmartMarket_origine -f "G:\My Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\import_data_logs.sql"`

### Modification de la bdd (ici SuperSmartMarket_origine) a executer dans un terminal
`psql -U postgres -d SuperSmartMarket_origine -f "G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\alter_table_database.sql"`
`psql -U postgres -d SuperSmartMarket_origine -f "G:\My Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\alter_table_database.sql"`

### Ajout de la contrainte sur bdd (ici SuperSmartMarket_origine) a executer dans un terminal
`psql -U postgres -d SuperSmartMarket_origine -f "G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\add_constraint_day_off.sql"`
`psql -U postgres -d SuperSmartMarket_origine -f "G:\My Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\add_constraint_day_off.sql"`

### Alternative si connecté a psql en tant que postgre pour l'importation
\i 'G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\create_database.sql'
\i 'G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\import_data.sql'
\i 'G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\create_table_logs.sql'
\i 'G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\create_table_logs.sql'
\i 'G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\import_data_logs.sql'
\i 'G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\alter_table_database.sql'
\i 'G:\Mon Drive\_formation_over_git\P4_Auditez_un_environnement_de_donnees_bailleul_aymeric\_projet\scripts\add_constraint_day_off.sql'