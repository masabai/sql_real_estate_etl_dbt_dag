import csv
import os
import sys
from rag.generate import generate_sql
from rag.validate import validate_sql
from rag.repair import repair_sql
from rag.database import execute_sql, connect_db, build_schema_context
from sample_questions import get_questions

# Adds the 'RealEstate' directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


# Initialize DB connection and schema
conn = connect_db()
cursor = conn.cursor()
schema = build_schema_context(cursor)

questions = get_questions()
failed = []

for q in questions:
    try:
        # Generate SQL
        sql = generate_sql(q, schema)

        # Validate and possibly repair
        valid, err = validate_sql(sql)
        if not valid:
            sql = repair_sql(sql, err)

        # Execute SQL
        rows, cols, runtime, error = execute_sql(conn, sql)

        # Mark as failed only if rows is None or empty
        if rows is None or len(rows) == 0:
            failed.append((q, "empty_result"))

    except Exception as e:
        failed.append((q, str(e)))

# Write failures only
with open("failed_queries.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["question", "error"])
    writer.writerows(failed)

print("Done. Failed:", len(failed))