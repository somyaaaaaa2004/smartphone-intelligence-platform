-- ============================================================================
-- Snowflake Permissions Grant Script
-- ============================================================================
-- This script grants all necessary permissions for the smartphone intelligence
-- pipeline to operate on SMARTPHONE_INTELLIGENCE_DB.PUBLIC schema.
--
-- Prerequisites:
--   1. Run this script as ACCOUNTADMIN or SECURITYADMIN role
--   2. Replace <ROLE_NAME> with your actual role name (e.g., PUBLIC, or a custom role)
--      To find your role: SELECT CURRENT_ROLE();
--   3. Alternatively, replace <ROLE_NAME> with your username to grant directly to user
--
-- Usage:
--   Run this script in Snowflake Web UI or via SnowSQL
-- ============================================================================

-- Set variables (adjust these as needed)
SET ROLE_NAME = 'PUBLIC';  -- Change to your role name, e.g., 'PUBLIC', 'SMARTPHONE_ROLE', or your username
SET DATABASE_NAME = 'SMARTPHONE_INTELLIGENCE_DB';
SET SCHEMA_NAME = 'PUBLIC';

-- ============================================================================
-- Step 1: Grant USAGE on Database
-- ============================================================================
GRANT USAGE ON DATABASE IDENTIFIER($DATABASE_NAME) TO ROLE IDENTIFIER($ROLE_NAME);

-- ============================================================================
-- Step 2: Grant USAGE on Schema
-- ============================================================================
GRANT USAGE ON SCHEMA IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME) TO ROLE IDENTIFIER($ROLE_NAME);

-- ============================================================================
-- Step 3: Grant privileges on existing tables
-- ============================================================================

-- Grant on COUNTRIES table
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLE IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME).COUNTRIES TO ROLE IDENTIFIER($ROLE_NAME);

-- Grant on MACRO_INDICATORS table
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLE IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME).MACRO_INDICATORS TO ROLE IDENTIFIER($ROLE_NAME);

-- ============================================================================
-- Step 4: Grant privileges on future tables in the schema
-- ============================================================================
-- This ensures any new tables created in the schema will automatically have these privileges
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON FUTURE TABLES IN SCHEMA IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME) TO ROLE IDENTIFIER($ROLE_NAME);

-- ============================================================================
-- Step 5: Grant CREATE TABLE privilege (if tables need to be created)
-- ============================================================================
GRANT CREATE TABLE ON SCHEMA IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME) TO ROLE IDENTIFIER($ROLE_NAME);

-- ============================================================================
-- Verification Queries (run these to verify grants)
-- ============================================================================
-- Show grants on database
-- SHOW GRANTS ON DATABASE IDENTIFIER($DATABASE_NAME);

-- Show grants on schema
-- SHOW GRANTS ON SCHEMA IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME);

-- Show grants on tables
-- SHOW GRANTS ON TABLE IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME).COUNTRIES;
-- SHOW GRANTS ON TABLE IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME).MACRO_INDICATORS;

-- Show grants to your role
-- SHOW GRANTS TO ROLE IDENTIFIER($ROLE_NAME);

-- ============================================================================
-- Alternative: Grant directly to USER (if you prefer user-level grants)
-- ============================================================================
-- Uncomment and replace <USERNAME> with your Snowflake username (e.g., SMARTPHONE_USER)
-- GRANT USAGE ON DATABASE IDENTIFIER($DATABASE_NAME) TO USER '<USERNAME>';
-- GRANT USAGE ON SCHEMA IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME) TO USER '<USERNAME>';
-- GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLE IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME).COUNTRIES TO USER '<USERNAME>';
-- GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLE IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME).MACRO_INDICATORS TO USER '<USERNAME>';
-- GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON FUTURE TABLES IN SCHEMA IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME) TO USER '<USERNAME>';
-- GRANT CREATE TABLE ON SCHEMA IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME) TO USER '<USERNAME>';
