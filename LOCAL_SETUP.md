# 本地服务器设置指南

## 快速开始

### 1. 安装依赖
```bash
pip3 install -r requirements.txt
```

### 2. 启动服务器
```bash
# 方法1: 使用启动脚本
chmod +x start_local.sh
./start_local.sh

# 方法2: 直接运行Python脚本
python3 run_local.py
```

### 3. 访问服务器
- 管理界面: http://127.0.0.1:5000/
- API端点: http://127.0.0.1:5000/dev/<encrypted_data>

## 测试功能

### 测试加密解密功能
```bash
python3 test_local_server.py crypto
```

### 测试完整服务器功能
```bash
# 确保服务器在另一个终端运行
python3 test_local_server.py
```

## 调试订阅问题

### 1. 检查解密是否正常
使用 `crypto_tool.py` 测试加密解密:
```bash
# 加密订阅URL
python3 crypto_tool.py -i "vmess://xxx?tag=test&emoji=1"

# 解密响应
python3 crypto_tool.py -o "encrypted_string_here"
```

### 2. 分析订阅处理流程
在 `main.py` 的 `process_subscribes` 函数中添加调试输出:
```python
_nodes = get_nodes(subscribe['url'])
print(f"DEBUG: 订阅 {subscribe['url']} 返回节点数量: {len(_nodes) if _nodes else 0}")
```

### 3. 检查网络连接
确保本地可以访问订阅URL:
```bash
curl -v "your_subscription_url_here"
```

## 常见问题

### Q: 服务器启动失败
A: 检查以下几点:
1. Python3是否已安装: `python3 --version`
2. 依赖是否安装: `pip3 list | grep -i flask`
3. 端口5000是否被占用: `lsof -i :5000`

### Q: 解密后只有direct outbounds
A: 可能的原因:
1. 订阅URL无效或返回空内容
2. 订阅内容格式不被支持
3. 网络连接问题
4. 加密参数不匹配

### Q: 如何调试具体的订阅处理
A: 在 `main.py` 中添加调试输出:
```python
# 在 get_nodes 函数中
print(f"Processing URL: {url}")
print(f"Content type: {type(content)}")
print(f"Content preview: {str(content)[:200]}")

# 在 process_subscribes 函数中  
print(f"Subscribe config: {subscribe}")
print(f"Nodes found: {len(_nodes) if _nodes else 0}")
```

## 环境变量配置

服务器会自动设置以下环境变量:
- `TEMP_JSON_DATA`: 默认订阅配置
- `FLASK_DEBUG`: 启用Flask调试模式

如需自定义配置，可以在 `run_local.py` 中修改 `default_temp_json` 变量。

## 与Vercel的区别

本地服务器与Vercel部署的主要区别:
1. **环境变量**: 本地使用默认配置，Vercel使用部署时设置的环境变量
2. **依赖管理**: 本地需要手动安装依赖，Vercel自动处理
3. **调试**: 本地可以实时修改代码和添加调试输出
4. **网络**: 本地可能有不同的网络环境和防火墙设置

## 生产环境注意事项

如果要将本地服务器用于生产环境:
1. 修改 `run_local.py` 中的 `host='0.0.0.0'` 以允许外部访问
2. 使用 `gunicorn` 或 `uwsgi` 替代 Flask 开发服务器
3. 设置适当的安全配置和防火墙规则
4. 配置 HTTPS 和域名