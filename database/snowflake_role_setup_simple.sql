-- ============================================================================
-- Snowflake Role Setup (Simple Version)
-- ============================================================================
-- Replace <USERNAME> with your Snowflake username (e.g., SMARTPHONE_USER)
-- Run as ACCOUNTADMIN or SECURITYADMIN
-- ============================================================================

-- Check current user and role
SELECT CURRENT_USER() AS current_user, CURRENT_ROLE() AS current_role;

-- Step 1: Create the role (if it doesn't exist)
CREATE ROLE IF NOT EXISTS SMARTPHONE_ROLE;

-- Step 2: Grant the role to your user
GRANT ROLE SMARTPHONE_ROLE TO USER <USERNAME>;

-- Step 3: Grant USAGE on Warehouse (replace with your warehouse name)
GRANT USAGE ON WAREHOUSE SMARTPHONE_WH TO ROLE SMARTPHONE_ROLE;

-- Step 4: Grant database permissions
GRANT USAGE ON DATABASE SMARTPHONE_INTELLIGENCE_DB TO ROLE SMARTPHONE_ROLE;
GRANT USAGE ON SCHEMA SMARTPHONE_INTELLIGENCE_DB.PUBLIC TO ROLE SMARTPHONE_ROLE;

-- Step 5: Grant table permissions
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLE SMARTPHONE_INTELLIGENCE_DB.PUBLIC.COUNTRIES TO ROLE SMARTPHONE_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLE SMARTPHONE_INTELLIGENCE_DB.PUBLIC.MACRO_INDICATORS TO ROLE SMARTPHONE_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON FUTURE TABLES IN SCHEMA SMARTPHONE_INTELLIGENCE_DB.PUBLIC TO ROLE SMARTPHONE_ROLE;
GRANT CREATE TABLE ON SCHEMA SMARTPHONE_INTELLIGENCE_DB.PUBLIC TO ROLE SMARTPHONE_ROLE;

-- Step 6: Set role as default for user (optional but recommended)
ALTER USER <USERNAME> SET DEFAULT_ROLE = SMARTPHONE_ROLE;

-- ============================================================================
-- Verification
-- ============================================================================
-- Check current user and role
SELECT CURRENT_USER() AS current_user, CURRENT_ROLE() AS current_role;

-- Show roles granted to user
SHOW GRANTS TO USER <USERNAME>;

-- Show grants on the role
SHOW GRANTS TO ROLE SMARTPHONE_ROLE;

-- ============================================================================
-- User Activation Commands (run as the user, not as admin)
-- ============================================================================
-- Activate the role in current session:
-- USE ROLE SMARTPHONE_ROLE;
--
-- Verify activation:
-- SELECT CURRENT_ROLE();  -- Should return 'SMARTPHONE_ROLE'
