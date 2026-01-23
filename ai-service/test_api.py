"""
API 测试脚本

用于测试 AI Test Assistant Service 的 API 端点
"""

import requests
import json
import sys

# API 基础 URL
BASE_URL = "http://localhost:5000"

def test_health():
    """测试健康检查端点"""
    print("\n" + "="*60)
    print("测试 1: 健康检查")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_generate_simple():
    """测试简单的测试用例生成"""
    print("\n" + "="*60)
    print("测试 2: 生成测试用例（简单需求）")
    print("="*60)
    
    payload = {
        "message": "本地播放器：支持播放本地音频文件（MP3、WAV、FLAC 格式）",
        "project_id": "22609631-524b-4490-8c02-33f271fea409"
    }
    
    print(f"请求: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai/generate",
            json=payload,
            timeout=120  # 2分钟超时
        )
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 成功!")
            print(f"任务类型: {result.get('task_type')}")
            print(f"对话 ID: {result.get('conversation_id')}")
            
            if result.get('test_cases'):
                print(f"\n生成的测试用例数量: {len(result['test_cases'])}")
                print(f"\n第一个测试用例:")
                print(json.dumps(result['test_cases'][0], indent=2, ensure_ascii=False))
            elif result.get('analysis'):
                print(f"\n需求分析结果:")
                print(json.dumps(result['analysis'], indent=2, ensure_ascii=False))
            else:
                print(f"\n完整响应:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('metadata'):
                print(f"\n元数据:")
                print(json.dumps(result['metadata'], indent=2, ensure_ascii=False))
            
            return True
        else:
            print(f"❌ 失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_generate_complex():
    """测试复杂需求的测试用例生成"""
    print("\n" + "="*60)
    print("测试 3: 生成测试用例（复杂需求）")
    print("="*60)
    
    payload = {
        "message": """
        本地播放器播放控制功能需求：
        1. 支持播放、暂停、停止操作
        2. 支持上一曲、下一曲切换
        3. 支持进度条拖动调整播放位置
        4. 支持音量调节（0-100）
        5. 支持播放模式切换（顺序播放、单曲循环、随机播放）
        """,
        "project_id": "22609631-524b-4490-8c02-33f271fea409"
    }
    
    print(f"请求: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai/generate",
            json=payload,
            timeout=120
        )
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 成功!")
            print(f"任务类型: {result.get('task_type')}")
            
            if result.get('test_cases'):
                print(f"\n生成的测试用例数量: {len(result['test_cases'])}")
                for i, tc in enumerate(result['test_cases'][:3], 1):  # 只显示前3个
                    print(f"\n测试用例 {i}: {tc.get('title')}")
                    print(f"  优先级: {tc.get('priority')}")
                    print(f"  类型: {tc.get('type')}")
            elif result.get('analysis'):
                print(f"\n需求分析结果:")
                print(json.dumps(result['analysis'], indent=2, ensure_ascii=False))
            else:
                print(f"\n完整响应:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            
            return True
        else:
            print(f"❌ 失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_chat_stream():
    """测试流式对话"""
    print("\n" + "="*60)
    print("测试 4: 流式对话（SSE）")
    print("="*60)
    
    payload = {
        "message": "帮我分析一下本地播放器的播放列表管理功能的测试点",
        "project_id": "22609631-524b-4490-8c02-33f271fea409",
        "stream": True
    }
    
    print(f"请求: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai/chat/stream",
            json=payload,
            stream=True,
            timeout=120
        )
        
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"\n✅ 开始接收流式响应:")
            print("-" * 60)
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data = json.loads(line_str[6:])
                        
                        if data['type'] == 'start':
                            print(f"[开始] 对话 ID: {data['conversation_id']}")
                        elif data['type'] == 'content':
                            print(data['content'], end='', flush=True)
                        elif data['type'] == 'done':
                            print(f"\n[完成] 对话 ID: {data['conversation_id']}")
                        elif data['type'] == 'error':
                            print(f"\n[错误] {data['error']}")
            
            print("-" * 60)
            return True
        else:
            print(f"❌ 失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_list_conversations(project_id: str = "22609631-524b-4490-8c02-33f271fea409"):
    """测试列出对话"""
    print("\n" + "="*60)
    print("测试 5: 列出对话")
    print("="*60)
    
    print(f"查询参数: project_id={project_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/ai/conversations", params={"project_id": project_id})
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 成功!")
            print(f"对话总数: {result.get('total')}")
            
            if result.get('conversations'):
                print(f"\n对话列表:")
                for conv in result['conversations'][:5]:  # 只显示前5个
                    print(f"  - ID: {conv['conversation_id']}")
                    print(f"    项目: {conv['project_id']}")
                    print(f"    消息数: {conv['message_count']}")
                    print(f"    更新时间: {conv['updated_at']}")
            
            return True
        else:
            print(f"❌ 失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("AI Test Assistant Service - API 测试")
    print("="*60)
    print(f"API 地址: {BASE_URL}")
    print("\n请确保服务已启动: python main.py")
    print("="*60)
    
    results = []
    
    # 运行测试
    results.append(("健康检查", test_health()))
    
    # 询问是否继续（因为后续测试需要真实的 API 密钥）
    print("\n" + "="*60)
    print("注意: 后续测试需要真实的 BRConnector API 密钥")
    print("请确保 .env 文件中配置了 BRCONNECTOR_API_KEY")
    print("="*60)
    
    choice = input("\n是否继续测试? (y/n): ").strip().lower()
    if choice != 'y':
        print("\n测试已取消")
        return
    
    results.append(("简单测试用例生成", test_generate_simple()))
    results.append(("复杂测试用例生成", test_generate_complex()))
    results.append(("流式对话", test_chat_stream()))
    results.append(("列出对话", test_list_conversations()))
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n总计: {passed}/{total} 通过")
    print("="*60)


if __name__ == "__main__":
    main()
