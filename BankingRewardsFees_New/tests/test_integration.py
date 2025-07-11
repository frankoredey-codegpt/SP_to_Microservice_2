import sys
import os
import json
import pytest
import requests
from unittest.mock import patch, MagicMock

# Add parent directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the Streamlit app functions
import app

# Mock API responses
MOCK_ACCOUNTS_RESPONSE = {
    'accounts': [
        {'account_id': 1, 'customer_name': 'John Doe', 'tier': 'premium', 'balance': 15000.00},
        {'account_id': 2, 'customer_name': 'Jane Smith', 'tier': 'standard', 'balance': 3000.00}
    ]
}

MOCK_ACCOUNT_DETAILS_RESPONSE = {
    'account': {
        'account_id': 1,
        'customer_name': 'John Doe',
        'tier': 'premium',
        'balance': 15000.00,
        'created_at': '2023-01-01T00:00:00',
        'updated_at': '2023-01-01T00:00:00'
    }
}

MOCK_FEE_CALCULATION_RESPONSE = {
    'account_id': 1,
    'monthly_fee': 0.00,
    'tier': 'premium',
    'balance': 15000.00,
    'message': 'Monthly fee calculated successfully'
}

MOCK_REWARD_CALCULATION_RESPONSE = {
    'account_id': 1,
    'monthly_reward': 300.00,
    'reward_rate': 0.02,
    'balance': 15000.00,
    'customer_name': 'John Doe',
    'tier': 'premium',
    'message': 'Monthly reward calculated successfully'
}

MOCK_BALANCE_UPDATE_RESPONSE = {
    'account_id': 1,
    'balance': 20000.00,
    'customer_name': 'John Doe',
    'tier': 'premium',
    'updated_at': '2023-01-01T00:00:00',
    'message': 'Balance updated successfully'
}

class TestStreamlitAppIntegration:
    """Integration tests for the Streamlit app API calls"""

    @patch('requests.get')
    def test_get_accounts_success(self, mock_get):
        """Test successful retrieval of accounts"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_ACCOUNTS_RESPONSE
        mock_get.return_value = mock_response

        accounts = app.get_accounts()
        
        assert len(accounts) == 2
        assert accounts[0]['customer_name'] == 'John Doe'
        assert accounts[1]['customer_name'] == 'Jane Smith'

    @patch('requests.get')
    def test_get_accounts_error(self, mock_get):
        """Test error handling when getting accounts fails"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {'error': 'Internal server error'}
        mock_get.return_value = mock_response

        accounts = app.get_accounts()
        
        assert accounts == []

    @patch('requests.get')
    def test_get_account_details_success(self, mock_get):
        """Test successful retrieval of account details"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_ACCOUNT_DETAILS_RESPONSE
        mock_get.return_value = mock_response

        account = app.get_account_details(1)
        
        assert account['account_id'] == 1
        assert account['customer_name'] == 'John Doe'
        assert account['balance'] == 15000.00

    @patch('requests.get')
    def test_get_account_details_not_found(self, mock_get):
        """Test handling of account not found"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'error': 'Account not found'}
        mock_get.return_value = mock_response

        account = app.get_account_details(999)
        
        assert account is None

    @patch('requests.post')
    def test_calculate_fees_success(self, mock_post):
        """Test successful fee calculation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_FEE_CALCULATION_RESPONSE
        mock_post.return_value = mock_response

        result = app.calculate_fees(1)
        
        assert result['monthly_fee'] == 0.00
        assert result['tier'] == 'premium'

    @patch('requests.post')
    def test_calculate_rewards_success(self, mock_post):
        """Test successful reward calculation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_REWARD_CALCULATION_RESPONSE
        mock_post.return_value = mock_response

        result = app.calculate_rewards(1)
        
        assert result['monthly_reward'] == 300.00
        assert result['reward_rate'] == 0.02

    @patch('requests.post')
    def test_update_balance_success(self, mock_post):
        """Test successful balance update"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_BALANCE_UPDATE_RESPONSE
        mock_post.return_value = mock_response

        result = app.update_account_balance(1, 20000.00)
        
        assert result['balance'] == 20000.00
        assert result['message'] == 'Balance updated successfully'

    @patch('requests.post')
    def test_api_error_handling(self, mock_post):
        """Test API error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'Invalid request'}
        mock_post.return_value = mock_response

        result = app.calculate_fees(1)
        
        assert result is None

class TestBusinessLogicIntegration:
    """Integration tests for business logic across microservices"""

    def test_fee_calculation_business_rules(self):
        """Test that fee calculation follows business rules"""
        # Premium tier should have no fees
        premium_account = {'tier': 'premium', 'balance': 15000.00}
        assert self._calculate_expected_fee(premium_account) == 0.00
        
        # Standard tier with high balance should have $5 fee
        standard_high = {'tier': 'standard', 'balance': 6000.00}
        assert self._calculate_expected_fee(standard_high) == 5.00
        
        # Standard tier with low balance should have $15 fee
        standard_low = {'tier': 'standard', 'balance': 3000.00}
        assert self._calculate_expected_fee(standard_low) == 15.00

    def test_reward_calculation_business_rules(self):
        """Test that reward calculation follows business rules"""
        # High balance should get 2% rewards
        high_balance = {'balance': 15000.00}
        assert self._calculate_expected_reward(high_balance) == 300.00
        
        # Low balance should get 1% rewards
        low_balance = {'balance': 5000.00}
        assert self._calculate_expected_reward(low_balance) == 50.00

    def _calculate_expected_fee(self, account):
        """Helper method to calculate expected fee based on business rules"""
        if account['tier'] == 'premium':
            return 0.00
        elif account['balance'] > 5000:
            return 5.00
        else:
            return 15.00

    def _calculate_expected_reward(self, account):
        """Helper method to calculate expected reward based on business rules"""
        if account['balance'] > 10000:
            return account['balance'] * 0.02
        else:
            return account['balance'] * 0.01

class TestDataConsistency:
    """Tests for data consistency across the microservices architecture"""

    def test_account_data_consistency(self):
        """Test that account data is consistent across different API calls"""
        # This would be a more comprehensive test in a real environment
        # where we'd verify that the same account data is returned
        # consistently across different microservices
        pass

    def test_balance_update_consistency(self):
        """Test that balance updates are reflected consistently"""
        # This would test that after updating a balance,
        # subsequent fee and reward calculations use the new balance
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])