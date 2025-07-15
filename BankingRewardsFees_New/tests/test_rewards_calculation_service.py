import unittest
from unittest.mock import Mock, patch
import json
import sys
import os

# Add the lambda_functions directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda_functions'))

from rewards_calculation_service import lambda_handler

class TestRewardsCalculationService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_context = Mock()
        self.mock_context.aws_request_id = 'test-request-id'
    
    @patch('rewards_calculation_service.mysql.connector.connect')
    def test_calculate_rewards_high_balance(self, mock_connect):
        """Test rewards calculation for balance > $10,000 (should be 2%)."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data with high balance
        mock_cursor.fetchone.return_value = {
            'account_id': 1,
            'balance': 15000.00
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
        self.assertEqual(response_data['calculated_reward'], 300.00)  # 15000 * 0.02
        self.assertEqual(response_data['reward_rate'], 0.02)
        self.assertEqual(response_data['balance'], 15000.00)
        
        # Verify database calls
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('rewards_calculation_service.mysql.connector.connect')
    def test_calculate_rewards_low_balance(self, mock_connect):
        """Test rewards calculation for balance ≤ $10,000 (should be 1%)."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data with low balance
        mock_cursor.fetchone.return_value = {
            'account_id': 2,
            'balance': 5000.00
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
        self.assertEqual(response_data['calculated_reward'], 50.00)  # 5000 * 0.01
        self.assertEqual(response_data['reward_rate'], 0.01)
        self.assertEqual(response_data['balance'], 5000.00)
    
    @patch('rewards_calculation_service.mysql.connector.connect')
    def test_calculate_rewards_boundary_balance_10000(self, mock_connect):
        """Test rewards calculation for exactly $10,000 balance (should be 1%)."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data with exactly $10,000
        mock_cursor.fetchone.return_value = {
            'account_id': 3,
            'balance': 10000.00
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
        self.assertEqual(response_data['calculated_reward'], 100.00)  # 10000 * 0.01
        self.assertEqual(response_data['reward_rate'], 0.01)
        self.assertEqual(response_data['balance'], 10000.00)
    
    @patch('rewards_calculation_service.mysql.connector.connect')
    def test_calculate_rewards_boundary_balance_10001(self, mock_connect):
        """Test rewards calculation for $10,001 balance (should be 2%)."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data with $10,001
        mock_cursor.fetchone.return_value = {
            'account_id': 4,
            'balance': 10001.00
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
        self.assertEqual(response_data['calculated_reward'], 200.02)  # 10001 * 0.02
        self.assertEqual(response_data['reward_rate'], 0.02)
        self.assertEqual(response_data['balance'], 10001.00)
    
    @patch('rewards_calculation_service.mysql.connector.connect')
    def test_calculate_rewards_zero_balance(self, mock_connect):
        """Test rewards calculation for zero balance."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data with zero balance
        mock_cursor.fetchone.return_value = {
            'account_id': 5,
            'balance': 0.00
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
        self.assertEqual(response_data['calculated_reward'], 0.00)  # 0 * 0.01
        self.assertEqual(response_data['reward_rate'], 0.01)
        self.assertEqual(response_data['balance'], 0.00)
    
    @patch('rewards_calculation_service.mysql.connector.connect')
    def test_calculate_rewards_decimal_precision(self, mock_connect):
        """Test rewards calculation with decimal precision."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data with balance that results in decimal rewards
        mock_cursor.fetchone.return_value = {
            'account_id': 6,
            'balance': 1234.56
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
        self.assertEqual(response_data['calculated_reward'], 12.35)  # 1234.56 * 0.01, rounded to 2 decimal places
        self.assertEqual(response_data['reward_rate'], 0.01)
        self.assertEqual(response_data['balance'], 1234.56)
    
    @patch('rewards_calculation_service.mysql.connector.connect')
    def test_calculate_rewards_large_balance(self, mock_connect):
        """Test rewards calculation for very large balance."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data with large balance
        mock_cursor.fetchone.return_value = {
            'account_id': 7,
            'balance': 100000.00
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
        self.assertEqual(response_data['calculated_reward'], 2000.00)  # 100000 * 0.02
        self.assertEqual(response_data['reward_rate'], 0.02)
        self.assertEqual(response_data['balance'], 100000.00)
    
    @patch('rewards_calculation_service.mysql.connector.connect')
    def test_calculate_rewards_account_not_found(self, mock_connect):
        """Test rewards calculation for non-existent account."""
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
    
    def test_calculate_rewards_missing_account_id(self):
        """Test rewards calculation with missing account ID."""
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
    
    @patch('rewards_calculation_service.mysql.connector.connect')
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
    
    @patch('rewards_calculation_service.mysql.connector.connect')
    def test_calculate_rewards_null_balance(self, mock_connect):
        """Test rewards calculation with null balance."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock account data with null balance
        mock_cursor.fetchone.return_value = {
            'account_id': 8,
            'balance': None
        }
        
        # Create test event
        event = {
            'httpMethod': 'POST',
            'pathParameters': {'account_id': '8'},
            'queryStringParameters': None,
            'body': json.dumps({'account_id': 8})
        }
        
        # Call the lambda handler
        response = lambda_handler(event, self.mock_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        response_data = json.loads(response['body'])
        self.assertEqual(response_data['calculated_reward'], 0.00)  # Null balance treated as 0
        self.assertEqual(response_data['balance'], 0.00)

if __name__ == '__main__':
    unittest.main()