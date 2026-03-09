"""
main.py – Pipeline principal : orchestration de bout en bout

Execute sequentiellement toutes les etapes du pipeline :
  1. Initialisation de la base (schemas + tables)
  2. Ingestion des donnees RH (XLSX -> staging.employes)
  3. Ingestion des donnees sportives (XLSX -> staging.pratiques_declarees)
  4. Simulation des activites Strava (-> raw.activites_strava)
  5. Nettoyage Strava (raw -> staging)
  6. Calcul des metriques gold (distances, eligibilites, impact financier)
  7. Generation des notifications Slack (mock JSON)

Options CLI :
  --reset       Reinitialiser la base avant execution
  --skip-api    Ne pas recalculer les distances (reutilise le cache)
  --seed N      Graine aleatoire pour la simulation Strava (defaut : 42)
  --step N      Executer uniquement l'etape N (1 a 7)
  --dry-run     Afficher les etapes sans les executer

Utilisation :
    python -m src.main                   # pipeline complet
    python -m src.main --reset           # reset + pipeline complet
    python -m src.main --step 4          # simulation Strava uniquement
    python -m src.main --dry-run         # afficher les etapes
"""

import argparse
import logging
import sys
import time

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Definition des etapes du pipeline
# Chaque etape est un tuple (nom, description, fonction a appeler)
# Les fonctions sont importees a l'interieur de run_pipeline() pour eviter
# les imports circulaires et accelerer le --help / --dry-run
# ---------------------------------------------------------------------------

STEPS = [
    ("init_db",        "Initialisation de la base (schemas + tables)"),
    ("load_rh",        "Ingestion des donnees RH (XLSX -> staging.employes)"),
    ("load_sport",     "Ingestion des donnees sportives (XLSX -> staging.pratiques_declarees)"),
    ("generate_strava","Simulation des activites Strava (-> raw.activites_strava)"),
    ("staging",        "Nettoyage Strava (raw -> staging.activites_strava)"),
    ("gold",           "Calcul gold (distances, eligibilites, impact financier)"),
    ("mock_slack",     "Generation des notifications Slack (mock JSON)"),
]


def run_step(step_index, reset=False, seed=42, skip_api=False):
    """
    Execute une etape du pipeline par son index (0-based).

    Parameters
    ----------
    step_index : int
        Index de l'etape dans STEPS (0 a 6).
    reset : bool
        Si True et step_index == 0, reinitialise la base.
    seed : int
        Graine aleatoire pour la simulation Strava (etape 3).
    skip_api : bool
        Si True, ne pas appeler l'API Google Maps (etape 6, reutilise le cache).

    Returns
    -------
    dict ou int ou None
        Resultat retourne par la fonction de l'etape.
    """
    step_name = STEPS[step_index][0]

    if step_name == "init_db":
        from src.db.init_db import init_database
        init_database(reset=reset)

    elif step_name == "load_rh":
        from src.ingestion.load_rh import load_rh_to_staging
        return load_rh_to_staging()

    elif step_name == "load_sport":
        from src.ingestion.load_sport import load_sport_to_staging
        return load_sport_to_staging()

    elif step_name == "generate_strava":
        from src.simulation.generate_strava import generate_and_load
        return generate_and_load(seed=seed)

    elif step_name == "staging":
        from src.transformation.staging import clean_strava_to_staging
        return clean_strava_to_staging()

    elif step_name == "gold":
        from src.transformation.gold import run_gold_pipeline
        run_gold_pipeline(skip_api=skip_api)

    elif step_name == "mock_slack":
        from src.notifications.mock_slack import generate_slack_messages
        return generate_slack_messages()


def run_pipeline(reset=False, seed=42, step=None, dry_run=False, skip_api=False):
    """
    Execute le pipeline complet ou une etape specifique.

    Parameters
    ----------
    reset : bool
        Si True, reinitialise la base avant execution.
    seed : int
        Graine aleatoire pour la simulation Strava.
    step : int or None
        Si renseigne, execute uniquement cette etape (1-based).
    dry_run : bool
        Si True, affiche les etapes sans les executer.
    skip_api : bool
        Si True, ne pas appeler l'API Google Maps (reutilise le cache).
    """
    logger.info("=" * 70)
    logger.info("PIPELINE SPORT DATA SOLUTION – Avantages Sportifs")
    logger.info("=" * 70)

    # Determiner les etapes a executer
    if step is not None:
        # Execution d'une seule etape (1-based -> 0-based)
        indices = [step - 1]
        logger.info(f"Mode etape unique : etape {step}/7")
    else:
        indices = list(range(len(STEPS)))
        logger.info(f"Mode pipeline complet : {len(STEPS)} etapes")

    if dry_run:
        logger.info("[DRY-RUN] Aucune etape ne sera executee.")

    logger.info("-" * 70)

    # Execution des etapes
    total_start = time.time()
    nb_success = 0
    nb_erreurs = 0

    for i in indices:
        step_num = i + 1
        step_name, step_desc = STEPS[i]

        logger.info(f"")
        logger.info(f"--- Etape {step_num}/7 : {step_desc} ---")

        if dry_run:
            logger.info(f"  [DRY-RUN] {step_name} -> non execute")
            nb_success += 1
            continue

        step_start = time.time()
        try:
            run_step(i, reset=reset, seed=seed, skip_api=skip_api)
            elapsed = time.time() - step_start
            logger.info(f"  Etape {step_num} terminee en {elapsed:.1f}s")
            nb_success += 1

        except Exception as err:
            elapsed = time.time() - step_start
            logger.error(f"  ERREUR etape {step_num} ({step_name}) apres {elapsed:.1f}s : {err}")
            nb_erreurs += 1
            # On arrete le pipeline en cas d'erreur (les etapes sont dependantes)
            logger.error("  Pipeline interrompu. Corrigez l'erreur et relancez.")
            break

    # Recap final
    total_elapsed = time.time() - total_start
    logger.info("")
    logger.info("=" * 70)
    logger.info(f"PIPELINE TERMINE – {nb_success} etape(s) OK, {nb_erreurs} erreur(s)")
    logger.info(f"Duree totale : {total_elapsed:.1f}s")
    logger.info("=" * 70)

    return nb_erreurs == 0


# ---------------------------------------------------------------------------
# Point d'entree CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline Sport Data Solution – Avantages Sportifs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python -m src.main                   # pipeline complet
  python -m src.main --reset           # reset base + pipeline complet
  python -m src.main --step 4          # simulation Strava uniquement
  python -m src.main --step 6          # recalcul gold uniquement
  python -m src.main --dry-run         # afficher les etapes
  python -m src.main --seed 123        # seed personnalise
""",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reinitialiser la base (DROP + CREATE) avant execution",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Graine aleatoire pour la simulation Strava (defaut: 42)",
    )
    parser.add_argument(
        "--step",
        type=int,
        choices=range(1, 8),
        metavar="N",
        help="Executer uniquement l'etape N (1-7)",
    )
    parser.add_argument(
        "--skip-api",
        action="store_true",
        help="Ne pas appeler l'API Google Maps (reutilise le cache existant)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Afficher les etapes sans les executer",
    )

    args = parser.parse_args()

    success = run_pipeline(
        reset=args.reset,
        seed=args.seed,
        step=args.step,
        dry_run=args.dry_run,
        skip_api=args.skip_api,
    )

    sys.exit(0 if success else 1)
