# 11 — Cheatsheet NoSQL (MongoDB • Administration)

Résumé opérationnel de « Administrez vos données avec MongoDB »: installation, commandes clés, sécurité, haute disponibilité, sauvegarde, performance.

## Concepts rapides
- Modèle: base → collections → documents (BSON/JSON), index.
- Moteur: WiredTiger (journalisation, compression, cache).
- Cohérence/Dispo: readConcern / writeConcern; réplicas; sharding pour l’échelle.

## Installation & démarrage (local)
- Dossier de données (ex Windows): `C:\data\db`
- Lancer le serveur:
```powershell
# Windows (exemple basique)
"C:\\Program Files\\MongoDB\\Server\\<version>\\bin\\mongod.exe" --dbpath C:\\data\\db
```
- Se connecter (shell moderne):
```powershell
mongosh "mongodb://localhost:27017"
```

## Basiques shell
```javascript
// Sélection base
db = db.getSiblingDB("mydb")

// CRUD
db.users.insertOne({name: "Alice", age: 30, tags: ["vip"]})
db.users.insertMany([{name:"Bob"},{name:"Eve"}])

// Lecture
db.users.find({age: {$gte: 18}}, {name:1, age:1}).sort({age:-1}).limit(10)

// Mise à jour
db.users.updateOne({name:"Alice"}, {$set:{age:31}})
db.users.updateMany({tags:"vip"}, {$inc:{score:1}}, {upsert:false})

// Suppression
db.users.deleteOne({_id: ObjectId("...")})
db.users.deleteMany({inactive:true})
```

## Indexation
```javascript
// Index simple et composé
db.users.createIndex({email:1}, {unique:true})
db.users.createIndex({country:1, created_at:-1})

// Index TTL (auto-expiration)
db.sessions.createIndex({expiresAt:1}, {expireAfterSeconds:0})

// Text / Hashed / Partiel
db.articles.createIndex({content:"text"})
db.users.createIndex({userId:"hashed"})
db.orders.createIndex({status:1}, {partialFilterExpression:{status:"PAID"}})

// Analyse de requête
db.users.find({email:"a@b.com"}).explain("executionStats")
```
Bonnes pratiques: indexer selon les requêtes dominantes; préférer des index avec sélectivité élevée; limiter le nombre d’index inutiles (coût écriture/mémoire).

## Agrégation (pipeline)
```javascript
db.orders.aggregate([
  {$match:{status:"PAID"}},
  {$group:{_id:"$customerId", total:{$sum:"$amount"}}},
  {$sort:{total:-1}},
  {$limit:10}
])
```
Étapes fréquentes: `$match`, `$project`, `$group`, `$unwind`, `$sort`, `$lookup`, `$facet`, `$addFields`.

## Validation de schéma (contrôles)
```javascript
db.createCollection("users", {
  validator: {$jsonSchema: {
    bsonType:"object",
    required:["email","created_at"],
    properties:{
      email:{bsonType:"string", pattern:"^.+@.+$"},
      age:{bsonType:"int", minimum:0}
    }
  }},
  validationLevel:"moderate",   // off|moderate|strict
  validationAction:"error"       // warn|error
})
```

## Transactions (multi-documents)
- Nécessitent un replica set (même en local: `--replSet <name>` puis `rs.initiate()` dans mongosh).
```javascript
const session = db.getMongo().startSession();
session.withTransaction(() => {
  const u = session.getDatabase("mydb").users;
  u.updateOne({_id: id}, {$inc:{balance:-10}});
  u.updateOne({_id: other}, {$inc:{balance:10}});
}, {writeConcern:{w:"majority"}, readConcern:{level:"local"}});
session.endSession();
```

## Replica set (HA)
- Démarrer chaque noeud avec `--replSet rs0` puis initialiser:
```javascript
rs.initiate({
  _id:"rs0",
  members:[
    {_id:0, host:"host1:27017"},
    {_id:1, host:"host2:27017"},
    {_id:2, host:"host3:27017"}
  ]
})
rs.status()
```
- Écritures durables: `writeConcern: {w:"majority", j:true}`.

## Sharding (échelle horizontale)
- Activer et choisir une clé de shard stable, à bonne cardinalité (éviter monotone).
```javascript
sh.enableSharding("mydb")
sh.shardCollection("mydb.orders", {customerId:1, created_at:1})
sh.status()
```
- Surveiller le balancing (chunks), tailles et hot partitions.

## Sécurité (auth, réseau)
```javascript
// Créer un utilisateur admin
use admin
db.createUser({
  user:"admin",
  pwd:"<motdepasse>",
  roles:[{role:"root", db:"admin"}]
})

// Démarrer mongod avec authentification
# ajouter au config (mongod.conf):
# security:
#   authorization: enabled
# net:
#   bindIp: 127.0.0.1,10.0.0.5
```
Bonnes pratiques: rôles minimaux (RBAC), IP binding restreint, TLS/SSL, secrets hors dépôt, rotation des mots de passe/keys.

## Import/Export & Sauvegarde
```powershell
# Import JSON/CSV
mongoimport --db mydb --collection users --file users.json --jsonArray
mongoimport --db mydb --collection users --type csv --headerline --file users.csv

# Export
mongoexport --db mydb --collection users --out users.json --jsonArray

# Sauvegarde logique
mongodump   --db mydb   --out backup/
# Restauration
mongorestore --db mydb  backup/mydb
```
- Pour le point‑dans‑le‑temps (PIT): snapshots stockage + oplog (réplicas) ou services managés (Atlas Backup).

## Monitoring & Perf
- Profiler: `db.setProfilingLevel(1|2)`; logs lenteur; `currentOp`, `serverStatus()`.
- `explain()` sur requêtes; surveiller p95/p99, ratio cache, lock %, I/O; éviter `$where`.
- Dimensionner RAM/CPU/IO; limiter documents trop gros; préférer projections et pipeline ciblé.

## Paramétrages utiles
- `writeConcern`: `{w:1|majority, j:true, wtimeout:ms}`
- `readConcern`: `local|majority|linearizable|snapshot`
- `readPreference`: `primary|primaryPreferred|secondary|secondaryPreferred|nearest`

## Anti‑patterns (à éviter)
- Clé de shard monotone (ex: date seule) → hotspots.
- Index manquants ou pléthoriques; index non utilisés.
- Documents géants “attrape‑tout”; schéma non pensé aux requêtes.
- Transactions longues/bavardes; fetch de gros volumes sans pagination.

## Outils & Cloud
- mongosh, MongoDB Compass (GUI), drivers officiels.
- MongoDB Atlas (cloud managé): backups gérés, métriques, autoscaling, sécurité avancée.

## À retenir (5 points)
1. Modéliser selon les requêtes et la croissance (index + shard key).
2. Sécu: auth activée, rôles minimaux, TLS, IP bind strict.
3. HA: replica sets; scale-out: sharding avec clé bien choisie.
4. Qualité: validation JSON Schema; write/read concern adaptés.
5. Opérations: sauvegarde/restore testées, monitoring continu, `explain()` systématique.
