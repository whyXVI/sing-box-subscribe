#!/usr/bin/env python3
"""
测试大型响应的加密解密
"""
import json
from crypto_helper import encrypt_response, decrypt_response, SERVER_SEED2

def create_large_config():
    """创建一个约20KB的配置文件"""
    config = {
        "log": {
            "disabled": False,
            "level": "info",
            "timestamp": True
        },
        "dns": {
            "servers": [
                {
                    "tag": "proxy",
                    "address": "tls://1.1.1.1",
                    "detour": "proxy"
                },
                {
                    "tag": "direct", 
                    "address": "223.5.5.5",
                    "detour": "direct"
                }
            ],
            "rules": []
        },
        "inbounds": [
            {
                "tag": "tun",
                "type": "tun",
                "interface_name": "tun0",
                "inet4_address": "172.19.0.1/30",
                "auto_route": True,
                "strict_route": True,
                "sniff": True
            }
        ],
        "outbounds": []
    }
    
    # 生成大量代理节点以达到20KB
    for i in range(300):
        proxy = {
            "tag": f"proxy-{i:03d}",
            "type": "vmess",
            "server": f"server{i}.example.com",
            "server_port": 443 + (i % 100),
            "uuid": f"550e8400-e29b-41d4-a716-446655440{i:03d}",
            "security": "auto",
            "alter_id": 0,
            "transport": {
                "type": "ws",
                "path": f"/path{i}",
                "headers": {
                    "Host": f"host{i}.example.com"
                }
            },
            "tls": {
                "enabled": True,
                "server_name": f"server{i}.example.com",
                "insecure": False
            }
        }
        config["outbounds"].append(proxy)
    
    # 添加选择器
    config["outbounds"].append({
        "tag": "Proxy",
        "type": "selector", 
        "outbounds": [f"proxy-{i:03d}" for i in range(300)]
    })
    
    # 添加直连和阻断
    config["outbounds"].extend([
        {"tag": "direct", "type": "direct"},
        {"tag": "block", "type": "block"}
    ])
    
    return json.dumps(config, indent=2, ensure_ascii=False)

def test_large_response():
    """测试大型响应的加密解密"""
    print("=== 测试大型响应加密解密 ===")
    
    # 创建大型配置
    large_config = create_large_config()
    original_size = len(large_config)
    
    print(f"原始配置大小: {original_size:,} 字符 ({original_size/1024:.1f} KB)")
    print(f"配置前100字符: {large_config[:100]}...")
    
    # 加密
    print("\n🔒 加密中...")
    encrypted = encrypt_response(large_config, SERVER_SEED2)
    encrypted_size = len(encrypted)
    
    print(f"加密后大小: {encrypted_size:,} 字符 ({encrypted_size/1024:.1f} KB)")
    print(f"加密前100字符: {encrypted[:100]}...")
    
    # 解密
    print("\n🔓 解密中...")
    decrypted = decrypt_response(encrypted, SERVER_SEED2)
    
    if decrypted:
        decrypted_size = len(decrypted)
        print(f"解密后大小: {decrypted_size:,} 字符 ({decrypted_size/1024:.1f} KB)")
        
        # 验证完整性
        matches = decrypted == large_config
        print(f"数据完整性: {'✅ 完全匹配' if matches else '❌ 不匹配'}")
        
        # 冗余分析
        overhead = encrypted_size - original_size
        overhead_percent = (overhead / original_size) * 100
        compression_ratio = encrypted_size / original_size
        
        print(f"\n📊 详细分析:")
        print(f"原始大小:     {original_size:,} 字符 ({original_size/1024:.1f} KB)")
        print(f"加密大小:     {encrypted_size:,} 字符 ({encrypted_size/1024:.1f} KB)")
        print(f"冗余开销:     {overhead:,} 字符 ({overhead/1024:.1f} KB)")
        print(f"冗余率:       {overhead_percent:.1f}%")
        print(f"压缩比:       {compression_ratio:.2f}:1")
        
        # Base64编码分析
        import base64
        raw_bytes = large_config.encode('utf-8')
        b64_encoded = base64.b64encode(raw_bytes).decode('utf-8')
        b64_overhead = len(b64_encoded) - len(raw_bytes)
        
        print(f"\n🔍 Base64编码对比:")
        print(f"原始UTF-8:    {len(raw_bytes):,} 字节")
        print(f"Base64编码:   {len(b64_encoded):,} 字符")
        print(f"Base64冗余:   {b64_overhead:,} 字符 ({(b64_overhead/len(raw_bytes))*100:.1f}%)")
        
        print(f"\n💡 分析结论:")
        print(f"- 我们的加密冗余 ({overhead_percent:.1f}%) 接近Base64编码冗余 (~33%)")
        print(f"- 8字节随机nonce增加了额外的安全性")
        print(f"- 对于20KB数据，冗余约{overhead/1024:.1f}KB，在可接受范围内")
        
        return encrypted
    else:
        print("❌ 解密失败!")
        return None

if __name__ == "__main__":
    encrypted_data = test_large_response()
    
    if encrypted_data:
        print(f"\n🔧 使用crypto_tool.py解密此数据:")
        print(f"python3 crypto_tool.py -o \"{encrypted_data[:50]}...\"")
        
        # 保存加密数据到文件供测试
        with open('/workspace/test_encrypted.txt', 'w') as f:
            f.write(encrypted_data)
        print(f"\n💾 加密数据已保存到 test_encrypted.txt")