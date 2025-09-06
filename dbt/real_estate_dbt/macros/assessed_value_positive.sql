-- Test that assessed_value > 0
{% test assessed_value_positive(model, column_name) %}
SELECT *
FROM {{ model }}
WHERE {{ column_name }} <= 0
{% endtest %}