"""
Script de benchmark pour mesurer les performances de lecture/écriture MongoDB
Mesure les temps d'accès en fonction du volume de données
"""
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import statistics

# Charger les variables d'environnement
load_dotenv()

def get_mongo_client():
    """Créer un client MongoDB"""
    mongo_host = os.getenv('MONGODB_HOST', 'mongodb.weather-pipeline.local')
    mongo_port = os.getenv('MONGODB_PORT', '27017')
    mongo_user = os.getenv('MONGODB_ROOT_USER', 'admin')
    mongo_password = os.getenv('MONGODB_ROOT_PASSWORD', '')
    
    if mongo_user and mongo_password:
        mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/"
    else:
        mongo_uri = f"mongodb://{mongo_host}:{mongo_port}/"
    
    return MongoClient(mongo_uri)

def benchmark_write(collection, num_records=1000, iterations=5):
    """
    Benchmark des opérations d'écriture
    
    Args:
        collection: Collection MongoDB
        num_records: Nombre de documents à insérer par itération
        iterations: Nombre d'itérations pour calculer la moyenne
    
    Returns:
        dict: Statistiques de performance
    """
    print(f"\n{'='*80}")
    print(f"BENCHMARK ÉCRITURE - {num_records} documents x {iterations} itérations")
    print(f"{'='*80}")
    
    times = []
    
    for i in range(iterations):
        # Générer des documents de test
        test_docs = []
        for j in range(num_records):
            doc = {
                'unique_key': f'BENCH_WRITE_{i}_{j}_{int(time.time()*1000)}',
                'id_station': 'BENCHMARK',
                'dh_utc': datetime.now().isoformat(),
                'temperature': 20.5 + j * 0.1,
                'humidite': 75,
                'pression': 1013.25,
                'benchmark_type': 'write',
                'iteration': i,
                'index': j
            }
            test_docs.append(doc)
        
        # Mesurer le temps d'insertion
        start_time = time.time()
        result = collection.insert_many(test_docs)
        end_time = time.time()
        
        elapsed = end_time - start_time
        times.append(elapsed)
        
        throughput = num_records / elapsed
        print(f"  Itération {i+1}: {elapsed:.4f}s ({throughput:.0f} docs/s)")
        
        # Nettoyer les documents de test
        collection.delete_many({'benchmark_type': 'write', 'iteration': i})
    
    # Calculer les statistiques
    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    min_time = min(times)
    max_time = max(times)
    avg_throughput = num_records / avg_time
    
    print(f"\nRÉSULTATS ÉCRITURE:")
    print(f"  Temps moyen: {avg_time:.4f}s (±{std_dev:.4f}s)")
    print(f"  Min/Max: {min_time:.4f}s / {max_time:.4f}s")
    print(f"  Débit moyen: {avg_throughput:.0f} documents/seconde")
    
    return {
        'operation': 'write',
        'num_records': num_records,
        'iterations': iterations,
        'avg_time': avg_time,
        'std_dev': std_dev,
        'min_time': min_time,
        'max_time': max_time,
        'throughput': avg_throughput
    }

def benchmark_read_sequential(collection, num_records=1000, iterations=5):
    """
    Benchmark des lectures séquentielles (scan complet)
    
    Args:
        collection: Collection MongoDB
        num_records: Nombre de documents à lire
        iterations: Nombre d'itérations
    
    Returns:
        dict: Statistiques de performance
    """
    print(f"\n{'='*80}")
    print(f"BENCHMARK LECTURE SÉQUENTIELLE - {num_records} documents x {iterations} itérations")
    print(f"{'='*80}")
    
    # Insérer des documents de test
    test_docs = []
    for i in range(num_records):
        doc = {
            'unique_key': f'BENCH_READ_SEQ_{i}_{int(time.time()*1000)}',
            'id_station': 'BENCHMARK',
            'dh_utc': datetime.now().isoformat(),
            'temperature': 20.5 + i * 0.1,
            'benchmark_type': 'read_sequential'
        }
        test_docs.append(doc)
    
    collection.insert_many(test_docs)
    
    times = []
    
    for i in range(iterations):
        # Mesurer le temps de lecture
        start_time = time.time()
        docs = list(collection.find({'benchmark_type': 'read_sequential'}).limit(num_records))
        end_time = time.time()
        
        elapsed = end_time - start_time
        times.append(elapsed)
        
        throughput = len(docs) / elapsed
        print(f"  Itération {i+1}: {elapsed:.4f}s ({throughput:.0f} docs/s, {len(docs)} docs lus)")
    
    # Nettoyer
    collection.delete_many({'benchmark_type': 'read_sequential'})
    
    # Statistiques
    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    min_time = min(times)
    max_time = max(times)
    avg_throughput = num_records / avg_time
    
    print(f"\nRÉSULTATS LECTURE SÉQUENTIELLE:")
    print(f"  Temps moyen: {avg_time:.4f}s (±{std_dev:.4f}s)")
    print(f"  Min/Max: {min_time:.4f}s / {max_time:.4f}s")
    print(f"  Débit moyen: {avg_throughput:.0f} documents/seconde")
    
    return {
        'operation': 'read_sequential',
        'num_records': num_records,
        'iterations': iterations,
        'avg_time': avg_time,
        'std_dev': std_dev,
        'min_time': min_time,
        'max_time': max_time,
        'throughput': avg_throughput
    }

def benchmark_read_indexed(collection, num_records=1000, iterations=5):
    """
    Benchmark des lectures par index (recherche par clé)
    
    Args:
        collection: Collection MongoDB
        num_records: Nombre de recherches à effectuer
        iterations: Nombre d'itérations
    
    Returns:
        dict: Statistiques de performance
    """
    print(f"\n{'='*80}")
    print(f"BENCHMARK LECTURE INDEXÉE - {num_records} recherches x {iterations} itérations")
    print(f"{'='*80}")
    
    # Insérer des documents de test avec unique_key
    test_docs = []
    test_keys = []
    for i in range(num_records):
        key = f'BENCH_READ_IDX_{i}_{int(time.time()*1000)}'
        doc = {
            'unique_key': key,
            'id_station': 'BENCHMARK',
            'dh_utc': datetime.now().isoformat(),
            'temperature': 20.5 + i * 0.1,
            'benchmark_type': 'read_indexed'
        }
        test_docs.append(doc)
        test_keys.append(key)
    
    collection.insert_many(test_docs)
    
    times = []
    
    for i in range(iterations):
        # Mesurer le temps de recherche par unique_key
        start_time = time.time()
        for key in test_keys:
            doc = collection.find_one({'unique_key': key})
        end_time = time.time()
        
        elapsed = end_time - start_time
        times.append(elapsed)
        
        throughput = num_records / elapsed
        avg_query_time = elapsed / num_records * 1000  # en ms
        print(f"  Itération {i+1}: {elapsed:.4f}s ({throughput:.0f} recherches/s, {avg_query_time:.2f}ms/recherche)")
    
    # Nettoyer
    collection.delete_many({'benchmark_type': 'read_indexed'})
    
    # Statistiques
    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    min_time = min(times)
    max_time = max(times)
    avg_throughput = num_records / avg_time
    avg_query_ms = avg_time / num_records * 1000
    
    print(f"\nRÉSULTATS LECTURE INDEXÉE:")
    print(f"  Temps moyen: {avg_time:.4f}s (±{std_dev:.4f}s)")
    print(f"  Min/Max: {min_time:.4f}s / {max_time:.4f}s")
    print(f"  Débit moyen: {avg_throughput:.0f} recherches/seconde")
    print(f"  Temps moyen par recherche: {avg_query_ms:.2f}ms")
    
    return {
        'operation': 'read_indexed',
        'num_records': num_records,
        'iterations': iterations,
        'avg_time': avg_time,
        'std_dev': std_dev,
        'min_time': min_time,
        'max_time': max_time,
        'throughput': avg_throughput,
        'avg_query_ms': avg_query_ms
    }

def benchmark_update(collection, num_records=1000, iterations=5):
    """
    Benchmark des opérations de mise à jour
    
    Args:
        collection: Collection MongoDB
        num_records: Nombre de documents à mettre à jour
        iterations: Nombre d'itérations
    
    Returns:
        dict: Statistiques de performance
    """
    print(f"\n{'='*80}")
    print(f"BENCHMARK MISE À JOUR - {num_records} documents x {iterations} itérations")
    print(f"{'='*80}")
    
    # Insérer des documents de test
    test_docs = []
    test_keys = []
    for i in range(num_records):
        key = f'BENCH_UPDATE_{i}_{int(time.time()*1000)}'
        doc = {
            'unique_key': key,
            'id_station': 'BENCHMARK',
            'temperature': 20.5,
            'benchmark_type': 'update'
        }
        test_docs.append(doc)
        test_keys.append(key)
    
    collection.insert_many(test_docs)
    
    times = []
    
    for i in range(iterations):
        # Mesurer le temps de mise à jour
        start_time = time.time()
        for j, key in enumerate(test_keys):
            collection.update_one(
                {'unique_key': key},
                {'$set': {'temperature': 25.0 + j * 0.1, 'updated_at': datetime.now().isoformat()}}
            )
        end_time = time.time()
        
        elapsed = end_time - start_time
        times.append(elapsed)
        
        throughput = num_records / elapsed
        print(f"  Itération {i+1}: {elapsed:.4f}s ({throughput:.0f} updates/s)")
    
    # Nettoyer
    collection.delete_many({'benchmark_type': 'update'})
    
    # Statistiques
    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    min_time = min(times)
    max_time = max(times)
    avg_throughput = num_records / avg_time
    
    print(f"\nRÉSULTATS MISE À JOUR:")
    print(f"  Temps moyen: {avg_time:.4f}s (±{std_dev:.4f}s)")
    print(f"  Min/Max: {min_time:.4f}s / {max_time:.4f}s")
    print(f"  Débit moyen: {avg_throughput:.0f} mises à jour/seconde")
    
    return {
        'operation': 'update',
        'num_records': num_records,
        'iterations': iterations,
        'avg_time': avg_time,
        'std_dev': std_dev,
        'min_time': min_time,
        'max_time': max_time,
        'throughput': avg_throughput
    }

def benchmark_aggregate(collection, iterations=5):
    """
    Benchmark des opérations d'agrégation
    
    Args:
        collection: Collection MongoDB
        iterations: Nombre d'itérations
    
    Returns:
        dict: Statistiques de performance
    """
    print(f"\n{'='*80}")
    print(f"BENCHMARK AGRÉGATION - {iterations} itérations")
    print(f"{'='*80}")
    
    times = []
    
    for i in range(iterations):
        # Mesurer le temps d'agrégation (groupement par station)
        start_time = time.time()
        pipeline = [
            {'$group': {
                '_id': '$id_station',
                'count': {'$sum': 1},
                'avg_temp': {'$avg': '$temperature'}
            }},
            {'$sort': {'count': -1}}
        ]
        results = list(collection.aggregate(pipeline))
        end_time = time.time()
        
        elapsed = end_time - start_time
        times.append(elapsed)
        
        print(f"  Itération {i+1}: {elapsed:.4f}s ({len(results)} groupes)")
    
    # Statistiques
    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    min_time = min(times)
    max_time = max(times)
    
    print(f"\nRÉSULTATS AGRÉGATION:")
    print(f"  Temps moyen: {avg_time:.4f}s (±{std_dev:.4f}s)")
    print(f"  Min/Max: {min_time:.4f}s / {max_time:.4f}s")
    
    return {
        'operation': 'aggregate',
        'iterations': iterations,
        'avg_time': avg_time,
        'std_dev': std_dev,
        'min_time': min_time,
        'max_time': max_time
    }

def main():
    """Fonction principale pour exécuter tous les benchmarks"""
    print(f"\n{'#'*80}")
    print(f"# BENCHMARK MONGODB - PERFORMANCE LECTURE/ÉCRITURE")
    print(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*80}")
    
    # Connexion MongoDB
    client = get_mongo_client()
    db = client[os.getenv('MONGODB_DATABASE', 'weather_data')]
    collection = db[os.getenv('MONGODB_COLLECTION', 'measurements')]
    
    # Vérifier la connexion
    try:
        client.admin.command('ping')
        print(f"\n✓ Connexion MongoDB établie")
        print(f"  Base de données: {db.name}")
        print(f"  Collection: {collection.name}")
        print(f"  Documents existants: {collection.count_documents({})}")
    except Exception as e:
        print(f"\n✗ Erreur de connexion MongoDB: {e}")
        return
    
    # Configurer les paramètres de benchmark
    small_size = 100
    medium_size = 1000
    iterations = 5
    
    results = []
    
    # Benchmark Écriture
    results.append(benchmark_write(collection, num_records=small_size, iterations=iterations))
    results.append(benchmark_write(collection, num_records=medium_size, iterations=iterations))
    
    # Benchmark Lecture Séquentielle
    results.append(benchmark_read_sequential(collection, num_records=small_size, iterations=iterations))
    results.append(benchmark_read_sequential(collection, num_records=medium_size, iterations=iterations))
    
    # Benchmark Lecture Indexée
    results.append(benchmark_read_indexed(collection, num_records=small_size, iterations=iterations))
    results.append(benchmark_read_indexed(collection, num_records=medium_size, iterations=iterations))
    
    # Benchmark Mise à jour
    results.append(benchmark_update(collection, num_records=small_size, iterations=iterations))
    results.append(benchmark_update(collection, num_records=medium_size, iterations=iterations))
    
    # Benchmark Agrégation (sur données réelles)
    results.append(benchmark_aggregate(collection, iterations=iterations))
    
    # Résumé global
    print(f"\n{'#'*80}")
    print(f"# RÉSUMÉ GLOBAL DES PERFORMANCES")
    print(f"{'#'*80}")
    print(f"\n{'Opération':<20} {'Taille':<10} {'Temps Moyen':<15} {'Débit':<20}")
    print(f"{'-'*80}")
    
    for result in results:
        op = result['operation']
        size = result.get('num_records', 'N/A')
        avg_time = result['avg_time']
        throughput = result.get('throughput', 'N/A')
        
        if throughput != 'N/A':
            throughput_str = f"{throughput:.0f} docs/s"
        else:
            throughput_str = "N/A"
        
        print(f"{op:<20} {str(size):<10} {avg_time:<15.4f} {throughput_str:<20}")
    
    print(f"\n{'#'*80}")
    print(f"# Benchmark terminé avec succès")
    print(f"{'#'*80}\n")
    
    client.close()

if __name__ == "__main__":
    main()
