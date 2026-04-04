from rag.config import client

def generate_sql(question, schema_context):
    """
       Translates a natural language question into a PostgreSQL query.
       Uses schema metadata to ensure correct table and column references.
    """

    prompt = f"""
    You are a PostgreSQL expert. Generate a single, deterministic SQL query.

DATABASE SCHEMA:
{schema_context}

CRITICAL NOTES ABOUT THIS DATABASE:
- dim_town table has ONLY one column: town (text) - do NOT join, use fact_sales.town directly
- residential_type_id is a TEXT column in fact_sales with values: 'Single Family', 'Condo', 'Unknown', 'Two Family', 'Three Family', 'Four Family'
- property_type_id is a TEXT column in fact_sales - do NOT join dim_property_type
- property_type_id is a TEXT column in fact_sales with values: 'Residential','Commercial','Industrial', 'Public Utility', 'Unknown', 'Vacant Land', 'Apartments', 'Four Family'
- Use fact_sales.residential_type_id directly for filtering on residential type (it contains TEXT values, not numeric IDs)
- Use fact_sales.property_type_id directly (it contains TEXT values, not numeric IDs)
- Only use foreign keys if they reference tables with meaningful data

CRITICAL DATA RULES:
- All currency-related columns (sale_amount, sale_price, assessed_value, etc.):
    - Must be returned as **numeric** (do not cast to text). Eg. sale_amount = 14685000.00
- DATE FILTERING: Always use 'date_recorded'. Example: EXTRACT(YEAR FROM fs.date_recorded) = 2021.
- CASE SENSITIVITY: Always use UPPER() or ILIKE for text.
   Example: UPPER(fs.town) = UPPER('Greenwich') or fs.town ILIKE 'Greenwich'.
- CALCULATED COLUMNS:
   - "Sales Ratio": Use fs.avg_sales_ratio.
- AGGREGATES:
   - Use ROUND((SUM(fs.sale_amount))::numeric, 2) for all currency.
   - Use ROUND((AVG(fs.avg_sales_ratio))::numeric, 4) for ratios.
- RESIDENTIAL FILTER: Use fs.residential_type_id. Values: 'Single Family', 'Condo', 'Two Family', etc.

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
- FORMATTING: Always wrap sale_amount and assessed_value in ROUND(..., 2), even when not using an aggregate.
- Example: ROUND(fs.assessed_value::numeric, 2)
- DO NOT include semicolons at the end of SQL
- Return ONLY SQL, no explanations
- DO NOT round or cast COUNT(*) results; return counts as absolute integers without decimals.
- Highest/most questions should ordered by DESC and use Limit 1 for single result
- For "Year-over-Year" (YoY) growth, use the CTE pattern provided below.

FOR "GROWING FASTEST" OR "YEAR-OVER-YEAR" QUESTIONS:
- Filter out any town that has a NULL growth percentage
- Use INNER JOIN for YoY growth so towns with missing data in either year are hidden 
- Only show towns with a growth_pct that is NOT NULL
- Define two CTEs (current_yr, prev_yr).
- Join on town or property_type.
- Growth Pct = ROUND(((current.val - prev.val) / NULLIF(prev.val, 0) * 100)::numeric, 2)
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
    # Generate completion using Llama-3.1-8b
    chat = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai/gpt-oss-120b",
        temperature=0
    )

    # Clean the response: remove markdown blocks and trailing semicolons
    sql = chat.choices[0].message.content \
        .replace("```sql", "") \
        .replace("```", "") \
        .strip()

    sql = sql.rstrip(";").strip()

    return sql
