# AWS Lambda Deployment Instructions

## Overview
This folder contains three microservices that need to be deployed as AWS Lambda functions:

1. **Account Service** (`account_service.py`) - Handles account operations
2. **Fee Calculation Service** (`fee_calculation_service.py`) - Calculates monthly fees
3. **Rewards Calculation Service** (`rewards_calculation_service.py`) - Calculates monthly rewards

## Deployment Steps

### 1. Create Lambda Functions in AWS Console

For each service, create a new Lambda function:

#### Account Service
- **Function name**: `Account_Service`
- **Runtime**: Python 3.9 or higher
- **Handler**: `account_service.lambda_handler`

#### Fee Calculation Service
- **Function name**: `Fee_Calculation_Service`
- **Runtime**: Python 3.9 or higher
- **Handler**: `fee_calculation_service.lambda_handler`

#### Rewards Calculation Service
- **Function name**: `Rewards_Calculation_Service`
- **Runtime**: Python 3.9 or higher
- **Handler**: `rewards_calculation_service.lambda_handler`

### 2. Package and Upload Code

For each Lambda function:

1. Create a deployment package:
   ```bash
   # Create a new directory for the package
   mkdir lambda_package
   cd lambda_package
   
   # Install dependencies
   pip install mysql-connector-python -t .
   
   # Copy the Python file
   cp ../account_service.py lambda_function.py  # Rename to lambda_function.py
   
   # Create ZIP file
   zip -r account_service.zip .
   ```

2. Upload the ZIP file to the Lambda function in AWS Console

### 3. Configure Environment Variables

For each Lambda function, set these environment variables:

- `DB_HOST`: Your MySQL RDS endpoint
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_NAME`: `BankingRewardsFees_New`

### 4. Set up API Gateway

For each Lambda function, create an API Gateway trigger:

1. Go to API Gateway in AWS Console
2. Create a new REST API
3. Create resources and methods:

#### Account Service API
- `GET /` - List all accounts
- `GET /{account_id}` - Get specific account
- `PUT /{account_id}` - Update account balance

#### Fee Calculation Service API
- `POST /{account_id}` - Calculate fees for account

#### Rewards Calculation Service API
- `POST /{account_id}` - Calculate rewards for account

### 5. Configure CORS

Enable CORS for all methods to allow the Streamlit app to call the APIs:

1. Select each method in API Gateway
2. Actions → Enable CORS
3. Set Access-Control-Allow-Origin to '*'
4. Deploy the API

### 6. Update Environment Variables

Update the `aws_lambda_api.env` file with your actual API Gateway URLs:

```
ACCOUNT_SERVICE_URL = "https://your-api-id.execute-api.region.amazonaws.com/stage/Account_Service"
FEE_CALCULATION_URL = "https://your-api-id.execute-api.region.amazonaws.com/stage/Fee_Calculation_Service"
REWARDS_CALCULATION_URL = "https://your-api-id.execute-api.region.amazonaws.com/stage/Rewards_Calculation_Service"
```

### 7. Database Permissions

Ensure your Lambda functions have network access to your MySQL RDS instance:

1. Configure VPC settings if RDS is in a private subnet
2. Update security groups to allow Lambda access
3. Test database connectivity

## Testing

Test each Lambda function individually before integrating with the Streamlit app:

1. Use the AWS Lambda console test feature
2. Create test events with sample payloads
3. Verify database connections and operations
4. Check CloudWatch logs for any errors

## Monitoring

Set up CloudWatch monitoring for:
- Function execution duration
- Error rates
- Database connection issues
- API Gateway request/response metrics