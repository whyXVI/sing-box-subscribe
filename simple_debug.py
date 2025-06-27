#!/usr/bin/env python3
"""
Simple debug script to understand the direct issue
"""
import json
import base64
from crypto_helper import (
    encrypt_complete_url, decrypt_complete_url,
    SERVER_SEED
)

def decode_vmess_url(vmess_url):
    """Decode a vmess URL to see its content"""
    if vmess_url.startswith('vmess://'):
        try:
            encoded_data = vmess_url[8:]  # Remove 'vmess://' prefix
            decoded_data = base64.urlsafe_b64decode(encoded_data + '==')  # Add padding if needed
            return json.loads(decoded_data.decode('utf-8'))
        except Exception as e:
            print(f"Error decoding vmess: {e}")
            return None
    return None

def test_simple_vmess():
    """Test with a simple VMess URL"""
    print("=== Testing Simple VMess URL ===")
    
    # Create a simple vmess configuration
    vmess_config = {
        "add": "example.com",
        "aid": "0", 
        "host": "",
        "id": "abcdefgh-ijkl-mnop-qrst-uvwxyz123456",
        "net": "tcp",
        "path": "",
        "port": "443",
        "ps": "Test Server",
        "scy": "auto",
        "sni": "",
        "tls": "",
        "type": "none",
        "v": "2"
    }
    
    # Encode it as a vmess URL
    config_json = json.dumps(vmess_config)
    encoded = base64.urlsafe_b64encode(config_json.encode('utf-8')).decode('utf-8')
    vmess_url = f"vmess://{encoded}"
    
    print(f"VMess URL: {vmess_url}")
    print(f"Decoded config: {vmess_config}")
    
    return vmess_url

def test_direct_url():
    """Test what happens when we pass a direct URL instead of subscription"""
    print("\n=== Testing Direct URL vs Subscription ===")
    
    # Test 1: Direct vmess URL
    vmess_url = test_simple_vmess()
    
    # Test 2: What if we encrypt just 'direct' as the subscription content
    direct_content = "direct"
    encrypted_direct = encrypt_complete_url(direct_content, SERVER_SEED)
    
    print(f"\nDirect content: {direct_content}")
    print(f"Encrypted direct: {encrypted_direct}")
    
    # Decrypt it back
    decrypted_direct, _ = decrypt_complete_url(encrypted_direct, SERVER_SEED)
    print(f"Decrypted back: {decrypted_direct}")
    
    # Test 3: What if subscription content is empty or null
    empty_contents = ["", " ", "null", "None", "[]", "{}"]
    
    print(f"\nTesting empty/null contents:")
    for content in empty_contents:
        try:
            encrypted = encrypt_complete_url(content, SERVER_SEED)
            decrypted, _ = decrypt_complete_url(encrypted, SERVER_SEED)
            print(f"  '{content}' -> '{decrypted}'")
        except Exception as e:
            print(f"  '{content}' -> Error: {e}")

def test_subscription_response_format():
    """Test what different subscription response formats look like"""
    print("\n=== Testing Subscription Response Formats ===")
    
    # Format 1: Base64 encoded list of URLs
    vmess_url = test_simple_vmess()
    subscription_content = base64.urlsafe_b64encode(vmess_url.encode('utf-8')).decode('utf-8')
    print(f"Format 1 (Base64): {subscription_content[:50]}...")
    
    # Format 2: Plain text URLs
    plain_content = vmess_url
    print(f"Format 2 (Plain): {plain_content[:50]}...")
    
    # Format 3: JSON with outbounds (sing-box format)
    singbox_format = {
        "outbounds": [
            {
                "tag": "proxy1",
                "type": "vmess",
                "server": "example.com",
                "server_port": 443,
                "uuid": "abcdefgh-ijkl-mnop-qrst-uvwxyz123456"
            },
            {
                "tag": "direct", 
                "type": "direct"
            }
        ]
    }
    json_content = json.dumps(singbox_format, indent=2)
    print(f"Format 3 (JSON): {json_content[:100]}...")
    
    # Format 4: Clash format
    clash_format = {
        "proxies": [
            {
                "name": "Test Server",
                "type": "vmess",
                "server": "example.com",
                "port": 443,
                "uuid": "abcdefgh-ijkl-mnop-qrst-uvwxyz123456"
            }
        ]
    }
    clash_content = json.dumps(clash_format, indent=2)
    print(f"Format 4 (Clash): {clash_content[:100]}...")

if __name__ == "__main__":
    test_simple_vmess()
    test_direct_url()
    test_subscription_response_format()