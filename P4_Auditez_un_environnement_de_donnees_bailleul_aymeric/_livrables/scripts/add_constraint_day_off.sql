-- Function qui renvoie true si day_off est a false (en gros renvoie vrai pour les jour ouvrés et false pour les jour férié) 
CREATE OR REPLACE FUNCTION est_jour_ouvrable(date_achat DATE)
RETURNS BOOLEAN AS $$
DECLARE
    is_day_off BOOLEAN;
BEGIN
    SELECT day_off INTO is_day_off
    FROM calendrier
    WHERE date = date_achat;
    -- Si la date n'existe pas dans le calendrier, on considére qu'elle est valide.
    -- S'il y a une ligne, on vérifie si day_off est false.
    RETURN NOT is_day_off;
END;
$$ LANGUAGE plpgsql;


-- Ajout d'une contrainte sur vente_detail pour empécher la saisi si a la date choisi day_off est a true
ALTER TABLE vente_detail
ADD CONSTRAINT check_jour_ouvrable
CHECK (est_jour_ouvrable("Date achat"));