#!/bin/bash
# 本地服务器启动脚本

echo "=== Sing-Box 订阅转换本地服务器 ==="
echo ""

# 检查Python版本
python3 --version
if [ $? -ne 0 ]; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查并安装依赖
echo "检查依赖..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "警告: 依赖安装可能有问题，但会尝试继续运行"
    fi
else
    echo "警告: 未找到requirements.txt文件"
fi

# 设置权限
chmod +x run_local.py
chmod +x test_local_server.py

echo ""
echo "启动本地服务器..."
echo "服务器地址: http://127.0.0.1:5000"
echo ""
echo "可用端点:"
echo "  管理界面: http://127.0.0.1:5000/"
echo "  加密订阅: http://127.0.0.1:5000/dev/<encrypted_data>"
echo "  普通订阅: http://127.0.0.1:5000/config/<subscription_url>"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
python3 run_local.py