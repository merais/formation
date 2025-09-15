Bien sûr, voici une antisèche complète pour le langage SQL, rédigée en français.

---

### Langage de manipulation de données (DML) ✍️

* **SELECT** : Permet de récupérer des données d'une base de données.
    * `SELECT colonne1, colonne2 FROM nom_de_la_table;`
    * `SELECT * FROM nom_de_la_table;` (Sélectionne toutes les colonnes)
* **WHERE** : Filtre les enregistrements.
    * `SELECT colonne1 FROM nom_de_la_table WHERE condition;`
* **AND, OR, NOT** : Opérateurs logiques.
    * `SELECT * FROM nom_de_la_table WHERE condition1 AND condition2;`
* **ORDER BY** : Trie les résultats.
    * `SELECT * FROM nom_de_la_table ORDER BY colonne1 ASC/DESC;` (ASC pour ascendant, DESC pour descendant)
* **INSERT INTO** : Insère de nouveaux enregistrements.
    * `INSERT INTO nom_de_la_table (colonne1, colonne2) VALUES (valeur1, valeur2);`
* **UPDATE** : Modifie des enregistrements existants.
    * `UPDATE nom_de_la_table SET colonne1 = valeur1 WHERE condition;`
* **DELETE** : Supprime des enregistrements.
    * `DELETE FROM nom_de_la_table WHERE condition;`
* **LIKE** : Recherche un motif.
    * `SELECT * FROM nom_de_la_table WHERE colonne LIKE 'a%';` (Commence par 'a')
    * `SELECT * FROM nom_de_la_table WHERE colonne LIKE '%a';` (Se termine par 'a')
    * `SELECT * FROM nom_de_la_table WHERE colonne LIKE '%a%';` (Contient 'a')
* **IN** : Spécifie plusieurs valeurs possibles.
    * `SELECT * FROM nom_de_la_table WHERE colonne IN (valeur1, valeur2);`
* **BETWEEN** : Sélectionne des valeurs dans une plage.
    * `SELECT * FROM nom_de_la_table WHERE colonne BETWEEN valeur1 AND valeur2;`
* **LIMIT/TOP** : Limite le nombre de lignes renvoyées (la syntaxe varie selon le système de gestion de base de données).
    * `SELECT * FROM nom_de_la_table LIMIT 10;` (Utilisé sur MySQL/PostgreSQL)
    * `SELECT TOP 10 * FROM nom_de_la_table;` (Utilisé sur SQL Server)

---

### Langage de définition de données (DDL) 🏗️

* **CREATE DATABASE** : Crée une nouvelle base de données.
    * `CREATE DATABASE nom_de_la_base;`
* **CREATE TABLE** : Crée une nouvelle table.
    * `CREATE TABLE nom_de_la_table (colonne1 type_de_donnee, colonne2 type_de_donnee);`
* **ALTER TABLE** : Modifie la structure d'une table.
    * `ALTER TABLE nom_de_la_table ADD nom_colonne type_de_donnee;`
    * `ALTER TABLE nom_de_la_table DROP COLUMN nom_colonne;`
* **DROP TABLE** : Supprime une table.
    * `DROP TABLE nom_de_la_table;`
* **DROP DATABASE** : Supprime une base de données.
    * `DROP DATABASE nom_de_la_base;`

---

### Jointures 🤝

* **INNER JOIN** : Renvoie les lignes ayant des valeurs correspondantes dans les deux tables.
    * `SELECT * FROM table1 INNER JOIN table2 ON table1.id = table2.id;`
* **LEFT JOIN** (ou **LEFT OUTER JOIN**) : Renvoie toutes les lignes de la table de gauche et les lignes correspondantes de la table de droite.
    * `SELECT * FROM table1 LEFT JOIN table2 ON table1.id = table2.id;`
* **RIGHT JOIN** (ou **RIGHT OUTER JOIN**) : Renvoie toutes les lignes de la table de droite et les lignes correspondantes de la table de gauche.
    * `SELECT * FROM table1 RIGHT JOIN table2 ON table1.id = table2.id;`
* **FULL JOIN** (ou **FULL OUTER JOIN**) : Renvoie toutes les lignes lorsqu'il y a une correspondance dans l'une ou l'autre des tables.
    * `SELECT * FROM table1 FULL JOIN table2 ON table1.id = table2.id;`

---

### Fonctions d'agrégation et regroupement 📊

* **COUNT()** : Compte le nombre de lignes.
    * `SELECT COUNT(nom_colonne) FROM nom_de_la_table;`
* **SUM()** : Calcule la somme d'une colonne.
    * `SELECT SUM(nom_colonne) FROM nom_de_la_table;`
* **AVG()** : Calcule la valeur moyenne d'une colonne.
    * `SELECT AVG(nom_colonne) FROM nom_de_la_table;`
* **MIN()** : Renvoie la valeur minimale.
    * `SELECT MIN(nom_colonne) FROM nom_de_la_table;`
* **MAX()** : Renvoie la valeur maximale.
    * `SELECT MAX(nom_colonne) FROM nom_de_la_table;`
* **GROUP BY** : Regroupe les lignes ayant les mêmes valeurs dans des lignes récapitulatives.
    * `SELECT colonne1, COUNT(*) FROM nom_de_la_table GROUP BY colonne1;`
* **HAVING** : Filtre les groupes créés par `GROUP BY`.
    * `SELECT colonne1, COUNT(*) FROM nom_de_la_table GROUP BY colonne1 HAVING COUNT(*) > 1;`