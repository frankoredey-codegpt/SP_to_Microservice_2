# Banking Rewards & Fees - Modern Microservices Deployment Guide

## Architecture Overview

The modernized application follows a microservices architecture with:
- **Frontend**: Streamlit app (UI only, no direct database access)
- **Backend**: AWS Lambda functions for business logic
- **Database**: MySQL with normalized schema (separate Customers and Accounts tables)

## Lambda Functions

### 1. Get Accounts Lambda (`get_accounts_lambda.py`)
- **Purpose**: Retrieve account information
- **API Gateway Method**: GET
- **Endpoint**: `/accounts` (all accounts) or `/accounts?account_id=X` (specific account)

### 2. Calculate Fees Lambda (`calculate_fees_lambda.py`)
- **Purpose**: Calculate monthly fees based on business rules
- **API Gateway Method**: POST
- **Endpoint**: `/accounts/fees`
- **Payload**: `{"account_id": 123}`

### 3. Calculate Rewards Lambda (`calculate_rewards_lambda.py`)
- **Purpose**: Calculate monthly rewards based on balance
- **API Gateway Method**: POST
- **Endpoint**: `/accounts/rewards`
- **Payload**: `{"account_id": 123}`

### 4. Update Balance Lambda (`update_balance_lambda.py`)
- **Purpose**: Update account balance (only microservice that modifies database)
- **API Gateway Method**: POST
- **Endpoint**: `/accounts/balance`
- **Payload**: `{"account_id": 123, "new_balance": 1500.00}`

## AWS Deployment Steps

### Step 1: Create Lambda Functions

For each Lambda function:

1. Create a new Lambda function in AWS Console
2. Set runtime to Python 3.9 or higher
3. Upload the function code
4. Set environment variables:
   - `DB_HOST`: Your MySQL host
   - `DB_USER`: Database username
   - `DB_PASSWORD`: Database password
   - `DB_NAME`: BankingRewardsFees_New

### Step 2: Create Lambda Layers (for dependencies)

1. Create a layer for mysql-connector-python:
   ```bash
   mkdir python
   pip install mysql-connector-python -t python/
   zip -r mysql-layer.zip python/
   ```
2. Upload to AWS Lambda Layers
3. Attach the layer to all Lambda functions

### Step 3: Set up API Gateway

1. Create a new REST API in API Gateway
2. Create resources and methods:

```
/accounts
  - GET (link to get_accounts_lambda)
  
/accounts/fees
  - POST (link to calculate_fees_lambda)
  
/accounts/rewards
  - POST (link to calculate_rewards_lambda)
  
/accounts/balance
  - POST (link to update_balance_lambda)
```

3. Enable CORS for all methods
4. Deploy the API to a stage (e.g., 'prod')

### Step 4: Update Streamlit App Configuration

In `app.py`, update the `API_BASE_URL` with your actual API Gateway URL:

```python
API_BASE_URL = "https://your-actual-api-id.execute-api.us-west-2.amazonaws.com/prod"
```

### Step 5: Deploy Streamlit App

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run locally for testing:
   ```bash
   streamlit run app.py
   ```

3. Deploy to your preferred platform (AWS EC2, Heroku, Streamlit Cloud, etc.)

## Database Migration

The new schema separates customer and account data:

### Old Schema (BankingRewardsFees_Old):
```sql
Accounts (account_id, customer_name, customer_tier, balance, monthly_fees, monthly_rewards, legacy_flag, created_at, updated_at)
```

### New Schema (BankingRewardsFees_New):
```sql
Customers (customer_id, name, tier, created_at, updated_at)
Accounts (account_id, customer_id, balance, created_at, updated_at)
```

### Migration Script:
```sql
-- Insert customers (deduplicated)
INSERT INTO BankingRewardsFees_New.Customers (customer_id, name, tier, created_at, updated_at)
SELECT DISTINCT 
    ROW_NUMBER() OVER (ORDER BY customer_name) as customer_id,
    customer_name as name,
    customer_tier as tier,
    created_at,
    updated_at
FROM BankingRewardsFees_Old.Accounts;

-- Insert accounts with customer references
INSERT INTO BankingRewardsFees_New.Accounts (account_id, customer_id, balance, created_at, updated_at)
SELECT 
    o.account_id,
    c.customer_id,
    o.balance,
    o.created_at,
    o.updated_at
FROM BankingRewardsFees_Old.Accounts o
JOIN BankingRewardsFees_New.Customers c ON c.name = o.customer_name AND c.tier = o.customer_tier;
```

## Key Architectural Changes

### 1. Removed Dead Code
- `CalculateReferralBonus` stored procedure (no longer used)
- `LegacyAccountCleanup` stored procedure (no longer called)
- `monthly_fees`, `monthly_rewards`, `legacy_flag` columns (calculated in real-time now)

### 2. Microservices Benefits
- **Separation of Concerns**: Each Lambda handles one business function
- **Scalability**: Functions scale independently
- **Maintainability**: Business logic in Python instead of SQL
- **Security**: Database access only through controlled APIs

### 3. Real-time Calculations
- Fees and rewards are calculated on-demand, not stored
- Eliminates data consistency issues
- Always reflects current business rules

## Testing

Run the unit tests to verify functionality:
```bash
cd tests
python -m pytest test_lambda_functions.py -v
```

## Monitoring and Logging

- Lambda functions include comprehensive error handling
- CloudWatch logs capture all function executions
- API Gateway provides request/response logging
- Consider adding AWS X-Ray for distributed tracing

## Security Considerations

- Database credentials stored in environment variables
- CORS enabled for frontend access
- Consider using AWS Secrets Manager for production
- Implement API authentication if needed (API Keys, Cognito, etc.)

## Cost Optimization

- Lambda functions only run when called (pay-per-use)
- API Gateway charges per request
- Consider reserved capacity for high-traffic scenarios
- Monitor CloudWatch metrics for optimization opportunities