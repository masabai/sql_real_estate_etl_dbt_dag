def validate_sql(sql):
    """
    Security check to prevent destructive operations and SQL injection.
    Only allows read-only (SELECT/WITH) operations.
    """
    blocked = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]

    sql_strip = sql.strip()  # remove leading/trailing spaces
    sql_lower = sql_strip.lower()

    # Ensure query starts with safe keywords
    if not (sql_lower.startswith("select") or sql_lower.startswith("with")):
        return False, "SQL validation failed: Only SELECT or WITH (CTEs) queries allowed"

    # Check for destructive keywords
    for word in blocked:
        if word in sql_strip.upper():
            return False, f"Unsafe SQL detected: {word}"

    # Block semicolons to prevent multiple statement injection
    if ";" in sql_strip:
        return False, "Multiple SQL statements not allowed"

    return True, None