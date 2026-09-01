import streamlit as st
import pandas as pd
from query_engine.validate import validate_sql
from query_engine.generate import generate_sql
from query_engine.repair import repair_sql
from query_engine.database import connect_db, execute_sql, build_schema_context, log_query

# Initialize Database connection and Schema Context
conn = connect_db()
schema_context = build_schema_context(conn.cursor())

# Remove extra space above page title
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="CT Property Insights")
st.title(":blue[CT Real Estate Intelligence]")
st.markdown("Query Connecticut real estate history using natural language OR SQL.")

# --- USER INPUT ---
#question = st.text_input("Ask a question about Connecticut real estate:")
# Height=200 makes the box big enough for 10+ lines of SQL
question = st.text_area(
    "Ask a question or enter SQL:",
    height=200,
    placeholder="e.g., SELECT * FROM fact_sales LIMIT 5..."
)

if st.button("Ask AI", type="secondary"):
    if question:
        # STEP 1: Generate the initial SQL query
        sql = generate_sql(question, schema_context)

        # STEP 2: Pre-execution Validation (Security & Syntax check)
        ok, error = validate_sql(sql) # ok, error -> False, syntax error

        if not ok:
            st.error(f"SQL validation failed: {error}")
        else:
            # STEP 3: Initial Execution Attempt
            rows, columns, runtime, sql_error = execute_sql(conn, sql)

            # Auto-repair
            if sql_error:
                st.warning("First attempt failed. AI is attempting to repair the SQL...")

                # Use the repair module to fix the SQL based on the DB error message
                sql = repair_sql(question, sql, sql_error, schema_context)

                # Final Attempt with repaired SQL
                rows, columns, runtime, sql_error = execute_sql(conn, sql)

            # Display Results
            if sql_error:
                st.error(f"Execution failed after repair attempt: {sql_error}")
            elif not rows:
                st.info("No results found. The query was valid, but no data matched your filters.")
                st.subheader("SQL Attempted")
                st.code(sql)
            else:
                st.subheader("Results")
                df = pd.DataFrame(rows, columns=columns)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Metadata and technical transparency
                st.caption(f"SQL executed in {runtime:.3f}s")
                with st.expander("View Generated SQL"):
                    st.code(sql, language="sql")

        # STEP 4: Log the interaction for audit/analytics
        log_query(conn, question, sql, runtime)


# SIDEBAR: Schema Map & Sample Questions
with st.sidebar:
    st.header(":blue[CT Property Intelligence]")

    # 1. Schema at the top for quick reference (No scrolling needed)
    with st.expander(":orange[View Database Schema]"):
        st.caption("Available tables and columns in 'clean' schema:")
        st.code(build_schema_context(conn.cursor()), language="text")

    # 3. Sample Questions for Non-Tech Users
    st.header(":blue[Sample Questions]")

    st.markdown("""
    1. *Top 5 towns by average sale price in 2020?*
    2. *How many residential properties sold in each town in 2021?*
    3. *Which town was most expensive in 2021?*
    4. *List the top 10 highest-priced sales.*
    5. *What is the average sales ratio in Stamford?*
    6. *Show properties sold over $5M in Greenwich.*
    7. *Which town had the most 'Single Family' sales in 2022?*
    8. *Total sale amount for all of CT in 2021?*
    9. *Find the 5 cheapest sales in Bridgeport (min $50k).*
    10. *Compare average prices in Hartford vs West Hartford for 2020.*
    """)
