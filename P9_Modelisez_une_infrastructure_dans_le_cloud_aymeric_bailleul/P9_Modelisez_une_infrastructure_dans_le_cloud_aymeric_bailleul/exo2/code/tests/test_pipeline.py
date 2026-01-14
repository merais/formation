"""
Tests pytest pour valider le pipeline de tickets
Vérifie que les données sont correctement ingérées et traitées dans MySQL
"""
import pytest
import mysql.connector
from mysql.connector import Error
import os


# Configuration MySQL
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'database': os.getenv('MYSQL_DATABASE', 'ticket_system'),
    'user': os.getenv('MYSQL_USER', 'ticket_user'),
    'password': os.getenv('MYSQL_PASSWORD', 'ticket_password')
}


@pytest.fixture(scope="module")
def db_connection():
    """Fixture pour créer une connexion MySQL réutilisable"""
    conn = None
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        yield conn
    except Error as e:
        pytest.fail(f"Impossible de se connecter à MySQL: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()


@pytest.fixture
def db_cursor(db_connection):
    """Fixture pour créer un curseur par test (évite les problèmes d'unread results)"""
    cursor = db_connection.cursor(dictionary=True, buffered=True)
    yield cursor
    cursor.close()


class TestDatabaseConnection:
    """Tests de connexion à la base de données"""
    
    def test_connection_successful(self, db_connection):
        """Vérifie que la connexion à MySQL est établie"""
        assert db_connection.is_connected(), "La connexion à MySQL a échoué"
    
    def test_database_exists(self, db_cursor):
        """Vérifie que la base de données ticket_system existe"""
        db_cursor.execute("SELECT DATABASE()")
        result = db_cursor.fetchone()
        assert result['DATABASE()'] == 'ticket_system', "Base de données incorrecte"


class TestTablesExistence:
    """Tests de présence des tables"""
    
    def test_table_tickets_enrichis_exists(self, db_cursor):
        """Vérifie que la table tickets_enrichis existe"""
        db_cursor.execute("SHOW TABLES LIKE 'tickets_enrichis'")
        assert db_cursor.fetchone() is not None, "Table tickets_enrichis n'existe pas"
    
    def test_table_stats_par_type_exists(self, db_cursor):
        """Vérifie que la table stats_par_type existe"""
        db_cursor.execute("SHOW TABLES LIKE 'stats_par_type'")
        assert db_cursor.fetchone() is not None, "Table stats_par_type n'existe pas"
    
    def test_table_stats_par_priorite_exists(self, db_cursor):
        """Vérifie que la table stats_par_priorite existe"""
        db_cursor.execute("SHOW TABLES LIKE 'stats_par_priorite'")
        assert db_cursor.fetchone() is not None, "Table stats_par_priorite n'existe pas"
    
    def test_table_stats_par_equipe_exists(self, db_cursor):
        """Vérifie que la table stats_par_equipe existe"""
        db_cursor.execute("SHOW TABLES LIKE 'stats_par_equipe'")
        assert db_cursor.fetchone() is not None, "Table stats_par_equipe n'existe pas"


class TestViewsExistence:
    """Tests de présence des vues SQL"""
    
    def test_view_charge_equipes_exists(self, db_cursor):
        """Vérifie que la vue v_charge_equipes existe"""
        db_cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW' AND Tables_in_ticket_system = 'v_charge_equipes'")
        assert db_cursor.fetchone() is not None, "Vue v_charge_equipes n'existe pas"
    
    def test_view_tickets_recents_exists(self, db_cursor):
        """Vérifie que la vue v_tickets_recents existe"""
        db_cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW' AND Tables_in_ticket_system = 'v_tickets_recents'")
        assert db_cursor.fetchone() is not None, "Vue v_tickets_recents n'existe pas"
    
    def test_view_analyse_type_priorite_exists(self, db_cursor):
        """Vérifie que la vue v_analyse_type_priorite existe"""
        db_cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW' AND Tables_in_ticket_system = 'v_analyse_type_priorite'")
        assert db_cursor.fetchone() is not None, "Vue v_analyse_type_priorite n'existe pas"


class TestDataIngestion:
    """Tests d'ingestion des données"""
    
    def test_tickets_are_ingested(self, db_cursor):
        """Vérifie que des tickets ont été ingérés"""
        db_cursor.execute("SELECT COUNT(*) as count FROM tickets_enrichis")
        result = db_cursor.fetchone()
        assert result['count'] > 0, "Aucun ticket n'a été ingéré dans la base de données"
    
    def test_tickets_have_required_columns(self, db_cursor):
        """Vérifie que les tickets contiennent toutes les colonnes requises"""
        db_cursor.execute("SELECT * FROM tickets_enrichis LIMIT 1")
        if db_cursor.rowcount > 0:
            result = db_cursor.fetchone()
            required_columns = ['ticket_id', 'client_id', 'date_creation', 'demande', 
                              'type_demande', 'priorite', 'equipe_assignee', 'timestamp_traitement']
            for col in required_columns:
                assert col in result, f"Colonne {col} manquante dans tickets_enrichis"
    
    def test_tickets_have_valid_team_assignment(self, db_cursor):
        """Vérifie que tous les tickets ont une équipe assignée valide"""
        db_cursor.execute("""
            SELECT COUNT(*) as count 
            FROM tickets_enrichis 
            WHERE equipe_assignee IS NULL OR equipe_assignee = ''
        """)
        result = db_cursor.fetchone()
        assert result['count'] == 0, "Certains tickets n'ont pas d'équipe assignée"


class TestDataQuality:
    """Tests de qualité des données"""
    
    def test_ticket_ids_are_unique(self, db_cursor):
        """Vérifie que les ticket_id sont uniques"""
        db_cursor.execute("""
            SELECT ticket_id, COUNT(*) as count 
            FROM tickets_enrichis 
            GROUP BY ticket_id 
            HAVING count > 1
        """)
        duplicates = db_cursor.fetchall()
        assert len(duplicates) == 0, f"Des ticket_id dupliqués ont été trouvés: {duplicates}"
    
    def test_valid_priority_values(self, db_cursor):
        """Vérifie que les priorités sont valides"""
        valid_priorities = ['Basse', 'Moyenne', 'Haute', 'Critique']
        db_cursor.execute("SELECT DISTINCT priorite FROM tickets_enrichis")
        priorities = [row['priorite'] for row in db_cursor.fetchall()]
        for priority in priorities:
            assert priority in valid_priorities, f"Priorité invalide trouvée: {priority}"
    
    def test_valid_type_demande_values(self, db_cursor):
        """Vérifie que les types de demande sont valides"""
        valid_types = ['Technique', 'Facturation', 'Commercial', 'Support', 'Réclamation']
        db_cursor.execute("SELECT DISTINCT type_demande FROM tickets_enrichis")
        types = [row['type_demande'] for row in db_cursor.fetchall()]
        for type_demande in types:
            assert type_demande in valid_types, f"Type de demande invalide trouvé: {type_demande}"
    
    def test_valid_team_assignment_mapping(self, db_cursor):
        """Vérifie que le mapping type_demande -> équipe est correct"""
        expected_mapping = {
            'Technique': 'Equipe Support Technique',
            'Facturation': 'Equipe Comptabilité',
            'Commercial': 'Equipe Commerciale',
            'Support': 'Equipe Assistance Client',
            'Réclamation': 'Equipe Qualité'
        }
        
        db_cursor.execute("""
            SELECT DISTINCT type_demande, equipe_assignee 
            FROM tickets_enrichis
        """)
        mappings = db_cursor.fetchall()
        
        for mapping in mappings:
            type_demande = mapping['type_demande']
            equipe = mapping['equipe_assignee']
            assert expected_mapping[type_demande] == equipe, \
                f"Mapping incorrect: {type_demande} -> {equipe}, attendu: {expected_mapping[type_demande]}"


class TestStatistics:
    """Tests des statistiques et agrégations"""
    
    def test_stats_par_type_has_data(self, db_cursor):
        """Vérifie que les statistiques par type sont générées"""
        db_cursor.execute("SELECT COUNT(*) as count FROM stats_par_type")
        result = db_cursor.fetchone()
        assert result['count'] > 0, "Aucune statistique par type n'a été générée"
    
    def test_stats_par_priorite_has_data(self, db_cursor):
        """Vérifie que les statistiques par priorité sont générées"""
        db_cursor.execute("SELECT COUNT(*) as count FROM stats_par_priorite")
        result = db_cursor.fetchone()
        assert result['count'] > 0, "Aucune statistique par priorité n'a été générée"
    
    def test_stats_par_equipe_has_data(self, db_cursor):
        """Vérifie que les statistiques par équipe sont générées"""
        db_cursor.execute("SELECT COUNT(*) as count FROM stats_par_equipe")
        result = db_cursor.fetchone()
        assert result['count'] > 0, "Aucune statistique par équipe n'a été générée"
    
    def test_stats_coherence_tickets_count(self, db_cursor):
        """Vérifie que les statistiques les plus récentes sont cohérentes"""
        db_cursor.execute("SELECT COUNT(*) as total FROM tickets_enrichis")
        total_tickets = db_cursor.fetchone()['total']

        # Récupérer la dernière entrée de stats par priorité (la plus récente)
        db_cursor.execute("""
            SELECT SUM(nombre_tickets) as sum 
            FROM stats_par_priorite 
            WHERE timestamp_calcul = (SELECT MAX(timestamp_calcul) FROM stats_par_priorite)
        """)
        result = db_cursor.fetchone()
        stats_sum = result['sum'] if result and result['sum'] is not None else 0

        # Tolérance de 10% car les stats peuvent être légèrement décalées
        tolerance = total_tickets * 0.1
        assert abs(total_tickets - stats_sum) <= tolerance, \
            f"Incohérence: {total_tickets} tickets vs {stats_sum} dans les dernières stats"

class TestViews:
    """Tests des vues SQL"""
    
    def test_view_charge_equipes_returns_data(self, db_cursor):
        """Vérifie que la vue v_charge_equipes retourne des données"""
        db_cursor.execute("SELECT COUNT(*) as count FROM v_charge_equipes")
        result = db_cursor.fetchone()
        assert result['count'] > 0, "La vue v_charge_equipes ne retourne aucune donnée"
    
    def test_view_charge_equipes_has_all_teams(self, db_cursor):
        """Vérifie que toutes les équipes sont présentes dans la vue"""
        expected_teams = ['Equipe Support Technique', 'Equipe Comptabilité', 
                         'Equipe Commerciale', 'Equipe Assistance Client', 'Equipe Qualité']
        
        db_cursor.execute("SELECT equipe_assignee FROM v_charge_equipes")
        teams = [row['equipe_assignee'] for row in db_cursor.fetchall()]
        
        for expected_team in expected_teams:
            assert expected_team in teams, f"Équipe {expected_team} manquante dans la vue"


class TestPerformance:
    """Tests de performance et volumétrie"""
    
    def test_minimum_tickets_threshold(self, db_cursor):
        """Vérifie qu'un nombre minimum de tickets est présent (pipeline fonctionnel)"""
        db_cursor.execute("SELECT COUNT(*) as count FROM tickets_enrichis")
        result = db_cursor.fetchone()
        # Au moins 10 tickets doivent être présents pour considérer que le pipeline fonctionne
        assert result['count'] >= 10, f"Seulement {result['count']} tickets présents, attendu au moins 10"
    
    def test_recent_data_ingestion(self, db_cursor):
        """Vérifie que des données récentes ont été ingérées (dernière heure)"""
        db_cursor.execute("""
            SELECT COUNT(*) as count 
            FROM tickets_enrichis 
            WHERE timestamp_traitement >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
        """)
        result = db_cursor.fetchone()
        assert result['count'] > 0, "Aucun ticket récent (< 1h) n'a été ingéré"


if __name__ == "__main__":
    # Permet de lancer les tests directement avec python test_pipeline.py
    pytest.main([__file__, "-v", "--tb=short"])
