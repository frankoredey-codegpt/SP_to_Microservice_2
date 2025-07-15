import unittest
from unittest.mock import Mock, patch
import json
import sys
import os

# Add the lambda_functions directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda_functions'))

from fee_calculation_service import lambda_handler

class TestFeeCalculationService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_context = Mock()
        self.mock_context.aws_request_id = 'test-request-id'
    
    @patch('fee_calculation_service.mysql.connector.connect')
    def test_calculate_fee_premium_customer(self, mock_connect):
        """Test fee calculation for premium customer (should be $0)."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data for premium customer
        mock_cursor.fetchone.return_value = {
            'account_id': 1,
            'balance': 5000.00,
            'customer_tier': 'premium'
        }
        
        # Create test event
        event = {
            'httpMethod': 'POST',
            'pathParameters': {'account_id': '1'},
            'queryStringParameters': None,
            'body': json.dumps({'account_id': 1})
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        response_data = json.loads(response['body'])
        self.assertEqual(response_data['calculated_fee'], 0.00)
        self.assertEqual(response_data['customer_tier'], 'premium')
        self.assertEqual(response_data['balance'], 5000.00)
        
        # Verify database calls
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('fee_calculation_service.mysql.connector.connect')
    def test_calculate_fee_standard_high_balance(self, mock_connect):
        """Test fee calculation for standard customer with high balance (should be $5)."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data for standard customer with high balance
        mock_cursor.fetchone.return_value = {
            'account_id': 2,
            'balance': 7500.00,
            'customer_tier': 'standard'
        }
        
        # Create test event
        event = {
            'httpMethod': 'POST',
            'pathParameters': {'account_id': '2'},
            'queryStringParameters': None,
            'body': json.dumps({'account_id': 2})
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        response_data = json.loads(response['body'])
        self.assertEqual(response_data['calculated_fee'], 5.00)
        self.assertEqual(response_data['customer_tier'], 'standard')
        self.assertEqual(response_data['balance'], 7500.00)
    
    @patch('fee_calculation_service.mysql.connector.connect')
    def test_calculate_fee_standard_low_balance(self, mock_connect):
        """Test fee calculation for standard customer with low balance (should be $15)."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data for standard customer with low balance
        mock_cursor.fetchone.return_value = {
            'account_id': 3,
            'balance': 1200.00,
            'customer_tier': 'standard'
        }
        
        # Create test event
        event = {
            'httpMethod': 'POST',
            'pathParameters': {'account_id': '3'},
            'queryStringParameters': None,
            'body': json.dumps({'account_id': 3})
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        response_data = json.loads(response['body'])
        self.assertEqual(response_data['calculated_fee'], 15.00)
        self.assertEqual(response_data['customer_tier'], 'standard')
        self.assertEqual(response_data['balance'], 1200.00)
    
    @patch('fee_calculation_service.mysql.connector.connect')
    def test_calculate_fee_boundary_balance_5000(self, mock_connect):
        """Test fee calculation for exactly $5000 balance (should be $15)."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data for standard customer with exactly $5000
        mock_cursor.fetchone.return_value = {
            'account_id': 4,
            'balance': 5000.00,
            'customer_tier': 'standard'
        }
        
        # Create test event
        event = {
            'httpMethod': 'POST',
            'pathParameters': {'account_id': '4'},
            'queryStringParameters': None,
            'body': json.dumps({'account_id': 4})
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        response_data = json.loads(response['body'])
        self.assertEqual(response_data['calculated_fee'], 15.00)  # Exactly 5000 should get $15 fee
        self.assertEqual(response_data['customer_tier'], 'standard')
        self.assertEqual(response_data['balance'], 5000.00)
    
    @patch('fee_calculation_service.mysql.connector.connect')
    def test_calculate_fee_boundary_balance_5001(self, mock_connect):
        """Test fee calculation for $5001 balance (should be $5)."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data for standard customer with $5001
        mock_cursor.fetchone.return_value = {
            'account_id': 5,
            'balance': 5001.00,
            'customer_tier': 'standard'
        }
        
        # Create test event
        event = {
            'httpMethod': 'POST',
            'pathParameters': {'account_id': '5'},
            'queryStringParameters': None,
            'body': json.dumps({'account_id': 5})
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        response_data = json.loads(response['body'])
        self.assertEqual(response_data['calculated_fee'], 5.00)  # Over 5000 should get $5 fee
        self.assertEqual(response_data['customer_tier'], 'standard')
        self.assertEqual(response_data['balance'], 5001.00)
    
    @patch('fee_calculation_service.mysql.connector.connect')
    def test_calculate_fee_zero_balance(self, mock_connect):
        """Test fee calculation for zero balance."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data for standard customer with zero balance
        mock_cursor.fetchone.return_value = {
            'account_id': 6,
            'balance': 0.00,
            'customer_tier': 'standard'
        }
        
        # Create test event
        event = {
            'httpMethod': 'POST',
            'pathParameters': {'account_id': '6'},
            'queryStringParameters': None,
            'body': json.dumps({'account_id': 6})
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        response_data = json.loads(response['body'])
        self.assertEqual(response_data['calculated_fee'], 15.00)
        self.assertEqual(response_data['customer_tier'], 'standard')
        self.assertEqual(response_data['balance'], 0.00)
    
    @patch('fee_calculation_service.mysql.connector.connect')
    def test_calculate_fee_account_not_found(self, mock_connect):
        """Test fee calculation for non-existent account."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        # Create test event
        event = {
            'httpMethod': 'POST',
            'pathParameters': {'account_id': '999'},
            'queryStringParameters': None,
            'body': json.dumps({'account_id': 999})
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 404)
        response_data = json.loads(response['body'])
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Account not found')
    
    def test_calculate_fee_missing_account_id(self):
        """Test fee calculation with missing account ID."""
        # Create test event without account_id
        event = {
            'httpMethod': 'POST',
            'pathParameters': None,
            'queryStringParameters': None,
            'body': json.dumps({})
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 400)
        response_data = json.loads(response['body'])
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Missing account_id')
    
    @patch('fee_calculation_service.mysql.connector.connect')
    def test_database_connection_error(self, mock_connect):
        """Test database connection error handling."""
        # Mock database connection to raise an exception
        mock_connect.side_effect = Exception('Database connection failed')
        
        # Create test event
        event = {
            'httpMethod': 'POST',
            'pathParameters': {'account_id': '1'},
            'queryStringParameters': None,
            'body': json.dumps({'account_id': 1})
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 500)
        response_data = json.loads(response['body'])
        self.assertIn('error', response_data)
        self.assertIn('Database connection failed', response_data['error'])
    
    @patch('fee_calculation_service.mysql.connector.connect')
    def test_calculate_fee_null_balance(self, mock_connect):
        """Test fee calculation with null balance."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data with null balance
        mock_cursor.fetchone.return_value = {
            'account_id': 7,
            'balance': None,
            'customer_tier': 'standard'
        }
        
        # Create test event
        event = {
            'httpMethod': 'POST',
            'pathParameters': {'account_id': '7'},
            'queryStringParameters': None,
            'body': json.dumps({'account_id': 7})
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        response_data = json.loads(response['body'])
        self.assertEqual(response_data['calculated_fee'], 15.00)  # Null balance treated as 0
        self.assertEqual(response_data['balance'], 0.00)

if __name__ == '__main__':
    unittest.main()