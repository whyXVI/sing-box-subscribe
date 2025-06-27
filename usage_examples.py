#!/usr/bin/env python3
"""
crypto_tool.py 使用示例和冗余分析完整报告
"""
from crypto_helper import encrypt_response, decrypt_response, SERVER_SEED2
import subprocess
import json

def run_crypto_tool(args):
    """运行crypto_tool.py并返回输出"""
    try:
        result = subprocess.run(['python3', 'crypto_tool.py'] + args, 
                               capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"错误: {e.stderr}"

def demo_usage():
    """演示crypto_tool.py的使用"""
    print("=== crypto_tool.py 使用演示 ===\n")
    
    # 示例1: 加密请求
    print("1. 📤 加密请求 - 生成服务器链接")
    print("命令: python3 crypto_tool.py -i \"https://sub.example.com/api?token=abc123&emoji=1&tag=MyProxy\"")
    print()
    output = run_crypto_tool(['-i', 'https://sub.example.com/api?token=abc123&emoji=1&tag=MyProxy'])
    print(output)
    
    # 示例2: 创建一个小的加密响应进行解密测试
    print("2. 📥 解密响应测试")
    test_response = '{"status": "success", "config": {"outbounds": [{"tag": "proxy", "type": "vmess", "server": "example.com"}]}}'
    encrypted_test = encrypt_response(test_response, SERVER_SEED2)
    
    print(f"测试响应: {test_response}")
    print(f"加密后: {encrypted_test[:100]}...")
    print()
    print(f"命令: python3 crypto_tool.py -o \"{encrypted_test}\"")
    print()
    output = run_crypto_tool(['-o', encrypted_test])
    print(output)

def comprehensive_overhead_analysis():
    """全面的冗余开销分析"""
    print("\n=== 详细冗余分析报告 ===\n")
    
    # 不同类型的数据测试
    test_cases = [
        ("空数据", ""),
        ("短URL", "https://example.com"),
        ("带参数URL", "https://sub.com/api?token=abc123&emoji=1&tag=test"),
        ("小型JSON", '{"outbounds":[{"tag":"proxy","type":"vmess","server":"example.com","server_port":443}]}'),
        ("中型JSON", json.dumps({
            "outbounds": [
                {"tag": f"proxy-{i}", "type": "vmess", "server": f"server{i}.com", "server_port": 443+i}
                for i in range(50)
            ]
        }, indent=2)),
        ("大型JSON (20KB)", json.dumps({
            "outbounds": [
                {
                    "tag": f"proxy-{i:03d}",
                    "type": "vmess", 
                    "server": f"server{i}.example.com",
                    "server_port": 443 + (i % 100),
                    "uuid": f"550e8400-e29b-41d4-a716-446655440{i:03d}",
                    "transport": {"type": "ws", "path": f"/path{i}"}
                }
                for i in range(200)
            ]
        }, indent=2))
    ]
    
    print(f"{'数据类型':<15} {'原始大小':<12} {'加密大小':<12} {'冗余开销':<12} {'冗余率':<8} {'效率'}")
    print("-" * 80)
    
    total_original = 0
    total_encrypted = 0
    
    for name, data in test_cases:
        if len(data) == 0:
            # 空数据特殊处理
            original_size = 0
            encrypted_size = len(encrypt_response(" ", SERVER_SEED2)) - 1  # 减去添加的空格
        else:
            original_size = len(data)
            encrypted_size = len(encrypt_response(data, SERVER_SEED2))
        
        total_original += original_size
        total_encrypted += encrypted_size
        
        if original_size > 0:
            overhead = encrypted_size - original_size
            overhead_percent = (overhead / original_size) * 100
            efficiency = (original_size / encrypted_size) * 100
        else:
            overhead = encrypted_size
            overhead_percent = 0
            efficiency = 0
        
        size_kb = f"{original_size/1024:.1f}KB" if original_size > 1024 else f"{original_size}B"
        enc_kb = f"{encrypted_size/1024:.1f}KB" if encrypted_size > 1024 else f"{encrypted_size}B"
        over_kb = f"{overhead/1024:.1f}KB" if overhead > 1024 else f"{overhead}B"
        
        print(f"{name:<15} {size_kb:<12} {enc_kb:<12} {over_kb:<12} {overhead_percent:<7.1f}% {efficiency:<6.1f}%")
    
    # 总体统计
    print("-" * 80)
    total_overhead = total_encrypted - total_original
    total_overhead_percent = (total_overhead / total_original) * 100 if total_original > 0 else 0
    total_efficiency = (total_original / total_encrypted) * 100
    
    print(f"{'总计':<15} {total_original/1024:<11.1f}KB {total_encrypted/1024:<11.1f}KB {total_overhead/1024:<11.1f}KB {total_overhead_percent:<7.1f}% {total_efficiency:<6.1f}%")

def bandwidth_impact_analysis():
    """带宽影响分析"""
    print("\n=== 带宽影响分析 ===\n")
    
    # 假设不同的使用场景
    scenarios = [
        ("轻度使用", 10, 5),    # 每天10次请求，平均5KB响应
        ("中度使用", 50, 10),   # 每天50次请求，平均10KB响应  
        ("重度使用", 200, 20),  # 每天200次请求，平均20KB响应
    ]
    
    print(f"{'使用场景':<10} {'请求/天':<8} {'响应大小':<10} {'明文流量':<12} {'加密流量':<12} {'额外开销'}")
    print("-" * 70)
    
    for scenario, requests_per_day, avg_response_kb in scenarios:
        daily_plaintext = requests_per_day * avg_response_kb  # KB
        daily_encrypted = daily_plaintext * 1.333  # 33.3% 冗余
        daily_overhead = daily_encrypted - daily_plaintext
        
        monthly_plaintext = daily_plaintext * 30
        monthly_encrypted = daily_encrypted * 30
        monthly_overhead = daily_overhead * 30
        
        print(f"{scenario:<10} {requests_per_day:<8} {avg_response_kb}KB{'':<6} {daily_plaintext:<11.1f}KB {daily_encrypted:<11.1f}KB {daily_overhead:<8.1f}KB")
        print(f"{'月度':<10} {'':<8} {'':<10} {monthly_plaintext/1024:<11.1f}MB {monthly_encrypted/1024:<11.1f}MB {monthly_overhead/1024:<8.1f}MB")
        print()

def security_vs_efficiency_summary():
    """安全性与效率权衡总结"""
    print("=== 安全性与效率权衡总结 ===\n")
    
    print("🔒 安全性收益:")
    print("  ✅ 请求完全隐藏（URL和参数结构不可见）")
    print("  ✅ 响应内容加密保护")
    print("  ✅ 每次响应包含随机nonce（防重放）")
    print("  ✅ 双向不同加密算法（增加破解难度）")
    print("  ✅ Seed不通过网络传输")
    
    print("\n💰 效率成本:")
    print("  📊 加密冗余: ~33.3% (接近Base64编码开销)")
    print("  📊 20KB数据增加约6.7KB传输量")
    print("  📊 处理时间: 加密/解密操作较快")
    print("  📊 内存占用: 略有增加")
    
    print("\n⚖️ 权衡建议:")
    print("  🎯 学习研究: 完全适合，能很好演示加密原理")
    print("  🎯 隐私保护: 相比明文传输有显著改善") 
    print("  ⚠️  生产环境: 建议使用AES-GCM等标准算法")
    print("  ⚠️  高频使用: 注意33%的带宽开销")
    
    print("\n🚀 改进方向:")
    print("  🔧 使用更强的加密算法 (AES-GCM)")
    print("  🔧 实现数据压缩减少冗余")
    print("  🔧 添加完整性验证 (HMAC)")
    print("  🔧 实现密钥轮换机制")

if __name__ == "__main__":
    demo_usage()
    comprehensive_overhead_analysis()
    bandwidth_impact_analysis() 
    security_vs_efficiency_summary()
    
    print("\n" + "="*60)
    print("📋 快速参考:")
    print("  加密请求: python3 crypto_tool.py -i \"url?params\"")
    print("  解密响应: python3 crypto_tool.py -o \"encrypted_text\"")
    print("  分析冗余: python3 crypto_tool.py --analyze")
    print("="*60)