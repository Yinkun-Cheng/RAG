"""
检索工具单元测试

测试 SearchPRDTool、SearchTestCaseTool 和 GetRelatedCasesTool 的功能。
这些工具现在通过调用 Go 后端的搜索 API 实现。
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.tool.retrieval_tools import (
    SearchPRDTool,
    SearchTestCaseTool,
    GetRelatedCasesTool,
)
from app.tool.base import ToolError


@pytest.fixture
def backend_url():
    """Go 后端 URL"""
    return "http://localhost:8080"


@pytest.fixture
def search_prd_tool(backend_url):
    """创建 SearchPRDTool 实例"""
    return SearchPRDTool(backend_url=backend_url)


@pytest.fixture
def search_testcase_tool(backend_url):
    """创建 SearchTestCaseTool 实例"""
    return SearchTestCaseTool(backend_url=backend_url)


@pytest.fixture
def get_related_cases_tool(backend_url):
    """创建 GetRelatedCasesTool 实例"""
    return GetRelatedCasesTool(backend_url=backend_url)


# ============================================================================
# SearchPRDTool 测试
# ============================================================================

@pytest.mark.asyncio
async def test_search_prd_tool_success(search_prd_tool):
    """测试 PRD 搜索成功"""
    # 模拟 Go 后端响应
    mock_response = {
        "code": 200,
        "message": "success",
        "data": {
            "results": [
                {
                    "id": "prd-1",
                    "title": "用户登录功能",
                    "content": "实现用户登录功能...",
                    "score": 0.95,
                    "metadata": {"version": "1.0"}
                },
                {
                    "id": "prd-2",
                    "title": "用户注册功能",
                    "content": "实现用户注册功能...",
                    "score": 0.85,
                    "metadata": {"version": "1.0"}
                }
            ],
            "total": 2,
            "query": "用户登录",
            "type": "prd"
        }
    }
    
    # 模拟 HTTP 客户端
    with patch.object(search_prd_tool.http_client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        
        # 执行搜索
        results = await search_prd_tool.execute(
            query="用户登录",
            limit=5,
            threshold=0.7,
            project_id="project-123"
        )
        
        # 验证结果
        assert len(results) == 2
        assert results[0]["id"] == "prd-1"
        assert results[0]["title"] == "用户登录功能"
        assert results[0]["score"] == 0.95
        assert results[1]["id"] == "prd-2"
        
        # 验证 API 调用
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "project-123" in call_args[0][0]  # URL 包含 project_id


@pytest.mark.asyncio
async def test_search_prd_tool_missing_project_id(search_prd_tool):
    """测试缺少 project_id 参数"""
    with pytest.raises(ToolError) as exc_info:
        await search_prd_tool.execute(
            query="用户登录",
            limit=5,
            threshold=0.7,
            project_id=None  # 缺少 project_id
        )
    
    assert "project_id 是必需参数" in str(exc_info.value)


@pytest.mark.asyncio
async def test_search_prd_tool_api_error(search_prd_tool):
    """测试 API 返回错误"""
    # 模拟 HTTP 错误响应
    with patch.object(search_prd_tool.http_client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock(
            status_code=500,
            text="Internal Server Error"
        )
        
        # 执行搜索应该抛出异常
        with pytest.raises(ToolError) as exc_info:
            await search_prd_tool.execute(
                query="用户登录",
                limit=5,
                threshold=0.7,
                project_id="project-123"
            )
        
        assert "Go 后端搜索 API 返回错误: 500" in str(exc_info.value)


# ============================================================================
# SearchTestCaseTool 测试
# ============================================================================

@pytest.mark.asyncio
async def test_search_testcase_tool_success(search_testcase_tool):
    """测试测试用例搜索成功"""
    # 模拟 Go 后端响应
    mock_response = {
        "code": 200,
        "message": "success",
        "data": {
            "results": [
                {
                    "id": "tc-1",
                    "title": "测试用户登录成功",
                    "content": "前置条件: 用户已注册...",
                    "score": 0.92,
                    "metadata": {"priority": "high", "type": "functional"}
                },
                {
                    "id": "tc-2",
                    "title": "测试用户登录失败",
                    "content": "前置条件: 用户未注册...",
                    "score": 0.88,
                    "metadata": {"priority": "medium", "type": "exception"}
                }
            ],
            "total": 2,
            "query": "用户登录",
            "type": "testcase"
        }
    }
    
    # 模拟 HTTP 客户端
    with patch.object(search_testcase_tool.http_client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        
        # 执行搜索
        results = await search_testcase_tool.execute(
            query="用户登录",
            limit=10,
            threshold=0.7,
            project_id="project-123"
        )
        
        # 验证结果
        assert len(results) == 2
        assert results[0]["id"] == "tc-1"
        assert results[0]["title"] == "测试用户登录成功"
        assert results[0]["metadata"]["priority"] == "high"


@pytest.mark.asyncio
async def test_search_testcase_tool_with_priority_filter(search_testcase_tool):
    """测试带优先级过滤的测试用例搜索"""
    # 模拟 Go 后端响应（包含不同优先级的用例）
    mock_response = {
        "code": 200,
        "message": "success",
        "data": {
            "results": [
                {
                    "id": "tc-1",
                    "title": "高优先级用例",
                    "content": "...",
                    "score": 0.92,
                    "metadata": {"priority": "high"}
                },
                {
                    "id": "tc-2",
                    "title": "中优先级用例",
                    "content": "...",
                    "score": 0.88,
                    "metadata": {"priority": "medium"}
                }
            ],
            "total": 2,
            "query": "用户登录",
            "type": "testcase"
        }
    }
    
    # 模拟 HTTP 客户端
    with patch.object(search_testcase_tool.http_client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        
        # 执行搜索，只要高优先级
        results = await search_testcase_tool.execute(
            query="用户登录",
            limit=10,
            threshold=0.7,
            project_id="project-123",
            priority="high"  # 过滤高优先级
        )
        
        # 验证结果：只返回高优先级用例
        assert len(results) == 1
        assert results[0]["id"] == "tc-1"
        assert results[0]["metadata"]["priority"] == "high"


# ============================================================================
# GetRelatedCasesTool 测试
# ============================================================================

@pytest.mark.asyncio
async def test_get_related_cases_tool_success(get_related_cases_tool):
    """测试获取相关测试用例成功"""
    # 模拟 Go 后端推荐 API 响应
    mock_response = {
        "code": 200,
        "message": "success",
        "data": {
            "results": [
                {
                    "id": "tc-2",
                    "title": "相关用例 1",
                    "content": "...",
                    "score": 0.85,
                    "metadata": {"priority": "high"}
                },
                {
                    "id": "tc-3",
                    "title": "相关用例 2",
                    "content": "...",
                    "score": 0.80,
                    "metadata": {"priority": "medium"}
                }
            ],
            "total": 2,
            "query": "基于 testcase 的推荐",
            "type": "all"
        }
    }
    
    # 模拟 HTTP 客户端
    with patch.object(get_related_cases_tool.http_client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        
        # 执行查询
        results = await get_related_cases_tool.execute(
            test_case_id="tc-1",
            project_id="project-123",
            limit=5
        )
        
        # 验证结果
        assert len(results) == 2
        assert results[0]["id"] == "tc-2"
        assert results[1]["id"] == "tc-3"
        
        # 验证 API 调用
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "tc-1" in call_args[0][0]  # URL 包含 test_case_id
        assert "project-123" in call_args[0][0]  # URL 包含 project_id


@pytest.mark.asyncio
async def test_get_related_cases_tool_missing_project_id(get_related_cases_tool):
    """测试缺少 project_id 参数"""
    with pytest.raises(ToolError) as exc_info:
        await get_related_cases_tool.execute(
            test_case_id="tc-1",
            project_id=None,  # 缺少 project_id
            limit=5
        )
    
    assert "project_id 是必需参数" in str(exc_info.value)
