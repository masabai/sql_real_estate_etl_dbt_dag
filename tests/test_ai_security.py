import pytest

# The core deterministic security guardrail function to test
def validate_sql(sql):
    blocked = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]
    sql_strip = sql.strip()
    sql_lower = sql_strip.lower()
    
    if not (sql_lower.startswith("select") or sql_lower.startswith("with")):
        return False, "SQL validation failed: Only SELECT or WITH (CTEs) queries allowed"
        
    for word in blocked:
        if word in sql_strip.upper():
            return False, f"Unsafe SQL detected: {word}"
            
    if ";" in sql_strip:
        return False, "Multiple SQL statements not allowed"
        
    return True, None

# --- AUTOMATED TEST SCENARIOS ---

def test_guardrail_allows_safe_queries():
    """Verify clean, standard AI-generated SQL passes the firewall."""
    safe_sql = "SELECT town, SUM(sale_amount) FROM fact_sales GROUP BY town"
    is_valid, message = validate_sql(safe_sql)
    assert is_valid is True
    assert message is None

def test_guardrail_blocks_destructive_hallucinations():
    """Verify that if an LLM hallucinates a DROP table statement, it is immediately caught."""
    bad_sql = "DROP TABLE fact_sales"
    is_valid, message = validate_sql(bad_sql)
    assert is_valid is False
    assert "Unsafe SQL detected: DROP" in message

def test_guardrail_blocks_non_select_start():
    """Verify queries trying to bypass constraints by not starting with SELECT/WITH fail."""
    sneaky_sql = "GRANT ALL PRIVILEGES TO unauthorized_user"
    is_valid, message = validate_sql(sneaky_sql)
    assert is_valid is False
    assert "Only SELECT or WITH" in message

def test_guardrail_blocks_semicolon_injection():
    """Verify that multi-statement malicious injections are completely blocked."""
    injection_sql = "SELECT * FROM dim_location; DELETE FROM fact_sales"
    is_valid, message = validate_sql(injection_sql)
    assert is_valid is False
    assert "Multiple SQL statements not allowed" in message
