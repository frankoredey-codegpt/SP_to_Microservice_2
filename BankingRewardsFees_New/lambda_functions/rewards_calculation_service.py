import json
import mysql.connector
import os
from decimal import Decimal

def lambda_handler(event, context):
    """
    Rewards Calculation Service Lambda Function
    Calculates monthly rewards based on account balance
    Business Rules:
    - Accounts with balance > $10,000: 2% of balance as rewards
    - Accounts with balance ≤ $10,000: 1% of balance as rewards
    """
    
    # Database connection
    def get_connection():
        return mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'database-2.crq7shsasjo0.us-west-2.rds.amazonaws.com'),
            user=os.environ.get('DB_USER', 'admin'),
            password=os.environ.get('DB_PASSWORD', 'demo1234!'),
            database=os.environ.get('DB_NAME', 'BankingRewardsFees_New')
        )
    
    try:
        # Parse the request
        http_method = event.get('httpMethod', 'POST')
        path_parameters = event.get('pathParameters') or {}
        body = event.get('body')
        
        if body:
            body = json.loads(body)
        
        account_id = path_parameters.get('account_id') or (body.get('account_id') if body else None)
        
        if not account_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing account_id'})
            }
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get account balance
        query = """
            SELECT a.account_id, a.balance
            FROM Accounts a
            WHERE a.account_id = %s
        """
        cursor.execute(query, (account_id,))
        account = cursor.fetchone()
        
        if not account:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Account not found'})
            }
        
        # Calculate rewards based on business rules
        balance = float(account['balance']) if account['balance'] else 0.0
        
        if balance > 10000:
            reward_rate = 0.02  # 2%
        else:
            reward_rate = 0.01  # 1%
        
        calculated_reward = balance * reward_rate
        
        # Return the calculated reward (no longer storing in database)
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'account_id': account_id,
                'balance': balance,
                'reward_rate': reward_rate,
                'calculated_reward': round(calculated_reward, 2),
                'calculation_timestamp': str(context.aws_request_id) if context else 'local'
            })
        }
    
    except Exception as e:
        response = {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return response