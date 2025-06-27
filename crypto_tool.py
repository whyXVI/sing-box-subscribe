#!/usr/bin/env python3
"""
简单的加密/解密工具
用法:
  python crypto_tool.py -i "url?param1=value1&param2=value2"  # 生成请求链接
  python crypto_tool.py -o "encrypted_response_text"          # 解密响应
"""

import argparse
import sys
from crypto_helper import (
    encrypt_complete_url, encrypt_full_payload, decrypt_full_payload,
    encrypt_response, decrypt_response,
    SERVER_SEED, SERVER_SEED2
)

def extract_server_url(input_url):
    """
    从完整URL中提取服务器部分
    例如: https://server.com/dev/https:/sub.com/api?params -> https://server.com
    """
    import re
    
    # 匹配第一个https://到第一个顶级域名结尾
    # 支持常见的顶级域名
    tld_pattern = r'https://[^/]+\.(?:com|net|org|app|dev|io|cn|co|uk|de|fr|jp|kr|tw|hk|sg)'
    match = re.match(tld_pattern, input_url)
    
    if match:
        return match.group(0)
    
    # 如果没有匹配到，尝试提取到第一个/dev/之前的部分
    dev_match = re.match(r'(https://[^/]+)/dev/', input_url)
    if dev_match:
        return dev_match.group(1)
    
    # 最后的回退方案，使用默认服务器
    return "http://localhost:5000"

def extract_subscription_path(input_url, server_url):
    """
    从完整URL中提取订阅路径部分（要加密的部分）
    """
    if input_url.startswith(server_url):
        # 移除server部分，保留/dev/之后的所有内容
        remaining = input_url[len(server_url):]
        if remaining.startswith('/dev/'):
            return remaining[5:]  # 移除/dev/前缀
    
    # 如果解析失败，返回整个输入作为备用
    return input_url

def encrypt_request(input_data):
    """
    加密请求数据，生成服务器请求链接
    输入格式: 完整的服务器URL，包含多个订阅地址
    """
    print("=== 加密请求 ===")
    
    # 提取服务器URL
    server_url = extract_server_url(input_data)
    print(f"检测到的服务器: {server_url}")
    
    # 提取要加密的订阅路径和参数
    subscription_data = extract_subscription_path(input_data, server_url)
    print(f"要加密的订阅数据: {subscription_data}")
    
    # 为了向后兼容，仍然显示URL和参数的分割（仅用于显示）
    if '?' in subscription_data:
        display_url, display_params = subscription_data.split('?', 1)
    else:
        display_url = subscription_data
        display_params = ""
    
    print(f"原始URL: {server_url}/dev/{display_url}")
    print(f"原始参数: {display_params}")
    
    # 加密完整的订阅数据
    encrypted_payload = encrypt_complete_url(subscription_data, SERVER_SEED)
    
    # 生成请求链接，使用检测到的服务器
    request_url = f"{server_url}/dev/{encrypted_payload}?enc_resp=1"
    
    print(f"\n加密后的payload: {encrypted_payload}")
    print(f"\n🔗 发送到服务器的完整链接:")
    print(request_url)
    
    print(f"\n📊 长度统计:")
    print(f"原始数据长度: {len(subscription_data)} 字符")
    print(f"加密后长度: {len(encrypted_payload)} 字符")
    print(f"完整URL长度: {len(request_url)} 字符")
    
    return request_url

def decrypt_server_response(encrypted_data):
    """
    解密服务器响应
    """
    print("=== 解密响应 ===")
    print(f"加密响应长度: {len(encrypted_data)} 字符")
    print(f"加密响应前100字符: {encrypted_data[:100]}...")
    
    # 解密
    decrypted = decrypt_response(encrypted_data, SERVER_SEED2)
    
    if decrypted:
        print(f"\n✅ 解密成功!")
        print(f"解密后长度: {len(decrypted)} 字符")
        print(f"\n📄 解密后的内容:")
        print(decrypted)
        
        print(f"\n📊 冗余分析:")
        overhead = len(encrypted_data) - len(decrypted)
        overhead_percent = (overhead / len(decrypted)) * 100
        print(f"原始数据: {len(decrypted)} 字符")
        print(f"加密数据: {len(encrypted_data)} 字符")
        print(f"冗余开销: {overhead} 字符 ({overhead_percent:.1f}%)")
        
        return decrypted
    else:
        print("❌ 解密失败!")
        return None

def analyze_overhead():
    """分析不同数据大小的加密冗余"""
    print("\n=== 加密冗余分析 ===")
    
    # 测试不同大小的数据
    test_sizes = [
        ("小数据 (100字节)", "A" * 100),
        ("中等数据 (1KB)", "B" * 1024),
        ("大数据 (20KB)", "C" * 20480),
        ("JSON配置 (模拟)", '{"outbounds":[' + '{"tag":"proxy","type":"vmess","server":"example.com"},' * 200 + ']}')
    ]
    
    print(f"{'数据类型':<15} {'原始大小':<10} {'加密大小':<10} {'冗余':<8} {'冗余率':<8}")
    print("-" * 60)
    
    for name, data in test_sizes:
        encrypted = encrypt_response(data, SERVER_SEED2)
        overhead = len(encrypted) - len(data)
        overhead_percent = (overhead / len(data)) * 100
        
        print(f"{name:<15} {len(data):<10} {len(encrypted):<10} {overhead:<8} {overhead_percent:.1f}%")

def main():
    parser = argparse.ArgumentParser(
        description="加密/解密工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 加密请求 (生成服务器链接)
  python crypto_tool.py -i "https://sub.com/api?token=abc123&emoji=1&tag=test"
  
  # 解密响应
  python crypto_tool.py -o "4b-TZbqv6fIRPouqPOe3Rg5qRy..."
  
  # 分析加密冗余
  python crypto_tool.py --analyze
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-i', '--input', help='输入要加密的请求数据 (URL?params)')
    group.add_argument('-o', '--output', help='输入要解密的响应密文')
    group.add_argument('--analyze', action='store_true', help='分析加密冗余')
    
    args = parser.parse_args()
    
    if args.input:
        encrypt_request(args.input)
    elif args.output:
        decrypt_server_response(args.output)
    elif args.analyze:
        analyze_overhead()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()