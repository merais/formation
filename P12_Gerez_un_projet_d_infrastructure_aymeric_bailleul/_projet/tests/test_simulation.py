"""
test_simulation.py – Tests de qualite sur les donnees Strava simulees

Verifie les donnees presentes dans raw.activites_strava :
  - Distances >= 0
  - Durees >= 0
  - Dates dans les 12 derniers mois
  - IDs salaries tous presents dans staging.employes
  - Types de sport dans la liste fermee
"""

from datetime import datetime, timedelta

import pytest

from src.transformation.staging import SPORTS_VALIDES


# ---------------------------------------------------------------------------
# Tests sur raw.activites_strava
# ---------------------------------------------------------------------------


class TestSimulationDistances:
    """Toutes les distances doivent etre strictement positives."""

    def test_distances_positives(self, activites_raw):
        """Aucune distance <= 0 dans raw.activites_strava."""
        invalides = [(row[0], row[4]) for row in activites_raw if row[4] <= 0]
        assert len(invalides) == 0, (
            f"{len(invalides)} activites avec distance <= 0 : {invalides[:5]}"
        )


class TestSimulationDurees:
    """Toutes les durees doivent etre strictement positives."""

    def test_durees_positives(self, activites_raw):
        """Aucune duree <= 0 dans raw.activites_strava."""
        invalides = [(row[0], row[5]) for row in activites_raw if row[5] <= 0]
        assert len(invalides) == 0, (
            f"{len(invalides)} activites avec duree <= 0 : {invalides[:5]}"
        )


class TestSimulationDates:
    """Les dates doivent etre dans les 13 derniers mois (marge de securite)."""

    def test_dates_dans_periode(self, activites_raw):
        """Toutes les dates de raw sont dans les 13 derniers mois."""
        date_limite_basse = datetime.now() - timedelta(days=395)
        date_limite_haute = datetime.now() + timedelta(days=1)  # marge pour le jour en cours

        hors_periode = []
        for row in activites_raw:
            date_debut = row[2]
            if date_debut < date_limite_basse or date_debut > date_limite_haute:
                hors_periode.append((row[0], date_debut))

        assert len(hors_periode) == 0, (
            f"{len(hors_periode)} activites hors periode : {hors_periode[:5]}"
        )


class TestSimulationIDs:
    """Les IDs salaries doivent correspondre a des employes existants."""

    def test_ids_salaries_valides(self, activites_raw, employes):
        """Chaque id_salarie de raw existe dans staging.employes."""
        ids_employes = {row[0] for row in employes}
        ids_activites = {row[1] for row in activites_raw}
        ids_inconnus = ids_activites - ids_employes
        assert len(ids_inconnus) == 0, (
            f"{len(ids_inconnus)} IDs salaries inconnus dans raw : {ids_inconnus}"
        )

    def test_seuls_sportifs_ont_des_activites(self, activites_raw, pratiques):
        """Les salaries ayant des activites sont ceux ayant une pratique declaree (hors 'Non declare')."""
        sportifs = {row[0] for row in pratiques if row[1] != "Non déclaré"}
        ids_activites = {row[1] for row in activites_raw}
        ids_non_sportifs = ids_activites - sportifs
        assert len(ids_non_sportifs) == 0, (
            f"{len(ids_non_sportifs)} salaries non sportifs avec activites : {ids_non_sportifs}"
        )


class TestSimulationSports:
    """Les types de sport doivent appartenir a la liste fermee."""

    def test_types_sport_valides(self, activites_raw):
        """Chaque type_sport est dans SPORTS_VALIDES."""
        sports_invalides = set()
        for row in activites_raw:
            if row[3] not in SPORTS_VALIDES:
                sports_invalides.add(row[3])
        assert len(sports_invalides) == 0, (
            f"Sports invalides trouves : {sports_invalides}"
        )

    def test_nombre_activites_par_salarie(self, activites_raw):
        """Chaque salarie a entre 5 et 40 activites (bornes de la simulation)."""
        from collections import Counter
        compteur = Counter(row[1] for row in activites_raw)
        hors_bornes = {s: n for s, n in compteur.items() if n < 5 or n > 40}
        assert len(hors_bornes) == 0, (
            f"Salaries hors bornes 5-40 activites : {hors_bornes}"
        )


class TestSimulationVolume:
    """Tests de volume global."""

    def test_nombre_total_activites(self, activites_raw):
        """La simulation avec seed 42 produit exactement 2256 activites."""
        assert len(activites_raw) == 2256, (
            f"Attendu 2256 activites, obtenu {len(activites_raw)}"
        )

    def test_nombre_sportifs(self, activites_raw):
        """95 salaries distincts ont des activites."""
        nb_sportifs = len(set(row[1] for row in activites_raw))
        assert nb_sportifs == 95, (
            f"Attendu 95 sportifs, obtenu {nb_sportifs}"
        )
