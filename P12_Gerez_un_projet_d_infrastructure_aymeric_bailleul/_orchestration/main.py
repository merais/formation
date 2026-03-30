"""
main.py – Pipeline d'initialisation complet Sport Data Orchestration

Enchaine les etapes dans l'ordre correct :
  1. Initialisation de la base de donnees (schemas + tables + meta)
  2. Chargement des donnees RH (XLSX -> staging.employes + rh_prive.identites)
  3. Chargement des pratiques sportives (XLSX -> staging.pratiques_declarees)
  4. Generation des activites Strava simulees (staging -> raw.activites_strava)
  5. Nettoyage Strava (raw -> staging.activites_strava)
  6. Pipeline gold (distances + eligibilites + impact financier)

Utilisation :
    python main.py                   # pipeline complet
    python main.py --reset           # recrée la base avant le pipeline
    python main.py --skip-api        # pas d'appel Google Maps (reutilise cache)
    python main.py --seed 42         # generation Strava reproductible
"""

import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_pipeline(reset: bool = False, skip_api: bool = False, seed: int = None):
    """Execute le pipeline complet d'initialisation."""

    # ── Etape 1 : Initialisation de la base ────────────────────────────────
    logger.info("=" * 60)
    logger.info("ETAPE 1/6 – Initialisation de la base de donnees")
    logger.info("=" * 60)
    from src.db.init_db import init_database
    init_database(reset=reset)

    # ── Etape 2 : Chargement RH ────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("ETAPE 2/6 – Chargement des donnees RH")
    logger.info("=" * 60)
    from src.ingestion.load_rh import load_rh_to_staging
    stats_rh = load_rh_to_staging()
    logger.info(f"RH : {stats_rh}")

    # ── Etape 3 : Chargement pratiques sportives ────────────────────────────
    logger.info("=" * 60)
    logger.info("ETAPE 3/6 – Chargement des pratiques sportives")
    logger.info("=" * 60)
    from src.ingestion.load_sport import load_sport_to_staging
    nb_sport = load_sport_to_staging()
    logger.info(f"Sport : {nb_sport} lignes chargees")

    # ── Etape 4 : Generation des activites Strava ──────────────────────────
    logger.info("=" * 60)
    logger.info("ETAPE 4/6 – Generation des activites Strava simulees")
    logger.info("=" * 60)
    from src.simulation.generate_strava import generate_and_load
    nb_strava = generate_and_load(seed=seed)
    logger.info(f"Strava : {nb_strava} activites generees")

    # ── Etape 5 : Nettoyage Strava (raw -> staging) ─────────────────────────
    logger.info("=" * 60)
    logger.info("ETAPE 5/6 – Nettoyage des activites Strava (raw -> staging)")
    logger.info("=" * 60)
    from src.transformation.staging import clean_strava_to_staging
    stats_staging = clean_strava_to_staging()
    logger.info(f"Staging : {stats_staging['valides']} valides / {stats_staging['total_raw']} brutes")

    # ── Etape 6 : Pipeline gold ─────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("ETAPE 6/6 – Pipeline gold (distances + eligibilites)")
    logger.info("=" * 60)
    from src.transformation.gold import run_gold_pipeline
    run_gold_pipeline(skip_api=skip_api)

    logger.info("=" * 60)
    logger.info("Pipeline d'initialisation termine avec succes.")
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline complet Sport Data Orchestration"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Supprimer et recreer la base avant le pipeline",
    )
    parser.add_argument(
        "--skip-api",
        action="store_true",
        dest="skip_api",
        help="Ne pas appeler l'API Google Maps (reutilise le cache)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Graine aleatoire pour la generation Strava (reproductibilite)",
    )
    args = parser.parse_args()

    try:
        run_pipeline(reset=args.reset, skip_api=args.skip_api, seed=args.seed)
    except Exception as e:
        logger.error(f"Pipeline echoue : {e}")
        sys.exit(1)
