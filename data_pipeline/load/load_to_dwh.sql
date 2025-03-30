-- Create target tables if not exists
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY,
    full_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    status VARCHAR(50),
    tier_name VARCHAR(50),
    customer_segment VARCHAR(50),
    original_value DECIMAL(10,2),
    discounted_value DECIMAL(10,2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customer_metrics (
    metric_date DATE,
    segment VARCHAR(50),
    tier VARCHAR(50),
    customer_count INT,
    total_value DECIMAL(15,2),
    avg_discount DECIMAL(5,2),
    PRIMARY KEY (metric_date, segment, tier)
);

-- Load customer data
INSERT INTO customers (
    customer_id, full_name, email, phone, status,
    tier_name, customer_segment, original_value,
    discounted_value, created_at, updated_at
)
SELECT 
    id, full_name, email, phone, status,
    tier_name, customer_segment, value,
    discounted_value, created_at, updated_at
FROM temp_customers
ON CONFLICT (customer_id) DO UPDATE SET
    full_name = EXCLUDED.full_name,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    status = EXCLUDED.status,
    tier_name = EXCLUDED.tier_name,
    customer_segment = EXCLUDED.customer_segment,
    original_value = EXCLUDED.original_value,
    discounted_value = EXCLUDED.discounted_value,
    updated_at = EXCLUDED.updated_at,
    load_date = CURRENT_TIMESTAMP;

-- Update metrics
INSERT INTO customer_metrics
SELECT
    CURRENT_DATE AS metric_date,
    customer_segment,
    tier_name,
    COUNT(*) AS customer_count,
    SUM(discounted_value) AS total_value,
    AVG(1 - (discounted_value / NULLIF(original_value, 0))) * 100 AS avg_discount
FROM customers
WHERE updated_at >= CURRENT_DATE - INTERVAL '1 day'
GROUP BY customer_segment, tier_name
ON CONFLICT (metric_date, segment, tier) DO UPDATE SET
    customer_count = EXCLUDED.customer_count,
    total_value = EXCLUDED.total_value,
    avg_discount = EXCLUDED.avg_discount;