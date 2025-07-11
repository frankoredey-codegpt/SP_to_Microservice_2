import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
from config import ENDPOINTS, APP_TITLE, PAGE_ICON, LAYOUT

# API endpoints are now imported from config.py

# ---- API Calls ----
def get_accounts():
    """Get list of all accounts"""
    try:
        response = requests.get(ENDPOINTS['get_accounts'])
        if response.status_code == 200:
            data = response.json()
            # Handle both direct array and wrapped object formats
            if isinstance(data, dict) and 'accounts' in data:
                return data['accounts']
            elif isinstance(data, list):
                return data
            else:
                st.error(f"Unexpected response format: {data}")
                return []
        else:
            error_msg = "Unknown error"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', error_msg)
            except:
                error_msg = response.text
            st.error(f"Error fetching accounts: {error_msg}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def get_account_details(account_id):
    """Get details for a specific account"""
    try:
        response = requests.get(ENDPOINTS['get_account'].format(account_id=account_id))
        if response.status_code == 200:
            data = response.json()
            # Handle different response formats
            if isinstance(data, dict) and 'account' in data:
                return data['account']
            elif isinstance(data, dict) and 'account_id' in data:
                return data
            elif isinstance(data, dict) and 'accounts' in data:
                # API is returning all accounts, find the specific one
                accounts = data['accounts']
                account = next((acc for acc in accounts if acc['account_id'] == account_id), None)
                if account:
                    # Add updated_at field if missing
                    if 'updated_at' not in account:
                        account['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    return account
                else:
                    st.error(f"Account {account_id} not found in response")
                    return None
            else:
                st.error(f"Unexpected account response format: {data}")
                return None
        else:
            error_msg = "Unknown error"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', error_msg)
            except:
                error_msg = response.text
            st.error(f"Error fetching account details: {error_msg}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def update_account_balance(account_id, new_balance):
    """Update account balance via Lambda function"""
    try:
        response = requests.post(
            ENDPOINTS['update_balance'],
            json={'account_id': account_id, 'new_balance': new_balance}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error updating balance: {response.json().get('error', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def calculate_fees(account_id):
    """Calculate fees via Lambda function"""
    try:
        response = requests.post(
            ENDPOINTS['calculate_fees'],
            json={'account_id': account_id}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error calculating fees: {response.json().get('error', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def calculate_rewards(account_id):
    """Calculate rewards via Lambda function"""
    try:
        response = requests.post(
            ENDPOINTS['calculate_rewards'],
            json={'account_id': account_id}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error calculating rewards: {response.json().get('error', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

# ---- Streamlit UI ----
st.title(APP_TITLE)

# Get and display accounts
accounts = get_accounts()
account_options = {f"{a['customer_name']} (ID: {a['account_id']})": a['account_id'] for a in accounts}

if account_options:
    selected_account_label = st.selectbox("Select an Account", options=list(account_options.keys()))
    selected_account_id = account_options[selected_account_label]

    # Create columns for action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Calculate Fees"):
            fee_result = calculate_fees(selected_account_id)
            if fee_result:
                st.success(f"Monthly Fee: ${fee_result['monthly_fee']:.2f}")
                st.info(f"Based on: Tier={fee_result['tier']}, Balance=${fee_result['balance']:,.2f}")

    with col2:
        if st.button("Calculate Rewards"):
            reward_result = calculate_rewards(selected_account_id)
            if reward_result:
                st.success(f"Monthly Reward: ${reward_result['monthly_reward']:.2f}")
                st.info(f"Rate: {reward_result['reward_rate']*100}% (Balance=${reward_result['balance']:,.2f})")

    # Display and edit account details
    account_details = get_account_details(selected_account_id)
    if account_details:
        st.subheader("Account Details")
        
        # Make balance editable
        current_balance = float(account_details.get('balance', 0.0))
        new_balance = st.number_input("Balance", value=current_balance, format="%.2f")
        
        if st.button("Save Balance"):
            update_result = update_account_balance(selected_account_id, new_balance)
            if update_result:
                st.success(f"Balance updated to ${new_balance:,.2f}!")
                # Refresh account details
                account_details = get_account_details(selected_account_id)
        
        # Display other account details
        details_df = pd.DataFrame([{
            'Customer Name': account_details['customer_name'],
            'Customer Tier': account_details['tier'],
            'Last Updated': account_details['updated_at']
        }])
        st.write(details_df)
else:
    st.warning("No accounts found in the system.")