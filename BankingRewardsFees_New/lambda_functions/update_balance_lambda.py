import json
import mysql.connector
import os
from decimal import Decimal
from datetime import datetime

def lambda_handler(event, context):
    """
    AWS Lambda function to update account balance.
    """
    try:
        # Parse the incoming request
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        account_id = body.get('account_id')
        new_balance = body.get('new_balance')
        
        if not account_id or new_balance is None:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'error': 'account_id and new_balance are required'
                })
            }
        
        # Validate balance is not negative
        if new_balance < 0:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'error': 'Balance cannot be negative'
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
        
        # Check if account exists and get current data
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
        
        # Update the balance
        update_query = """
        UPDATE Accounts 
        SET balance = %s, updated_at = %s 
        WHERE account_id = %s
        """
        current_time = datetime.now()
        cursor.execute(update_query, (Decimal(str(new_balance)), current_time, account_id))
        conn.commit()
        
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
                'balance': new_balance,
                'customer_name': account_data['name'],
                'tier': account_data['tier'],
                'updated_at': current_time.isoformat(),
                'message': 'Balance updated successfully'
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
        'body': json.dumps({'account_id': 1, 'new_balance': 20000.00})
    }
    result = lambda_handler(test_event, {})
    print(json.dumps(result, indent=2))