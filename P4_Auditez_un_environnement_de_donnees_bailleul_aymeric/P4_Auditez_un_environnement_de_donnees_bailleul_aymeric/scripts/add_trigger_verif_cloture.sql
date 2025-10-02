-- Fonction interroge directement la table calendrier en utilisant la date de la transaction que l'on tente de modifier.
CREATE OR REPLACE FUNCTION verifier_cloture_calendrier()
RETURNS TRIGGER AS $$
DECLARE
    est_jour_cloture BOOLEAN;
    date_a_verifier DATE;
BEGIN
    -- 1. Déterminer la date à vérifier (OLD pour UPDATE/DELETE)
    IF TG_OP IN ('UPDATE', 'DELETE') THEN
        date_a_verifier := OLD."Date achat";
    ELSE -- Déterminer la date à vérifier (NEW pour INSERT) >> Plus de sécurité
        date_a_verifier := NEW."Date achat";
    END IF;

    -- 2. Récupérer le statut de clôture pour cette date
    SELECT is_closed INTO est_jour_cloture
    FROM calendrier
    WHERE date = date_a_verifier;

    -- 3. Vérification de la condition de verrouillage
    -- La modification est bloquée si le jour est marqué comme clôturé (est_cloture = TRUE)
    IF est_jour_cloture = TRUE THEN
        RAISE EXCEPTION 'Opération annulée : La transaction du % a été clôturée (est_cloture = TRUE). La modification des données historiques est interdite.',
            date_a_verifier
        USING HINT = 'Veuillez modifier uniquement les transactions pour les dates où est_cloture est FALSE.';
    END IF;

    -- Retourner la ligne pour l'opération
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;

END;
$$ LANGUAGE plpgsql;


-- Suppression de l'ancien trigger (en cas de réécriture du trigger ou réinsertion)
DROP TRIGGER IF EXISTS trigger_verrouillage_historique ON vente_detail;

-- Création du nouveau TRIGGER sur la table 'vente_detail'
CREATE TRIGGER trigger_verrouillage_calendrier
BEFORE UPDATE OR DELETE ON vente_detail
FOR EACH ROW
EXECUTE FUNCTION verifier_cloture_calendrier();