-- Test that avg_sales_ratio is between 0 and 5
{% test sales_ratio_range(model, column_name) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} < 0 OR {{ column_name }} > 5

{% endtest %}