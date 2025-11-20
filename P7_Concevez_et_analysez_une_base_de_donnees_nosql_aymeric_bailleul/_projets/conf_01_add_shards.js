/**
 * Script pour ajouter les shards au cluster MongoDB
 * À exécuter avec: mongosh --port 27001 --file add_shards.js
 */

print("=".repeat(80));
print("AJOUT DES SHARDS AU CLUSTER MONGODB");
print("=".repeat(80));

// ============================================================================
// ÉTAPE 1: Configurer le Write Concern par défaut (MongoDB 8.0+)
// ============================================================================
print("\n[1/3] Configuration du Write Concern par defaut...");
try {
    db.adminCommand({
        setDefaultRWConcern: 1,
        defaultWriteConcern: { w: "majority" }
    });
    print("OK - Write Concern configure");
} catch (e) {
    print("ERREUR:", e.message);
}

// ============================================================================
// ÉTAPE 2: Ajouter les Shards au Cluster
// ============================================================================
print("\n[2/3] Ajout des shards au cluster...");
try {
    sh.addShard("shard1RS/localhost:27018,localhost:27019,localhost:27020");
    print("OK - Shard1RS ajoute");
} catch (e) {
    print("WARN - Shard1RS:", e.message);
}

try {
    sh.addShard("shard2RS/localhost:27021,localhost:27022,localhost:27023");
    print("OK - Shard2RS ajoute");
} catch (e) {
    print("WARN - Shard2RS:", e.message);
}

// ============================================================================
// ÉTAPE 3: Vérifier la Configuration
// ============================================================================
print("\n[3/3] Verification de la configuration...");
print("\n--- Shards du Cluster ---");
db = db.getSiblingDB("config");
db.shards.find().forEach(function(shard) {
    print("- " + shard._id + ": " + shard.host);
});

print("\n" + "=".repeat(80));
print("SHARDS AJOUTES AVEC SUCCES");
print("=".repeat(80));