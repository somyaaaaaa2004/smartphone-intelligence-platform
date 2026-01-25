# Snowflake Role Setup Instructions

## Quick Setup (Run as ACCOUNTADMIN or SECURITYADMIN)

### Step 1: Check Current User and Role
```sql
SELECT CURRENT_USER() AS current_user, CURRENT_ROLE() AS current_role;
```

### Step 2: Create Role and Assign to User
```sql
-- Create the role
CREATE ROLE IF NOT EXISTS SMARTPHONE_ROLE;

-- Grant role to your user (replace SMARTPHONE_USER with your actual username)
GRANT ROLE SMARTPHONE_ROLE TO USER SMARTPHONE_USER;

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE SMARTPHONE_WH TO ROLE SMARTPHONE_ROLE;

-- Grant database permissions
GRANT USAGE ON DATABASE SMARTPHONE_INTELLIGENCE_DB TO ROLE SMARTPHONE_ROLE;
GRANT USAGE ON SCHEMA SMARTPHONE_INTELLIGENCE_DB.PUBLIC TO ROLE SMARTPHONE_ROLE;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLE SMARTPHONE_INTELLIGENCE_DB.PUBLIC.COUNTRIES TO ROLE SMARTPHONE_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLE SMARTPHONE_INTELLIGENCE_DB.PUBLIC.MACRO_INDICATORS TO ROLE SMARTPHONE_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON FUTURE TABLES IN SCHEMA SMARTPHONE_INTELLIGENCE_DB.PUBLIC TO ROLE SMARTPHONE_ROLE;
GRANT CREATE TABLE ON SCHEMA SMARTPHONE_INTELLIGENCE_DB.PUBLIC TO ROLE SMARTPHONE_ROLE;

-- Set role as default for user (optional but recommended)
ALTER USER SMARTPHONE_USER SET DEFAULT_ROLE = SMARTPHONE_ROLE;
```

### Step 3: Verify Role Assignment
```sql
-- Check roles granted to user
SHOW GRANTS TO USER SMARTPHONE_USER;

-- Check grants on the role
SHOW GRANTS TO ROLE SMARTPHONE_ROLE;
```

## Activating the Role

### Option 1: Set as Default (Recommended)
The role is already set as default with the `ALTER USER` command above. It will activate automatically on next login.

### Option 2: Activate in Current Session
Run this command as the user (not as admin):
```sql
USE ROLE SMARTPHONE_ROLE;
```

### Option 3: Activate via Python Connection
Add `SNOWFLAKE_ROLE=SMARTPHONE_ROLE` to your `.env` file. The Python connection code will automatically use it.

## Verification Commands

### Check Current User and Role
```sql
SELECT CURRENT_USER() AS current_user, CURRENT_ROLE() AS current_role;
```

### List All Available Roles
```sql
SHOW GRANTS;
```

### Test Role Permissions
```sql
-- This should work if role is properly activated
SELECT COUNT(*) FROM SMARTPHONE_INTELLIGENCE_DB.PUBLIC.COUNTRIES;
```

## Troubleshooting

### Error: "Requested role SMARTPHONE_ROLE is not assigned to executing user"
**Solution:** Run the `GRANT ROLE` command as ACCOUNTADMIN or SECURITYADMIN:
```sql
GRANT ROLE SMARTPHONE_ROLE TO USER SMARTPHONE_USER;
```

### Error: "Insufficient privileges"
**Solution:** Ensure all GRANT commands were run successfully. Check with:
```sql
SHOW GRANTS TO ROLE SMARTPHONE_ROLE;
```

### Role not activating automatically
**Solution 1:** Set it as default:
```sql
ALTER USER SMARTPHONE_USER SET DEFAULT_ROLE = SMARTPHONE_ROLE;
```

**Solution 2:** Manually activate in session:
```sql
USE ROLE SMARTPHONE_ROLE;
```

**Solution 3:** Add to `.env` file:
```
SNOWFLAKE_ROLE=SMARTPHONE_ROLE
```
