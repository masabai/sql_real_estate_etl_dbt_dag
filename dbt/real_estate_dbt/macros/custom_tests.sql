-- macros/custom_tests.sql
{% macro test_dim_property_type_valid(model, column_name) %}
select {{ column_name }}
from {{ model }}
where {{ column_name }} not in (
    'Unknown',
    'Residential',
    'Public Utility',
    'Vacant Land',
    'Industrial',
    'Apartments',
    'Commercial'
)
{% endmacro %}
