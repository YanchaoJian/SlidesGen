import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import json

def load_env_config():
    """从根目录的 .env 文件加载配置"""
    # 获取项目根目录（假设 test/ 在项目根目录下）
    root_dir = Path(__file__).parent.parent
    env_path = root_dir / '.env'
    
    if not env_path.exists():
        raise FileNotFoundError(f"未找到 .env 文件: {env_path}")
    
    load_dotenv(env_path)
    
    config = {
        'base_url': os.getenv('OPENAI_BASE_URL'),
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': os.getenv('OPENAI_MODEL')
    }
    
    # 检查配置是否完整
    missing = [k for k, v in config.items() if not v]
    if missing:
        raise ValueError(f".env 文件缺少以下配置: {missing}")
    
    return config

def test_connection(config):
    """测试 API 连接"""
    base_url = config['base_url'].rstrip('/')
    api_key = config['api_key']
    model = config['model']
    
    print(f"正在测试连接到: {base_url}")
    print(f"使用模型: {model}")
    print("-" * 50)
    
    # 根据不同 API 格式调整端点
    endpoints_to_try = [
        f"{base_url}/models",
        f"{base_url}/v1/models",
        f"{base_url}/api/models",
    ]
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 尝试获取模型列表
    for endpoint in endpoints_to_try:
        try:
            print(f"尝试端点: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ 连接成功! 状态码: {response.status_code}")
                data = response.json()
                
                # 检查模型是否存在
                if 'data' in data and isinstance(data['data'], list):
                    models = [m.get('id', m.get('name')) for m in data['data']]
                    print(f"可用模型数: {len(models)}")
                    
                    if model in models:
                        print(f"✅ 目标模型 '{model}' 可用")
                    else:
                        print(f"⚠️ 目标模型 '{model}' 不在列表中")
                        print(f"可用模型: {models[:5]}...")
                
                return True
            else:
                print(f"❌ 状态码: {response.status_code}")
                print(f"响应: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败: 无法连接到服务器")
        except requests.exceptions.Timeout:
            print(f"❌ 请求超时")
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
    
    return False

def test_chat_completion(config):
    """测试简单的对话请求"""
    base_url = config['base_url'].rstrip('/')
    api_key = config['api_key']
    model = config['model']
    
    print("\n" + "=" * 50)
    print("测试对话接口...")
    print("-" * 50)
    
    # 常见端点格式
    chat_endpoints = [
        f"{base_url}/chat/completions",
        f"{base_url}/v1/chat/completions",
        f"{base_url}/api/chat",
    ]
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "你好，这是一个测试消息。请回复'测试成功'。"}
        ],
        "max_tokens": 50
    }
    
    for endpoint in chat_endpoints:
        try:
            print(f"尝试: {endpoint}")
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 对话接口测试成功!")
                
                # 解析回复
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0].get('message', {}).get('content', '')
                    print(f"模型回复: {content}")
                return True
            else:
                print(f"❌ 状态码: {response.status_code}")
                print(f"错误信息: {response.text[:300]}")
                
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
    
    return False

if __name__ == "__main__":
    try:
        print("=" * 50)
        print("API 连接测试工具")
        print("=" * 50)
        
        # 加载配置
        config = load_env_config()
        print(f"\n配置加载成功:")
        print(f"  Base URL: {config['base_url']}")
        print(f"  Model: {config['model']}")
        print(f"  API Key: {'*' * 10}{config['api_key'][-4:] if len(config['api_key']) > 4 else ''}")
        
        # 测试连接
        conn_success = test_connection(config)
        
        if conn_success:
            # 测试对话
            chat_success = test_chat_completion(config)
            
            if chat_success:
                print("\n" + "=" * 50)
                print("🎉 所有测试通过！API 配置正确。")
                print("=" * 50)
            else:
                print("\n⚠️ 连接成功但对话接口测试失败")
        else:
            print("\n❌ 连接测试失败，请检查:")
            print("   1. .env 文件中的 baseurl 是否正确")
            print("   2. API 服务是否运行")
            print("   3. 网络连接是否正常")
            
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        print("\n请确保 .env 文件位于项目根目录，并包含以下内容:")
        print("  baseurl=https://api.example.com")
        print("  apikey=your-api-key")
        print("  model=gpt-3.5-turbo")
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")