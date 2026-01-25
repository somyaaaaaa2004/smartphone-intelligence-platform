-- ============================================================================
-- Snowflake Permissions Grant Script (Simple Version)
-- ============================================================================
-- Replace <ROLE_NAME> with your role (e.g., 'PUBLIC', 'SMARTPHONE_ROLE')
-- To find your current role: SELECT CURRENT_ROLE();
-- 
-- Run as ACCOUNTADMIN or SECURITYADMIN
-- ============================================================================

-- Grant USAGE on Database
GRANT USAGE ON DATABASE SMARTPHONE_INTELLIGENCE_DB TO ROLE <ROLE_NAME>;

-- Grant USAGE on Schema
GRANT USAGE ON SCHEMA SMARTPHONE_INTELLIGENCE_DB.PUBLIC TO ROLE <ROLE_NAME>;

-- Grant privileges on COUNTRIES table
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLE SMARTPHONE_INTELLIGENCE_DB.PUBLIC.COUNTRIES TO ROLE <ROLE_NAME>;

-- Grant privileges on MACRO_INDICATORS table
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLE SMARTPHONE_INTELLIGENCE_DB.PUBLIC.MACRO_INDICATORS TO ROLE <ROLE_NAME>;

-- Grant privileges on future tables (for any new tables created)
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON FUTURE TABLES IN SCHEMA SMARTPHONE_INTELLIGENCE_DB.PUBLIC TO ROLE <ROLE_NAME>;

-- Grant CREATE TABLE privilege (if tables need to be created)
GRANT CREATE TABLE ON SCHEMA SMARTPHONE_INTELLIGENCE_DB.PUBLIC TO ROLE <ROLE_NAME>;

-- ============================================================================
-- Verification (run these to check grants)
-- ============================================================================
-- SHOW GRANTS TO ROLE <ROLE_NAME>;
-- SHOW GRANTS ON DATABASE SMARTPHONE_INTELLIGENCE_DB;
-- SHOW GRANTS ON SCHEMA SMARTPHONE_INTELLIGENCE_DB.PUBLIC;
