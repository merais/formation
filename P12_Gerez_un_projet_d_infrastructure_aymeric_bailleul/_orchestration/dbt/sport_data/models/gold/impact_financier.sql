-- impact_financier.sql
-- Agrege l impact financier par departement.
--
-- Logique :
--   - Primes : nb et total EUR par departement (eligibles uniquement)
--   - Bien-etre : nb salaries eligibles et total jours par departement
--   - FULL OUTER JOIN pour garantir qu un departement apparait meme
--     s il n a que des primes ou que du bien-etre
--
-- Dependances : ref(eligibilite_prime) + ref(eligibilite_bien_etre)

{{
  config(
    materialized = 'table',
    alias        = 'impact_financier'
  )
}}

with primes as (
    select
        departement,
        count(*) filter (where est_eligible)                         as nb_primes,
        coalesce(sum(montant_prime) filter (where est_eligible), 0)  as total_primes
    from {{ ref('eligibilite_prime') }}
    group by departement
),

bien_etre as (
    select
        departement,
        count(*) filter (where est_eligible)                              as nb_bien_etre,
        coalesce(sum(nb_jours_bien_etre) filter (where est_eligible), 0)  as total_jours
    from {{ ref('eligibilite_bien_etre') }}
    group by departement
)

select
    coalesce(p.departement, b.departement)  as departement,
    coalesce(p.nb_primes,   0)              as nb_primes,
    coalesce(p.total_primes, 0)             as total_primes,
    coalesce(b.nb_bien_etre, 0)             as nb_bien_etre,
    coalesce(b.total_jours, 0)              as total_jours_bien_etre
from primes p
full outer join bien_etre b
    on p.departement = b.departement
order by departement
