"""
Script d'analyse des données stockées dans MySQL
Permet d'interroger les données et générer des rapports

Usage:
    python test_analyses.py
"""
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime, timedelta
import os


# Configuration MySQL
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'database': os.getenv('MYSQL_DATABASE', 'ticket_system'),
    'user': os.getenv('MYSQL_USER', 'ticket_user'),
    'password': os.getenv('MYSQL_PASSWORD', 'ticket_password')
}


def get_connection():
    """Établit une connexion à MySQL"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        if conn.is_connected():
            print(f"Connecté à MySQL: {MYSQL_CONFIG['database']}\n")
            return conn
    except Error as e:
        print(f"Erreur de connexion: {e}")
        return None


def execute_query(conn, query, description=""):
    """Exécute une requête et retourne un DataFrame pandas"""
    try:
        if description:
            print(f"{description}")
            print("-" * 60)
        
        df = pd.read_sql(query, conn)
        print(df.to_string(index=False))
        print()
        return df
    except Error as e:
        print(f"Erreur lors de l'exécution: {e}\n")
        return None


def test_total_tickets(conn):
    """Compte le nombre total de tickets"""
    query = "SELECT COUNT(*) as total_tickets FROM tickets_enrichis"
    return execute_query(conn, query, "Total des tickets traités")


def test_tickets_par_type(conn):
    """Affiche la distribution des tickets par type"""
    query = """
        SELECT 
            type_demande,
            equipe_assignee,
            COUNT(*) as nombre_tickets,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tickets_enrichis), 2) as pourcentage
        FROM tickets_enrichis
        GROUP BY type_demande, equipe_assignee
        ORDER BY nombre_tickets DESC
    """
    return execute_query(conn, query, "Distribution des tickets par type de demande")


def test_tickets_par_priorite(conn):
    """Affiche la distribution des tickets par priorité"""
    query = """
        SELECT 
            priorite,
            COUNT(*) as nombre_tickets,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tickets_enrichis), 2) as pourcentage
        FROM tickets_enrichis
        GROUP BY priorite
        ORDER BY 
            FIELD(priorite, 'Critique', 'Haute', 'Moyenne', 'Basse')
    """
    return execute_query(conn, query, "Distribution des tickets par priorité")


def test_charge_par_equipe(conn):
    """Affiche la charge de travail par équipe"""
    query = """
        SELECT 
            equipe_assignee,
            COUNT(*) as total_tickets,
            SUM(CASE WHEN priorite = 'Critique' THEN 1 ELSE 0 END) as critiques,
            SUM(CASE WHEN priorite = 'Haute' THEN 1 ELSE 0 END) as haute,
            SUM(CASE WHEN priorite = 'Moyenne' THEN 1 ELSE 0 END) as moyenne,
            SUM(CASE WHEN priorite = 'Basse' THEN 1 ELSE 0 END) as basse
        FROM tickets_enrichis
        GROUP BY equipe_assignee
        ORDER BY total_tickets DESC
    """
    return execute_query(conn, query, "Charge de travail par équipe")


def test_tickets_recents(conn, limit=10):
    """Affiche les tickets les plus récents"""
    query = f"""
        SELECT 
            ticket_id,
            client_id,
            DATE_FORMAT(date_creation, '%Y-%m-%d %H:%i:%s') as date_creation,
            type_demande,
            priorite,
            equipe_assignee,
            SUBSTRING(demande, 1, 50) as demande_extrait
        FROM tickets_enrichis
        ORDER BY date_creation DESC
        LIMIT {limit}
    """
    return execute_query(conn, query, f"Les {limit} tickets les plus récents")


def test_stats_temporelles(conn):
    """Affiche les statistiques des dernières 24h"""
    query = """
        SELECT 
            DATE_FORMAT(date_creation, '%Y-%m-%d %H:00:00') as heure,
            COUNT(*) as nombre_tickets,
            SUM(CASE WHEN priorite IN ('Critique', 'Haute') THEN 1 ELSE 0 END) as prioritaires
        FROM tickets_enrichis
        WHERE date_creation >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        GROUP BY DATE_FORMAT(date_creation, '%Y-%m-%d %H:00:00')
        ORDER BY heure DESC
        LIMIT 10
    """
    return execute_query(conn, query, "Tickets par heure (dernières 24h)")


def test_top_clients(conn, limit=10):
    """Affiche les clients avec le plus de tickets"""
    query = f"""
        SELECT 
            client_id,
            COUNT(*) as nombre_tickets,
            SUM(CASE WHEN priorite = 'Critique' THEN 1 ELSE 0 END) as tickets_critiques,
            GROUP_CONCAT(DISTINCT type_demande ORDER BY type_demande) as types_demandes
        FROM tickets_enrichis
        GROUP BY client_id
        ORDER BY nombre_tickets DESC
        LIMIT {limit}
    """
    return execute_query(conn, query, f"Top {limit} clients par nombre de tickets")


def test_vue_charge_equipes(conn):
    """Teste la vue v_charge_equipes"""
    query = "SELECT * FROM v_charge_equipes"
    return execute_query(conn, query, "Vue: Charge globale des équipes")


def test_vue_analyse_type_priorite(conn):
    """Teste la vue v_analyse_type_priorite"""
    query = "SELECT * FROM v_analyse_type_priorite LIMIT 20"
    return execute_query(conn, query, "Vue: Analyse croisée type/priorité")


def generate_summary_report(conn):
    """Génère un rapport de synthèse complet"""
    print("\n" + "=" * 80)
    print(" " * 25 + "RAPPORT DE SYNTHÈSE")
    print("=" * 80 + "\n")
    
    # Statistiques générales
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total FROM tickets_enrichis")
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(DISTINCT client_id) as clients FROM tickets_enrichis")
    clients = cursor.fetchone()['clients']
    
    cursor.execute("SELECT COUNT(DISTINCT equipe_assignee) as equipes FROM tickets_enrichis")
    equipes = cursor.fetchone()['equipes']
    
    cursor.execute("""
        SELECT priorite, COUNT(*) as count 
        FROM tickets_enrichis 
        WHERE priorite IN ('Critique', 'Haute') 
        GROUP BY priorite
    """)
    prioritaires = sum([row['count'] for row in cursor.fetchall()])
    
    print(f"Total de tickets traités: {total}")
    print(f"Nombre de clients uniques: {clients}")
    print(f"Nombre d'équipes actives: {equipes}")
    print(f"Tickets prioritaires (Critique/Haute): {prioritaires} ({round(prioritaires*100/total if total > 0 else 0, 1)}%)")
    print("\n" + "=" * 80 + "\n")
    
    cursor.close()


def main():
    """Fonction principale - exécute toutes les analyses"""
    print("\n" + "=" * 80)
    print(" " * 20 + "ANALYSE DES DONNÉES - SYSTÈME DE TICKETS")
    print("=" * 80 + "\n")
    
    # Connexion à MySQL
    conn = get_connection()
    if not conn:
        print("Impossible de se connecter à MySQL")
        return
    
    try:
        # Exécuter les analyses
        test_total_tickets(conn)
        generate_summary_report(conn)
        test_tickets_par_type(conn)
        test_tickets_par_priorite(conn)
        test_charge_par_equipe(conn)
        test_tickets_recents(conn, limit=10)
        test_top_clients(conn, limit=10)
        test_stats_temporelles(conn)
        
        # Tester les vues
        print("\n" + "=" * 80)
        print(" " * 30 + "VUES SQL")
        print("=" * 80 + "\n")
        test_vue_charge_equipes(conn)
        test_vue_analyse_type_priorite(conn)
        
        print("=" * 80)
        print("Analyse terminée avec succès!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\nErreur lors de l'analyse: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("✓ Connexion MySQL fermée\n")


if __name__ == "__main__":
    main()
