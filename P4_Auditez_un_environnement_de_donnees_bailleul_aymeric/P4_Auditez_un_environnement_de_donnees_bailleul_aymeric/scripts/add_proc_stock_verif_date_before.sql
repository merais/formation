CREATE OR REPLACE FUNCTION insert_vente_detail(
    p_id_bdd VARCHAR,
    p_customer_id_old VARCHAR, -- Ancien CUSTOMER_ID (VARCHAR)
    p_id_employe_old VARCHAR,  -- Ancien id_employe (VARCHAR)
    p_ean_old BIGINT,          -- Ancien EAN (BIGINT)
    p_date_achat_text TEXT,
    p_id_ticket VARCHAR
)
RETURNS VOID AS $$
DECLARE
    v_date_achat_formatee DATE;
    v_id_client_new INT;      -- Variable pour le nouvel ID client (INT)
    v_id_employe_new INT;     -- Variable pour le nouvel ID employé (INT)
    v_id_produit_new INT;     -- Variable pour le nouvel ID produit (INT)
BEGIN
    -- ÉTAPE 1 : FORMATAGE ET VÉRIFICATION DE LA DATE (inchangée)
    BEGIN
        v_date_achat_formatee := p_date_achat_text::DATE;
    EXCEPTION
        WHEN invalid_datetime_format THEN
            RAISE EXCEPTION 'Format de date invalide fourni (%). Veuillez utiliser un format reconnu par PostgreSQL (AAAA-MM-JJ).', p_date_achat_text;
    END;

    -- ÉTAPE 2 : RÉCUPÉRATION DES NOUVELLES CLÉS NUMÉRIQUES (INT)
    
    -- Récupération du nouvel id_client (INT) à partir du CUSTOMER_ID original (VARCHAR)
    SELECT id_client INTO v_id_client_new
    FROM clients
    WHERE num_customer = p_customer_id_old; -- 'num_customer' est l'ancien 'CUSTOMER_ID' renommé
    
    -- Récupération du nouvel id_employe (INT) à partir du num_employe original (VARCHAR)
    SELECT id_employe INTO v_id_employe_new
    FROM employers
    WHERE num_employe = p_id_employe_old;
    
    -- Récupération du nouvel id_produit (INT) à partir de l'EAN original (BIGINT)
    SELECT id_produit INTO v_id_produit_new
    FROM produits
    WHERE EAN = p_ean_old;

    -- Vérification des clés de référence (si non trouvé, cela lève une exception implicite)
    IF v_id_client_new IS NULL THEN
        RAISE EXCEPTION 'ID Client (%) introuvable dans la table "clients".', p_customer_id_old;
    END IF;
    IF v_id_employe_new IS NULL THEN
        RAISE EXCEPTION 'ID Employé (%) introuvable dans la table "employers".', p_id_employe_old;
    END IF;
    IF v_id_produit_new IS NULL THEN
        RAISE EXCEPTION 'EAN Produit (%) introuvable dans la table "produits".', p_ean_old;
    END IF;

    -- ÉTAPE 3 : VÉRIFICATION DANS LA TABLE CALENDRIER (inchangée, mais utilise la nouvelle colonne 'is_closed')
    IF NOT EXISTS (SELECT 1 FROM calendrier WHERE date = v_date_achat_formatee) THEN
        RAISE EXCEPTION 'Date de transaction (%) introuvable dans la table de référence "calendrier".', v_date_achat_formatee;
    END IF;

    -- Vérification si la date est un jour fermé (day_off = TRUE)
    IF EXISTS (SELECT 1 FROM calendrier WHERE date = v_date_achat_formatee AND day_off = TRUE) THEN
        RAISE EXCEPTION 'Insertion annulée : La date de transaction (%) n''est pas un jour ouvré.', v_date_achat_formatee;
    END IF;

    -- Vérification si la date est clôturée (is_closed = TRUE)
    IF EXISTS (SELECT 1 FROM calendrier WHERE date = v_date_achat_formatee AND is_closed = TRUE) THEN
        RAISE EXCEPTION 'Insertion annulée : La date de transaction (%) est déjà clôturée.', v_date_achat_formatee;
    END IF;

    -- ÉTAPE 4 : INSERTION DES DONNÉES avec les NOUVELLES CLÉS NUMÉRIQUES (INT)
    INSERT INTO vente_detail (
        ID_BDD, id_client, id_employe, id_produit, "Date achat", "ID ticket"
    )
    VALUES (
        p_id_bdd, v_id_client_new, v_id_employe_new, v_id_produit_new, v_date_achat_formatee, p_id_ticket
    );

END;
$$ LANGUAGE plpgsql;


-- Permet de revoquer les droits d'écriture directe sur vente_detail et d'obligé la saisi dans la table tampon
-- N'ayant pas connaissance des différent rôles, app_role est utilisé à titre d'exemple
-- REVOKE INSERT ON vente_detail FROM app_role;
-- GRANT EXECUTE ON FUNCTION insert_vente_detail(VARCHAR, VARCHAR, VARCHAR, BIGINT, TEXT, VARCHAR) TO app_role;