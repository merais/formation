-- stg_activites_strava.sql
-- Nettoyage des activites Strava : raw.activites_strava --> staging.activites_strava
--
-- Controles de qualite appliques :
--   - distance_m > 0
--   - duree_s > 0
--   - date_debut dans les 395 derniers jours (13 mois, marge de securite)
--   - type_sport dans la liste des 15 sports valides
--   - id_salarie present dans staging.employes ET actif = TRUE
--
-- Materalisation : table dans le schema staging (alias = activites_strava)

{{
  config(
    materialized = 'table',
    alias        = 'activites_strava'
  )
}}

with sports_valides as (
    select unnest(array[
        'Running', 'Randonnée', 'Tennis', 'Natation', 'Football', 'Rugby',
        'Badminton', 'Voile', 'Boxe', 'Judo', 'Escalade', 'Triathlon',
        'Tennis de table', 'Équitation', 'Basketball'
    ]) as type_sport
),

ids_salaries_valides as (
    -- Seuls les salaries actifs connus dans staging.employes sont acceptes
    -- (actif = FALSE : employe retire du fichier RH source)
    select id_salarie
    from {{ source('staging', 'employes') }}
    where actif = true
),

raw_activites as (
    select
        id_salarie,
        date_debut,
        type_sport,
        distance_m,
        duree_s,
        commentaire
    from {{ source('raw', 'activites_strava') }}
)

select
    raw_activites.id_salarie,
    raw_activites.date_debut,
    raw_activites.type_sport,
    raw_activites.distance_m,
    raw_activites.duree_s,
    raw_activites.commentaire
from raw_activites
inner join ids_salaries_valides
    on raw_activites.id_salarie = ids_salaries_valides.id_salarie
inner join sports_valides
    on raw_activites.type_sport = sports_valides.type_sport
where
    raw_activites.distance_m > 0
    and raw_activites.duree_s > 0
    and raw_activites.date_debut >= now() - interval '395 days'
