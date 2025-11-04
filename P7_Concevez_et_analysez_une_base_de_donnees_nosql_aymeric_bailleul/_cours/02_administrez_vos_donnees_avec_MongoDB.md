# Administrez vos données avec MongoDB

Ce document est une version Markdown structurée et exécutable du cours PDF. Il regroupe les notions et commandes avec des blocs de code correctement balisés.

## Sommaire
- Présentation et concepts
- Installation et démarrage (Windows, macOS, Linux)
- Connexion et bases du shell (mongosh)
- Modélisation et CRUD
- Indexation et analyse de requêtes
- Pipeline d’agrégation
- Validation de schéma (JSON Schema)
- Transactions
- Replica sets (HA)
- Sharding (échelle horizontale)
- Sécurité (auth, réseau)
- Import/Export et sauvegarde/restauration
- Monitoring et performance
- Paramétrages de cohérence
- Anti‑patterns
- Outils & Cloud

---

## Présentation et concepts

- Modèle MongoDB: bases → collections → documents (BSON/JSON), index.
- Moteur de stockage par défaut: WiredTiger (journalisation, compression, cache).
- Notions de cohérence/disponibilité: writeConcern, readConcern, readPreference.

---

## Installation et démarrage

### Windows
- Créer le dossier de données: `C:\data\db`
- Lancer le serveur:
```powershell
"C:\\Program Files\\MongoDB\\Server\\<version>\\bin\\mongod.exe" --dbpath C:\\data\\db
```

### macOS
- Installer via archive/installer ou Homebrew.
- Exemple (Homebrew):
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### Linux (Debian/Ubuntu)
- Installer le serveur:
```bash
sudo apt update
sudo apt install -y mongodb
```
- Dossier de données (si besoin):
```bash
sudo mkdir -p /data/db
sudo chown "$USER":"$USER" /data/db
```

---

## Connexion et bases du shell (mongosh)

- Se connecter:
```powershell
mongosh "mongodb://localhost:27017"
```
- Sélectionner une base:
```javascript
use mydb
// ou
db = db.getSiblingDB("mydb")
```

---

## Modélisation et CRUD

- Insertion:
```javascript
// Un document
db.users.insertOne({name: "Alice", age: 30, tags: ["vip"]})
// Plusieurs
db.users.insertMany([{name:"Bob"}, {name:"Eve"}])
```
- Lecture (projection, tri, pagination):
```javascript
db.users.find({age: {$gte: 18}}, {name:1, age:1}).sort({age:-1}).limit(10)
```
- Mise à jour:
```javascript
db.users.updateOne({name:"Alice"}, {$set:{age:31}})
db.users.updateMany({tags:"vip"}, {$inc:{score:1}}, {upsert:false})
```
- Suppression:
```javascript
db.users.deleteOne({_id: ObjectId("...")})
db.users.deleteMany({inactive:true})
```

Bonnes pratiques:
- Modéliser selon les requêtes dominantes (query‑driven design).
- Éviter les documents géants et les niveaux d’imbrication excessifs.

---

## Indexation et analyse de requêtes

- Création d’index:
```javascript
// Simple et unique
db.users.createIndex({email:1}, {unique:true})
// Composé
db.users.createIndex({country:1, created_at:-1})
// TTL
db.sessions.createIndex({expiresAt:1}, {expireAfterSeconds:0})
// Text / Hashed / Partiel
db.articles.createIndex({content:"text"})
db.users.createIndex({userId:"hashed"})
db.orders.createIndex({status:1}, {partialFilterExpression:{status:"PAID"}})
```
- Expliquer une requête:
```javascript
db.users.find({email:"a@b.com"}).explain("executionStats")
```

Bonnes pratiques:
- Indexer ce qui est réellement lu/filtré/trié.
- Vérifier la sélectivité et les ordres des champs dans les index composés.

---

## Pipeline d’agrégation

```javascript
db.orders.aggregate([
  {$match:{status:"PAID"}},
  {$group:{_id:"$customerId", total:{$sum:"$amount"}}},
  {$sort:{total:-1}},
  {$limit:10}
])
```
Étapes fréquentes: `$match`, `$project`, `$group`, `$unwind`, `$sort`, `$lookup`, `$facet`, `$addFields`.

---

## Validation de schéma (JSON Schema)

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

---

## Transactions

- Requiert un replica set (même en local: démarrer mongod avec `--replSet <name>` puis `rs.initiate()`).
```javascript
const session = db.getMongo().startSession();
session.withTransaction(() => {
  const u = session.getDatabase("mydb").users;
  u.updateOne({_id: id}, {$inc:{balance:-10}});
  u.updateOne({_id: other}, {$inc:{balance:10}});
}, {writeConcern:{w:"majority"}, readConcern:{level:"local"}});
session.endSession();
```

---

## Replica sets (haute disponibilité)

- Démarrer chaque noeud avec `--replSet rs0`, puis initialiser:
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
- Durabilité écritures:
```javascript
// Journalisation + majorité
db.collection.insertOne(doc, {writeConcern:{w:"majority", j:true}})
```

---

## Sharding (échelle horizontale)

- Activer le sharding et définir une clé adaptée (cardinalité suffisante, non monotone):
```javascript
sh.enableSharding("mydb")
sh.shardCollection("mydb.orders", {customerId:1, created_at:1})
sh.status()
```

---

## Sécurité (auth, réseau)

- Créer un utilisateur administrateur:
```javascript
use admin
db.createUser({
  user:"admin",
  pwd:"<motdepasse>",
  roles:[{role:"root", db:"admin"}]
})
```
- Extrait de configuration `mongod.conf`:
```yaml
security:
  authorization: enabled
net:
  bindIp: 127.0.0.1,10.0.0.5
```

Bonnes pratiques:
- RBAC minimal, IP binding restreint, TLS/SSL, secrets hors dépôt, rotation des credentials.

---

## Import/Export et sauvegarde/restauration

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

- Pour des restaurations point‑dans‑le‑temps: utiliser snapshots du stockage + oplog (réplication) ou services managés (Atlas Backup).

---

## Monitoring et performance

- Profiler et stats:
```javascript
db.setProfilingLevel(1)   // 0/1/2
```
- Outils utiles: logs lenteur, `currentOp`, `serverStatus()`, `explain()`.
- Surveiller p95/p99, ratio de cache, locks, I/O; réduire projections et parcours inutiles.

---

## Paramétrages de cohérence

```javascript
// Écriture
db.coll.insertOne(d, {writeConcern:{w:1}})        // latence faible
db.coll.insertOne(d, {writeConcern:{w:"majority", j:true, wtimeout:5000}})

// Lecture
// readConcern: local|majority|linearizable|snapshot
// readPreference: primary|primaryPreferred|secondary|secondaryPreferred|nearest
```

---

## Anti‑patterns

- Clé de shard monotone (ex: date seule) → points chauds.
- Trop/pas assez d’index; index non utilisés.
- Documents géants trop hétérogènes; schéma non pensé aux requêtes.
- Transactions longues; scans massifs sans pagination.

---

## Outils & Cloud

- mongosh, MongoDB Compass (GUI), drivers officiels.
- MongoDB Atlas: backups gérés, métriques, autoscaling, sécurité avancée.

---

## À retenir

1) Modéliser selon les requêtes et la croissance (index + shard key).
2) Sécurité activée (auth, roles minimaux, TLS, IP bind).
3) HA: replica sets; scale‑out: sharding approprié.
4) Qualité: validation JSON Schema; read/write concern adaptés.
5) Opérations: sauvegardes testées; monitoring continu; explain systématique.
