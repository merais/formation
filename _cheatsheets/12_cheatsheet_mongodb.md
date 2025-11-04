# 12 — Cheatsheet MongoDB (commandes de base)

Objectif: démarrer vite avec MongoDB, créer une base/collection et importer des données.

## 1. Installation & démarrage (local)

- Dossier de données Windows: `C:\\data\\db`
- Lancer le serveur (exemple):
```powershell
"C:\\Program Files\\MongoDB\\Server\\<version>\\bin\\mongod.exe" --dbpath C:\\data\\db
```
- Ouvrir le shell:
```powershell
mongosh "mongodb://localhost:27017"
```

## 2. Créer une base et une collection (mongosh)

```javascript
// Sélectionner/créer une base (créée à la 1ère écriture)
use mydb

// Créer une collection explicitement (optionnel)
db.createCollection("users")

// Vérifier
show dbs
show collections
```

## 3. Insérer / Lire / Mettre à jour / Supprimer (CRUD rapide)

```javascript
// Insert
db.users.insertOne({name: "Alice", age: 30})
db.users.insertMany([{name: "Bob"}, {name: "Eve", age: 25}])

// Read (projection, tri, limite)
db.users.find({age: {$gte: 18}}, {name:1, age:1}).sort({age:-1}).limit(10)
db.users.findOne()

// Update
db.users.updateOne({name:"Alice"}, {$set:{age:31}})

// Delete
db.users.deleteOne({name:"Bob"})
```

## 4. Créer un index (basique)

```javascript
// Unique sur l'email
db.users.createIndex({email:1}, {unique:true})
```

## 5. Importer des données dans une collection

- Préparer un fichier `users.json` (JSON lignes ou tableau JSON)
- Importer avec `mongoimport`:
```powershell
# JSON tableau
mongoimport --db mydb --collection users --file users.json --jsonArray

# CSV
mongoimport --db mydb --collection users --type csv --headerline --file users.csv
```

Astuce: si `mongoimport` n'est pas dans le PATH, utiliser le chemin complet vers l'exécutable.

## 6. Agrégation minimale

```javascript
db.orders.aggregate([
  {$match:{status:"PAID"}},
  {$group:{_id:"$customerId", total:{$sum:"$amount"}}},
  {$sort:{total:-1}},
  {$limit:5}
])
```

## 7. Bonnes pratiques express

- Modéliser selon les requêtes dominantes (query‑driven).
- Indexer ce qui est filtré/trié; éviter les index inutiles.
- Paginer (limit/skip) ou par curseur.
- Sauvegardes régulières; tester la restauration (`mongodump/mongorestore`).