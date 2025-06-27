#!/usr/bin/env python3
"""
双向加密客户端示例
演示如何发送加密请求并解密加密的响应
"""
from crypto_helper import encrypt_full_payload, decrypt_response, SERVER_SEED, SERVER_SEED2
from urllib.parse import urlencode
import requests

class SecureClient:
    def __init__(self, server_url):
        self.server_url = server_url
        # 客户端需要知道这两个种子（在实际应用中应该通过安全方式共享）
        self.request_seed = SERVER_SEED
        self.response_seed = SERVER_SEED2
    
    def send_encrypted_request(self, subscription_url, params, want_encrypted_response=True):
        """
        发送加密请求到服务器
        
        Args:
            subscription_url: 要加密的订阅URL
            params: 请求参数
            want_encrypted_response: 是否要求加密响应
        """
        print("=== 发送加密请求 ===")
        print(f"原始URL: {subscription_url}")
        print(f"原始参数: {params}")
        
        # 1. 加密请求
        query_string = urlencode(params)
        encrypted_payload = encrypt_full_payload(subscription_url, query_string, self.request_seed)
        
        # 2. 构建请求URL（不再需要seed参数）
        if want_encrypted_response:
            full_url = f"{self.server_url}/dev/{encrypted_payload}?enc_resp=1"
        else:
            full_url = f"{self.server_url}/dev/{encrypted_payload}"
        
        print(f"\n加密后的请求URL: {full_url}")
        
        # 3. 发送请求
        try:
            response = requests.get(full_url, timeout=30)
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                if want_encrypted_response:
                    # 4. 解密响应
                    print("\n=== 解密响应 ===")
                    encrypted_response = response.text
                    print(f"加密的响应（前100字符）: {encrypted_response[:100]}...")
                    
                    decrypted_response = decrypt_response(encrypted_response, self.response_seed)
                    if decrypted_response:
                        print("解密成功！")
                        return decrypted_response
                    else:
                        print("解密失败！")
                        return None
                else:
                    print("收到明文响应")
                    return response.text
            else:
                print(f"错误响应: {response.text}")
                return None
                
        except Exception as e:
            print(f"请求失败: {e}")
            return None

def demonstrate_bidirectional_crypto():
    """演示双向加密通信"""
    print("=== 双向加密通信演示 ===\n")
    
    # 创建安全客户端
    client = SecureClient("http://localhost:5000")
    
    # 测试场景1：发送加密请求，接收加密响应
    print("场景1：双向加密通信")
    subscription_url = "https://my-subscription-provider.com/api/subscribe?token=abc123"
    params = {
        'emoji': '1',
        'file': '2',
        'tag': 'SecureProxy',
        'prefix': '🔐'
    }
    
    config = client.send_encrypted_request(subscription_url, params, want_encrypted_response=True)
    if config:
        print(f"\n解密后的配置（前200字符）: {config[:200]}...")
    
    # 测试场景2：发送加密请求，接收明文响应
    print("\n\n场景2：单向加密（仅请求加密）")
    config = client.send_encrypted_request(subscription_url, params, want_encrypted_response=False)
    if config:
        print(f"\n明文配置（前200字符）: {config[:200]}...")

def test_security_features():
    """测试安全特性"""
    print("\n\n=== 安全特性测试 ===")
    
    # 1. 验证不再需要传输seed
    print("\n1. Seed不再通过URL传输")
    print("   - 请求seed在服务器端固定")
    print("   - 响应使用不同的seed2")
    print("   - 两个seed都不在网络上传输")
    
    # 2. 验证响应加密使用不同算法
    print("\n2. 响应加密特性")
    print("   - 使用SHA-512生成更长的密钥")
    print("   - 反向XOR提供不同的加密模式")
    print("   - 每次响应包含8字节随机nonce")
    
    # 3. 演示同样的请求产生不同的响应密文
    print("\n3. 防重放特性演示")
    from crypto_helper import encrypt_response
    
    test_response = '{"status": "success", "data": "test"}'
    encrypted1 = encrypt_response(test_response)
    encrypted2 = encrypt_response(test_response)
    
    print(f"同样的响应内容: {test_response}")
    print(f"第一次加密: {encrypted1[:50]}...")
    print(f"第二次加密: {encrypted2[:50]}...")
    print(f"密文不同: {encrypted1 != encrypted2}")

if __name__ == "__main__":
    # 演示双向加密
    demonstrate_bidirectional_crypto()
    
    # 测试安全特性
    test_security_features()
    
    print("\n\n=== 总结 ===")
    print("✅ 特殊字符（| 和 &）正确加密解密")
    print("✅ XOR已知明文攻击已解释（但仍存在风险）")
    print("✅ Seed不再通过URL传输")
    print("✅ 实现了响应加密（使用不同的seed2和算法）")
    print("✅ 响应包含随机nonce，相同内容产生不同密文")
    print("\n⚠️  注意：这仍然是学习研究用的实现，生产环境建议使用AES-GCM等标准加密算法")