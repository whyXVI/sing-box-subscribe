#!/usr/bin/env python3
"""
Client example showing how to send encrypted subscription requests
"""
from crypto_helper import encrypt_url_with_seed
from urllib.parse import urlencode
import requests

def send_encrypted_subscription_request(server_url, subscription_url, params, seed):
    """
    Send an encrypted subscription request to the server
    
    Args:
        server_url: The server endpoint (e.g., "http://localhost:5000")
        subscription_url: The actual subscription URL to encrypt
        params: Dictionary of parameters (emoji, file, tag, etc.)
        seed: The encryption seed
    """
    # Encrypt the subscription URL and parameters
    encrypted_url, encrypted_params = encrypt_url_with_seed(subscription_url, params, seed)
    
    # Add seed to the parameters
    encrypted_params['seed'] = seed
    
    # Build the full request URL
    query_string = urlencode(encrypted_params)
    full_url = f"{server_url}/config/{encrypted_url}?{query_string}"
    
    print(f"Sending encrypted request to: {full_url}")
    
    # Send the request
    try:
        response = requests.get(full_url, timeout=30)
        if response.status_code == 200:
            print("Success! Config received.")
            return response.text
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Server configuration
    SERVER_URL = "http://localhost:5000"
    
    # Your subscription details
    SUBSCRIPTION_URL = "https://my-subscription-provider.com/api/subscribe?token=mytoken123"
    
    # Parameters
    PARAMS = {
        'emoji': '1',
        'file': '2',  # Use template #2
        'tag': 'MyProxy',
        'prefix': '🚀'
    }
    
    # Shared seed (both client and server must use the same seed)
    SEED = "shared-secret-seed-2024"
    
    print("=== Encrypted Subscription Request Example ===")
    print(f"Original URL: {SUBSCRIPTION_URL}")
    print(f"Parameters: {PARAMS}")
    print(f"Seed: {SEED}")
    print("")
    
    # Send the encrypted request
    config = send_encrypted_subscription_request(
        SERVER_URL,
        SUBSCRIPTION_URL,
        PARAMS,
        SEED
    )
    
    if config:
        print("\nReceived config (first 200 chars):")
        print(config[:200] + "...")