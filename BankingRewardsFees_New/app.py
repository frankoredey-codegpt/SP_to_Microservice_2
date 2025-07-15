import streamlit as st
import requests
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('aws_lambda_api.env')

# AWS Lambda API URLs
ACCOUNT_SERVICE_URL = os.getenv('ACCOUNT_SERVICE_URL', 'https://ule48xqcya.execute-api.us-west-2.amazonaws.com/default/Account_Service')
FEE_CALCULATION_URL = os.getenv('FEE_CALCULATION_URL', 'https://hsa8bd8loc.execute-api.us-west-2.amazonaws.com/default/Fee_Calculation_Service')
REWARDS_CALCULATION_URL = os.getenv('REWARDS_CALCULATION_URL', 'https://1gqnjvxjdl.execute-api.us-west-2.amazonaws.com/default/Rewards_Calculation_Service')

# ---- Mock Data for Testing ----
def get_mock_accounts():
    """Mock data for testing when Lambda services are not available"""
    return [
        {
            "account_id": 1,
            "balance": 1500.00,
            "customer_name": "Alice Johnson",
            "customer_tier": "standard"
        },
        {
            "account_id": 2,
            "balance": 15000.00,
            "customer_name": "Bob Smith",
            "customer_tier": "premium"
        },
        {
            "account_id": 3,
            "balance": 7500.00,
            "customer_name": "Carol Davis",
            "customer_tier": "standard"
        }
    ]

def get_mock_account_details(account_id):
    """Mock account details for testing"""
    mock_accounts = {
        1: {
            "account_id": 1,
            "balance": 1500.00,
            "customer_id": 1,
            "customer_name": "Alice Johnson",
            "customer_tier": "standard",
            "created_at": "2023-01-01 10:00:00",
            "updated_at": "2023-12-01 15:30:00"
        },
        2: {
            "account_id": 2,
            "balance": 15000.00,
            "customer_id": 2,
            "customer_name": "Bob Smith",
            "customer_tier": "premium",
            "created_at": "2023-02-15 09:00:00",
            "updated_at": "2023-12-01 14:20:00"
        },
        3: {
            "account_id": 3,
            "balance": 7500.00,
            "customer_id": 3,
            "customer_name": "Carol Davis",
            "customer_tier": "standard",
            "created_at": "2023-03-20 11:00:00",
            "updated_at": "2023-12-01 16:45:00"
        }
    }
    return mock_accounts.get(account_id)

def calculate_mock_fees(account_id):
    """Mock fee calculation for testing"""
    account = get_mock_account_details(account_id)
    if not account:
        return None
    
    customer_tier = account['customer_tier']
    balance = account['balance']
    
    if customer_tier == 'premium':
        fee = 0.00
    elif balance > 5000:
        fee = 5.00
    else:
        fee = 15.00
    
    return {
        'account_id': account_id,
        'customer_tier': customer_tier,
        'balance': balance,
        'calculated_fee': fee,
        'calculation_timestamp': 'mock_calculation'
    }

def calculate_mock_rewards(account_id):
    """Mock rewards calculation for testing"""
    account = get_mock_account_details(account_id)
    if not account:
        return None
    
    balance = account['balance']
    
    if balance > 10000:
        reward_rate = 0.02
    else:
        reward_rate = 0.01
    
    calculated_reward = balance * reward_rate
    
    return {
        'account_id': account_id,
        'balance': balance,
        'reward_rate': reward_rate,
        'calculated_reward': round(calculated_reward, 2),
        'calculation_timestamp': 'mock_calculation'
    }

# ---- API Helper Functions ----
def get_accounts():
    """Get all accounts from Account Service Lambda"""
    try:
        response = requests.get(ACCOUNT_SERVICE_URL, timeout=10)
        if response.status_code == 200:
            accounts_data = response.json()
            # Validate data structure
            if isinstance(accounts_data, list) and len(accounts_data) > 0:
                # Check if first account has required fields
                if 'customer_name' in accounts_data[0] and 'account_id' in accounts_data[0]:
                    return accounts_data
            st.warning("Invalid data structure from Account Service. Using mock data.")
            return get_mock_accounts()
        else:
            st.error(f"Failed to fetch accounts: {response.status_code}. Using mock data.")
            return get_mock_accounts()
    except requests.exceptions.RequestException as e:
        st.warning(f"Cannot connect to Account Service: {str(e)}")
        st.info("Using mock data for demonstration purposes")
        return get_mock_accounts()
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return get_mock_accounts()

def get_account_details(account_id):
    """Get specific account details from Account Service Lambda"""
    try:
        response = requests.get(f"{ACCOUNT_SERVICE_URL}/{account_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"Failed to fetch account details: {response.status_code}. Using mock data.")
            return get_mock_account_details(account_id)
    except requests.exceptions.RequestException as e:
        st.warning(f"Cannot connect to Account Service: {str(e)}")
        return get_mock_account_details(account_id)
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return get_mock_account_details(account_id)

def update_account_balance(account_id, new_balance):
    """Update account balance via Account Service Lambda"""
    try:
        payload = {"balance": new_balance}
        response = requests.put(
            f"{ACCOUNT_SERVICE_URL}/{account_id}",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if response.status_code == 200:
            return True
        else:
            st.error(f"Failed to update balance: {response.status_code}")
            st.info("Balance update would work with deployed Lambda functions")
            return False
    except requests.exceptions.RequestException as e:
        st.warning(f"Cannot connect to Account Service: {str(e)}")
        st.info("Balance update would work with deployed Lambda functions")
        return False
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return False

def calculate_fees(account_id):
    """Calculate fees via Fee Calculation Service Lambda"""
    try:
        payload = {"account_id": account_id}
        response = requests.post(
            f"{FEE_CALCULATION_URL}/{account_id}",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"Failed to calculate fees: {response.status_code}. Using mock calculation.")
            return calculate_mock_fees(account_id)
    except requests.exceptions.RequestException as e:
        st.warning(f"Cannot connect to Fee Calculation Service: {str(e)}")
        st.info("Using mock calculation for demonstration")
        return calculate_mock_fees(account_id)
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return calculate_mock_fees(account_id)

def calculate_rewards(account_id):
    """Calculate rewards via Rewards Calculation Service Lambda"""
    try:
        payload = {"account_id": account_id}
        response = requests.post(
            f"{REWARDS_CALCULATION_URL}/{account_id}",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"Failed to calculate rewards: {response.status_code}. Using mock calculation.")
            return calculate_mock_rewards(account_id)
    except requests.exceptions.RequestException as e:
        st.warning(f"Cannot connect to Rewards Calculation Service: {str(e)}")
        st.info("Using mock calculation for demonstration")
        return calculate_mock_rewards(account_id)
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return calculate_mock_rewards(account_id)

# ---- Streamlit UI ----
st.title("Banking Rewards & Fees Demo (Microservices Version)")
st.markdown("*Powered by AWS Lambda Microservices*")

# Show connection status
with st.expander("🔧 System Status", expanded=False):
    st.write("**Lambda Service URLs:**")
    st.code(f"Account Service: {ACCOUNT_SERVICE_URL}")
    st.code(f"Fee Calculation: {FEE_CALCULATION_URL}")
    st.code(f"Rewards Calculation: {REWARDS_CALCULATION_URL}")
    st.info("If Lambda services are not deployed, the app will use mock data for demonstration.")

# Initialize session state for calculations
if 'fee_result' not in st.session_state:
    st.session_state.fee_result = None
if 'rewards_result' not in st.session_state:
    st.session_state.rewards_result = None

# Get accounts
accounts = get_accounts()
if not accounts:
    st.error("Unable to load accounts. Please check the Account Service or deploy Lambda functions.")
    st.stop()

# Create account selection dropdown
try:
    account_options = {f"{a['customer_name']} (ID: {a['account_id']})": a['account_id'] for a in accounts}
except KeyError as e:
    st.error(f"Data structure error: Missing field {e}")
    st.write("Available account data:", accounts)
    st.stop()

selected_account_label = st.selectbox("Select an Account", options=list(account_options.keys()))
selected_account_id = account_options[selected_account_label]

# Action buttons in columns
col1, col2 = st.columns(2)

with col1:
    if st.button("Calculate Fees", type="primary"):
        with st.spinner("Calculating fees..."):
            fee_result = calculate_fees(selected_account_id)
            if fee_result:
                st.session_state.fee_result = fee_result
                st.success("Fees calculated successfully!")

with col2:
    if st.button("Calculate Rewards", type="primary"):
        with st.spinner("Calculating rewards..."):
            rewards_result = calculate_rewards(selected_account_id)
            if rewards_result:
                st.session_state.rewards_result = rewards_result
                st.success("Rewards calculated successfully!")

# Display calculation results
if st.session_state.fee_result:
    st.subheader("Fee Calculation Result")
    fee_data = st.session_state.fee_result
    st.info(f"**Monthly Fee:** ${fee_data['calculated_fee']:.2f}")
    st.caption(f"Based on: {fee_data['customer_tier']} tier, Balance: ${fee_data['balance']:.2f}")

if st.session_state.rewards_result:
    st.subheader("Rewards Calculation Result")
    rewards_data = st.session_state.rewards_result
    st.info(f"**Monthly Rewards:** ${rewards_data['calculated_reward']:.2f}")
    st.caption(f"Based on: {rewards_data['reward_rate']*100:.0f}% rate, Balance: ${rewards_data['balance']:.2f}")

# Account details and balance management
st.subheader("Account Management")
account_details = get_account_details(selected_account_id)

if account_details:
    # Balance management
    current_balance = float(account_details.get('balance', 0.0))
    new_balance = st.number_input(
        "Account Balance", 
        value=current_balance, 
        format="%.2f",
        help="Update the account balance"
    )
    
    if st.button("Save Balance", type="secondary"):
        if update_account_balance(selected_account_id, new_balance):
            st.success(f"Balance updated to ${new_balance:.2f}!")
            # Clear calculation results since balance changed
            st.session_state.fee_result = None
            st.session_state.rewards_result = None
            st.rerun()
    
    # Display account details
    st.subheader("Account Details")
    
    # Create a clean display of account information
    account_info = {
        "Account ID": account_details['account_id'],
        "Customer Name": account_details['customer_name'],
        "Customer Tier": account_details['customer_tier'].title(),
        "Current Balance": f"${account_details['balance']:.2f}",
        "Created": account_details.get('created_at', 'N/A'),
        "Last Updated": account_details.get('updated_at', 'N/A')
    }
    
    # Display as a nice table
    info_df = pd.DataFrame(list(account_info.items()), columns=['Field', 'Value'])
    st.table(info_df)
    
else:
    st.error("Unable to load account details.")

# Footer
st.markdown("---")
st.markdown("**Architecture:** Streamlit Frontend + AWS Lambda Microservices + MySQL Database")
st.markdown("**Services:** Account Service | Fee Calculation Service | Rewards Calculation Service")
st.markdown("**Note:** This app includes mock data fallback for testing when Lambda services are not deployed.")