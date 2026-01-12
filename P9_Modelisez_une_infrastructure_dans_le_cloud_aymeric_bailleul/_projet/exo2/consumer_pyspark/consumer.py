"""
Consommateur PySpark pour traiter les tickets clients depuis Redpanda
Lit les tickets, applique des transformations et sauvegarde dans MySQL
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, count, when, current_timestamp
)
from pyspark.sql.types import (
    StructType, StructField, StringType, TimestampType
)
import time
import os

# Configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'redpanda:29092')
TOPIC_NAME = 'client_tickets'

# Configuration MySQL
MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'ticket_system')
MYSQL_USER = os.getenv('MYSQL_USER', 'ticket_user')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'ticket_password')
MYSQL_URL = f"jdbc:mysql://{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Schéma des tickets
ticket_schema = StructType([
    StructField("ticket_id", StringType(), True),
    StructField("client_id", StringType(), True),
    StructField("date_creation", StringType(), True),
    StructField("demande", StringType(), True),
    StructField("type_demande", StringType(), True),
    StructField("priorite", StringType(), True)
])

# Mapping des équipes de support selon le type de demande
EQUIPE_MAPPING = {
    'Technique': 'Equipe Support Technique',
    'Facturation': 'Equipe Comptabilité',
    'Commercial': 'Equipe Commerciale',
    'Support': 'Equipe Assistance Client',
    'Réclamation': 'Equipe Qualité'
}


def create_spark_session():
    """Crée et configure la session Spark"""
    print("Création de la session Spark...")
    
    spark = SparkSession.builder \
        .appName("TicketAnalytics") \
        .config("spark.jars.packages", 
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
                "mysql:mysql-connector-java:8.0.33") \
        .config("spark.sql.shuffle.partitions", "2") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    print("Session Spark créée avec succès!\n")
    
    return spark


def write_to_mysql(df, table_name, mode="append"):
    """Écrit un DataFrame dans une table MySQL"""
    df.write \
        .format("jdbc") \
        .option("url", MYSQL_URL) \
        .option("dbtable", table_name) \
        .option("user", MYSQL_USER) \
        .option("password", MYSQL_PASSWORD) \
        .option("driver", "com.mysql.cj.jdbc.Driver") \
        .mode(mode) \
        .save()


def process_batch_tickets(batch_df, batch_id):
    """Traite un batch de tickets et l'écrit dans MySQL"""
    if batch_df.count() > 0:
        print(f"Traitement du batch {batch_id} avec {batch_df.count()} tickets...")
        write_to_mysql(batch_df, "tickets_enrichis", mode="append")
        print(f"Batch {batch_id} sauvegardé dans MySQL (tickets_enrichis)")


def process_batch_stats_type(batch_df, batch_id):
    """Traite les statistiques par type et les écrit dans MySQL"""
    if batch_df.count() > 0:
        df_with_timestamp = batch_df.withColumn("timestamp_calcul", current_timestamp())
        print(f"Traitement des stats par type (batch {batch_id})...")
        write_to_mysql(df_with_timestamp, "stats_par_type", mode="append")
        print(f"Stats par type sauvegardées (batch {batch_id})")


def process_batch_stats_priorite(batch_df, batch_id):
    """Traite les statistiques par priorité et les écrit dans MySQL"""
    if batch_df.count() > 0:
        df_with_timestamp = batch_df.withColumn("timestamp_calcul", current_timestamp())
        print(f"Traitement des stats par priorité (batch {batch_id})...")
        write_to_mysql(df_with_timestamp, "stats_par_priorite", mode="append")
        print(f"Stats par priorité sauvegardées (batch {batch_id})")


def process_batch_stats_equipe(batch_df, batch_id):
    """Traite les statistiques par équipe et les écrit dans MySQL"""
    if batch_df.count() > 0:
        df_with_timestamp = batch_df.withColumn("timestamp_calcul", current_timestamp())
        print(f"Traitement des stats par équipe (batch {batch_id})...")
        write_to_mysql(df_with_timestamp, "stats_par_equipe", mode="append")
        print(f"Stats par équipe sauvegardées (batch {batch_id})")



def main():
    """Fonction principale pour traiter les tickets"""
    print("=" * 60)
    print("Démarrage du consommateur PySpark...")
    print("=" * 60)
    print(f"Kafka Broker: {KAFKA_BROKER}")
    print(f"Topic: {TOPIC_NAME}")
    print(f"MySQL: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")
    print("=" * 60 + "\n")
    
    # Attendre que MySQL et Redpanda soient prêts
    print("Attente de l'initialisation des services...")
    time.sleep(20)
    
    # Créer la session Spark
    spark = create_spark_session()
    
    try:
        # Lire le stream depuis Redpanda
        print("Lecture du stream Kafka...")
        df_stream = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BROKER) \
            .option("subscribe", TOPIC_NAME) \
            .option("startingOffsets", "earliest") \
            .load()
        
        # Parser les données JSON
        df_parsed = df_stream \
            .select(from_json(col("value").cast("string"), ticket_schema).alias("data")) \
            .select("data.*")
        
        # Convertir la date en timestamp et assigner l'équipe
        df_enriched = df_parsed \
            .withColumn("date_creation", col("date_creation").cast("timestamp")) \
            .withColumn("equipe_assignee", 
                       when(col("type_demande") == "Technique", "Equipe Support Technique")
                       .when(col("type_demande") == "Facturation", "Equipe Comptabilité")
                       .when(col("type_demande") == "Commercial", "Equipe Commerciale")
                       .when(col("type_demande") == "Support", "Equipe Assistance Client")
                       .when(col("type_demande") == "Réclamation", "Equipe Qualité")
                       .otherwise("Equipe Générale")) \
            .withColumn("timestamp_traitement", current_timestamp())
        
        print("Données parsées et enrichies\n")
        
        # ========================================
        # ÉCRITURE 1: Tickets enrichis
        # ========================================
        print("Configuration de l'écriture des tickets enrichis dans MySQL...")
        
        query1 = df_enriched \
            .writeStream \
            .foreachBatch(process_batch_tickets) \
            .outputMode("append") \
            .start()
        
        # ========================================
        # ÉCRITURE 2: Statistiques par type
        # ========================================
        print("Configuration des statistiques par type...")
        
        df_by_type = df_enriched \
            .groupBy("type_demande", "equipe_assignee") \
            .agg(count("*").alias("nombre_tickets"))
        
        query2 = df_by_type \
            .writeStream \
            .foreachBatch(process_batch_stats_type) \
            .outputMode("complete") \
            .trigger(processingTime='30 seconds') \
            .start()
        
        # ========================================
        # ÉCRITURE 3: Statistiques par priorité
        # ========================================
        print("Configuration des statistiques par priorité...")
        
        df_by_priority = df_enriched \
            .groupBy("priorite") \
            .agg(count("*").alias("nombre_tickets"))
        
        query3 = df_by_priority \
            .writeStream \
            .foreachBatch(process_batch_stats_priorite) \
            .outputMode("complete") \
            .trigger(processingTime='30 seconds') \
            .start()
        
        # ========================================
        # ÉCRITURE 4: Statistiques par équipe
        # ========================================
        print("Configuration des statistiques par équipe...")
        
        df_by_team = df_enriched \
            .groupBy("equipe_assignee") \
            .agg(
                count("*").alias("total_tickets"),
                count(when(col("priorite") == "Critique", True)).alias("tickets_critiques"),
                count(when(col("priorite") == "Haute", True)).alias("tickets_haute_priorite")
            )
        
        query4 = df_by_team \
            .writeStream \
            .foreachBatch(process_batch_stats_equipe) \
            .outputMode("complete") \
            .trigger(processingTime='30 seconds') \
            .start()
        
        print("\n" + "=" * 60)
        print("Tous les streams sont configurés et démarrés!")
        print("Traitement en cours et écriture dans MySQL...")
        print("=" * 60 + "\n")
        
        # Attendre la fin des streams (ou Ctrl+C)
        query1.awaitTermination()
        
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Arrêt du consommateur PySpark...")
        print("=" * 60)
    except Exception as e:
        print(f"\nErreur: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        spark.stop()
        print("Consommateur PySpark arrêté proprement")


if __name__ == "__main__":
    main()
