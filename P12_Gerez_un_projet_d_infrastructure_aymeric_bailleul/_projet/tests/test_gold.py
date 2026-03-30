"""
test_gold.py – Tests de qualite sur les tables gold

Verifie :
  - Montant prime = salaire_brut * 0.05 si eligible, sinon 0
  - Aucun salarie non eligible ne recoit de prime
  - Nombre de jours bien-etre = 5 si >= 15 activites, sinon 0
  - Coherence de l'agregation impact_financier
"""

import pytest


# ---------------------------------------------------------------------------
# Tests sur gold.eligibilite_prime
# ---------------------------------------------------------------------------


class TestPrimeMontant:
    """Le montant de la prime est correctement calcule."""

    def test_prime_egal_5_pourcent_salaire(self, eligibilite_prime, salaires_par_id):
        """
        Pour chaque salarie eligible, montant_prime = salaire_brut * 0.05.
        Pour chaque non eligible, montant_prime = 0.
        """
        erreurs = []
        for row in eligibilite_prime:
            id_sal, _, _, _, _, _, est_eligible, montant_prime = row
            salaire = salaires_par_id.get(id_sal)
            if salaire is None:
                continue

            montant_prime = float(montant_prime)
            if est_eligible:
                attendu = round(salaire * 0.05, 2)
                if abs(montant_prime - attendu) > 0.01:
                    erreurs.append(
                        f"ID {id_sal} : prime {montant_prime} != attendu {attendu} (salaire {salaire})"
                    )
            else:
                if montant_prime != 0.0:
                    erreurs.append(
                        f"ID {id_sal} non eligible mais prime = {montant_prime}"
                    )

        assert len(erreurs) == 0, f"{len(erreurs)} erreurs de prime :\n" + "\n".join(erreurs[:10])


class TestPrimeNonEligible:
    """Aucun salarie non eligible ne recoit de prime."""

    def test_pas_de_prime_pour_non_eligibles(self, eligibilite_prime):
        """Les non eligibles ont montant_prime = 0."""
        violations = [
            (row[0], float(row[7]))
            for row in eligibilite_prime
            if not row[6] and float(row[7]) != 0.0
        ]
        assert len(violations) == 0, (
            f"{len(violations)} non eligibles avec prime > 0 : {violations[:5]}"
        )


# ---------------------------------------------------------------------------
# Tests sur gold.eligibilite_bien_etre
# ---------------------------------------------------------------------------


class TestBienEtreJours:
    """Le nombre de jours bien-etre suit la regle >= 15 activites -> 5 jours."""

    def test_5_jours_si_eligible(self, eligibilite_bien_etre):
        """
        Si eligible (>= 15 activites), nb_jours_bien_etre = 5.
        Sinon, nb_jours_bien_etre = 0.
        """
        erreurs = []
        for row in eligibilite_bien_etre:
            id_sal, _, nb_activites, est_eligible, nb_jours = row

            if est_eligible:
                if nb_jours != 5:
                    erreurs.append(f"ID {id_sal} eligible mais {nb_jours} jours (attendu 5)")
                if nb_activites < 15:
                    erreurs.append(f"ID {id_sal} eligible mais {nb_activites} activites (< 15)")
            else:
                if nb_jours != 0:
                    erreurs.append(f"ID {id_sal} non eligible mais {nb_jours} jours (attendu 0)")
                if nb_activites >= 15:
                    erreurs.append(f"ID {id_sal} non eligible mais {nb_activites} activites (>= 15)")

        assert len(erreurs) == 0, f"{len(erreurs)} erreurs bien-etre :\n" + "\n".join(erreurs[:10])

    def test_tous_les_salaries_presents(self, eligibilite_bien_etre, employes):
        """Chaque employe a une ligne dans gold.eligibilite_bien_etre."""
        ids_be = {row[0] for row in eligibilite_bien_etre}
        ids_emp = {row[0] for row in employes}
        assert ids_be == ids_emp


# ---------------------------------------------------------------------------
# Tests sur gold.impact_financier
# ---------------------------------------------------------------------------


class TestImpactFinancier:
    """Coherence de l'agregation par departement."""

    def test_5_departements(self, impact_financier):
        """gold.impact_financier contient exactement 5 departements."""
        assert len(impact_financier) == 5

    def test_total_primes_coherent(self, impact_financier, eligibilite_prime):
        """La somme des primes par departement = somme des montants eligibles."""
        # Total depuis impact_financier
        total_impact = sum(float(row[2]) for row in impact_financier)
        # Total depuis eligibilite_prime
        total_prime = sum(float(row[7]) for row in eligibilite_prime if row[6])
        assert abs(total_impact - total_prime) < 0.01, (
            f"impact_financier ({total_impact:.2f}) != eligibilite_prime ({total_prime:.2f})"
        )

    def test_total_bien_etre_coherent(self, impact_financier, eligibilite_bien_etre):
        """La somme des jours bien-etre par departement = somme des jours eligibles."""
        total_impact = sum(row[4] for row in impact_financier)
        total_be = sum(row[4] for row in eligibilite_bien_etre if row[3])
        assert total_impact == total_be, (
            f"impact_financier ({total_impact}) != eligibilite_bien_etre ({total_be})"
        )

    def test_nb_primes_coherent(self, impact_financier, eligibilite_prime):
        """Le nombre de primes par departement correspond aux eligibles."""
        from collections import Counter
        # Comptage depuis eligibilite_prime
        compteur = Counter(row[1] for row in eligibilite_prime if row[6])
        for row in impact_financier:
            dept, nb_primes = row[0], row[1]
            attendu = compteur.get(dept, 0)
            assert nb_primes == attendu, (
                f"Departement '{dept}' : {nb_primes} primes != attendu {attendu}"
            )

    def test_nb_bien_etre_coherent(self, impact_financier, eligibilite_bien_etre):
        """Le nombre de bien-etre par departement correspond aux eligibles."""
        from collections import Counter
        compteur = Counter(row[1] for row in eligibilite_bien_etre if row[3])
        for row in impact_financier:
            dept, nb_be = row[0], row[3]
            attendu = compteur.get(dept, 0)
            assert nb_be == attendu, (
                f"Departement '{dept}' : {nb_be} bien-etre != attendu {attendu}"
            )
