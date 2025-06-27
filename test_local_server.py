#!/usr/bin/env python3
"""
本地服务器测试脚本
"""
import json
import requests
import sys
from crypto_helper import encrypt_complete_url, decrypt_complete_url, SERVER_SEED

def test_local_server():
    """测试本地服务器"""
    base_url = "http://127.0.0.1:5000"
    
    print("=== 测试本地服务器 ===")
    
    # 1. 测试主页
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✓ 主页访问正常")
        else:
            print(f"✗ 主页访问失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 无法连接到本地服务器: {e}")
        print("请先运行 python3 run_local.py 启动服务器")
        return False
    
    # 2. 测试加密订阅功能
    print("\n--- 测试加密订阅功能 ---")
    
    # 创建测试订阅URL
    test_vmess = "vmess://eyJhZGQiOiIxMjcuMC4wLjEiLCJhaWQiOiIwIiwiaG9zdCI6IiIsImlkIjoiYWJjZGVmZ2gtaWprbC1tbm9wLXFyc3QtdXZ3eHl6MTIzNDU2IiwibmV0IjoidGNwIiwicGF0aCI6IiIsInBvcnQiOiI0NDMiLCJwcyI6IlRlc3QgU2VydmVyIiwic2N5IjoiYXV0byIsInNuaSI6IiIsInRscyI6IiIsInR5cGUiOiJub25lIiwidiI6IjIifQ=="
    
    # 加密订阅数据
    subscription_data = f"{test_vmess}?tag=TestProxy&emoji=1"
    encrypted_payload = encrypt_complete_url(subscription_data, SERVER_SEED)
    
    print(f"原始订阅数据: {subscription_data}")
    print(f"加密后载荷: {encrypted_payload}")
    
    # 测试解密
    decrypted_url, decrypted_params = decrypt_complete_url(encrypted_payload, SERVER_SEED)
    print(f"解密URL: {decrypted_url}")
    print(f"解密参数: {decrypted_params}")
    
    # 发送加密请求
    encrypted_url = f"{base_url}/dev/{encrypted_payload}"
    try:
        response = requests.get(encrypted_url)
        print(f"\n请求URL: {encrypted_url}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                config = response.json()
                print("✓ 成功获取配置")
                
                # 分析outbounds
                outbounds = config.get('outbounds', [])
                print(f"\nOutbounds 数量: {len(outbounds)}")
                
                proxy_outbounds = []
                for outbound in outbounds:
                    outbound_type = outbound.get('type', 'unknown')
                    outbound_tag = outbound.get('tag', 'no_tag')
                    
                    if outbound_type not in ['direct', 'block', 'dns', 'selector', 'urltest']:
                        proxy_outbounds.append({
                            'tag': outbound_tag,
                            'type': outbound_type,
                            'server': outbound.get('server', 'no_server')
                        })
                
                print(f"代理Outbounds 数量: {len(proxy_outbounds)}")
                
                if proxy_outbounds:
                    print("✓ 找到代理节点:")
                    for proxy in proxy_outbounds[:3]:  # 只显示前3个
                        print(f"  - {proxy['tag']}: {proxy['type']} -> {proxy['server']}")
                else:
                    print("✗ 没有找到代理节点，只有direct连接")
                    
                    # 检查选择器outbounds
                    selectors = [ob for ob in outbounds if ob.get('type') == 'selector']
                    if selectors:
                        print("\n选择器Outbounds:")
                        for selector in selectors[:3]:
                            selector_outbounds = selector.get('outbounds', [])
                            print(f"  - {selector['tag']}: {selector_outbounds}")
                
            except json.JSONDecodeError:
                print("✗ 响应不是有效的JSON")
                print(f"响应内容: {response.text[:500]}")
        else:
            print(f"✗ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"✗ 测试加密订阅时出错: {e}")
    
    # 3. 测试普通订阅功能
    print(f"\n--- 测试普通订阅功能 ---")
    
    # 使用base64编码的vmess作为测试
    import base64
    encoded_vmess = base64.b64encode(test_vmess.encode()).decode()
    normal_url = f"{base_url}/config/{encoded_vmess}?tag=TestProxy&emoji=1"
    
    try:
        response = requests.get(normal_url)
        print(f"请求URL: {normal_url}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ 普通订阅功能正常")
        else:
            print(f"✗ 普通订阅功能异常: {response.text[:200]}")
    except Exception as e:
        print(f"✗ 测试普通订阅时出错: {e}")

def test_crypto_functions():
    """测试加密解密函数"""
    print("\n=== 测试加密解密函数 ===")
    
    test_data = "vmess://test?tag=proxy&emoji=1"
    
    # 加密
    encrypted = encrypt_complete_url(test_data, SERVER_SEED)
    print(f"原始数据: {test_data}")
    print(f"加密结果: {encrypted}")
    
    # 解密
    decrypted_url, decrypted_params = decrypt_complete_url(encrypted, SERVER_SEED)
    print(f"解密URL: {decrypted_url}")
    print(f"解密参数: {decrypted_params}")
    
    # 验证
    if decrypted_url.split('?')[0] == test_data.split('?')[0]:
        print("✓ 加密解密功能正常")
    else:
        print("✗ 加密解密功能异常")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'crypto':
        test_crypto_functions()
    else:
        test_local_server()