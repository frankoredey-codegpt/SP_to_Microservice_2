import json
import mysql.connector
import os
from decimal import Decimal

def lambda_handler(event, context):
    """
    AWS Lambda function to get account information.
    Can return all accounts or a specific account based on query parameters.
    """
    try:
        # Check if specific account is requested
        query_params = event.get('queryStringParameters') or {}
        account_id = query_params.get('account_id')
        
        # Database connection
        conn = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'database-2.crq7shsasjo0.us-west-2.rds.amazonaws.com'),
            user=os.environ.get('DB_USER', 'admin'),
            password=os.environ.get('DB_PASSWORD', 'demo1234!'),
            database=os.environ.get('DB_NAME', 'BankingRewardsFees_New')
        )
        
        cursor = conn.cursor(dictionary=True)
        
        if account_id:
            # Get specific account
            query = """
            SELECT a.account_id, a.balance, c.name as customer_name, c.tier, 
                   a.created_at, a.updated_at
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
                        'Access-Control-Allow-Methods': 'GET, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type'
                    },
                    'body': json.dumps({
                        'error': 'Account not found'
                    })
                }
            
            # Convert Decimal to float for JSON serialization
            account_data['balance'] = float(account_data['balance'])
            account_data['created_at'] = account_data['created_at'].isoformat() if account_data['created_at'] else None
            account_data['updated_at'] = account_data['updated_at'].isoformat() if account_data['updated_at'] else None
            
            cursor.close()
            conn.close()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'account': account_data
                })
            }
        else:
            # Get all accounts
            query = """
            SELECT a.account_id, a.balance, c.name as customer_name, c.tier, 
                   a.created_at, a.updated_at
            FROM Accounts a 
            JOIN Customers c ON a.customer_id = c.customer_id 
            ORDER BY a.account_id
            """
            cursor.execute(query)
            accounts_data = cursor.fetchall()
            
            # Convert Decimal to float for JSON serialization
            for account in accounts_data:
                account['balance'] = float(account['balance'])
                account['created_at'] = account['created_at'].isoformat() if account['created_at'] else None
                account['updated_at'] = account['updated_at'].isoformat() if account['updated_at'] else None
            
            cursor.close()
            conn.close()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'accounts': accounts_data
                })
            }
        
    except mysql.connector.Error as db_error:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
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
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }

# For local testing
if __name__ == "__main__":
    # Test getting all accounts
    test_event = {}
    result = lambda_handler(test_event, {})
    print("All accounts:")
    print(json.dumps(result, indent=2))
    
    # Test getting specific account
    test_event = {'queryStringParameters': {'account_id': '1'}}
    result = lambda_handler(test_event, {})
    print("\nSpecific account:")
    print(json.dumps(result, indent=2))