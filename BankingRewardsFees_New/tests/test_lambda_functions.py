import sys
import os
import json
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add lambda_functions directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda_functions'))

# Import lambda functions
from calculate_fees_lambda import lambda_handler as fees_handler
from calculate_rewards_lambda import lambda_handler as rewards_handler
from update_balance_lambda import lambda_handler as balance_handler
from get_accounts_lambda import lambda_handler as accounts_handler

# Mock database connection and cursor
class MockCursor:
    def __init__(self, fetch_results=None):
        self.fetch_results = fetch_results or []
        self.executed_queries = []
        self.executed_args = []

    def execute(self, query, args=None):
        self.executed_queries.append(query)
        self.executed_args.append(args)

    def fetchone(self):
        return self.fetch_results[0] if self.fetch_results else None

    def fetchall(self):
        return self.fetch_results

    def close(self):
        pass

class MockConnection:
    def __init__(self, cursor):
        self.cursor = cursor

    def cursor(self, dictionary=True):
        return self.cursor

    def commit(self):
        pass

    def close(self):
        pass

# Test data
MOCK_ACCOUNT_PREMIUM = {
    'account_id': 1,
    'balance': Decimal('15000.00'),
    'tier': 'premium',
    'name': 'John Doe',
    'created_at': datetime.now(),
    'updated_at': datetime.now()
}

MOCK_ACCOUNT_STANDARD = {
    'account_id': 2,
    'balance': Decimal('3000.00'),
    'tier': 'standard',
    'name': 'Jane Smith',
    'created_at': datetime.now(),
    'updated_at': datetime.now()
}

# Test Calculate Fees Lambda
@pytest.mark.parametrize("account,expected_fee", [
    (MOCK_ACCOUNT_PREMIUM, 0.00),  # Premium tier: no fee
    (MOCK_ACCOUNT_STANDARD, 15.00),  # Standard tier, low balance: $15 fee
])
def test_calculate_fees(account, expected_fee):
    mock_cursor = MockCursor([account])
    mock_conn = MockConnection(mock_cursor)

    with patch('mysql.connector.connect', return_value=mock_conn):
        event = {'body': json.dumps({'account_id': account['account_id']})}
        response = fees_handler(event, {})
        
        assert response['statusCode'] == 200
        response_body = json.loads(response['body'])
        assert response_body['monthly_fee'] == expected_fee
        assert response_body['tier'] == account['tier']

# Test Calculate Rewards Lambda
@pytest.mark.parametrize("account,expected_rate", [
    (MOCK_ACCOUNT_PREMIUM, 0.02),  # Balance > 10000: 2% rate
    (MOCK_ACCOUNT_STANDARD, 0.01),  # Balance <= 10000: 1% rate
])
def test_calculate_rewards(account, expected_rate):
    mock_cursor = MockCursor([account])
    mock_conn = MockConnection(mock_cursor)

    with patch('mysql.connector.connect', return_value=mock_conn):
        event = {'body': json.dumps({'account_id': account['account_id']})}
        response = rewards_handler(event, {})
        
        assert response['statusCode'] == 200
        response_body = json.loads(response['body'])
        assert response_body['reward_rate'] == expected_rate
        assert response_body['monthly_reward'] == float(account['balance']) * expected_rate

# Test Update Balance Lambda
def test_update_balance():
    initial_account = dict(MOCK_ACCOUNT_PREMIUM)
    updated_account = dict(MOCK_ACCOUNT_PREMIUM)
    new_balance = 20000.00
    updated_account['balance'] = Decimal(str(new_balance))
    
    mock_cursor = MockCursor([initial_account, updated_account])
    mock_conn = MockConnection(mock_cursor)

    with patch('mysql.connector.connect', return_value=mock_conn):
        event = {
            'body': json.dumps({
                'account_id': initial_account['account_id'],
                'new_balance': new_balance
            })
        }
        response = balance_handler(event, {})
        
        assert response['statusCode'] == 200
        response_body = json.loads(response['body'])
        assert response_body['balance'] == new_balance

# Test Get Accounts Lambda
def test_get_all_accounts():
    mock_accounts = [MOCK_ACCOUNT_PREMIUM, MOCK_ACCOUNT_STANDARD]
    mock_cursor = MockCursor(mock_accounts)
    mock_conn = MockConnection(mock_cursor)

    with patch('mysql.connector.connect', return_value=mock_conn):
        event = {}
        response = accounts_handler(event, {})
        
        assert response['statusCode'] == 200
        response_body = json.loads(response['body'])
        assert len(response_body['accounts']) == len(mock_accounts)

def test_get_specific_account():
    mock_cursor = MockCursor([MOCK_ACCOUNT_PREMIUM])
    mock_conn = MockConnection(mock_cursor)

    with patch('mysql.connector.connect', return_value=mock_conn):
        event = {'queryStringParameters': {'account_id': '1'}}
        response = accounts_handler(event, {})
        
        assert response['statusCode'] == 200
        response_body = json.loads(response['body'])
        assert response_body['account']['account_id'] == MOCK_ACCOUNT_PREMIUM['account_id']

# Test Error Handling
def test_invalid_account_id():
    mock_cursor = MockCursor([])  # No results
    mock_conn = MockConnection(mock_cursor)

    with patch('mysql.connector.connect', return_value=mock_conn):
        event = {'queryStringParameters': {'account_id': '999'}}
        response = accounts_handler(event, {})
        
        assert response['statusCode'] == 404
        response_body = json.loads(response['body'])
        assert 'error' in response_body

def test_invalid_balance_update():
    event = {
        'body': json.dumps({
            'account_id': 1,
            'new_balance': -100  # Negative balance should be rejected
        })
    }
    response = balance_handler(event, {})
    
    assert response['statusCode'] == 400
    response_body = json.loads(response['body'])
    assert 'error' in response_body

def test_missing_required_parameters():
    event = {'body': json.dumps({})}  # Missing account_id
    
    response = fees_handler(event, {})
    assert response['statusCode'] == 400
    
    response = rewards_handler(event, {})
    assert response['statusCode'] == 400
    
    response = balance_handler(event, {})
    assert response['statusCode'] == 400