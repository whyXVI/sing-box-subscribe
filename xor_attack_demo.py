#!/usr/bin/env python3
"""
演示XOR加密的已知明文攻击
"""

def xor_bytes(data, key):
    """简单的XOR加密/解密"""
    result = bytearray()
    key_len = len(key)
    for i, byte in enumerate(data):
        result.append(byte ^ key[i % key_len])
    return bytes(result)

def demonstrate_known_plaintext_attack():
    print("=== XOR加密已知明文攻击演示 ===\n")
    
    # 1. 正常加密过程
    print("1. 正常加密过程:")
    secret_key = b"MySecretKey123"  # 服务器的密钥
    plaintext = b"https://subscription.example.com/api/v1/subscribe"
    ciphertext = xor_bytes(plaintext, secret_key)
    
    print(f"密钥: {secret_key}")
    print(f"明文: {plaintext}")
    print(f"密文: {ciphertext.hex()}")
    
    # 2. 攻击者的已知明文攻击
    print("\n2. 攻击者执行已知明文攻击:")
    print("假设攻击者知道：")
    print("- 部分明文开头是: 'https://'")
    print("- 对应的密文")
    
    known_plaintext = b"https://"
    known_ciphertext = ciphertext[:len(known_plaintext)]
    
    # XOR的特性: plaintext XOR key = ciphertext
    # 因此: plaintext XOR ciphertext = key
    recovered_key_part = xor_bytes(known_plaintext, known_ciphertext)
    print(f"\n通过 明文 XOR 密文 = 密钥")
    print(f"恢复的密钥片段: {recovered_key_part}")
    print(f"原始密钥片段: {secret_key[:len(known_plaintext)]}")
    print(f"密钥恢复成功: {recovered_key_part == secret_key[:len(known_plaintext)]}")
    
    # 3. 使用恢复的密钥解密更多内容
    print("\n3. 使用恢复的密钥片段解密更多内容:")
    # 因为XOR是循环使用密钥的，我们可以推测完整密钥长度
    # 并解密整个消息
    
    # 假设攻击者猜测密钥长度
    for key_len in range(8, 20):
        test_key = (recovered_key_part * (key_len // len(recovered_key_part) + 1))[:key_len]
        decrypted = xor_bytes(ciphertext[:30], test_key)
        if b"subscription" in decrypted:
            print(f"找到可能的密钥长度: {key_len}")
            print(f"解密的部分内容: {decrypted}")
            break
    
    # 4. 更严重的攻击场景
    print("\n4. 更严重的攻击场景:")
    print("如果攻击者知道多个明文-密文对，可以：")
    
    # 多个已知的URL模式
    known_patterns = [
        (b"https://", 0),
        (b".com/", 20),
        (b"/api/", 30),
    ]
    
    recovered_key = bytearray(50)  # 假设密钥最长50字节
    key_mask = [False] * 50  # 标记哪些位置的密钥已恢复
    
    for pattern, offset in known_patterns:
        if offset + len(pattern) <= len(ciphertext):
            pattern_cipher = ciphertext[offset:offset + len(pattern)]
            key_fragment = xor_bytes(pattern, pattern_cipher)
            
            # 填充恢复的密钥
            for i, byte in enumerate(key_fragment):
                key_pos = (offset + i) % len(secret_key)
                if not key_mask[key_pos]:
                    recovered_key[key_pos] = byte
                    key_mask[key_pos] = True
    
    print(f"通过多个已知模式恢复的密钥字节: {sum(key_mask)}/{len(secret_key)}")
    print(f"恢复的密钥: {bytes(recovered_key[:len(secret_key)])}")
    print(f"原始密钥: {secret_key}")

def explain_xor_weakness():
    print("\n=== XOR加密的根本弱点 ===")
    print("\n1. XOR的数学特性:")
    print("   A XOR B = C")
    print("   A XOR C = B")
    print("   B XOR C = A")
    print("   任意两个值可以推导出第三个值！")
    
    print("\n2. 循环密钥的问题:")
    print("   - 密钥会重复使用")
    print("   - 相同位置的密钥字节加密不同的明文")
    print("   - 统计分析可以找出密钥长度")
    
    print("\n3. 没有扩散性:")
    print("   - 每个字节独立加密")
    print("   - 改变一个明文字节只影响一个密文字节")
    print("   - 便于逐字节破解")
    
    print("\n4. 实际攻击场景:")
    print("   - 订阅URL通常有固定格式(https://...)")
    print("   - 参数名称是已知的(emoji=, tag=, file=)")
    print("   - 某些参数值可预测(emoji=1, file=1,2,3...)")

if __name__ == "__main__":
    demonstrate_known_plaintext_attack()
    explain_xor_weakness()