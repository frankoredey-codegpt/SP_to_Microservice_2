import json
import mysql.connector
import os
from decimal import Decimal

def lambda_handler(event, context):
    """
    AWS Lambda function to calculate monthly fees for a banking account.
    Replaces the CalculateMonthlyFees stored procedure.
    """
    try:
        # Parse the incoming request
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        account_id = body.get('account_id')
        
        if not account_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'error': 'account_id is required'
                })
            }
        
        # Database connection
        conn = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'database-2.crq7shsasjo0.us-west-2.rds.amazonaws.com'),
            user=os.environ.get('DB_USER', 'admin'),
            password=os.environ.get('DB_PASSWORD', 'demo1234!'),
            database=os.environ.get('DB_NAME', 'BankingRewardsFees_New')
        )
        
        cursor = conn.cursor(dictionary=True)
        
        # Get account information using the new schema
        query = """
        SELECT a.account_id, a.balance, c.name, c.tier 
        FROM Accounts a 
        JOIN Customers c ON a.customer_id = c.customer_id 
        WHERE a.account_id = %s
        """
        cursor.execute(query, (account_id,))
        account_data = cursor.fetchone()
        
        if not account_data:
            cursor.close()
            conn.close()
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'error': 'Account not found'
                })
            }
        
        # Calculate fees based on business logic
        balance = float(account_data['balance'])
        tier = account_data['tier']
        
        if tier == 'premium':
            monthly_fee = Decimal('0.00')  # Premium accounts have no fees
        elif balance > 5000:
            monthly_fee = Decimal('5.00')  # Standard accounts with high balance
        else:
            monthly_fee = Decimal('15.00')  # Standard accounts with low balance
        
        cursor.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'account_id': account_id,
                'monthly_fee': float(monthly_fee),
                'tier': tier,
                'balance': balance,
                'message': 'Monthly fee calculated successfully'
            })
        }
        
    except mysql.connector.Error as db_error:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'error': f'Database error: {str(db_error)}'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }

# For local testing
if __name__ == "__main__":
    test_event = {
        'body': json.dumps({'account_id': 1})
    }
    result = lambda_handler(test_event, {})
    print(json.dumps(result, indent=2))