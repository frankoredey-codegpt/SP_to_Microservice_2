#!/usr/bin/env python3
"""
Debug script to test Lambda API endpoints
"""

import requests
import json

# API URLs
ACCOUNT_SERVICE_URL = "https://ule48xqcya.execute-api.us-west-2.amazonaws.com/default/Account_Service"
FEE_CALCULATION_URL = "https://hsa8bd8loc.execute-api.us-west-2.amazonaws.com/default/Fee_Calculation_Service"
REWARDS_CALCULATION_URL = "https://1gqnjvxjdl.execute-api.us-west-2.amazonaws.com/default/Rewards_Calculation_Service"

def test_account_service():
    """Test Account Service endpoints"""
    print("=" * 60)
    print("TESTING ACCOUNT SERVICE")
    print("=" * 60)
    
    # Test GET all accounts
    print("\n1. Testing GET all accounts:")
    print(f"URL: {ACCOUNT_SERVICE_URL}")
    try:
        response = requests.get(ACCOUNT_SERVICE_URL, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data: {json.dumps(data, indent=2)}")
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")
    
    # Test GET specific account
    print("\n2. Testing GET specific account (ID: 1):")
    print(f"URL: {ACCOUNT_SERVICE_URL}/1")
    try:
        response = requests.get(f"{ACCOUNT_SERVICE_URL}/1", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data: {json.dumps(data, indent=2)}")
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")

def test_fee_calculation_service():
    """Test Fee Calculation Service"""
    print("\n" + "=" * 60)
    print("TESTING FEE CALCULATION SERVICE")
    print("=" * 60)
    
    print("\n1. Testing POST fee calculation (ID: 1):")
    print(f"URL: {FEE_CALCULATION_URL}/1")
    try:
        payload = {"account_id": 1}
        response = requests.post(
            f"{FEE_CALCULATION_URL}/1",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data: {json.dumps(data, indent=2)}")
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")

def test_rewards_calculation_service():
    """Test Rewards Calculation Service"""
    print("\n" + "=" * 60)
    print("TESTING REWARDS CALCULATION SERVICE")
    print("=" * 60)
    
    print("\n1. Testing POST rewards calculation (ID: 1):")
    print(f"URL: {REWARDS_CALCULATION_URL}/1")
    try:
        payload = {"account_id": 1}
        response = requests.post(
            f"{REWARDS_CALCULATION_URL}/1",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data: {json.dumps(data, indent=2)}")
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")

def test_api_gateway_options():
    """Test API Gateway CORS and OPTIONS"""
    print("\n" + "=" * 60)
    print("TESTING API GATEWAY CORS")
    print("=" * 60)
    
    for service_name, url in [
        ("Account Service", ACCOUNT_SERVICE_URL),
        ("Fee Calculation", FEE_CALCULATION_URL),
        ("Rewards Calculation", REWARDS_CALCULATION_URL)
    ]:
        print(f"\nTesting OPTIONS for {service_name}:")
        try:
            response = requests.options(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"CORS Headers: {dict(response.headers)}")
        except Exception as e:
            print(f"Exception: {str(e)}")

if __name__ == "__main__":
    print("LAMBDA API DEBUGGING TOOL")
    print("=" * 60)
    
    test_account_service()
    test_fee_calculation_service()
    test_rewards_calculation_service()
    test_api_gateway_options()
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)