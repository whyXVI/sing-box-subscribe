#!/usr/bin/env python3
"""
Debug script to investigate the 'direct' issue in outbounds
"""
import json
import os
import sys
import main
from crypto_helper import (
    encrypt_complete_url, decrypt_complete_url, 
    encrypt_response, decrypt_response,
    SERVER_SEED, SERVER_SEED2
)

def debug_subscription_processing():
    """Debug what happens when processing subscriptions"""
    print("=== Debug Subscription Processing ===")
    
    # Create a test subscription URL with actual proxy content
    test_vmess = "vmess://eyJhZGQiOiIxMjcuMC4wLjEiLCJhaWQiOiIwIiwiaG9zdCI6IiIsImlkIjoiYWJjZGVmZ2gtaWprbC1tbm9wLXFyc3QtdXZ3eHl6MTIzNDU2IiwibmV0IjoidGNwIiwicGF0aCI6IiIsInBvcnQiOiI0NDMiLCJwcyI6IlRlc3QgU2VydmVyIiwic2N5IjoiYXV0byIsInNuaSI6IiIsInRscyI6IiIsInR5cGUiOiJub25lIiwidiI6IjIifQ=="
    
    print(f"Test VMess URL: {test_vmess}")
    
    # Try to parse the vmess URL directly
    try:
        from parsers.vmess import parse
        parsed_node = parse(test_vmess)
        print(f"Parsed node: {json.dumps(parsed_node, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error parsing VMess: {e}")
    
    # Create temp JSON data with the test subscription
    temp_json_data = {
        "subscribes": [
            {
                "url": test_vmess,
                "tag": "test_subscription",
                "enabled": True,
                "emoji": 1,
                "subgroup": "",
                "prefix": "",
                "ex-node-name": "",
                "User-Agent": "v2rayng"
            }
        ],
        "auto_set_outbounds_dns": {
            "proxy": "",
            "direct": ""
        },
        "save_config_path": "./debug_config.json",
        "auto_backup": False,
        "exclude_protocol": "",
        "config_template": "",
        "Only-nodes": False
    }
    
    # Save the temp data to environment
    os.environ['TEMP_JSON_DATA'] = json.dumps(temp_json_data)
    
    # Initialize parsers like main.py does
    main.init_parsers()
    
    # Set providers like main.py does
    main.providers = temp_json_data
    
    print(f"\nProcessing subscription...")
    
    # Process subscriptions
    try:
        nodes = main.process_subscribes(temp_json_data["subscribes"])
        print(f"Processed nodes: {json.dumps(nodes, indent=2, ensure_ascii=False)}")
        
        if nodes:
            # Load a simple template
            template_path = 'config_template/config_template_no_groups_tun_VN.json'
            with open(template_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"\nCombining nodes with template...")
            final_config = main.combin_to_config(config, nodes)
            
            # Check outbounds
            print(f"\nFinal outbounds:")
            for outbound in final_config.get('outbounds', []):
                print(f"  - {outbound.get('tag', 'NO_TAG')}: {outbound.get('type', 'NO_TYPE')}")
                if outbound.get('type') not in ['direct', 'block', 'dns', 'selector', 'urltest']:
                    print(f"    Server: {outbound.get('server', 'NO_SERVER')}")
            
        else:
            print("No nodes found!")
            
    except Exception as e:
        print(f"Error processing: {e}")
        import traceback
        traceback.print_exc()

def debug_encrypted_subscription():
    """Debug what happens with encrypted subscription"""
    print("\n=== Debug Encrypted Subscription ===")
    
    # Create a simple vmess URL for testing
    test_vmess = "vmess://eyJhZGQiOiIxMjcuMC4wLjEiLCJhaWQiOiIwIiwiaG9zdCI6IiIsImlkIjoiYWJjZGVmZ2gtaWprbC1tbm9wLXFyc3QtdXZ3eHl6MTIzNDU2IiwibmV0IjoidGNwIiwicGF0aCI6IiIsInBvcnQiOiI0NDMiLCJwcyI6IlRlc3QgU2VydmVyIiwic2N5IjoiYXV0byIsInNuaSI6IiIsInRscyI6IiIsInR5cGUiOiJub25lIiwidiI6IjIifQ=="
    
    # Encrypt the subscription URL
    subscription_data = f"{test_vmess}?emoji=1&tag=TestProxy"
    encrypted_payload = encrypt_complete_url(subscription_data, SERVER_SEED)
    
    print(f"Original subscription data: {subscription_data}")
    print(f"Encrypted payload: {encrypted_payload}")
    
    # Decrypt and see what we get
    decrypted_url, decrypted_params = decrypt_complete_url(encrypted_payload, SERVER_SEED)
    print(f"Decrypted URL: {decrypted_url}")
    print(f"Decrypted params: {decrypted_params}")

if __name__ == "__main__":
    debug_subscription_processing()
    debug_encrypted_subscription()