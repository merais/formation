## Aide-mémoire PostgreSQL

Voici un pense-bête pour les commandes et fonctions les plus courantes de PostgreSQL. Il regroupe les fonctions de manipulation de chaînes de caractères, ainsi que les commandes de base et avancées pour la gestion des bases de données et des tables.

-----

### Fonctions de manipulation de chaînes de caractères

| Fonction | Description | Exemple | Résultat |
|:---|:---|:---|:---|
| **CONCAT** | Combine plusieurs chaînes de caractères. | `CONCAT('A', 'B', 'C')` | `'ABC'` |
| **CONCAT\_WS** | Combine plusieurs chaînes avec un séparateur. | `CONCAT_WS('-', 'A', 'B', 'C')` | `'A-B-C'` |
| **LEFT / RIGHT** | Extrait des caractères depuis la gauche ou la droite. | `LEFT('PostgreSQL', 4)`\<br\>`RIGHT('PostgreSQL', 3)` | `'Post'`\<br\>`'SQL'` |
| **LENGTH** | Calcule la longueur d'une chaîne. | `LENGTH('PostgreSQL')` | `10` |
| **LOWER / UPPER** | Convertit une chaîne en minuscules ou majuscules. | `LOWER('PostgreSQL')`\<br\>`UPPER('PostgreSQL')` | `'postgresql'`\<br\>`'POSTGRESQL'` |
| **LTRIM / RTRIM** | Supprime les espaces ou caractères au début (LTRIM) ou à la fin (RTRIM). | `LTRIM('  PostgreSQL')`\<br\>`RTRIM('PostgreSQL  ')` | `'PostgreSQL'`\<br\>`'PostgreSQL'` |
| **TRIM** | Supprime les espaces ou caractères au début et à la fin. | `TRIM('  PostgreSQL  ')` | `'PostgreSQL'` |
| **POSITION** | Trouve la position d'une sous-chaîne. | `POSITION('B' in 'A B C')` | `3` |
| **REPEAT** | Répète une chaîne un nombre spécifié de fois. | `REPEAT('*', 5)` | `'*****'` |
| **REPLACE** | Remplace toutes les occurrences d'une sous-chaîne. | `REPLACE('PostgreSQL','PostGre','My')` | `'MySQL'` |
| **REVERSE** | Renverse l'ordre des caractères. | `REVERSE('PostgreSQL')` | `'LQSergtsoP'` |
| **SPLIT\_PART** | Divise une chaîne en parties et renvoie une partie spécifique. | `SPLIT_PART('2024-12-26','-',2)` | `'12'` |
| **SUBSTRING** | Extrait une sous-chaîne. | `SUBSTRING('PostgreSQL',1, 4)` | `'Post'` |

-----

### Commandes SQL de base

#### **Gestion des bases de données et des tables**

  * **Créer une base de données :** `CREATE DATABASE nom_db;`
  * **Supprimer une base de données :** `DROP DATABASE nom_db;`
  * **Se connecter à une base de données :** `\c nom_db;`
  * **Créer une table :**
    ```sql
    CREATE TABLE nom_table (
        colonne1 type_donnees,
        colonne2 type_donnees
    );
    ```
  * **Supprimer une table :** `DROP TABLE nom_table;`
  * **Afficher la structure d'une table :** `\d nom_table;`

#### **Manipulation des données**

  * **Insérer des données :**
    ```sql
    INSERT INTO nom_table (colonne1, colonne2) VALUES ('valeur1', 'valeur2');
    ```
  * **Sélectionner des données :** `SELECT colonne1, colonne2 FROM nom_table WHERE condition;`
  * **Mettre à jour des données :** `UPDATE nom_table SET colonne1 = 'nouvelle_valeur' WHERE condition;`
  * **Supprimer des données :** `DELETE FROM nom_table WHERE condition;`

-----

### Commandes SQL avancées

  * **Ajouter une colonne :** `ALTER TABLE nom_table ADD COLUMN nouvelle_colonne type_donnees;`
  * **Modifier le type d'une colonne :** `ALTER TABLE nom_table ALTER COLUMN nom_colonne TYPE nouveau_type;`
  * **Renommer une colonne :** `ALTER TABLE nom_table RENAME COLUMN ancien_nom TO nouveau_nom;`
  * **Créer un index :** `CREATE INDEX nom_index ON nom_table (colonne);`
  * **Joindre des tables :** `SELECT * FROM table1 JOIN table2 ON table1.id = table2.id;`
  * **Créer une vue :**
    ```sql
    CREATE VIEW nom_vue AS
    SELECT colonne1, colonne2 FROM nom_table
    WHERE condition;
    ```
  * **Créer un trigger :**
    ```sql
    CREATE OR REPLACE FUNCTION nom_fonction() RETURNS TRIGGER AS $$
    BEGIN
        -- Code à exécuter
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER nom_trigger
    BEFORE INSERT ON nom_table
    FOR EACH ROW EXECUTE FUNCTION nom_fonction();
    ```
  * **Utiliser des CTE (Common Table Expressions) :**
    ```sql
    WITH nom_cte AS (
        SELECT colonne1, COUNT(*) AS total
        FROM nom_table
        GROUP BY colonne1
    )
    SELECT * FROM nom_cte WHERE total > 10;
    ```
  * **Gérer les transactions :**
    ```sql
    BEGIN;
    -- Commandes SQL
    COMMIT; -- Valider la transaction
    ROLLBACK; -- Annuler la transaction
    ```
  * **Créer un utilisateur et attribuer des privilèges :**
    ```sql
    CREATE USER nom_utilisateur WITH PASSWORD 'mot_de_passe';
    GRANT SELECT, INSERT ON nom_table TO nom_utilisateur;
    ```
  * **Sauvegarder et restaurer une base de données :**
      * Sauvegarde : `pg_dump -U utilisateur -d nom_db -f sauvegarde.sql`
      * Restauration : `psql -U utilisateur -d nom_db -f sauvegarde.sql`

-----

### Commandes utiles pour PostgreSQL

| Commande | Description |
|:---|:---|
| `SHOW ALL;` | Affiche toutes les informations de configuration du serveur PostgreSQL. |
| `\d` | Liste toutes les tables de la base de données actuelle. |
| `\d table_name` | Affiche les détails d'une table spécifique. |
| `\d+ table_name` | Affiche les index et informations détaillées d'une table. |
| `\df` | Liste toutes les fonctions et procédures stockées. |
| `\dS table_name` | Liste les triggers associés à une table spécifique. |

### Table importante : `pg_settings`

La table `pg_settings` contient toutes les informations de configuration du serveur PostgreSQL. Elle est utile pour examiner et modifier les paramètres de configuration.

#### Exemple :
```sql
SELECT name, setting, unit, category, short_desc
FROM pg_settings
WHERE name = 'work_mem';
```

-----

### Fonctions de fenêtre (Window Functions)

| Catégorie | Fonction | Description |
|:---|:---|:---|
| **Agrégation** | `SUM()` | Calcule la somme des valeurs dans une partition. |
|  | `AVG()` | Calcule la moyenne des valeurs dans une partition. |
|  | `COUNT()` | Compte le nombre de lignes dans une partition. |
|  | `MAX()` | Retourne la valeur maximale dans une partition. |
|  | `MIN()` | Retourne la valeur minimale dans une partition. |
| **Classement** | `ROW_NUMBER()` | Attribue un numéro unique à chaque ligne dans un ensemble ordonné. |
|  | `RANK()` | Attribue un rang aux lignes, en laissant des trous dans le classement. |
|  | `DENSE_RANK()` | Attribue un rang sans laisser de trous dans le classement. |
| **Offset** | `LEAD()` | Récupère la valeur de la ligne suivante dans un ensemble ordonné. |
|  | `LAG()` | Récupère la valeur de la ligne précédente dans un ensemble ordonné. |
|  | `FIRST_VALUE()` | Récupère la première valeur d’un ensemble ordonné. |
|  | `LAST_VALUE()` | Récupère la dernière valeur d’un ensemble ordonné. |
