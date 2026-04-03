from config import client

def repair_sql(question, bad_sql, error, schema_context):
    """
    Attempts to fix a failing SQL query based on database error messages.
    Applies specific business rules for table joins and column data types.
    """
    prompt = f"""
You are a PostgreSQL expert fixing broken SQL.

DATABASE SCHEMA:
{schema_context}

DATABASE SCHEMA:
{schema_context}
- clean.fact_sales: (list_year int, date_recorded date, town text, property_type_id text, residential_type_id text, sale_amount double precision, assessed_value int, avg_sales_ratio double precision)
- clean.compare_current_previous: (list_year int, date_recorded date, town text, address text, property_type text, price_change double precision, next_sale_price double precision)
- clean.sales_flag_summary: (ratio_flag text, flag_count bigint, pct text)

CRITICAL NOTES ABOUT THIS DATABASE:
- dim_town table has ONLY one column: town (text) - do NOT join, use fact_sales.town directly
- residential_type_id is a TEXT column in fact_sales with values: 'Single Family', 'Condo', 'Unknown', 'Two Family', 'Three Family', 'Four Family'
- property_type_id is a TEXT column in fact_sales - do NOT join dim_property_type
- Use fact_sales.residential_type_id directly for filtering on residential type (it contains TEXT values, not numeric IDs)
- Use fact_sales.property_type_id directly (it contains TEXT values, not numeric IDs)
- Only use foreign keys if they reference tables with meaningful data
- NO tables exist for: compare_current_previous, price_change, or similar derived tables

CRITICAL DATA RULES:
- DATE FILTERING: Always use 'date_recorded'. Example: EXTRACT(YEAR FROM fs.date_recorded) = 2021.
- CASE SENSITIVITY: 11M rows are messy. Always use UPPER() or ILIKE for text.
   Example: UPPER(fs.town) = UPPER('Greenwich') or fs.town ILIKE 'Greenwich'.
- CALCULATED COLUMNS:
   - "Sales Ratio": Use fs.avg_sales_ratio.
   - "Price Change/Growth": Use clean.compare_current_previous.price_change.
- AGGREGATES:
   - Use ROUND((SUM(fs.sale_amount))::numeric, 2) for all currency.
   - Use ROUND((AVG(fs.avg_sales_ratio))::numeric, 4) for ratios.
- RESIDENTIAL FILTER: Use fs.residential_type_id. Values: 'Single Family', 'Condo', 'Two Family', etc.
- JOINING: Only join clean.compare_current_previous if the user specifically asks about "price change", "next sale", or "previous sale".


RULES FOR SQL GENERATION:
- PostgreSQL syntax only
- Only SELECT or WITH queries (CTEs for complex logic)
- ORDER BY columns must appear in SELECT
- Use table aliases (fs=fact_sales)
- Use direct columns when they exist (town, residential_type_id, property_type_id)
- For "how much sales" or "total sales" questions, use SUM(fs.sale_amount)
- Include GROUP BY when using aggregations (SUM, AVG, COUNT, MAX, MIN)
- For total/sum across entire dataset, do NOT use GROUP BY (just aggregate)
- Wrap SUM and AVG in parentheses, cast to numeric, and round to 2 decimals: ROUND((SUM(column))::numeric, 2).
- Round to 2 decimal points using: ROUND((aggregate_expression)::numeric, 2)
  Example: ROUND((SUM(fs.sale_amount))::numeric, 2) or ROUND((AVG(fs.sale_amount))::numeric, 2)
  Wrap entire aggregate in parentheses before casting to numeric
- DO NOT include semicolons at the end of SQL
- Return ONLY SQL, no explanations
- DO NOT round or cast COUNT(*) results; return counts as absolute integers without decimals.
- Highest/most questions should ordered by DESC and use Limit 1 for single result
- For "Year-over-Year" (YoY) growth, use the CTE pattern provided below.

FOR "GROWING FASTEST" OR "YEAR-OVER-YEAR" QUESTIONS:
- Define two CTEs (current_yr, prev_yr).
- Join on town or property_type.
- Growth Pct = ROUND(((current.val - prev.val) / NULLIF(prev.val, 0) * 100)::numeric, 2).
- Use CTEs to calculate current year and previous year metrics separately
- Calculate growth as: (current - previous) / previous * 100
- Use EXTRACT(YEAR FROM sale_date) to filter by year
- Example structure:
  WITH current_year AS (
    SELECT town, SUM(sale_amount) as sales FROM fact_sales 
    WHERE EXTRACT(YEAR FROM sale_date) = EXTRACT(YEAR FROM CURRENT_DATE) 
    GROUP BY town
  ),
  previous_year AS (
    SELECT town, SUM(sale_amount) as sales FROM fact_sales 
    WHERE EXTRACT(YEAR FROM sale_date) = EXTRACT(YEAR FROM CURRENT_DATE) - 1 
    GROUP BY town
  )
  SELECT cy.town, ROUND(((cy.sales - py.sales) / py.sales * 100)::numeric, 2) as growth_pct
  FROM current_year cy 
  LEFT JOIN previous_year py ON cy.town = py.town 
  ORDER BY growth_pct DESC

USER QUESTION: {question}

Generate the SQL (return only the SQL, nothing else):
"""

    chat = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        temperature=0
    )

    # Clean the repaired SQL output
    fixed_sql = chat.choices[0].message.content \
        .replace("```sql", "") \
        .replace("```", "") \
        .strip()

    fixed_sql = fixed_sql.rstrip(";").strip()

    return fixed_sql

