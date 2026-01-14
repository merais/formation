# Quick Start - Procédure Rapide
## 1. Démarrer le pipeline (1 commande)
```powershell
docker-compose up --build
```

---

## 2. Vérifier que ça fonctionne
### Interface Web Redpanda Console
Ouvrir dans le navigateur : **http://localhost:8080**

- Cliquer sur "Topics" → `client_tickets`  

### Interface Web Spark UI
Ouvrir dans le navigateur : **http://localhost:4040**

- Voir les jobs Spark en cours
- Métriques de streaming (batch processing)
- Performances et temps d'exécution

### Nombre de tickets dans Redpanda (via commande)
```powershell
docker exec redpanda rpk topic describe client_tickets --print-partitions
```

---

## 3. Voir les données en détail
### Les 10 derniers tickets
```powershell
docker exec -it ticket-mysql mysql -u ticket_user -pticket_password -D ticket_system -e "SELECT ticket_id, type_demande, priorite, equipe_assignee FROM tickets_enrichis ORDER BY date_creation DESC LIMIT 10;"
```

### Charge par équipe
```powershell
docker exec -it ticket-mysql mysql -u ticket_user -pticket_password -D ticket_system -e "SELECT * FROM v_charge_equipes;"
```

---

## 4. Lancer les tests automatisés

```powershell
cd tests
py -m pip install -r requirements.txt
py -m pytest test_pipeline.py -v
```

**Résultat attendu** : 24 tests passent !

### Détail des 24 tests

#### Connexion à la base (2 tests)
1. `test_connection_successful` - Connexion MySQL établie
2. `test_database_exists` - Base de données ticket_system existe

#### Existence des tables (4 tests)
3. `test_table_tickets_enrichis_exists` - Table tickets_enrichis
4. `test_table_stats_par_type_exists` - Table stats_par_type
5. `test_table_stats_par_priorite_exists` - Table stats_par_priorite
6. `test_table_stats_par_equipe_exists` - Table stats_par_equipe

#### Existence des vues SQL (3 tests)
7. `test_view_charge_equipes_exists` - Vue v_charge_equipes
8. `test_view_tickets_recents_exists` - Vue v_tickets_recents
9. `test_view_analyse_type_priorite_exists` - Vue v_analyse_type_priorite

#### Ingestion des données (3 tests)
10. `test_tickets_are_ingested` - Des tickets ont été ingérés
11. `test_tickets_have_required_columns` - Toutes les colonnes requises présentes
12. `test_tickets_have_valid_team_assignment` - Toutes les équipes assignées

#### Qualité des données (4 tests)
13. `test_ticket_ids_are_unique` - Les ticket_id sont uniques
14. `test_valid_priority_values` - Priorités valides (Basse, Moyenne, Haute, Critique)
15. `test_valid_type_demande_values` - Types valides (Technique, Facturation, Commercial, Support, Réclamation)
16. `test_valid_team_assignment_mapping` - Mapping type → équipe correct

#### Statistiques (4 tests)
17. `test_stats_par_type_has_data` - Statistiques par type générées
18. `test_stats_par_priorite_has_data` - Statistiques par priorité générées
19. `test_stats_par_equipe_has_data` - Statistiques par équipe générées
20. `test_stats_coherence_tickets_count` - Cohérence des comptages

#### Vues SQL fonctionnelles (2 tests)
21. `test_view_charge_equipes_returns_data` - Vue charge équipes retourne données
22. `test_view_charge_equipes_has_all_teams` - Toutes les équipes présentes

#### Performance (2 tests)
23. `test_minimum_tickets_threshold` - Au moins 10 tickets présents
24. `test_recent_data_ingestion` - Données récentes (< 1h) ingérées

---

## 5. Voir le rapport d'analyse

```powershell
cd tests
py analyses_report.py
```

Vous verrez :
- Total de tickets
- Distribution par type
- Distribution par priorité
- Charge par équipe
- Top clients

---

## 6. Arrêter le pipeline

```powershell
docker-compose down
```

Pour tout nettoyer (données incluses) :
```powershell
docker-compose down -v
```

---

## Résumé : Le pipeline en action

```
1. Producer génère des tickets aléatoires → Redpanda
2. PySpark lit Redpanda → Enrichit les tickets (assigne équipe)
3. PySpark écrit dans MySQL → 4 tables
4. Vous interrogez MySQL → Analyses en temps réel
```

---

## Recap test ultra-rapide 

```powershell
# 1. Démarrer
docker-compose up -d

# 2. Vérifier
#    Affichage du nombre de lignes créer dans mysql
docker exec -it ticket-mysql mysql -u ticket_user -pticket_password -D ticket_system -e "SELECT COUNT(*) FROM tickets_enrichis; SELECT * FROM v_charge_equipes;"

#    Affichage du nombre de lignes créer dans mysql (actualisation toutes les secondes)
while ($true) { Clear-Host; docker exec -it ticket-mysql mysql -u ticket_user -pticket_password -D ticket_system -e "SELECT COUNT(*) FROM tickets_enrichis; SELECT * FROM v_charge_equipes;"; Start-Sleep -Seconds 1 }

# Affichage des logs en temps réel du producteur
docker logs -f ticket-producer

#    Affichage des logs en temps réel de spark
docker logs -f pyspark-consumer


# 3. Voir Redpanda Console
start http://localhost:8080

# 4. Voir Spark UI
start http://localhost:4040

# 5. Arrêter
docker-compose down
```