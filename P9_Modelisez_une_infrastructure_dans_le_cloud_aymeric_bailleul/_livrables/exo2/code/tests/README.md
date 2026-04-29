# Guide d'utilisation du script d'analyse

## Installation

```bash
cd tests
pip install -r requirements.txt
```

## Configuration

Par défaut, le script se connecte à MySQL sur `localhost:3306`. 

Pour modifier la configuration, utilisez les variables d'environnement :

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_DATABASE=ticket_system
export MYSQL_USER=ticket_user
export MYSQL_PASSWORD=ticket_password
```

**Sous Windows PowerShell :**
```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_DATABASE="ticket_system"
$env:MYSQL_USER="ticket_user"
$env:MYSQL_PASSWORD="ticket_password"
```

## Exécution

```bash
python test_analyses.py
```

## Analyses disponibles

Le script génère automatiquement :

1. **Total des tickets traités**
2. **Rapport de synthèse** (nombre de clients, équipes, tickets prioritaires)
3. **Distribution par type de demande** (avec pourcentages)
4. **Distribution par priorité** (Critique, Haute, Moyenne, Basse)
5. **Charge de travail par équipe**
6. **Top 10 tickets les plus récents**
7. **Top 10 clients** (par nombre de tickets)
8. **Statistiques temporelles** (tickets par heure)
9. **Vues SQL** :
   - `v_charge_equipes` : Charge globale avec délai moyen
   - `v_analyse_type_priorite` : Analyse croisée

## Exemple de sortie

```
================================================================================
                    ANALYSE DES DONNÉES - SYSTÈME DE TICKETS
================================================================================

Connecté à MySQL: ticket_system

Total des tickets traités
------------------------------------------------------------
total_tickets
          150

================================================================================
                         RAPPORT DE SYNTHÈSE
================================================================================

Total de tickets traités: 150
Nombre de clients uniques: 78
Nombre d'équipes actives: 5
Tickets prioritaires (Critique/Haute): 72 (48.0%)

================================================================================
```

## Utilisation avec Docker

Si vous souhaitez exécuter le script depuis l'intérieur d'un conteneur Docker :

```bash
docker run --rm --network exo2_ticket-network \
  -e MYSQL_HOST=mysql \
  -e MYSQL_PORT=3306 \
  -e MYSQL_DATABASE=ticket_system \
  -e MYSQL_USER=ticket_user \
  -e MYSQL_PASSWORD=ticket_password \
  -v $(pwd)/tests:/app \
  python:3.11 \
  bash -c "cd /app && pip install -r requirements.txt && python test_analyses.py"
```

## Personnalisation

Vous pouvez modifier `test_analyses.py` pour :
- Ajouter de nouvelles requêtes SQL
- Modifier les limites (par défaut 10 pour les tops)
- Exporter les résultats vers CSV/Excel
- Générer des graphiques avec matplotlib

## Intégration avec pytest

Pour utiliser ce script comme test pytest :

```bash
pytest test_analyses.py -v
```

Note : Le script actuel n'utilise pas pytest pour l'instant, mais peut être facilement adapté.
