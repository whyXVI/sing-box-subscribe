#!/usr/bin/env python3
"""
本地运行服务器脚本
"""
import os
import sys
import json
from api.app import app

def setup_local_environment():
    """设置本地环境变量"""
    
    # 设置默认的临时JSON数据
    default_temp_json = {
        "subscribes": [
            {
                "url": "",
                "tag": "default", 
                "enabled": True,
                "emoji": 1,
                "subgroup": "",
                "prefix": "",
                "ex-node-name": "",
                "User-Agent": "v2rayng"
            }
        ],
        "auto_set_outbounds_dns": {
            "proxy": "",
            "direct": ""
        },
        "save_config_path": "./config.json",
        "auto_backup": False,
        "exclude_protocol": "",
        "config_template": "",
        "Only-nodes": False
    }
    
    # 设置环境变量
    os.environ['TEMP_JSON_DATA'] = json.dumps(default_temp_json, ensure_ascii=False)
    
    # 设置调试模式
    os.environ['FLASK_DEBUG'] = '1'
    
    print("本地环境设置完成")
    print(f"TEMP_JSON_DATA: {os.environ.get('TEMP_JSON_DATA', 'Not set')}")

def main():
    """主函数"""
    print("=== 本地Sing-Box订阅转换服务器 ===")
    
    # 检查依赖
    try:
        import flask
        import requests
        import yaml
        print("✓ 所有依赖已安装")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 设置环境
    setup_local_environment()
    
    # 启动服务器
    print("\n启动本地服务器...")
    print("服务器地址: http://127.0.0.1:5000")
    print("API端点:")
    print("  - 管理界面: http://127.0.0.1:5000/")
    print("  - 加密订阅: http://127.0.0.1:5000/dev/<encrypted_data>")
    print("  - 普通订阅: http://127.0.0.1:5000/config/<subscription_url>")
    print("\n按 Ctrl+C 停止服务器")
    
    try:
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=False  # 避免重复启动
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")

if __name__ == '__main__':
    main()