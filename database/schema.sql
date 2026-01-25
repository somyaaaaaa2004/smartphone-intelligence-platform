USE smartphone_intelligence;

CREATE TABLE IF NOT EXISTS countries (
    country_code VARCHAR(10) PRIMARY KEY,
    country_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS macro_indicators (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    country_code VARCHAR(10),
    year INT,
    indicator VARCHAR(50),
    value DOUBLE,
    source VARCHAR(100),
    UNIQUE(country_code, year, indicator)
);

CREATE TABLE IF NOT EXISTS company_financials (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    company VARCHAR(50),
    year INT,
    revenue_usd DOUBLE,
    net_income_usd DOUBLE,
    UNIQUE(company, year)
);

CREATE TABLE IF NOT EXISTS forecasts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    entity_type VARCHAR(50),
    entity_name VARCHAR(50),
    year INT,
    forecast_value DOUBLE,
    model_used VARCHAR(50)
);
