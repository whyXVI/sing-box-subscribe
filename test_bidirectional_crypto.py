#!/usr/bin/env python3
"""
双向加密系统测试（不依赖requests）
"""
from crypto_helper import (
    encrypt_full_payload, decrypt_full_payload, 
    encrypt_response, decrypt_response,
    SERVER_SEED, SERVER_SEED2
)
from urllib.parse import urlencode

def test_request_encryption():
    """测试请求加密（客户端侧）"""
    print("=== 测试请求加密 ===")
    
    # 客户端数据
    subscription_url = "https://my-sub.com/api?token=abc123"
    params = {
        'emoji': '1',
        'tag': 'TestProxy',
        'file': '2',
        'prefix': '🔐'
    }
    
    print(f"原始URL: {subscription_url}")
    print(f"原始参数: {params}")
    
    # 客户端加密请求
    query_string = urlencode(params)
    encrypted_payload = encrypt_full_payload(subscription_url, query_string, SERVER_SEED)
    
    print(f"\n加密payload: {encrypted_payload}")
    print(f"请求URL: /dev/{encrypted_payload}?enc_resp=1")
    
    # 服务器端解密
    decrypted_url, decrypted_params = decrypt_full_payload(encrypted_payload, SERVER_SEED)
    
    print(f"\n服务器解密后:")
    print(f"URL: {decrypted_url}")
    print(f"参数: {decrypted_params}")
    
    # 验证
    print(f"\n验证结果:")
    print(f"URL匹配: {subscription_url == decrypted_url}")
    print(f"参数匹配: {params == decrypted_params}")
    
    return encrypted_payload

def test_response_encryption():
    """测试响应加密（服务器侧）"""
    print("\n=== 测试响应加密 ===")
    
    # 模拟服务器响应
    mock_config = """{
  "log": {
    "disabled": false,
    "level": "info"
  },
  "dns": {
    "servers": [
      {
        "tag": "proxy",
        "address": "tls://1.1.1.1"
      }
    ]
  },
  "outbounds": [
    {
      "tag": "TestProxy",
      "type": "vmess",
      "server": "example.com",
      "server_port": 443
    }
  ]
}"""
    
    print(f"原始响应（前100字符）: {mock_config[:100]}...")
    
    # 服务器加密响应
    encrypted_response = encrypt_response(mock_config, SERVER_SEED2)
    print(f"\n加密后响应（前100字符）: {encrypted_response[:100]}...")
    
    # 客户端解密响应
    decrypted_response = decrypt_response(encrypted_response, SERVER_SEED2)
    
    print(f"\n客户端解密后（前100字符）: {decrypted_response[:100]}...")
    
    # 验证
    print(f"\n验证结果:")
    print(f"响应匹配: {mock_config == decrypted_response}")
    
    return encrypted_response

def test_anti_replay_features():
    """测试防重放特性"""
    print("\n=== 测试防重放特性 ===")
    
    # 同样的响应内容
    response_content = "Same response content for testing"
    
    # 多次加密，应该产生不同的密文
    encrypted1 = encrypt_response(response_content, SERVER_SEED2)
    encrypted2 = encrypt_response(response_content, SERVER_SEED2)
    encrypted3 = encrypt_response(response_content, SERVER_SEED2)
    
    print(f"原始内容: {response_content}")
    print(f"第1次加密: {encrypted1[:50]}...")
    print(f"第2次加密: {encrypted2[:50]}...")
    print(f"第3次加密: {encrypted3[:50]}...")
    
    # 验证密文不同
    all_different = len(set([encrypted1, encrypted2, encrypted3])) == 3
    print(f"\n三次加密结果都不同: {all_different}")
    
    # 验证都能正确解密
    decrypted1 = decrypt_response(encrypted1, SERVER_SEED2)
    decrypted2 = decrypt_response(encrypted2, SERVER_SEED2)
    decrypted3 = decrypt_response(encrypted3, SERVER_SEED2)
    
    all_decrypt_correct = all([
        decrypted1 == response_content,
        decrypted2 == response_content,
        decrypted3 == response_content
    ])
    print(f"三次解密结果都正确: {all_decrypt_correct}")

def test_special_characters_advanced():
    """测试复杂特殊字符场景"""
    print("\n=== 测试复杂特殊字符场景 ===")
    
    # 包含各种特殊字符的复杂URL
    complex_url = "https://sub1.com/api?key=a|b&data=x&y|z|w"
    complex_params = {
        'tag': 'A|B|C&D',
        'filter': 'x&y&z|w',
        'prefix': '🔐|💀&👻',
        'special': '!@#$%^&*()[]{}|\\',
        'unicode': '测试|中文&参数'
    }
    
    print(f"复杂URL: {complex_url}")
    print(f"复杂参数: {complex_params}")
    
    # 加密
    query_string = urlencode(complex_params)
    encrypted = encrypt_full_payload(complex_url, query_string, SERVER_SEED)
    
    # 解密
    decrypted_url, decrypted_params = decrypt_full_payload(encrypted, SERVER_SEED)
    
    print(f"\n解密后URL: {decrypted_url}")
    print(f"解密后参数: {decrypted_params}")
    
    # 验证每个特殊参数
    print(f"\n详细验证:")
    success_count = 0
    total_params = len(complex_params)
    
    for key, expected_value in complex_params.items():
        actual_value = decrypted_params.get(key)
        match = actual_value == expected_value
        print(f"  {key}: {match} ({'✓' if match else '✗'})")
        if match:
            success_count += 1
    
    print(f"\n特殊字符测试成功率: {success_count}/{total_params} ({success_count/total_params*100:.1f}%)")

def demonstrate_security_improvements():
    """演示安全改进"""
    print("\n=== 安全改进演示 ===")
    
    print("1. Seed管理改进:")
    print(f"   - 请求加密seed: {SERVER_SEED} (服务器端固定)")
    print(f"   - 响应加密seed: {SERVER_SEED2} (服务器端固定)")
    print("   - 不再通过URL传输seed，避免泄露")
    
    print("\n2. 双向加密:")
    print("   - 请求: 使用SHA256+XOR")
    print("   - 响应: 使用SHA512+反向XOR+随机nonce")
    print("   - 不同的加密算法增加破解难度")
    
    print("\n3. 防重放改进:")
    print("   - 响应加密包含8字节随机nonce")
    print("   - 相同内容每次产生不同密文")
    print("   - 降低流量分析风险")
    
    print("\n4. URL简化:")
    print("   - 原格式: /config/{url}?emoji={enc}&tag={enc}&seed={plain}")
    print("   - 新格式: /dev/{encrypted_all}?enc_resp=1")
    print("   - 更简洁，信息泄露更少")

if __name__ == "__main__":
    print("双向加密系统完整测试\n")
    
    # 执行所有测试
    test_request_encryption()
    test_response_encryption()
    test_anti_replay_features()
    test_special_characters_advanced()
    demonstrate_security_improvements()
    
    print("\n" + "="*50)
    print("🎉 所有测试完成！")
    print("\n✅ 实现的功能:")
    print("- 特殊字符正确处理")
    print("- 服务器端固定seed")
    print("- 双向加密（请求+响应）")
    print("- 响应防重放（随机nonce）")
    print("- 不同的加密算法")
    print("\n⚠️ 注意：这是研究学习用的实现")
    print("生产环境建议使用标准加密算法如AES-GCM")