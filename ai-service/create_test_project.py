"""
创建测试项目

用于在 Go 后端创建测试项目
"""

import requests
import json

# Go 后端 URL
GO_BACKEND_URL = "http://localhost:8080"

def create_project():
    """创建测试项目"""
    print("创建测试项目...")
    
    url = f"{GO_BACKEND_URL}/api/v1/projects"
    payload = {
        "name": "AI 测试助手项目",
        "description": "用于测试 AI Test Assistant Service 的项目"
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"✅ 项目创建成功!")
            print(f"项目 ID: {result.get('data', {}).get('id')}")
            print(f"项目名称: {result.get('data', {}).get('name')}")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ 创建失败: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def list_projects():
    """列出所有项目"""
    print("\n列出所有项目...")
    
    url = f"{GO_BACKEND_URL}/api/v1/projects"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            projects = result.get('data', [])
            print(f"✅ 找到 {len(projects)} 个项目:")
            for project in projects:
                print(f"  - ID: {project.get('id')}, 名称: {project.get('name')}")
            return True
        else:
            print(f"❌ 获取失败: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Go 后端测试项目创建工具")
    print("=" * 60)
    
    # 先列出现有项目
    list_projects()
    
    # 创建新项目
    create_project()
    
    # 再次列出项目
    list_projects()
    
    print("\n=" * 60)
    print("完成！现在可以使用项目 ID 进行测试了")
    print("=" * 60)
