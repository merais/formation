"""
Script de test Apache Spark
"""

from pyspark.sql import SparkSession

def test_spark():
    print("Initialisation de Spark...")
    
    # Créer une session Spark
    spark = SparkSession.builder \
        .appName("Test Spark") \
        .master("local[*]") \
        .getOrCreate()
    
    print(f"Spark version: {spark.version}")
    print(f"Spark config: {spark.sparkContext.getConf().getAll()}")
    
    # Créer un DataFrame simple
    data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
    columns = ["nom", "age"]
    
    df = spark.createDataFrame(data, columns)
    
    print("\nDataFrame Spark:")
    df.show()
    
    print("\nStatistiques:")
    df.describe().show()
    
    print("\nFiltre age > 28:")
    df.filter(df.age > 28).show()
    
    # Arrêter la session Spark
    spark.stop()
    print("\nSpark stoppé. Test réussi !")

if __name__ == "__main__":
    test_spark()
