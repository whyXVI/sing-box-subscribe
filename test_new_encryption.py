#!/usr/bin/env python3
from crypto_helper import encrypt_full_payload, decrypt_full_payload, SeedCrypto
from urllib.parse import urlencode, quote

def test_full_payload_encryption():
    print("=== Full Payload Encryption Test ===")
    seed = "test-seed-2024"
    
    # Original data (what would normally come after /config/)
    original_url = "https://subscription.example.com/api/v1/client/subscribe?token=abc123"
    original_params = {
        'emoji': '1',
        'file': 'config_template.json',
        'tag': 'my-proxy',
        'prefix': '❤️',
        'ua': 'v2rayng'
    }
    
    # Build query string
    query_string = urlencode(original_params)
    
    # Encrypt the full payload
    encrypted_payload = encrypt_full_payload(original_url, query_string, seed)
    
    print(f"Original URL: {original_url}")
    print(f"Original Query String: {query_string}")
    print(f"Full Payload: {original_url}?{query_string}")
    print(f"\nEncrypted Payload: {encrypted_payload}")
    print(f"Encrypted Length: {len(encrypted_payload)} chars")
    
    # Decrypt
    decrypted_url, decrypted_params = decrypt_full_payload(encrypted_payload, seed)
    
    print(f"\nDecrypted URL: {decrypted_url}")
    print(f"Decrypted Params: {decrypted_params}")
    
    # Verify
    print(f"\nURL Match: {original_url == decrypted_url}")
    print(f"Params Match: {all(original_params[k] == decrypted_params[k] for k in original_params)}")

def compare_implementations():
    print("\n=== Implementation Comparison ===")
    
    # Test data
    subscription_url = "https://my-sub.example.com/sub/12345"
    params = {
        'emoji': '1',
        'tag': 'JP-Servers',
        'file': '2',
        'prefix': '🚀'
    }
    seed = "shared-secret"
    
    # Method 1: Individual encryption (previous implementation)
    print("\nMethod 1 - Individual Parameter Encryption:")
    from crypto_helper import encrypt_url_with_seed
    encrypted_url, encrypted_params = encrypt_url_with_seed(subscription_url, params, seed)
    encrypted_params['seed'] = seed
    query1 = urlencode(encrypted_params)
    url1 = f"/config/{encrypted_url}?{query1}"
    print(f"Request URL: {url1}")
    print(f"Total Length: {len(url1)} chars")
    
    # Method 2: Full payload encryption (new implementation)
    print("\nMethod 2 - Full Payload Encryption:")
    query_string = urlencode(params)
    encrypted_payload = encrypt_full_payload(subscription_url, query_string, seed)
    url2 = f"/dev/{encrypted_payload}?seed={seed}"
    print(f"Request URL: {url2}")
    print(f"Total Length: {len(url2)} chars")
    
    print(f"\nLength Difference: {len(url1) - len(url2)} chars (Method 1 is {'longer' if len(url1) > len(url2) else 'shorter'})")

def test_edge_cases():
    print("\n=== Edge Cases Test ===")
    seed = "test-seed"
    
    # Test 1: URL with no parameters
    print("\n1. URL with no parameters:")
    url = "https://example.com/subscribe"
    encrypted = encrypt_full_payload(url, "", seed)
    decrypted_url, decrypted_params = decrypt_full_payload(encrypted, seed)
    print(f"Original: {url}")
    print(f"Decrypted: {decrypted_url}")
    print(f"Params: {decrypted_params}")
    print(f"Success: {url == decrypted_url and len(decrypted_params) == 0}")
    
    # Test 2: URL with special characters
    print("\n2. URL with special characters:")
    url = "https://example.com/sub?token=abc+123&user=test@example.com"
    encrypted = encrypt_full_payload(url, "", seed)
    decrypted_url, decrypted_params = decrypt_full_payload(encrypted, seed)
    print(f"Original: {url}")
    print(f"Decrypted: {decrypted_url}?{urlencode(decrypted_params)}")
    print(f"Success: {decrypted_url == 'https://example.com/sub'}")
    
    # Test 3: Multiple URLs separated by |
    print("\n3. Multiple URLs (pipe-separated):")
    url = "https://sub1.com/api|https://sub2.com/api|https://sub3.com/api"
    params = {'emoji': '1', 'tag': 'multi'}
    query_string = urlencode(params)
    encrypted = encrypt_full_payload(url, query_string, seed)
    decrypted_url, decrypted_params = decrypt_full_payload(encrypted, seed)
    print(f"Original: {url}")
    print(f"Decrypted: {decrypted_url}")
    print(f"Success: {url == decrypted_url}")

if __name__ == "__main__":
    test_full_payload_encryption()
    compare_implementations()
    test_edge_cases()