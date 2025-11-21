# LOGBOOK SHARDING

## Étape 1: Créer la Structure des Dossiers

- Créer les répertoires pour les données
    `mkdir -p .\shard1\data_paris`
    `mkdir -p .\shard1\data_lyon`
    `mkdir -p .\shard1\arbiter`
    `mkdir -p .\shard2\data_paris`
    `mkdir -p .\shard2\data_lyon`
    `mkdir -p .\shard2\arbiter`
    `mkdir -p .\config1`
    `mkdir -p .\config2`
    `mkdir -p .\_logs`


## Étape 2: Démarrer les Config Servers (Replica Set)

- **Config Server 1**

    `mongod --configsvr --replSet configRS --port 27100 --dbpath ./data_replicatset_sharded/config1 --logpath ./data_replicatset_sharded/_logs/config1.log --bind_ip localhost`

- **Config Server 2**

    `mongod --configsvr --replSet configRS --port 27101 --dbpath ./data_replicatset_sharded/config2 --logpath ./data_replicatset_sharded/_logs/config2.log --bind_ip localhost`

- **Initialiser le Replica Set des Config Servers**

    `mongosh --port 27100 --eval "rs.initiate({_id: 'configRS', configsvr: true, members: [{_id: 0, host: 'localhost:27100'}, {_id: 1, host: 'localhost:27101'}]})"`


## Étape 3: Démarrer le Shard 1 (Replica Set)

- **Shard 1 - Membre 1 (Primary)**

    `mongod --shardsvr --replSet shard1RS --port 27018 --dbpath ./data_replicatset_sharded/shard1/data_paris --logpath ./data_replicatset_sharded/_logs/shard1_data_paris.log --bind_ip localhost`

- **Shard 1 - Membre 2 (Secondary)**

    `mongod --shardsvr --replSet shard1RS --port 27019 --dbpath ./data_replicatset_sharded/shard1/data_lyon --logpath ./data_replicatset_sharded/_logs/shard1_data_lyon.log --bind_ip localhost`

- **Shard 1 - Arbitre**

    `mongod --shardsvr --replSet shard1RS --port 27020 --dbpath ./data_replicatset_sharded/shard1/arbiter --logpath ./data_replicatset_sharded/_logs/shard1_arbiter.log --bind_ip localhost`

- **Initialiser le Replica Set du Shard 1**

    `mongosh --port 27018 --eval "rs.initiate({_id: 'shard1RS', members: [{_id: 0, host: 'localhost:27018'}, {_id: 1, host: 'localhost:27019'}, {_id: 2, host: 'localhost:27020', arbiterOnly: true}]})"`


## Étape 4: Démarrer le Shard 2 (Replica Set)

- **Shard 1 - Membre 1 (Primary)**

    `mongod --shardsvr --replSet shard2RS --port 27021 --dbpath ./data_replicatset_sharded/shard2/data_paris --logpath ./data_replicatset_sharded/_logs/shard2_data_paris.log --bind_ip localhost`

- **Shard 1 - Membre 2 (Secondary)**

    `mongod --shardsvr --replSet shard2RS --port 27022 --dbpath ./data_replicatset_sharded/shard2/data_lyon --logpath ./data_replicatset_sharded/_logs/shard2_data_lyon.log --bind_ip localhost`

- **Shard 1 - Arbitre**

    `mongod --shardsvr --replSet shard2RS --port 27023 --dbpath ./data_replicatset_sharded/shard2/arbiter --logpath ./data_replicatset_sharded/_logs/shard2_arbiter.log --bind_ip localhost`

- **Initialiser le Replica Set du Shard 2**

    `mongosh --port 27021 --eval "rs.initiate({_id: 'shard2RS', members: [{_id: 0, host: 'localhost:27021'}, {_id: 1, host: 'localhost:27022'}, {_id: 2, host: 'localhost:27023', arbiterOnly: true}]})"`


## Étape 5: Démarrer les 2 Routeurs Mongos
 
- **Mongos 1 (port 27001)**

    `mongos --configdb configRS/localhost:27100,localhost:27101 --port 27001 --logpath ./data_replicatset_sharded/_logs/mongos1.log --bind_ip localhost`

- **Mongos 2 (port 27002)**

    `mongos --configdb configRS/localhost:27100,localhost:27101 --port 27002 --logpath ./data_replicatset_sharded/_logs/mongos2.log --bind_ip localhost`


## Étape 6: Ajouter les Shards au Cluster

- **Exécuter le script d'ajout des shards**

    `mongosh --port 27001 --file conf_01_add_shards.js`
      
- **OU Configuration manuelle**

  - `mongosh --port 27001`
  - `db.adminCommand({ setDefaultRWConcern: 1, defaultWriteConcern: { w: "majority" } })`
  - `sh.addShard("shard1RS/localhost:27018,localhost:27019,localhost:27020")`
  - `sh.addShard("shard2RS/localhost:27021,localhost:27022,localhost:27023")`
  - `sh.status()`


## Étape 7: Charger les données

- **Exécuter le script d'intégration des données**

    `python ABAI_P7_script_02_integration_data.py`
      
- **Important** : Vérifier que les ports des mongos sont bien 27001 et 27002 dans le script

## Étape 8: Configurer le Sharding sur la Collection

- **Exécuter le script de configuration du sharding**

    `mongosh --port 27001 --file conf_02_setup_sharding_collection.js`
      
- **OU Configuration manuelle**

  - `mongosh --port 27001`
  - `sh.startBalancer()`
  - `sh.enableSharding("listings")`
  - `use listings`
  - `db.short_location.createIndex({ "host_id": 1 })`
  - `sh.shardCollection("listings.short_location", { "host_id": 1 })`
  - `db.short_location.getShardDistribution()`