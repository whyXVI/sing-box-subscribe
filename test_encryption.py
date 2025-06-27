#!/usr/bin/env python3
from crypto_helper import SeedCrypto, encrypt_url_with_seed, decrypt_request_with_seed
from urllib.parse import urlencode, quote

# Test basic encryption/decryption
def test_basic_crypto():
    print("=== Basic Crypto Test ===")
    seed = "my-secret-seed-12345"
    crypto = SeedCrypto(seed)
    
    # Test string
    original = "https://example.com/subscription/link"
    encrypted = crypto.encrypt(original)
    decrypted = crypto.decrypt(encrypted)
    
    print(f"Original: {original}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {original == decrypted}\n")

# Test URL and params encryption
def test_url_encryption():
    print("=== URL Encryption Test ===")
    seed = "test-seed-2024"
    
    # Original subscription URL and parameters
    original_url = "https://subscription.example.com/api/v1/client/subscribe?token=abc123"
    original_params = {
        'emoji': '1',
        'file': 'config_template.json',
        'tag': 'my-proxy',
        'prefix': '❤️',
        'ua': 'v2rayng'
    }
    
    # Encrypt
    encrypted_url, encrypted_params = encrypt_url_with_seed(original_url, original_params, seed)
    
    print(f"Original URL: {original_url}")
    print(f"Encrypted URL: {encrypted_url}")
    print(f"\nOriginal Params: {original_params}")
    print(f"Encrypted Params: {encrypted_params}")
    
    # Build encrypted request
    encrypted_params['seed'] = seed  # Add seed to params
    
    # Decrypt
    decrypted_url, decrypted_params = decrypt_request_with_seed(encrypted_url, encrypted_params, seed)
    
    print(f"\nDecrypted URL: {decrypted_url}")
    print(f"Decrypted Params: {decrypted_params}")
    print(f"\nURL Match: {original_url == decrypted_url}")
    print(f"Params Match: {all(original_params[k] == decrypted_params[k] for k in original_params)}\n")

# Test building an encrypted request URL
def test_build_request():
    print("=== Build Encrypted Request Test ===")
    seed = "production-seed-xyz789"
    
    # Original data
    subscription_url = "https://my-sub.example.com/sub/12345"
    params = {
        'emoji': '1',
        'tag': 'JP-Servers',
        'file': '2'
    }
    
    # Encrypt
    encrypted_url, encrypted_params = encrypt_url_with_seed(subscription_url, params, seed)
    encrypted_params['seed'] = seed
    
    # Build the full request URL
    base_url = "http://localhost:5000/config/"
    query_string = urlencode(encrypted_params)
    full_request_url = f"{base_url}{encrypted_url}?{query_string}"
    
    print(f"Original subscription URL: {subscription_url}")
    print(f"Encrypted request URL: {full_request_url}\n")
    
    # Show how to manually decrypt
    print("Server-side decryption process:")
    print(f"1. Extract seed from params: {seed}")
    print(f"2. Decrypt URL path: {encrypted_url} -> {subscription_url}")
    print(f"3. Decrypt each parameter:")
    for key, value in encrypted_params.items():
        if key != 'seed':
            crypto = SeedCrypto(seed)
            decrypted = crypto.decrypt(value)
            print(f"   {key}: {value} -> {decrypted}")

if __name__ == "__main__":
    test_basic_crypto()
    test_url_encryption()
    test_build_request()