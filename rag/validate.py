
def validate_sql(sql):
    """
    Security check to prevent destructive operations and SQL injection.
    Only allows read-only (SELECT/WITH) operations.
    """
    blocked = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]

    # Ensure query starts with safe keywords
    if not sql.lower().startswith("select") and not sql.lower().startswith("with"):
        return False, "Only SELECT or WITH (CTEs) queries allowed"

    # Check for destructive keywords
    for word in blocked:
        if word in sql.upper():
            return False, f"Unsafe SQL detected: {word}"

    # Block semicolons to prevent multiple statement injection
    if ";" in sql:
        return False, "Multiple SQL statements not allowed"

    return True, None
