{% macro generate_schema_name(custom_schema_name, node) -%}
    {#
      Use exactly what you set in +schema: (like "staging" or "clean"),
      otherwise fall back to target.schema
    #}
    {{ custom_schema_name if custom_schema_name is not none else target.schema }}
{%- endmacro %}
