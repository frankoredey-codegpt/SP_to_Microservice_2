import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add the lambda_functions directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda_functions'))

from account_service import lambda_handler

class TestAccountService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_context = Mock()
        self.mock_context.aws_request_id = 'test-request-id'
        
        # Sample account data
        self.sample_account = {
            'account_id': 1,
            'balance': 1500.00,
            'created_at': '2023-01-01 00:00:00',
            'updated_at': '2023-01-01 00:00:00',
            'customer_id': 1,
            'customer_name': 'John Doe',
            'customer_tier': 'standard'
        }
        
        self.sample_accounts = [
            {
                'account_id': 1,
                'balance': 1500.00,
                'customer_name': 'John Doe',
                'customer_tier': 'standard'
            },
            {
                'account_id': 2,
                'balance': 15000.00,
                'customer_name': 'Jane Smith',
                'customer_tier': 'premium'
            }
        ]
    
    @patch('account_service.mysql.connector.connect')
    def test_get_all_accounts_success(self, mock_connect):
        """Test successful retrieval of all accounts."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = self.sample_accounts
        
        # Create test event
        event = {
            'httpMethod': 'GET',
            'pathParameters': None,
            'queryStringParameters': None,
            'body': None
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Content-Type', response['headers'])
        self.assertEqual(response['headers']['Content-Type'], 'application/json')
        
        # Parse response body
        response_data = json.loads(response['body'])
        self.assertEqual(len(response_data), 2)
        self.assertEqual(response_data[0]['account_id'], 1)
        self.assertEqual(response_data[1]['account_id'], 2)
        
        # Verify database calls
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('account_service.mysql.connector.connect')
    def test_get_specific_account_success(self, mock_connect):
        """Test successful retrieval of a specific account."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = self.sample_account
        
        # Create test event
        event = {
            'httpMethod': 'GET',
            'pathParameters': {'account_id': '1'},
            'queryStringParameters': None,
            'body': None
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        response_data = json.loads(response['body'])
        self.assertEqual(response_data['account_id'], 1)
        self.assertEqual(response_data['customer_name'], 'John Doe')
        self.assertEqual(response_data['balance'], 1500.00)
    
    @patch('account_service.mysql.connector.connect')
    def test_get_specific_account_not_found(self, mock_connect):
        """Test retrieval of non-existent account."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        # Create test event
        event = {
            'httpMethod': 'GET',
            'pathParameters': {'account_id': '999'},
            'queryStringParameters': None,
            'body': None
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 404)
        response_data = json.loads(response['body'])
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Account not found')
    
    @patch('account_service.mysql.connector.connect')
    def test_update_balance_success(self, mock_connect):
        """Test successful balance update."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        # Create test event
        event = {
            'httpMethod': 'PUT',
            'pathParameters': {'account_id': '1'},
            'queryStringParameters': None,
            'body': json.dumps({'balance': 2000.00})
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        response_data = json.loads(response['body'])
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Balance updated successfully')
        
        # Verify database calls
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
    
    @patch('account_service.mysql.connector.connect')
    def test_update_balance_account_not_found(self, mock_connect):
        """Test balance update for non-existent account."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0
        
        # Create test event
        event = {
            'httpMethod': 'PUT',
            'pathParameters': {'account_id': '999'},
            'queryStringParameters': None,
            'body': json.dumps({'balance': 2000.00})
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 404)
        response_data = json.loads(response['body'])
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Account not found')
    
    def test_update_balance_missing_parameters(self):
        """Test balance update with missing parameters."""
        # Create test event with missing balance
        event = {
            'httpMethod': 'PUT',
            'pathParameters': {'account_id': '1'},
            'queryStringParameters': None,
            'body': json.dumps({})
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 400)
        response_data = json.loads(response['body'])
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Missing account_id or balance')
    
    def test_unsupported_http_method(self):
        """Test unsupported HTTP method."""
        # Create test event with unsupported method
        event = {
            'httpMethod': 'DELETE',
            'pathParameters': None,
            'queryStringParameters': None,
            'body': None
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 405)
        response_data = json.loads(response['body'])
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Method not allowed')
    
    @patch('account_service.mysql.connector.connect')
    def test_database_connection_error(self, mock_connect):
        """Test database connection error handling."""
        # Mock database connection to raise an exception
        mock_connect.side_effect = Exception('Database connection failed')
        
        # Create test event
        event = {
            'httpMethod': 'GET',
            'pathParameters': None,
            'queryStringParameters': None,
            'body': None
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 500)
        response_data = json.loads(response['body'])
        self.assertIn('error', response_data)
        self.assertIn('Database connection failed', response_data['error'])

if __name__ == '__main__':
    unittest.main()