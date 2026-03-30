-- eligibilite_prime.sql
-- Calcule l eligibilite a la prime sportive (5% du salaire brut).
--
-- Regles metier (identiques a distances.py + gold.py dans _projet) :
--   Modes eligibles :
--     - Marche/running     : distance domicile-bureau <= 15 km
--     - Velo/Trottinette/Autres : distance <= 25 km
--   Modes non eligibles : vehicule thermique/electrique, transports en commun
--   Montant prime : 5% du salaire_brut si eligible, 0 sinon
--
-- Source de la distance_km : staging.cache_distances
--   (cree et alimente par distances.py dans _projet via Google Maps ou haversine)
--
-- Materalisation : table dans le schema gold (alias = eligibilite_prime)

{{
  config(
    materialized = 'table',
    alias        = 'eligibilite_prime'
  )
}}

with employes as (
    select
        id_salarie,
        departement,
        moyen_deplacement,
        adresse_domicile,
        salaire_brut
    from {{ source('staging', 'employes') }}
),

distances as (
    select
        adresse_domicile,
        distance_km
    from {{ source('staging', 'cache_distances') }}
),

-- Seuils de distance par mode de deplacement eligible
seuils as (
    select 'Marche/running'           as moyen_deplacement, 15.0 as seuil_km
    union all
    select 'Vélo/Trottinette/Autres'  as moyen_deplacement, 25.0 as seuil_km
)

select
    e.id_salarie,
    e.departement,
    e.moyen_deplacement,
    e.adresse_domicile,
    d.distance_km,
    s.seuil_km,
    -- Est eligible si : mode eligible ET distance connue ET distance <= seuil
    case
        when s.seuil_km is null         then false   -- mode non eligible
        when d.distance_km is null      then false   -- distance non calculee
        when d.distance_km <= s.seuil_km then true
        else false
    end as est_eligible,
    -- Montant de la prime : 5% du salaire brut si eligible, 0 sinon
    case
        when s.seuil_km is null          then 0
        when d.distance_km is null       then 0
        when d.distance_km <= s.seuil_km then round(e.salaire_brut * 0.05, 2)
        else 0
    end as montant_prime

from employes e
left join distances d
    on e.adresse_domicile = d.adresse_domicile
left join seuils s
    on e.moyen_deplacement = s.moyen_deplacement

order by e.id_salarie
