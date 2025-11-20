/**
 * Script de configuration du sharding sur la collection
 * À exécuter APRÈS avoir chargé les données
 * Usage: mongosh --port 27001 --file setup_sharding_collection.js
 */

print("=".repeat(80));
print("CONFIGURATION DU SHARDING SUR LA COLLECTION");
print("=".repeat(80));

// ============================================================================
// ÉTAPE 1: Configurer le Balancer
// ============================================================================
print("\n[1/4] Configuration du balancer...");

// Activer le balancer
sh.startBalancer();
print("OK - Balancer active");

// Configurer la fenetre active (24h/24)
db = db.getSiblingDB("config");
db.settings.updateOne(
    { _id: "balancer" },
    { $set: { activeWindow: { start: "00:00", stop: "23:59" } } },
    { upsert: true }
);
print("OK - Fenetre du balancer configuree (00:00-23:59)");

// Definir la taille des chunks a 32 MB
db.settings.updateOne(
    { _id: "chunksize" },
    { $set: { value: 32 } },
    { upsert: true }
);
print("OK - Taille des chunks definie a 32 MB");

// ============================================================================
// ÉTAPE 2: Activer le Sharding sur la Base de Données
// ============================================================================
print("\n[2/4] Activation du sharding sur la base 'listings'...");
sh.enableSharding("listings");
print("OK - Sharding active sur 'listings'");

// ============================================================================
// ÉTAPE 3: Créer l'Index et Sharder la Collection
// ============================================================================
print("\n[3/4] Configuration de la collection 'short_location'...");

db = db.getSiblingDB("listings");

// Creer l'index sur la cle de sharding
db.short_location.createIndex({ "host_id": 1 });
print("OK - Index cree sur 'host_id'");

// Sharder la collection
sh.shardCollection("listings.short_location", { "host_id": 1 });
print("OK - Collection 'short_location' shardee");

// ============================================================================
// ÉTAPE 4: Vérifier la Configuration
// ============================================================================
print("\n[4/4] Verification de la configuration...");
print("\n--- Statut du Balancer ---");
print("Etat:", sh.getBalancerState() ? "Active" : "Desactive");
print("En cours d'execution:", sh.isBalancerRunning());

print("\n--- Shards du Cluster ---");
db = db.getSiblingDB("config");
db.shards.find().forEach(function(shard) {
    print("- " + shard._id + ": " + shard.host);
});

print("\n--- Distribution des Donnees ---");
db = db.getSiblingDB("listings");
try {
    db.short_location.getShardDistribution();
} catch (e) {
    print("Distribution non disponible:", e.message);
}

print("\n" + "=".repeat(80));
print("CONFIGURATION TERMINEE");
print("=".repeat(80));