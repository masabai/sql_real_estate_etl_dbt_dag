-- ======================================================
-- Step 6: Analytical Queries / EDA with Derived Features
-- ======================================================
-- Distribution of sales over time
SELECT list_year,
       COUNT(*) AS sales_count,
       AVG(sale_amount) AS avg_sale,
       AVG(sale_amount - assessed_value) AS avg_price_difference,
       AVG(sale_amount / NULLIF(assessed_value,0)) AS avg_sales_ratio
FROM staging.real_estate_clean
GROUP BY list_year
ORDER BY list_year;

-- Top 10 towns by sales volume
SELECT town,
       COUNT(*) AS sales_count,
       AVG(sale_amount) AS avg_sale,
       AVG(sale_amount - assessed_value) AS avg_price_difference,
       AVG(sale_amount / NULLIF(assessed_value,0)) AS avg_sales_ratio
FROM staging.real_estate_clean
GROUP BY town
ORDER BY sales_count DESC
LIMIT 10;

-- Property type breakdown
SELECT property_type,
       COUNT(*) AS count,
       AVG(sale_amount) AS avg_sale,
       AVG(sale_amount - assessed_value) AS avg_price_difference,
       AVG(sale_amount / NULLIF(assessed_value,0)) AS avg_sales_ratio
FROM staging.real_estate_clean
GROUP BY property_type
ORDER BY count DESC;

-- Extract year/month from date_recorded
SELECT EXTRACT(YEAR FROM date_recorded) AS sale_year,
       EXTRACT(MONTH FROM date_recorded) AS sale_month,
       COUNT(*) AS sales_count,
       ROUND(AVG(sale_amount::NUMERIC),2) AS avg_sale
FROM staging.real_estate_clean
GROUP BY sale_year, sale_month
ORDER BY sale_year, sale_month;