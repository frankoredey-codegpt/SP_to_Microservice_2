# Banking Rewards & Fees - Modern Microservices Architecture

## Overview

This is the modernized version of the Banking Rewards & Fees application, migrated from a legacy monolithic architecture to a modern microservices architecture using AWS Lambda functions.

## Architecture

### Legacy vs Modern Architecture

| Component | Legacy | Modern |
|-----------|--------|--------|
| **Frontend** | Streamlit with direct DB access | Streamlit (UI only) |
| **Business Logic** | MySQL Stored Procedures | AWS Lambda Functions |
| **Database** | Single denormalized table | Normalized schema (Customers + Accounts) |
| **Scalability** | Monolithic | Independent microservices |
| **Deployment** | Single application | Distributed services |

### Microservices

1. **Get Accounts Service** (`get_accounts_lambda.py`)
   - Retrieves account information
   - Supports both list all and get specific account

2. **Calculate Fees Service** (`calculate_fees_lambda.py`)
   - Calculates monthly fees based on customer tier and balance
   - Business Rules:
     - Premium tier: $0 fee
     - Standard tier (balance > $5,000): $5 fee
     - Standard tier (balance ≤ $5,000): $15 fee

3. **Calculate Rewards Service** (`calculate_rewards_lambda.py`)
   - Calculates monthly rewards based on account balance
   - Business Rules:
     - Balance > $10,000: 2% rewards
     - Balance ≤ $10,000: 1% rewards

4. **Update Balance Service** (`update_balance_lambda.py`)
   - Updates account balances (only service that modifies database)
   - Includes validation and error handling

## Database Schema

### New Normalized Schema

```sql
-- Customers table
CREATE TABLE Customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(255),
    tier VARCHAR(50),
    created_at DATETIME,
    updated_at DATETIME
);

-- Accounts table
CREATE TABLE Accounts (
    account_id INT PRIMARY KEY,
    customer_id INT,
    balance DECIMAL(10,2),
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);
```

### Removed Dead Code

The following stored procedures were identified as dead code and removed:
- `CalculateReferralBonus` - No longer used by business
- `LegacyAccountCleanup` - No longer called anywhere

### Deprecated Columns

The following columns were removed from the new schema:
- `monthly_fees` - Now calculated in real-time
- `monthly_rewards` - Now calculated in real-time  
- `legacy_flag` - No longer needed

## Installation & Setup

### Prerequisites

- Python 3.9+
- AWS Account with Lambda and API Gateway access
- MySQL database

### Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export DB_HOST=your-mysql-host
   export DB_USER=your-username
   export DB_PASSWORD=your-password
   export DB_NAME=BankingRewardsFees_New
   ```

4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

### AWS Deployment

See `deployment_guide.md` for detailed deployment instructions.

## API Endpoints

Once deployed to AWS API Gateway, the following endpoints will be available:

- `GET /accounts` - Get all accounts
- `GET /accounts?account_id=X` - Get specific account
- `POST /accounts/fees` - Calculate fees
- `POST /accounts/rewards` - Calculate rewards
- `POST /accounts/balance` - Update balance

## Testing

### Unit Tests

Run the unit tests:
```bash
cd tests
pip install -r test_requirements.txt
python -m pytest test_lambda_functions.py -v
```

### Integration Tests

Run the integration tests:
```bash
python -m pytest test_integration.py -v
```

## Key Improvements

### 1. Separation of Concerns
- Frontend handles only UI logic
- Business logic isolated in microservices
- Database access controlled through APIs

### 2. Scalability
- Each microservice scales independently
- No single point of failure
- Pay-per-use pricing model

### 3. Maintainability
- Business logic in Python instead of SQL
- Version control for all business rules
- Independent deployment of services

### 4. Real-time Calculations
- Fees and rewards calculated on-demand
- Always reflects current business rules
- No stale data issues

### 5. Data Consistency
- Normalized database schema
- Single source of truth for customer data
- Proper foreign key relationships

## Configuration

### Environment Variables

The Lambda functions use the following environment variables:

- `DB_HOST` - MySQL database host
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `DB_NAME` - Database name (BankingRewardsFees_New)

### API Gateway Configuration

Update the `API_BASE_URL` in `app.py` with your actual API Gateway URL:

```python
API_BASE_URL = "https://your-api-gateway-url.execute-api.us-west-2.amazonaws.com/prod"
```

## Monitoring

- Lambda function logs available in CloudWatch
- API Gateway request/response logging
- Database connection monitoring
- Error tracking and alerting

## Security

- Database credentials in environment variables
- CORS enabled for frontend access
- Input validation in all Lambda functions
- Error handling prevents information leakage

## Future Enhancements

- Add authentication/authorization
- Implement caching for frequently accessed data
- Add audit trail for balance changes
- Implement transaction history
- Add real-time notifications
- Performance monitoring and optimization

## Support

For issues or questions, please refer to the deployment guide or create an issue in the repository.