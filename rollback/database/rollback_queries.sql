-- Create backup table if not exists
CREATE TABLE IF NOT EXISTS customers_backup AS TABLE customers WITH NO DATA;

-- Backup current data before rollback
INSERT INTO customers_backup
SELECT * FROM customers WHERE load_date = CURRENT_DATE;

-- Rollback procedure
CREATE OR REPLACE PROCEDURE rollback_data(target_date DATE)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Delete newly loaded data
    DELETE FROM customers WHERE load_date = target_date;
    DELETE FROM customer_metrics WHERE metric_date = target_date;
    
    -- Restore from backup if available
    INSERT INTO customers
    SELECT * FROM customers_backup 
    WHERE load_date = target_date - INTERVAL '1 day';
    
    COMMIT;
END;
$$;