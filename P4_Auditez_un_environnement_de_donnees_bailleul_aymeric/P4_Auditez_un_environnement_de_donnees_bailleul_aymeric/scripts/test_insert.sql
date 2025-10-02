-- Le 15 est une jour de fermeture
UPDATE calendrier
SET day_off = TRUE
WHERE date = '2024-08-15';

-- le 14 est cloturé puisqu'il est passé
UPDATE calendrier
SET is_closed = TRUE
WHERE date = '2024-08-14';

-- Vérification de la table calendrier
select *
from calendrier
where date between '2024-08-14' and '2024-08-16'

-- T'entative d'insertion pour le 14 en passant par la procédure stockée
SELECT insert_vente_detail(
    '4EJKRN55ASEA7O7Y97MNMXKZ5UROK7SJDKL'::VARCHAR,    -- 1. p_id_bdd
    'CUST-2KYXXXW1NK7I'::VARCHAR,      -- 2. p_customer_id_old
    '6fa61d0ecae0b563fef18d36b2039c8e'::VARCHAR,               -- 3. p_id_employe_old
    5026767366043::BIGINT,           -- 4. p_ean_old
    '2024-08-14'::TEXT,              -- 5. p_date_achat_text
    'TICKET_2025_001'::VARCHAR       -- 6. p_id_ticket
);

-- T'entative d'insertion pour le 15 en passant par la procédure stockée
SELECT insert_vente_detail(
    '4EJKRN55ASEA7O7Y97MNMXKZ5UROK7SJDKL'::VARCHAR,    -- 1. p_id_bdd
    'CUST-2KYXXXW1NK7I'::VARCHAR,      -- 2. p_customer_id_old
    '6fa61d0ecae0b563fef18d36b2039c8e'::VARCHAR,               -- 3. p_id_employe_old
    5026767366043::BIGINT,           -- 4. p_ean_old
    '2024-08-15'::TEXT,              -- 5. p_date_achat_text
    'TICKET_2025_001'::VARCHAR       -- 6. p_id_ticket
);


-- T'entative d'insertion pour le 16 en passant par la procédure stockée avec une date erronée
SELECT insert_vente_detail(
    '4EJKRN55ASEA7O7Y97MNMXKZ5UROK7SJDKL'::VARCHAR,    -- 1. p_id_bdd
    'CUST-2KYXXXW1NK7I'::VARCHAR,      -- 2. p_customer_id_old
    '6fa61d0ecae0b563fef18d36b2039c8e'::VARCHAR,               -- 3. p_id_employe_old
    5026767366043::BIGINT,           -- 4. p_ean_old
    '16 aout 2024'::TEXT,              -- 5. p_date_achat_text
    'TICKET_2025_001'::VARCHAR       -- 6. p_id_ticket
);


-- T'entative d'insertion pour le 16 en passant par la procédure stockée
SELECT insert_vente_detail(
    '4EJKRN55ASEA7O7Y97MNMXKZ5UROK7SJDKL'::VARCHAR,    -- 1. p_id_bdd
    'CUST-2KYXXXW1NK7I'::VARCHAR,      -- 2. p_customer_id_old
    '6fa61d0ecae0b563fef18d36b2039c8e'::VARCHAR,               -- 3. p_id_employe_old
    5026767366043::BIGINT,           -- 4. p_ean_old
    '2024-08-16'::TEXT,              -- 5. p_date_achat_text
    'TICKET_2025_001'::VARCHAR       -- 6. p_id_ticket
);

-- Vérification que la ligne est bien créé
SELECT * FROM vente_detail WHERE id_bdd = '4EJKRN55ASEA7O7Y97MNMXKZ5UROK7SJDKL';

-- Supression de la ligne de test.
DELETE FROM vente_detail WHERE ID_BDD = '4EJKRN55ASEA7O7Y97MNMXKZ5UROK7SJDKL';