# Banking Rewards & Fees Management System - Microservices Version
test
## Overview

This is the modernized version of the Banking Rewards & Fees Management System, migrated from a legacy monolithic architecture to a modern microservices architecture using AWS Lambda functions and Streamlit frontend.
 
## Architecture

### Legacy vs Modern Architecture

**Legacy Architecture:**
- Monolithic Streamlit app with direct database connections
- Business logic embedded in MySQL stored procedures
- Single database table combining customer and account data

**Modern Architecture:**
- Streamlit frontend (UI only, no database access)
- AWS Lambda microservices for business logic
- Separated database schema (Customers and Accounts tables)
- RESTful API communication between frontend and services

### Microservices

1. **Account Service** (`account_service.py`)
   - Manages account operations (CRUD)
   - Handles balance updates
   - Joins customer and account data

2. **Fee Calculation Service** (`fee_calculation_service.py`)
   - Calculates monthly fees based on business rules
   - No database modifications (calculation only)

3. **Rewards Calculation Service** (`rewards_calculation_service.py`)
   - Calculates monthly rewards based on balance
   - No database modifications (calculation only)

## Business Rules

### Fee Calculation
- **Premium tier customers**: $0.00 monthly fee
- **Standard tier customers with balance > $5,000**: $5.00 monthly fee
- **Standard tier customers with balance ≤ $5,000**: $15.00 monthly fee

### Rewards Calculation
- **Accounts with balance > $10,000**: 2% of balance as rewards
- **Accounts with balance ≤ $10,000**: 1% of balance as rewards

## Database Schema

### New Schema (BankingRewardsFees_New)

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

### Migration from Legacy Schema

The legacy schema has been normalized:
- Customer information moved to separate `Customers` table
- Account information streamlined in `Accounts` table
- Deprecated columns removed: `monthly_fees`, `monthly_rewards`, `legacy_flag`
- Business logic moved from stored procedures to Lambda functions

## Installation and Setup

### Prerequisites

- Python 3.9+
- AWS Account with Lambda and API Gateway access
- MySQL database (RDS recommended)
- Streamlit

### Local Development Setup

1. **Clone and navigate to the project:**
   ```bash
   cd BankingRewardsFees_New
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Update `aws_lambda_api.env` with your actual Lambda API URLs:
   ```
   ACCOUNT_SERVICE_URL = "https://your-api-gateway-url/Account_Service"
   FEE_CALCULATION_URL = "https://your-api-gateway-url/Fee_Calculation_Service"
   REWARDS_CALCULATION_URL = "https://your-api-gateway-url/Rewards_Calculation_Service"
   ```

4. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

### AWS Lambda Deployment

See `lambda_functions/deployment_instructions.md` for detailed deployment steps.

## API Endpoints

### Account Service
- `GET /` - List all accounts with customer information
- `GET /{account_id}` - Get specific account details
- `PUT /{account_id}` - Update account balance

### Fee Calculation Service
- `POST /{account_id}` - Calculate monthly fees for account

### Rewards Calculation Service
- `POST /{account_id}` - Calculate monthly rewards for account

## Testing

### Running Unit Tests

1. **Install test dependencies:**
   ```bash
   pip install -r tests/test_requirements.txt
   ```

2. **Run all tests:**
   ```bash
   python tests/run_tests.py
   ```

3. **Run specific test module:**
   ```bash
   python tests/run_tests.py test_account_service
   ```

### Test Coverage

The test suite includes:
- **Account Service Tests**: CRUD operations, error handling, edge cases
- **Fee Calculation Tests**: Business rule validation, boundary conditions
- **Rewards Calculation Tests**: Calculation accuracy, decimal precision

## Key Improvements Over Legacy System

### Architecture Improvements
1. **Separation of Concerns**: UI, business logic, and data access are properly separated
2. **Scalability**: Each microservice can be scaled independently
3. **Maintainability**: Business logic is in Python code, not stored procedures
4. **Testability**: Comprehensive unit test coverage for all services

### Database Improvements
1. **Normalization**: Customer and account data properly separated
2. **Data Integrity**: Foreign key relationships enforced
3. **Performance**: Optimized queries with proper joins

### Business Logic Improvements
1. **Real-time Calculations**: Fees and rewards calculated on-demand
2. **No Data Duplication**: Calculated values not stored in database
3. **Flexibility**: Easy to modify business rules in Python code

## Dead Code Removal

The following stored procedures from the legacy system are no longer needed:
- `CalculateReferralBonus` - Business no longer uses referral bonuses
- `LegacyAccountCleanup` - Legacy flag management no longer needed

## Security Considerations

### Current Implementation
- Database credentials managed via environment variables
- CORS enabled for API access
- Basic error handling and input validation

### Production Recommendations
- Implement proper authentication/authorization
- Use AWS IAM roles for Lambda functions
- Enable API Gateway authentication
- Implement rate limiting
- Add comprehensive logging and monitoring

## Monitoring and Logging

### AWS CloudWatch Integration
- Lambda function execution logs
- API Gateway request/response logs
- Database connection monitoring
- Error rate and performance metrics

### Recommended Alerts
- High error rates in Lambda functions
- Database connection failures
- API Gateway 4xx/5xx responses
- Lambda function timeout issues

## Future Enhancements

### Potential Improvements
1. **Caching**: Implement Redis for frequently accessed data
2. **Event-Driven Architecture**: Use AWS EventBridge for service communication
3. **Data Validation**: Add comprehensive input validation
4. **Audit Trail**: Implement transaction logging
5. **Batch Processing**: Add batch calculation capabilities
6. **Real-time Updates**: WebSocket support for live data updates

### Additional Microservices
1. **Customer Service**: Dedicated customer management
2. **Transaction Service**: Handle account transactions
3. **Notification Service**: Send alerts and notifications
4. **Reporting Service**: Generate financial reports

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify Lambda function URLs in `aws_lambda_api.env`
   - Check API Gateway CORS configuration
   - Validate Lambda function permissions

2. **Database Connection Issues**
   - Verify database credentials in Lambda environment variables
   - Check VPC and security group configurations
   - Ensure RDS instance is accessible from Lambda

3. **Calculation Errors**
   - Review business logic in calculation services
   - Check for null/empty balance values
   - Validate customer tier values

### Debugging Tips
- Check CloudWatch logs for Lambda function errors
- Use API Gateway test feature to validate endpoints
- Test database connectivity from Lambda console
- Verify JSON request/response formats

## Contributing

### Development Guidelines
1. Follow PEP 8 Python style guidelines
2. Write comprehensive unit tests for new features
3. Update documentation for any changes
4. Test both locally and in AWS environment

### Code Review Process
1. Ensure all tests pass
2. Verify API compatibility
3. Check for security vulnerabilities
4. Validate business logic accuracy

## License

This project is for demonstration purposes and follows the same licensing as the original legacy system.

## Support

For technical support or questions about the migration:
1. Check the troubleshooting section
2. Review CloudWatch logs
3. Validate configuration files
4. Test individual components in isolation