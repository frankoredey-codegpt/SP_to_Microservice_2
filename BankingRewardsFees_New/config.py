"""
Configuration file for the Banking Rewards & Fees Streamlit application.
Update the API_BASE_URL with your actual AWS API Gateway URL after deployment.
"""

import os

# AWS Lambda API URLs
ACCOUNT_SERVICE_URL = "https://ule48xqcya.execute-api.us-west-2.amazonaws.com/default/Account_Service"
FEE_CALCULATION_URL = "https://hsa8bd8loc.execute-api.us-west-2.amazonaws.com/default/Fee_Calculation_Service"
REWARDS_CALCULATION_URL = "https://1gqnjvxjdl.execute-api.us-west-2.amazonaws.com/default/Rewards_Calculation_Service"

# Lambda Function Endpoints
ENDPOINTS = {
    'get_accounts': ACCOUNT_SERVICE_URL,
    'get_account': ACCOUNT_SERVICE_URL,  # Will append ?account_id=X
    'update_balance': ACCOUNT_SERVICE_URL,  # For balance updates
    'calculate_fees': FEE_CALCULATION_URL,
    'calculate_rewards': REWARDS_CALCULATION_URL
}

# Request timeout settings
REQUEST_TIMEOUT = 30  # seconds

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# UI Configuration
APP_TITLE = "Banking Rewards & Fees Demo (Modern Lambda Version)"
PAGE_ICON = "🏦"
LAYOUT = "wide"

# Feature flags
ENABLE_DEBUG_MODE = os.environ.get('DEBUG', 'False').lower() == 'true'
ENABLE_CACHING = os.environ.get('ENABLE_CACHING', 'True').lower() == 'true'