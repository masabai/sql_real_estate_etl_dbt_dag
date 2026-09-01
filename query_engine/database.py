import psycopg2
import time
from query_engine.config import DB_CONFIG

def connect_db():
    """Establishes connection to Postgres and sets the dbt schema search path."""
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        dbname=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        options=f"-c search_path={DB_CONFIG['schema']}" # set to "clean" schema
    )

def build_schema_context(cur):
    """
    Extracts table metadata, data types, and keys from information_schema.
    Formats this into a text prompt to help the AI understand the database.
    """
    cur.execute("""
    SELECT 
        t.table_name,
        c.column_name,
        c.data_type,
        CASE 
            WHEN tc.constraint_type = 'PRIMARY KEY' THEN '[PK]'
            WHEN tc.constraint_type = 'FOREIGN KEY' THEN '[FK]'
            ELSE ''
        END AS key_type
    FROM information_schema.tables t
    LEFT JOIN information_schema.columns c ON t.table_name = c.table_name AND t.table_schema = c.table_schema
    LEFT JOIN information_schema.key_column_usage kcu ON c.table_name = kcu.table_name AND c.column_name = kcu.column_name AND kcu.table_schema = t.table_schema
    LEFT JOIN information_schema.table_constraints tc ON kcu.constraint_name = tc.constraint_name AND tc.table_schema = t.table_schema
    WHERE t.table_schema='clean'
    ORDER BY t.table_name, c.ordinal_position
    """)

    schema_rows = cur.fetchall()
    schema_lines = []
    current_table = None #loop to compare the table_name of the current row to current_table

    for table_name, col_name, data_type, key_type in schema_rows:
        if col_name is None: continue

        if table_name != current_table:
            schema_lines.append(f"\nTABLE: {table_name}")
            current_table = table_name

        key_marker = f" {key_type}" if key_type else ""
        schema_lines.append(f"  - {col_name} ({data_type}){key_marker}")

    return "\n".join(schema_lines)

def execute_sql(conn, sql):
    """Executes SQL and returns results, column names, and timing. Rollback on failure."""
    cur = conn.cursor()
    try:
        start = time.time()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [c[0] for c in cur.description]#only column name, not the rest:type_code, display_size, etc
        runtime = time.time() - start
        cur.close()
        return rows, columns, runtime, None
    except Exception as e:
        conn.rollback()
        cur.close()
        return None, None, None, str(e)

def log_query(conn, question, sql, runtime):
    """Stores every user question and generated SQL for performance monitoring."""
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO ai_query_logs (question, generated_sql, execution_time) VALUES (%s,%s,%s)",
            (question, sql, runtime)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Logging error: {e}")
    finally:
        cur.close()

def create_log_table(conn):
    """Creates the log table if it doesn't exist."""
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ai_query_logs (
        id SERIAL PRIMARY KEY,
        question TEXT,
        generated_sql TEXT,
        execution_time FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    cur.close()
