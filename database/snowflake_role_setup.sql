-- ============================================================================
-- Snowflake Role Setup and Assignment Script
-- ============================================================================
-- This script creates a role, assigns it to a user, and verifies activation.
--
-- Prerequisites:
--   Run as ACCOUNTADMIN or SECURITYADMIN
--
-- Usage:
--   1. Replace <USERNAME> with your Snowflake username (e.g., SMARTPHONE_USER)
--   2. Optionally change ROLE_NAME if you want a different role name
--   3. Run this script in Snowflake Web UI or via SnowSQL
-- ============================================================================

-- Set variables (adjust these as needed)
SET USERNAME = 'SMARTPHONE_USER';  -- Replace with your actual username
SET ROLE_NAME = 'SMARTPHONE_ROLE';  -- Role name to create/assign
SET DATABASE_NAME = 'SMARTPHONE_INTELLIGENCE_DB';
SET SCHEMA_NAME = 'PUBLIC';

-- ============================================================================
-- Step 1: Check current user and role (for verification)
-- ============================================================================
SELECT CURRENT_USER() AS current_user, CURRENT_ROLE() AS current_role;

-- ============================================================================
-- Step 2: Create the role (if it doesn't exist)
-- ============================================================================
CREATE ROLE IF NOT EXISTS IDENTIFIER($ROLE_NAME)
    COMMENT = 'Role for smartphone intelligence platform operations';

-- ============================================================================
-- Step 3: Grant the role to the user
-- ============================================================================
GRANT ROLE IDENTIFIER($ROLE_NAME) TO USER IDENTIFIER($USERNAME);

-- ============================================================================
-- Step 4: Grant USAGE on Warehouse (required for queries)
-- ============================================================================
-- Replace 'SMARTPHONE_WH' with your actual warehouse name
GRANT USAGE ON WAREHOUSE SMARTPHONE_WH TO ROLE IDENTIFIER($ROLE_NAME);

-- ============================================================================
-- Step 5: Grant all necessary database permissions to the role
-- ============================================================================
-- Grant USAGE on Database
GRANT USAGE ON DATABASE IDENTIFIER($DATABASE_NAME) TO ROLE IDENTIFIER($ROLE_NAME);

-- Grant USAGE on Schema
GRANT USAGE ON SCHEMA IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME) TO ROLE IDENTIFIER($ROLE_NAME);

-- Grant privileges on existing tables
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLE IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME).COUNTRIES TO ROLE IDENTIFIER($ROLE_NAME);
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLE IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME).MACRO_INDICATORS TO ROLE IDENTIFIER($ROLE_NAME);

-- Grant privileges on future tables
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON FUTURE TABLES IN SCHEMA IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME) TO ROLE IDENTIFIER($ROLE_NAME);

-- Grant CREATE TABLE privilege
GRANT CREATE TABLE ON SCHEMA IDENTIFIER($DATABASE_NAME).IDENTIFIER($SCHEMA_NAME) TO ROLE IDENTIFIER($ROLE_NAME);

-- ============================================================================
-- Step 6: Set the role as default for the user (optional but recommended)
-- ============================================================================
ALTER USER IDENTIFIER($USERNAME) SET DEFAULT_ROLE = IDENTIFIER($ROLE_NAME);

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Check current user and role
SELECT CURRENT_USER() AS current_user, CURRENT_ROLE() AS current_role;

-- Show roles granted to user
SHOW GRANTS TO USER IDENTIFIER($USERNAME);

-- Show all roles available to current user
SHOW GRANTS;

-- Show grants on the role
SHOW GRANTS TO ROLE IDENTIFIER($ROLE_NAME);

-- ============================================================================
-- Instructions for User: How to Activate the Role
-- ============================================================================
-- After running the above script, the user needs to activate the role.
-- 
-- Option 1: Set it as default (already done above with ALTER USER)
--   The role will be automatically activated on next login
--
-- Option 2: Manually activate in current session
--   Run this command as the user:
--   USE ROLE SMARTPHONE_ROLE;
--
-- Option 3: Activate via connection parameter
--   In your Python connection, add: role='SMARTPHONE_ROLE'
--
-- Verify activation:
--   SELECT CURRENT_ROLE();  -- Should return 'SMARTPHONE_ROLE'
