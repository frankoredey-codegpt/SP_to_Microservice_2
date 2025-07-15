import json
import mysql.connector
import os
from decimal import Decimal

def lambda_handler(event, context):
    """
    Account Service Lambda Function
    Handles account operations: get accounts, get account details, update balance
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
        http_method = event.get('httpMethod', 'GET')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        body = event.get('body')
        
        if body:
            body = json.loads(body)
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        if http_method == 'GET':
            if 'account_id' in path_parameters:
                # Get specific account details with customer info
                account_id = path_parameters['account_id']
                query = """
                    SELECT a.account_id, a.balance, a.created_at, a.updated_at,
                           c.customer_id, c.name as customer_name, c.tier as customer_tier
                    FROM Accounts a
                    JOIN Customers c ON a.customer_id = c.customer_id
                    WHERE a.account_id = %s
                """
                cursor.execute(query, (account_id,))
                account = cursor.fetchone()
                
                if account:
                    # Convert Decimal to float for JSON serialization
                    if account['balance']:
                        account['balance'] = float(account['balance'])
                    
                    response = {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps(account)
                    }
                else:
                    response = {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Account not found'})
                    }
            else:
                # Get all accounts with customer info
                query = """
                    SELECT a.account_id, a.balance, c.name as customer_name, c.tier as customer_tier
                    FROM Accounts a
                    JOIN Customers c ON a.customer_id = c.customer_id
                    ORDER BY c.name
                """
                cursor.execute(query)
                accounts = cursor.fetchall()
                
                # Convert Decimal to float for JSON serialization
                for account in accounts:
                    if account['balance']:
                        account['balance'] = float(account['balance'])
                
                response = {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(accounts)
                }
        
        elif http_method == 'PUT':
            # Update account balance
            account_id = path_parameters.get('account_id')
            new_balance = body.get('balance')
            
            if not account_id or new_balance is None:
                response = {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Missing account_id or balance'})
                }
            else:
                cursor.execute(
                    "UPDATE Accounts SET balance = %s, updated_at = NOW() WHERE account_id = %s",
                    (new_balance, account_id)
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    response = {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'message': 'Balance updated successfully'})
                    }
                else:
                    response = {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Account not found'})
                    }
        
        else:
            response = {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Method not allowed'})
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