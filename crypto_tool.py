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
    encrypt_full_payload, decrypt_full_payload,
    encrypt_response, decrypt_response,
    SERVER_SEED, SERVER_SEED2
)

def encrypt_request(input_data):
    """
    加密请求数据，生成服务器请求链接
    输入格式: url?param1=value1&param2=value2
    """
    print("=== 加密请求 ===")
    
    # 解析输入
    if '?' in input_data:
        url, query_string = input_data.split('?', 1)
    else:
        url = input_data
        query_string = ""
    
    print(f"原始URL: {url}")
    print(f"原始参数: {query_string}")
    
    # 加密
    encrypted_payload = encrypt_full_payload(url, query_string, SERVER_SEED)
    
    # 生成请求链接
    server_url = "http://localhost:5000"  # 可以修改为实际服务器地址
    request_url = f"{server_url}/dev/{encrypted_payload}?enc_resp=1"
    
    print(f"\n加密后的payload: {encrypted_payload}")
    print(f"\n🔗 发送到服务器的完整链接:")
    print(request_url)
    
    print(f"\n📊 长度统计:")
    print(f"原始数据长度: {len(input_data)} 字符")
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