#!/usr/bin/env python3
"""
Simple test script to debug API responses from Lambda functions
"""

import requests
import json
from config import ACCOUNT_SERVICE_URL, FEE_CALCULATION_URL, REWARDS_CALCULATION_URL

def test_account_service():
    """Test the Account Service API"""
    print("=" * 50)
    print("Testing Account Service")
    print(f"URL: {ACCOUNT_SERVICE_URL}")
    print("=" * 50)
    
    # Test get_accounts action
    print("\n--- Testing get_accounts action ---")
    try:
        response = requests.post(
            ACCOUNT_SERVICE_URL, 
            json={'action': 'get_accounts'},
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"JSON Response: {json.dumps(json_data, indent=2)}")
            except json.JSONDecodeError:
                print("Response is not valid JSON")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test get_account_details action
    print("\n--- Testing get_account_details action ---")
    try:
        response = requests.post(
            ACCOUNT_SERVICE_URL, 
            json={'action': 'get_account_details', 'account_id': 1},
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"JSON Response: {json.dumps(json_data, indent=2)}")
            except json.JSONDecodeError:
                print("Response is not valid JSON")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def test_fee_calculation():
    """Test the Fee Calculation Service"""
    print("\n" + "=" * 50)
    print("Testing Fee Calculation Service")
    print(f"URL: {FEE_CALCULATION_URL}")
    print("=" * 50)
    
    try:
        # Test POST request with account_id
        test_payload = {"account_id": 1}
        response = requests.post(
            FEE_CALCULATION_URL, 
            json=test_payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"JSON Response: {json.dumps(json_data, indent=2)}")
            except json.JSONDecodeError:
                print("Response is not valid JSON")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def test_rewards_calculation():
    """Test the Rewards Calculation Service"""
    print("\n" + "=" * 50)
    print("Testing Rewards Calculation Service")
    print(f"URL: {REWARDS_CALCULATION_URL}")
    print("=" * 50)
    
    try:
        # Test POST request with account_id
        test_payload = {"account_id": 1}
        response = requests.post(
            REWARDS_CALCULATION_URL, 
            json=test_payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"JSON Response: {json.dumps(json_data, indent=2)}")
            except json.JSONDecodeError:
                print("Response is not valid JSON")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Lambda API Testing Script")
    print("This will help debug the API response formats")
    
    test_account_service()
    test_fee_calculation()
    test_rewards_calculation()
    
    print("\n" + "=" * 50)
    print("Testing Complete")
    print("=" * 50)