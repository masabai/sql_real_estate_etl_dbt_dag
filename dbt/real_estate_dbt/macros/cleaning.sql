
-- Macros for common cleaning operations in real estate project
{% macro clean_string(column_name) %}
    -- trim white spaces and change to title case
    INITCAP(TRIM({{ column_name }}))
{% endmacro %}

{% macro clean_text(col_name, default="Unknown")  %}
    -- trim white spaces and fill missing values with "Unknown"
    COALESCE(NULLIF(TRIM({{col_name}}), ''), '{{ default}}')
{% endmacro %}

{% macro round_numeric(col_name, precision=2) %}
    -- Round numeric values to given precision
    ROUND({{ col_name }}::numeric, {{ precision }})
{% endmacro %}

{% macro clean_date(col_name) %}
    -- Convert blank strings to NULL and cast to DATE
    NULLIF({{ col_name }}, '')::DATE
{% endmacro %}
