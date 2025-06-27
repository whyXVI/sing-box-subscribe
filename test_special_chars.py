#!/usr/bin/env python3
from crypto_helper import encrypt_full_payload, decrypt_full_payload, SeedCrypto
from urllib.parse import urlencode

def test_special_characters():
    print("=== 特殊字符加密解密测试 ===")
    seed = "test-seed"
    
    # 测试1: 管道符分隔的多个URL
    print("\n1. 测试管道符 | 分隔的多个URL:")
    url_with_pipe = "https://sub1.com/api|https://sub2.com/api|https://sub3.com/api"
    params = {'emoji': '1', 'tag': 'multi|test'}
    query_string = urlencode(params)
    
    encrypted = encrypt_full_payload(url_with_pipe, query_string, seed)
    decrypted_url, decrypted_params = decrypt_full_payload(encrypted, seed)
    
    print(f"原始URL: {url_with_pipe}")
    print(f"原始参数: {params}")
    print(f"加密后: {encrypted}")
    print(f"解密URL: {decrypted_url}")
    print(f"解密参数: {decrypted_params}")
    print(f"URL匹配: {url_with_pipe == decrypted_url}")
    print(f"参数匹配: {params == decrypted_params}")
    
    # 测试2: URL中包含&符号
    print("\n2. 测试URL中的 & 符号:")
    url_with_ampersand = "https://example.com/api?token=abc&user=test&session=xyz"
    params = {'file': 'config&test.json', 'prefix': 'A&B'}
    query_string = urlencode(params)
    
    encrypted = encrypt_full_payload(url_with_ampersand, query_string, seed)
    decrypted_url, decrypted_params = decrypt_full_payload(encrypted, seed)
    
    print(f"原始URL: {url_with_ampersand}")
    print(f"原始参数: {params}")
    print(f"加密后: {encrypted[:50]}...")
    print(f"解密URL: {decrypted_url}")
    print(f"解密参数: {decrypted_params}")
    
    # 验证原始URL的参数是否被正确解析
    expected_url = "https://example.com/api"
    expected_url_params = {'token': 'abc', 'user': 'test', 'session': 'xyz'}
    expected_params = {'file': 'config&test.json', 'prefix': 'A&B'}
    
    print(f"\nURL基础部分匹配: {decrypted_url == expected_url}")
    print(f"URL参数正确解析: {all(decrypted_params.get(k) == v for k, v in expected_url_params.items())}")
    print(f"额外参数正确解析: {all(decrypted_params.get(k) == v for k, v in expected_params.items())}")
    
    # 测试3: 综合测试
    print("\n3. 综合测试 (包含各种特殊字符):")
    complex_url = "https://sub.com/api?key=a|b&data=x|y|z"
    complex_params = {'tag': 'A|B|C', 'filter': 'x&y&z', 'special': '!@#$%^&*()'}
    query_string = urlencode(complex_params)
    
    encrypted = encrypt_full_payload(complex_url, query_string, seed)
    decrypted_url, decrypted_params = decrypt_full_payload(encrypted, seed)
    
    print(f"原始URL: {complex_url}")
    print(f"原始参数: {complex_params}")
    print(f"完整payload: {complex_url}&{query_string}")
    print(f"\n解密后URL: {decrypted_url}")
    print(f"解密后参数: {decrypted_params}")
    
    # 手动验证每个值
    print("\n详细验证:")
    print(f"URL基础: {decrypted_url}")
    for key in ['key', 'data', 'tag', 'filter', 'special']:
        if key in decrypted_params:
            print(f"  {key}: {decrypted_params[key]}")

if __name__ == "__main__":
    test_special_characters()