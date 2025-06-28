import hashlib
import base64
from urllib.parse import quote, unquote
import os

class SeedCrypto:
    def __init__(self, seed):
        self.seed = str(seed)
        self.key = self._generate_key()
    
    def _generate_key(self):
        return hashlib.sha256(self.seed.encode()).digest()
    
    def _xor_cipher(self, data):
        key_len = len(self.key)
        result = bytearray()
        for i, byte in enumerate(data):
            result.append(byte ^ self.key[i % key_len])
        return bytes(result)
    
    def encrypt(self, plaintext):
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        encrypted = self._xor_cipher(plaintext)
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, ciphertext):
        try:
            encrypted = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
            decrypted = self._xor_cipher(encrypted)
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

def encrypt_url_with_seed(url, params, seed):
    crypto = SeedCrypto(seed)
    
    encrypted_url = crypto.encrypt(url)
    
    encrypted_params = {}
    for key, value in params.items():
        if value:
            encrypted_params[key] = crypto.encrypt(str(value))
    
    return encrypted_url, encrypted_params

def decrypt_request_with_seed(encrypted_url, request_args, seed):
    crypto = SeedCrypto(seed)
    
    decrypted_url = crypto.decrypt(encrypted_url)
    if not decrypted_url:
        return None, None
    
    decrypted_params = {}
    for key, value in request_args.items():
        if key == 'seed':
            continue
        if value:
            decrypted_value = crypto.decrypt(value)
            if decrypted_value:
                decrypted_params[key] = decrypted_value
    
    return decrypted_url, decrypted_params

def encrypt_complete_url(complete_url, seed):
    """
    Encrypt the complete URL string as-is without any parsing
    This preserves multi-subscription URLs with encoded separators
    """
    crypto = SeedCrypto(seed)
    return crypto.encrypt(complete_url)

def decrypt_complete_url(encrypted_url, seed):
    """
    Decrypt the complete URL string as-is without any parsing
    This is the counterpart to encrypt_complete_url
    """
    crypto = SeedCrypto(seed)
    decrypted = crypto.decrypt(encrypted_url)
    if not decrypted:
        return None, {}
    
    # Check if this is a multi-subscription URL (contains | separator)
    if '|' in decrypted:
        # For multi-subscription URLs, return the complete string without parsing
        return decrypted, {}
    
    # Parse the decrypted URL into URL and parameters for single subscription
    if '?' in decrypted:
        url, query_string = decrypted.split('?', 1)
        # Parse query string into dict, but DON'T unquote values to preserve encoding
        params = {}
        if query_string:
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value  # Keep original encoding
        return url, params
    else:
        return decrypted, {}

def encrypt_full_payload(url, query_string, seed):
    """
    Encrypt the full URL path and query string as a single payload
    This is for the /dev/<encrypted> endpoint
    """
    crypto = SeedCrypto(seed)
    
    # Combine URL and query string
    if query_string:
        # Check if URL already has query parameters
        if '?' in url:
            full_payload = f"{url}&{query_string}"
        else:
            full_payload = f"{url}?{query_string}"
    else:
        full_payload = url
    
    # Encrypt the entire payload
    encrypted = crypto.encrypt(full_payload)
    return encrypted

def decrypt_full_payload(encrypted_payload, seed):
    """
    Decrypt the full payload back to URL and query string
    """
    crypto = SeedCrypto(seed)
    
    # Decrypt the payload
    decrypted = crypto.decrypt(encrypted_payload)
    if not decrypted:
        return None, None
    
    # Split into URL and query string
    if '?' in decrypted:
        url, query_string = decrypted.split('?', 1)
        # Parse query string into dict
        params = {}
        if query_string:
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = unquote(value)
        return url, params
    else:
        return decrypted, {}

# 服务器端固定的种子配置
SERVER_SEED = os.getenv('CRYPTO_SEED', 'default-server-seed-2024-secure')
SERVER_SEED2 = os.getenv('CRYPTO_SEED2', 'response-encryption-seed-2024')

class ResponseCrypto:
    """用于响应加密的不同加密算法"""
    def __init__(self, seed):
        self.seed = str(seed)
        self.key = self._generate_key()
    
    def _generate_key(self):
        # 使用不同的哈希算法生成密钥
        return hashlib.sha512(self.seed.encode()).digest()
    
    def _reverse_xor_cipher(self, data):
        """反向XOR加密，提供与请求加密不同的模式"""
        key_len = len(self.key)
        result = bytearray()
        # 反向使用密钥
        for i, byte in enumerate(data):
            result.append(byte ^ self.key[-(i % key_len) - 1])
        return bytes(result)
    
    def encrypt(self, plaintext):
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        # 添加随机前缀增加安全性
        nonce = os.urandom(8)
        plaintext_with_nonce = nonce + plaintext
        encrypted = self._reverse_xor_cipher(plaintext_with_nonce)
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, ciphertext):
        try:
            encrypted = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
            decrypted_with_nonce = self._reverse_xor_cipher(encrypted)
            # 移除nonce
            decrypted = decrypted_with_nonce[8:]
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"Response decryption error: {e}")
            return None

def encrypt_response(response_content, seed2=SERVER_SEED2):
    """加密服务器响应"""
    crypto = ResponseCrypto(seed2)
    return crypto.encrypt(response_content)

def decrypt_response(encrypted_response, seed2=SERVER_SEED2):
    """解密服务器响应"""
    crypto = ResponseCrypto(seed2)
    return crypto.decrypt(encrypted_response)