import json
import mysql.connector
import os
from decimal import Decimal

def lambda_handler(event, context):
    """
    Fee Calculation Service Lambda Function
    Calculates monthly fees based on customer tier and balance
    Business Rules:
    - Premium tier customers: $0.00 monthly fee
    - Standard tier customers with balance > $5,000: $5.00 monthly fee
    - Standard tier customers with balance ≤ $5,000: $15.00 monthly fee
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
        
        # Get account and customer information
        query = """
            SELECT a.account_id, a.balance, c.tier as customer_tier
            FROM Accounts a
            JOIN Customers c ON a.customer_id = c.customer_id
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
        
        # Calculate fee based on business rules
        customer_tier = account['customer_tier']
        balance = float(account['balance']) if account['balance'] else 0.0
        
        if customer_tier == 'premium':
            fee = 0.00
        elif balance > 5000:
            fee = 5.00
        else:
            fee = 15.00
        
        # Return the calculated fee (no longer storing in database)
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'account_id': account_id,
                'customer_tier': customer_tier,
                'balance': balance,
                'calculated_fee': fee,
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