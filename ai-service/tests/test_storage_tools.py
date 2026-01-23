"""
存储工具单元测试

测试 SaveTestCaseTool 和 UpdateTestCaseTool 的功能。
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.tool.storage_tools import SaveTestCaseTool, UpdateTestCaseTool
from app.tool.base import ToolError


# ============================================================================
# SaveTestCaseTool 测试
# ============================================================================

@pytest.mark.asyncio
async def test_save_test_case_tool_success():
    """测试保存测试用例成功"""
    tool = SaveTestCaseTool(go_backend_url="http://localhost:8080")
    
    # 准备测试用例数据
    test_case = {
        "title": "测试用户登录功能",
        "preconditions": "用户已注册",
        "steps": [
            {
                "step_number": 1,
                "action": "打开登录页面",
                "expected": "显示登录表单"
            },
            {
                "step_number": 2,
                "action": "输入用户名密码",
                "expected": "输入成功"
            }
        ],
        "expected_result": "登录成功",
        "priority": "high",
        "type": "functional"
    }
    
    # Mock HTTP 响应
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 0,
        "message": "success",
        "data": {
            "id": "test-case-123",
            "title": "测试用户登录功能",
            "version": 1,
            "created_at": "2024-01-01T00:00:00Z"
        }
    }
    
    # Mock httpx.AsyncClient
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        # 执行保存
        result = await tool.execute(
            project_id="project-123",
            test_case=test_case
        )
        
        # 验证结果
        assert result["id"] == "test-case-123"
        assert result["title"] == "测试用户登录功能"
        assert result["version"] == 1


@pytest.mark.asyncio
async def test_save_test_case_tool_with_optional_fields():
    """测试保存测试用例（包含可选字段）"""
    tool = SaveTestCaseTool(go_backend_url="http://localhost:8080")
    
    test_case = {
        "title": "测试用例",
        "preconditions": "前置条件",
        "steps": [],
        "expected_result": "预期结果",
        "priority": "medium",
        "type": "functional"
    }
    
    # Mock HTTP 响应
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 0,
        "data": {"id": "test-123"}
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        # 执行保存（包含可选字段）
        result = await tool.execute(
            project_id="project-123",
            test_case=test_case,
            prd_id="prd-456",
            module_id="module-789",
            tag_ids=["tag1", "tag2"]
        )
        
        # 验证结果
        assert result["id"] == "test-123"
        
        # 验证请求数据包含可选字段
        call_args = mock_post.call_args
        request_data = call_args[1]["json"]
        assert request_data["prd_id"] == "prd-456"
        assert request_data["module_id"] == "module-789"
        assert request_data["tag_ids"] == ["tag1", "tag2"]


@pytest.mark.asyncio
async def test_save_test_case_tool_http_error():
    """测试 HTTP 错误处理"""
    tool = SaveTestCaseTool(go_backend_url="http://localhost:8080")
    
    test_case = {
        "title": "测试用例",
        "preconditions": "",
        "steps": [],
        "expected_result": "",
        "priority": "medium",
        "type": "functional"
    }
    
    # Mock HTTP 错误响应
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        # 执行保存，应该抛出异常
        with pytest.raises(ToolError) as exc_info:
            await tool.execute(
                project_id="project-123",
                test_case=test_case
            )
        
        # 验证异常信息
        assert "HTTP 500" in str(exc_info.value)


@pytest.mark.asyncio
async def test_save_test_case_tool_invalid_response():
    """测试无效响应格式"""
    tool = SaveTestCaseTool(go_backend_url="http://localhost:8080")
    
    test_case = {
        "title": "测试用例",
        "preconditions": "",
        "steps": [],
        "expected_result": "",
        "priority": "medium",
        "type": "functional"
    }
    
    # Mock 无效响应
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 1,  # 错误代码
        "message": "error"
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        # 执行保存，应该抛出异常
        with pytest.raises(ToolError) as exc_info:
            await tool.execute(
                project_id="project-123",
                test_case=test_case
            )
        
        # 验证异常信息
        assert "响应格式错误" in str(exc_info.value)


# ============================================================================
# UpdateTestCaseTool 测试
# ============================================================================

@pytest.mark.asyncio
async def test_update_test_case_tool_success():
    """测试更新测试用例成功"""
    tool = UpdateTestCaseTool(go_backend_url="http://localhost:8080")
    
    # 准备更新数据
    test_case = {
        "title": "测试用户登录功能（更新）",
        "preconditions": "用户已注册且账户未锁定",
        "steps": [
            {
                "step_number": 1,
                "action": "打开登录页面",
                "expected": "显示登录表单"
            }
        ],
        "expected_result": "登录成功",
        "priority": "high",
        "type": "functional"
    }
    
    # Mock HTTP 响应
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 0,
        "message": "success",
        "data": {
            "id": "test-case-123",
            "title": "测试用户登录功能（更新）",
            "version": 2,
            "updated_at": "2024-01-02T00:00:00Z"
        }
    }
    
    # Mock httpx.AsyncClient
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.put = AsyncMock(
            return_value=mock_response
        )
        
        # 执行更新
        result = await tool.execute(
            project_id="project-123",
            test_case_id="test-case-123",
            test_case=test_case
        )
        
        # 验证结果
        assert result["id"] == "test-case-123"
        assert result["version"] == 2


@pytest.mark.asyncio
async def test_update_test_case_tool_with_change_description():
    """测试更新测试用例（包含变更说明）"""
    tool = UpdateTestCaseTool(go_backend_url="http://localhost:8080")
    
    test_case = {
        "title": "测试用例",
        "preconditions": "前置条件",
        "steps": [],
        "expected_result": "预期结果",
        "priority": "medium",
        "type": "functional"
    }
    
    # Mock HTTP 响应
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 0,
        "data": {"id": "test-123", "version": 2}
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_put = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.put = mock_put
        
        # 执行更新（包含变更说明）
        result = await tool.execute(
            project_id="project-123",
            test_case_id="test-123",
            test_case=test_case,
            change_description="更新测试步骤"
        )
        
        # 验证结果
        assert result["version"] == 2
        
        # 验证请求数据包含变更说明
        call_args = mock_put.call_args
        request_data = call_args[1]["json"]
        assert request_data["change_description"] == "更新测试步骤"


@pytest.mark.asyncio
async def test_update_test_case_tool_http_error():
    """测试更新时的 HTTP 错误"""
    tool = UpdateTestCaseTool(go_backend_url="http://localhost:8080")
    
    test_case = {
        "title": "测试用例",
        "preconditions": "",
        "steps": [],
        "expected_result": "",
        "priority": "medium",
        "type": "functional"
    }
    
    # Mock HTTP 错误响应
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Test case not found"
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.put = AsyncMock(
            return_value=mock_response
        )
        
        # 执行更新，应该抛出异常
        with pytest.raises(ToolError) as exc_info:
            await tool.execute(
                project_id="project-123",
                test_case_id="non-existent",
                test_case=test_case
            )
        
        # 验证异常信息
        assert "HTTP 404" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_test_case_tool_url_construction():
    """测试 URL 构建正确性"""
    tool = UpdateTestCaseTool(go_backend_url="http://localhost:8080/")  # 带尾部斜杠
    
    test_case = {
        "title": "测试用例",
        "preconditions": "",
        "steps": [],
        "expected_result": "",
        "priority": "medium",
        "type": "functional"
    }
    
    # Mock HTTP 响应
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 0,
        "data": {"id": "test-123"}
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_put = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.put = mock_put
        
        # 执行更新
        await tool.execute(
            project_id="project-123",
            test_case_id="test-456",
            test_case=test_case
        )
        
        # 验证 URL 构建正确（没有双斜杠）
        call_args = mock_put.call_args
        url = call_args[0][0]
        assert url == "http://localhost:8080/api/v1/projects/project-123/testcases/test-456"
        assert "//" not in url.replace("http://", "")
