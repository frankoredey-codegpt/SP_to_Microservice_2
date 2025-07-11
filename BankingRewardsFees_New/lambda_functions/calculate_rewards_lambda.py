import json
import mysql.connector
import os
from decimal import Decimal

def lambda_handler(event, context):
    """
    AWS Lambda function to calculate monthly rewards for a banking account.
    Replaces the CalculateRewards stored procedure.
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
        
        # Calculate rewards based on business logic
        balance = float(account_data['balance'])
        
        if balance > 10000:
            reward_rate = Decimal('0.02')  # 2%
        else:
            reward_rate = Decimal('0.01')  # 1%
        
        monthly_reward = Decimal(str(balance)) * reward_rate
        
        # Note: In the new architecture, we don't store calculated rewards in the database
        # Instead, we return the calculated value for real-time use
        
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
                'monthly_reward': float(monthly_reward),
                'reward_rate': float(reward_rate),
                'balance': balance,
                'customer_name': account_data['name'],
                'tier': account_data['tier'],
                'message': 'Monthly reward calculated successfully'
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