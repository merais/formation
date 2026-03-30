-- stg_activites_strava.sql
-- Nettoyage des activites Strava : raw.activites_strava --> staging.activites_strava
--
-- Controles de qualite appliques (memes regles que staging.py dans _projet) :
--   - distance_m > 0
--   - duree_s > 0
--   - date_debut dans les 395 derniers jours (13 mois, marge de securite)
--   - type_sport dans la liste des 15 sports valides
--   - id_salarie present dans staging.employes (FK implicite)
--
-- Materalisation : table dans le schema staging (alias = activites_strava)
-- pour conserver la compatibilite avec le reste du pipeline.

{{
  config(
    materialized = 'table',
    alias        = 'activites_strava'
  )
}}

with sports_valides as (
    -- Liste des 15 types de sport valides (coherent avec generate_strava.py)
    select unnest(array[
        'Running', 'Randonnée', 'Tennis', 'Natation', 'Football', 'Rugby',
        'Badminton', 'Voile', 'Boxe', 'Judo', 'Escalade', 'Triathlon',
        'Tennis de table', 'Équitation', 'Basketball'
    ]) as type_sport
),

ids_salaries_valides as (
    -- Seuls les salaries connus dans staging.employes sont acceptes
    select id_salarie
    from {{ source('staging', 'employes') }}
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
-- Filtre : id_salarie doit exister dans staging.employes
inner join ids_salaries_valides
    on raw_activites.id_salarie = ids_salaries_valides.id_salarie
-- Filtre : type de sport valide
inner join sports_valides
    on raw_activites.type_sport = sports_valides.type_sport
-- Filtres de coherence numerique et temporelle
where
    raw_activites.distance_m > 0
    and raw_activites.duree_s > 0
    and raw_activites.date_debut >= now() - interval '395 days'
