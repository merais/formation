-- generate_schema_name.sql
-- Surcharge le comportement par defaut de dbt qui genere des noms de schema
-- sous la forme {target_schema}_{custom_schema} (ex: public_staging).
-- Avec ce macro, le schema personnalise est utilise tel quel :
--   +schema: staging  -->  schema "staging"
--   +schema: gold     -->  schema "gold"

{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
