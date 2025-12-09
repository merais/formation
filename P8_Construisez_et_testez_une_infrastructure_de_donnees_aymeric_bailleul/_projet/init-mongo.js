// Script d'initialisation MongoDB
// Exécuté automatiquement au premier démarrage du conteneur

// Récupérer les variables d'environnement
const dbName = process.env.MONGO_INITDB_DATABASE || 'weather_data';
const collectionName = process.env.MONGODB_COLLECTION || 'measurements';

print(`[INFO] Initialisation de la base de données: ${dbName}`);

// Se connecter à la base de données
const db = db.getSiblingDB(dbName);

// Créer la collection principale
print(`[INFO] Création de la collection: ${collectionName}`);
db.createCollection(collectionName);

// Créer les index pour optimiser les requêtes
print('[INFO] Création des index...');

// Index unique sur la clé composite (évite les doublons)
db[collectionName].createIndex(
  { "unique_key": 1 },
  { unique: true, name: "idx_unique_key" }
);
print('[OK] Index unique créé sur unique_key');

// Index composé pour les requêtes par station et date
db[collectionName].createIndex(
  { "id_station": 1, "dh_utc": -1 },
  { name: "idx_station_date" }
);
print('[OK] Index créé sur id_station + dh_utc');

// Index sur la date pour les requêtes temporelles
db[collectionName].createIndex(
  { "dh_utc": -1 },
  { name: "idx_date" }
);
print('[OK] Index créé sur dh_utc');

// Index sur la station pour les requêtes par station
db[collectionName].createIndex(
  { "id_station": 1 },
  { name: "idx_station" }
);
print('[OK] Index créé sur id_station');

// Index sur le timestamp de traitement
db[collectionName].createIndex(
  { "processed_at": -1 },
  { name: "idx_processed_at" }
);
print('[OK] Index créé sur processed_at');

// Créer la collection de métadonnées pour suivre les imports
print('[INFO] Création de la collection de métadonnées: import_metadata');
db.createCollection('import_metadata');

db.import_metadata.createIndex(
  { "file_key": 1 },
  { unique: true, name: "idx_file_key" }
);
print('[OK] Index unique créé sur file_key dans import_metadata');

db.import_metadata.createIndex(
  { "imported_at": -1 },
  { name: "idx_imported_at" }
);
print('[OK] Index créé sur imported_at dans import_metadata');

// Afficher les statistiques
print('\n[INFO] Base de données initialisée avec succès!');
print(`[INFO] Collections créées: ${db.getCollectionNames().join(', ')}`);

// Afficher les index de la collection principale
print(`\n[INFO] Index sur ${collectionName}:`);
db[collectionName].getIndexes().forEach(function(idx) {
  print(`  - ${idx.name}: ${JSON.stringify(idx.key)}`);
});

print('\n[OK] Initialisation terminée');
