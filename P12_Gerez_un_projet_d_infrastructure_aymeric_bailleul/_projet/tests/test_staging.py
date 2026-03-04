"""
test_staging.py – Tests de qualite sur les donnees staging

Verifie staging.employes et staging.activites_strava :
  - Pas de doublon sur ID salarie
  - Salaires strictement positifs
  - Dates d'embauche anterieures a aujourd'hui
  - Coherence staging vs raw pour les activites Strava
"""

from datetime import date

import pytest


# ---------------------------------------------------------------------------
# Tests sur staging.employes
# ---------------------------------------------------------------------------


class TestEmployesDoublons:
    """Pas de doublon sur ID salarie."""

    def test_pas_de_doublon_id(self, employes):
        """Chaque id_salarie est unique dans staging.employes."""
        ids = [row[0] for row in employes]
        assert len(ids) == len(set(ids)), (
            f"Doublons detectes : {len(ids)} lignes, {len(set(ids))} uniques"
        )


class TestEmployesSalaires:
    """Les salaires doivent etre strictement positifs."""

    def test_salaires_positifs(self, employes):
        """Aucun salaire <= 0."""
        invalides = [(row[0], float(row[3])) for row in employes if float(row[3]) <= 0]
        assert len(invalides) == 0, (
            f"{len(invalides)} salaries avec salaire <= 0 : {invalides[:5]}"
        )

    def test_salaires_raisonnables(self, employes):
        """Les salaires sont dans une plage realiste (15 000 - 200 000 EUR brut annuel)."""
        hors_plage = [
            (row[0], float(row[3]))
            for row in employes
            if float(row[3]) < 15000 or float(row[3]) > 200000
        ]
        assert len(hors_plage) == 0, (
            f"{len(hors_plage)} salaires hors plage 15k-200k : {hors_plage[:5]}"
        )


class TestEmployesDatesEmbauche:
    """Les dates d'embauche doivent etre anterieures a aujourd'hui."""

    def test_dates_embauche_passees(self, employes):
        """Aucune date d'embauche dans le futur."""
        aujourd_hui = date.today()
        futures = [
            (row[0], row[2])
            for row in employes
            if row[2] > aujourd_hui
        ]
        assert len(futures) == 0, (
            f"{len(futures)} dates d'embauche dans le futur : {futures[:5]}"
        )


class TestEmployesCompletude:
    """Tests de completude des donnees employes."""

    def test_161_employes(self, employes):
        """staging.employes contient exactement 161 lignes."""
        assert len(employes) == 161, f"Attendu 161, obtenu {len(employes)}"

    def test_5_departements(self, employes):
        """Il y a exactement 5 departements."""
        departements = set(row[1] for row in employes)
        assert len(departements) == 5, (
            f"Attendu 5 departements, obtenu {len(departements)} : {departements}"
        )

    def test_adresses_non_vides(self, employes):
        """Aucune adresse domicile vide."""
        vides = [row[0] for row in employes if not row[6] or row[6].strip() == ""]
        assert len(vides) == 0, f"{len(vides)} adresses vides"

    def test_moyens_deplacement_valides(self, employes):
        """Les 4 moyens de deplacement attendus sont presents."""
        moyens_attendus = {
            "véhicule thermique/électrique",
            "Vélo/Trottinette/Autres",
            "Transports en commun",
            "Marche/running",
        }
        moyens_trouves = set(row[7] for row in employes)
        assert moyens_trouves == moyens_attendus, (
            f"Moyens attendus {moyens_attendus}, trouves {moyens_trouves}"
        )


# ---------------------------------------------------------------------------
# Tests sur staging.activites_strava
# ---------------------------------------------------------------------------


class TestStagingActivites:
    """Coherence des activites apres nettoyage staging."""

    def test_meme_volume_que_raw(self, activites_staging, activites_raw):
        """
        Avec des donnees bien simulees, aucune activite ne doit etre rejetee.
        staging et raw ont le meme nombre de lignes.
        """
        assert len(activites_staging) == len(activites_raw), (
            f"staging ({len(activites_staging)}) != raw ({len(activites_raw)})"
        )

    def test_distances_positives_staging(self, activites_staging):
        """Toutes les distances sont > 0 dans staging."""
        invalides = [row[0] for row in activites_staging if row[4] <= 0]
        assert len(invalides) == 0

    def test_durees_positives_staging(self, activites_staging):
        """Toutes les durees sont > 0 dans staging."""
        invalides = [row[0] for row in activites_staging if row[5] <= 0]
        assert len(invalides) == 0


# ---------------------------------------------------------------------------
# Tests sur staging.pratiques_declarees
# ---------------------------------------------------------------------------


class TestPratiquesDeclarees:
    """Coherence des pratiques sportives declarees."""

    def test_161_pratiques(self, pratiques):
        """staging.pratiques_declarees contient 161 lignes."""
        assert len(pratiques) == 161, f"Attendu 161, obtenu {len(pratiques)}"

    def test_pas_de_nan_brut(self, pratiques):
        """Aucune valeur NaN ou None dans pratique_sport (remplacee par 'Non declare')."""
        nans = [row[0] for row in pratiques if row[1] is None]
        assert len(nans) == 0, f"{len(nans)} valeurs None"

    def test_coherence_ids_employes(self, pratiques, employes):
        """Les IDs de pratiques_declarees correspondent aux IDs employes."""
        ids_pratiques = {row[0] for row in pratiques}
        ids_employes = {row[0] for row in employes}
        assert ids_pratiques == ids_employes
