-- ========================================
-- Step 3: Create Clean View
-- ========================================
-- Create a staging view from the raw real_estate table
-- Preserves all original columns for downstream processing

CREATE OR REPLACE VIEW staging.real_estate_clean AS
SELECT
    -- Preserve all original columns
    *
FROM staging.real_estate;
