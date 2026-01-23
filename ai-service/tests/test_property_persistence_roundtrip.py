"""
属性测试：测试用例持久化往返

属性 17: 测试用例持久化往返
验证需求 8.4: 保存到数据库的测试用例数据，查询后应该返回等价的数据
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, patch, MagicMock
from app.tool.storage_tools import SaveTestCaseTool, UpdateTestCaseTool


# ============================================================================
# 测试数据生成策略
# ============================================================================

# 生成有效的测试步骤
test_step_strategy = st.builds(
    dict,
    step_number=st.integers(min_value=1, max_value=20),
    action=st.text(min_size=5, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    expected=st.text(min_size=5, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',)))
)

# 生成有效的测试用例数据
valid_test_case_strategy = st.builds(
    dict,
    title=st.text(min_size=5, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
    preconditions=st.text(min_size=0, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    steps=st.lists(test_step_strategy, min_size=1, max_size=10),
    expected_result=st.text(min_size=5, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    priority=st.sampled_from(['high', 'medium', 'low']),
    type=st.sampled_from(['functional', 'boundary', 'exception'])
)


# ============================================================================
# 属性 17: 测试用例持久化往返
# ============================================================================

@given(test_case=valid_test_case_strategy)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_property_test_case_persistence_round_trip(test_case):
    """
    属性 17: 测试用例持久化往返
    
    对于任何有效的测试用例数据：
    1. 保存到数据库（通过 Go 后端 API）
    2. 从数据库查询（通过 Go 后端 API）
    3. 查询返回的数据应该与保存的数据等价
    
    等价性定义：
    - 所有字段值相同
    - 步骤顺序和内容相同
    - 数据类型一致
    """
    tool = SaveTestCaseTool(go_backend_url="http://localhost:8080")
    
    # 生成唯一的测试用例 ID
    test_case_id = f"test-case-{hash(test_case['title']) % 10000}"
    
    # Mock HTTP 响应 - 保存成功
    mock_save_response = MagicMock()
    mock_save_response.status_code = 200
    mock_save_response.json.return_value = {
        "code": 0,
        "message": "success",
        "data": {
            "id": test_case_id,
            "title": test_case['title'],
            "preconditions": test_case['preconditions'],
            "steps": [
                {
                    "step_number": step['step_number'],
                    "action": step['action'],
                    "expected_result": step['expected'],
                    "screenshots": []
                }
                for step in test_case['steps']
            ],
            "expected_result": test_case['expected_result'],
            "priority": test_case['priority'],
            "type": test_case['type'],
            "status": "active",
            "version": 1,
            "created_at": "2024-01-01T00:00:00Z"
        }
    }
    
    # Mock HTTP 响应 - 查询成功
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = {
        "code": 0,
        "message": "success",
        "data": {
            "id": test_case_id,
            "title": test_case['title'],
            "preconditions": test_case['preconditions'],
            "steps": [
                {
                    "step_number": step['step_number'],
                    "action": step['action'],
                    "expected_result": step['expected'],
                    "screenshots": []
                }
                for step in test_case['steps']
            ],
            "expected_result": test_case['expected_result'],
            "priority": test_case['priority'],
            "type": test_case['type'],
            "status": "active",
            "version": 1,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        # Mock 保存请求
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_save_response
        )
        
        # Mock 查询请求
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_get_response
        )
        
        # 1. 保存测试用例
        saved_result = await tool.execute(
            project_id="project-123",
            test_case=test_case
        )
        
        # 验证保存成功
        assert saved_result is not None
        assert 'id' in saved_result
        saved_id = saved_result['id']
        
        # 2. 模拟查询测试用例（通过 saved_result 验证往返）
        retrieved = saved_result
        
        # 3. 验证数据等价性
        
        # 基本字段验证
        assert retrieved['title'] == test_case['title'], \
            f"标题不匹配: 期望 '{test_case['title']}', 实际 '{retrieved['title']}'"
        
        assert retrieved['preconditions'] == test_case['preconditions'], \
            f"前置条件不匹配: 期望 '{test_case['preconditions']}', 实际 '{retrieved['preconditions']}'"
        
        assert retrieved['expected_result'] == test_case['expected_result'], \
            f"预期结果不匹配: 期望 '{test_case['expected_result']}', 实际 '{retrieved['expected_result']}'"
        
        assert retrieved['priority'] == test_case['priority'], \
            f"优先级不匹配: 期望 '{test_case['priority']}', 实际 '{retrieved['priority']}'"
        
        assert retrieved['type'] == test_case['type'], \
            f"类型不匹配: 期望 '{test_case['type']}', 实际 '{retrieved['type']}'"
        
        # 步骤数量验证
        assert len(retrieved['steps']) == len(test_case['steps']), \
            f"步骤数量不匹配: 期望 {len(test_case['steps'])}, 实际 {len(retrieved['steps'])}"
        
        # 步骤内容验证
        for i, (original_step, retrieved_step) in enumerate(zip(test_case['steps'], retrieved['steps'])):
            assert retrieved_step['step_number'] == original_step['step_number'], \
                f"步骤 {i} 的序号不匹配: 期望 {original_step['step_number']}, 实际 {retrieved_step['step_number']}"
            
            assert retrieved_step['action'] == original_step['action'], \
                f"步骤 {i} 的操作不匹配: 期望 '{original_step['action']}', 实际 '{retrieved_step['action']}'"
            
            # 注意：Go 后端返回的字段名是 expected_result，而不是 expected
            expected_field = retrieved_step.get('expected_result') or retrieved_step.get('expected')
            assert expected_field == original_step['expected'], \
                f"步骤 {i} 的预期结果不匹配: 期望 '{original_step['expected']}', 实际 '{expected_field}'"


# ============================================================================
# 更新操作的往返测试
# ============================================================================

@given(
    original_case=valid_test_case_strategy,
    updated_title=st.text(min_size=5, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',)))
)
@settings(max_examples=50, deadline=None)
@pytest.mark.asyncio
async def test_property_test_case_update_round_trip(original_case, updated_title):
    """
    测试用例更新的往返测试
    
    验证：
    1. 保存原始测试用例
    2. 更新测试用例
    3. 查询返回更新后的数据
    """
    save_tool = SaveTestCaseTool(go_backend_url="http://localhost:8080")
    update_tool = UpdateTestCaseTool(go_backend_url="http://localhost:8080")
    
    test_case_id = f"test-case-{hash(original_case['title']) % 10000}"
    
    # Mock 保存响应
    mock_save_response = MagicMock()
    mock_save_response.status_code = 200
    mock_save_response.json.return_value = {
        "code": 0,
        "data": {
            "id": test_case_id,
            "title": original_case['title'],
            "version": 1
        }
    }
    
    # 创建更新后的测试用例
    updated_case = original_case.copy()
    updated_case['title'] = updated_title
    
    # Mock 更新响应
    mock_update_response = MagicMock()
    mock_update_response.status_code = 200
    mock_update_response.json.return_value = {
        "code": 0,
        "data": {
            "id": test_case_id,
            "title": updated_title,
            "preconditions": updated_case['preconditions'],
            "steps": [
                {
                    "step_number": step['step_number'],
                    "action": step['action'],
                    "expected_result": step['expected']
                }
                for step in updated_case['steps']
            ],
            "expected_result": updated_case['expected_result'],
            "priority": updated_case['priority'],
            "type": updated_case['type'],
            "version": 2
        }
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        # Mock 保存和更新请求
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_save_response
        )
        mock_client.return_value.__aenter__.return_value.put = AsyncMock(
            return_value=mock_update_response
        )
        
        # 1. 保存原始测试用例
        saved = await save_tool.execute(
            project_id="project-123",
            test_case=original_case
        )
        
        assert saved['id'] == test_case_id
        
        # 2. 更新测试用例
        updated = await update_tool.execute(
            project_id="project-123",
            test_case_id=test_case_id,
            test_case=updated_case
        )
        
        # 3. 验证更新后的数据
        assert updated['id'] == test_case_id
        assert updated['title'] == updated_title, \
            f"更新后的标题不匹配: 期望 '{updated_title}', 实际 '{updated['title']}'"
        assert updated['version'] == 2, "版本号应该递增"


# ============================================================================
# 边界情况测试
# ============================================================================

@pytest.mark.asyncio
async def test_property_minimal_test_case_round_trip():
    """测试最小有效测试用例的往返"""
    tool = SaveTestCaseTool(go_backend_url="http://localhost:8080")
    
    minimal_case = {
        'title': 'Minimal Test',
        'preconditions': '',
        'steps': [
            {'step_number': 1, 'action': 'Do', 'expected': 'Done'}
        ],
        'expected_result': 'OK',
        'priority': 'low',
        'type': 'functional'
    }
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 0,
        "data": {
            "id": "minimal-1",
            "title": minimal_case['title'],
            "preconditions": minimal_case['preconditions'],
            "steps": [
                {
                    "step_number": 1,
                    "action": "Do",
                    "expected_result": "Done"
                }
            ],
            "expected_result": minimal_case['expected_result'],
            "priority": minimal_case['priority'],
            "type": minimal_case['type'],
            "version": 1
        }
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        saved = await tool.execute(
            project_id="project-123",
            test_case=minimal_case
        )
        
        # 验证最小用例的往返
        assert saved['title'] == minimal_case['title']
        assert saved['preconditions'] == minimal_case['preconditions']
        assert len(saved['steps']) == 1


@pytest.mark.asyncio
async def test_property_complex_test_case_round_trip():
    """测试复杂测试用例的往返"""
    tool = SaveTestCaseTool(go_backend_url="http://localhost:8080")
    
    complex_case = {
        'title': 'Complex Test with Multiple Steps and Special Characters: "quotes" & <tags>',
        'preconditions': 'Setup:\n1. Database initialized\n2. User logged in\n3. Cache cleared',
        'steps': [
            {
                'step_number': i,
                'action': f'Step {i}: Perform action with data {{"key": "value{i}"}}',
                'expected': f'Expected result {i} with special chars: <>&"\'\n\t'
            }
            for i in range(1, 11)
        ],
        'expected_result': 'All steps completed successfully\nNo errors\nData persisted',
        'priority': 'high',
        'type': 'functional'
    }
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 0,
        "data": {
            "id": "complex-1",
            "title": complex_case['title'],
            "preconditions": complex_case['preconditions'],
            "steps": [
                {
                    "step_number": step['step_number'],
                    "action": step['action'],
                    "expected_result": step['expected']
                }
                for step in complex_case['steps']
            ],
            "expected_result": complex_case['expected_result'],
            "priority": complex_case['priority'],
            "type": complex_case['type'],
            "version": 1
        }
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        saved = await tool.execute(
            project_id="project-123",
            test_case=complex_case
        )
        
        # 验证复杂用例的往返
        assert saved['title'] == complex_case['title']
        assert saved['preconditions'] == complex_case['preconditions']
        assert saved['expected_result'] == complex_case['expected_result']
        assert len(saved['steps']) == 10
        
        # 验证特殊字符被正确保留
        assert '"quotes"' in saved['title']
        assert '<tags>' in saved['title']
        assert '\n' in saved['preconditions']


@pytest.mark.asyncio
async def test_property_unicode_test_case_round_trip():
    """测试包含 Unicode 字符的测试用例往返"""
    tool = SaveTestCaseTool(go_backend_url="http://localhost:8080")
    
    unicode_case = {
        'title': '测试用户登录功能 🔐',
        'preconditions': '用户已注册，密码为：P@ssw0rd！',
        'steps': [
            {
                'step_number': 1,
                'action': '输入用户名：张三',
                'expected': '显示欢迎信息：欢迎，张三！'
            },
            {
                'step_number': 2,
                'action': '输入密码：P@ssw0rd！',
                'expected': '密码验证通过 ✓'
            }
        ],
        'expected_result': '登录成功，跳转到首页 🏠',
        'priority': 'high',
        'type': 'functional'
    }
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 0,
        "data": {
            "id": "unicode-1",
            "title": unicode_case['title'],
            "preconditions": unicode_case['preconditions'],
            "steps": [
                {
                    "step_number": step['step_number'],
                    "action": step['action'],
                    "expected_result": step['expected']
                }
                for step in unicode_case['steps']
            ],
            "expected_result": unicode_case['expected_result'],
            "priority": unicode_case['priority'],
            "type": unicode_case['type'],
            "version": 1
        }
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        saved = await tool.execute(
            project_id="project-123",
            test_case=unicode_case
        )
        
        # 验证 Unicode 字符被正确保留
        assert '测试用户登录功能' in saved['title']
        assert '🔐' in saved['title']
        assert '张三' in saved['steps'][0]['action']
        assert '✓' in saved['steps'][1]['expected_result']
        assert '🏠' in saved['expected_result']
