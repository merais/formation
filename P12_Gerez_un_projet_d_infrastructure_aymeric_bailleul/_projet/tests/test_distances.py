"""
test_distances.py – Tests de qualite sur les distances domicile-bureau

Verifie :
  - Aucune distance negative
  - Coherence distance / moyen de deplacement (seuils 15 km / 25 km)
  - Fonction haversine avec des coordonnees connues
  - Gestion d'une adresse invalide (pas de crash)
"""

import pytest

from src.transformation.distances import (
    MODES_ELIGIBLES,
    SEUILS_DISTANCE,
    haversine,
    distance_google_maps,
)


# ---------------------------------------------------------------------------
# Tests unitaires sur la fonction haversine
# ---------------------------------------------------------------------------


class TestHaversine:
    """Tests sur le calcul de distance a vol d'oiseau."""

    def test_haversine_meme_point(self):
        """Distance entre un point et lui-meme = 0."""
        assert haversine(43.5676, 3.9070, 43.5676, 3.9070) == 0.0

    def test_haversine_paris_marseille(self):
        """Distance Paris-Marseille ~ 660 km (vol d'oiseau)."""
        dist = haversine(48.8566, 2.3522, 43.2965, 5.3698)
        assert 650 < dist < 680, f"Paris-Marseille attendu ~660 km, obtenu {dist}"

    def test_haversine_courte_distance(self):
        """Distance Montpellier-Lattes ~ 5 km."""
        dist = haversine(43.6108, 3.8767, 43.5676, 3.9070)
        assert 3 < dist < 8, f"Montpellier-Lattes attendu ~5 km, obtenu {dist}"

    def test_haversine_toujours_positive(self):
        """Le resultat est toujours >= 0."""
        dist = haversine(0, 0, -10, -20)
        assert dist >= 0


# ---------------------------------------------------------------------------
# Tests sur les distances en base (gold.eligibilite_prime)
# ---------------------------------------------------------------------------


class TestDistancesEnBase:
    """Tests de coherence sur les distances calculees et stockees en gold."""

    def test_aucune_distance_negative(self, eligibilite_prime):
        """Aucune distance dans gold.eligibilite_prime ne doit etre negative."""
        for row in eligibilite_prime:
            distance_km = row[4]
            if distance_km is not None:
                assert distance_km >= 0, f"Distance negative pour salarie {row[0]} : {distance_km}"

    def test_tous_les_salaries_presents(self, eligibilite_prime, employes):
        """Chaque employe a une ligne dans gold.eligibilite_prime."""
        ids_prime = {row[0] for row in eligibilite_prime}
        ids_employes = {row[0] for row in employes}
        assert ids_prime == ids_employes, (
            f"IDs manquants dans eligibilite_prime : {ids_employes - ids_prime}"
        )

    def test_seuils_coherents(self, eligibilite_prime):
        """
        Le seuil applique correspond au moyen de deplacement :
          - Marche/running : 15 km
          - Velo/Trottinette/Autres : 25 km
          - Autres modes : 0 km (non eligible)
        """
        for row in eligibilite_prime:
            moyen = row[2]
            seuil = row[5]
            seuil_attendu = SEUILS_DISTANCE.get(moyen, 0.0)
            assert seuil == seuil_attendu, (
                f"Salarie {row[0]} : seuil {seuil} != attendu {seuil_attendu} pour '{moyen}'"
            )

    def test_eligibilite_coherente_avec_distance(self, eligibilite_prime):
        """
        Un salarie est eligible ssi :
          - son moyen de deplacement est dans MODES_ELIGIBLES
          - ET sa distance est <= au seuil
        """
        for row in eligibilite_prime:
            id_sal, _, moyen, _, distance_km, seuil_km, est_eligible, _ = row
            if moyen not in MODES_ELIGIBLES:
                assert not est_eligible, (
                    f"Salarie {id_sal} avec moyen '{moyen}' ne devrait pas etre eligible"
                )
            elif distance_km is not None and distance_km <= seuil_km:
                assert est_eligible, (
                    f"Salarie {id_sal} avec distance {distance_km} <= seuil {seuil_km} devrait etre eligible"
                )
            elif distance_km is not None and distance_km > seuil_km:
                assert not est_eligible, (
                    f"Salarie {id_sal} avec distance {distance_km} > seuil {seuil_km} ne devrait pas etre eligible"
                )

    def test_modes_non_eligibles_pas_de_prime(self, eligibilite_prime):
        """
        Les salaries avec un moyen de deplacement hors liste
        (vehicule thermique, transports en commun) ne recoivent pas de prime.
        """
        for row in eligibilite_prime:
            moyen = row[2]
            montant_prime = float(row[7])
            if moyen not in MODES_ELIGIBLES:
                assert montant_prime == 0.0, (
                    f"Salarie {row[0]} (moyen '{moyen}') a une prime de {montant_prime} EUR"
                )


# ---------------------------------------------------------------------------
# Tests sur la gestion des adresses invalides
# ---------------------------------------------------------------------------


class TestAdresseInvalide:
    """Test de robustesse avec une adresse inexistante."""

    def test_adresse_invalide_retourne_none(self):
        """
        L'appel API avec une adresse absurde retourne None (pas de crash).
        """
        result = distance_google_maps("adresse_totalement_inventee_zzz_999")
        # Peut retourner None ou une distance (si Google interprete)
        # L'important : pas d'exception levee
        assert result is None or isinstance(result, float)
