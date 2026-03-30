-- eligibilite_bien_etre.sql
-- Calcule l eligibilite aux 5 journees bien-etre.
--
-- Regles metier :
--   - Compter les activites Strava de chaque salarie actif sur toute la periode
--   - Seuil : >= 15 activites --> eligible a 5 jours bien-etre
--   - Salaries sans aucune activite Strava : 0 activite, non eligible
--
-- Seuls les employes actifs (actif = TRUE) sont pris en compte.
-- Source des activites : staging.activites_strava (produite par stg_activites_strava via ref())

{{
  config(
    materialized = 'table',
    alias        = 'eligibilite_bien_etre'
  )
}}

with employes as (
    select id_salarie, departement
    from {{ source('staging', 'employes') }}
    where actif = true
),

activites as (
    select id_salarie
    from {{ ref('stg_activites_strava') }}
)

select
    e.id_salarie,
    e.departement,
    count(a.id_salarie)                  as nb_activites_annee,
    count(a.id_salarie) >= 15            as est_eligible,
    case
        when count(a.id_salarie) >= 15 then 5
        else 0
    end                                  as nb_jours_bien_etre
from employes e
left join activites a on e.id_salarie = a.id_salarie
group by e.id_salarie, e.departement
order by e.id_salarie
