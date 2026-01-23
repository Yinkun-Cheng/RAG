"""
RegressionRecommendationWorkflow 单元测试
"""

import pytest
from unittest.mock import AsyncMock
from app.workflow.regression_recommendation_workflow import RegressionRecommendationWorkflow
from app.workflow.base import WorkflowResult
from app.tool.retrieval_tools import SearchTestCaseTool


@pytest.fixture
def mock_search_testcase_tool():
    """创建模拟的 SearchTestCaseTool"""
    tool = AsyncMock(spec=SearchTestCaseTool)
    return tool


@pytest.fixture
def workflow(mock_search_testcase_tool):
    """创建 RegressionRecommendationWorkflow 实例"""
    return RegressionRecommendationWorkflow(
        search_testcase_tool=mock_search_testcase_tool
    )


def test_workflow_properties(workflow):
    """测试工作流属性"""
    assert workflow.name == "regression_recommendation"
    assert workflow.description == "基于版本变更推荐回归测试用例"


@pytest.mark.asyncio
async def test_execute_success(workflow, mock_search_testcase_tool):
    """测试成功的工作流执行"""
    # 准备测试数据
    version_info = {
        'changed_modules': ['用户管理', '权限系统'],
        'version_name': 'v2.0.0',
        'change_description': '新增权限管理功能'
    }
    context = {
        'project_id': 'test-project-123',
        'limit': 10
    }
    
    # 模拟测试用例搜索结果
    module1_cases = [
        {
            'id': 'case1',
            'title': '用户登录测试',
            'score': 0.9,
            'metadata': {'priority': 'P0', 'module': '用户管理'}
        },
        {
            'id': 'case2',
            'title': '用户注册测试',
            'score': 0.8,
            'metadata': {'priority': 'P1', 'module': '用户管理'}
        }
    ]
    
    module2_cases = [
        {
            'id': 'case3',
            'title': '权限验证测试',
            'score': 0.95,
            'metadata': {'priority': 'P0', 'module': '权限系统'}
        },
        {
            'id': 'case4',
            'title': '角色管理测试',
            'score': 0.7,
            'metadata': {'priority': 'P2', 'module': '权限系统'}
        }
    ]
    
    # 模拟搜索工具返回不同模块的测试用例
    mock_search_testcase_tool.execute.side_effect = [module1_cases, module2_cases]
    
    # 执行工作流
    result = await workflow.execute(version_info, context)
    
    # 验证结果
    assert isinstance(result, WorkflowResult)
    assert result.success is True
    assert result.error is None
    
    # 验证返回的数据
    assert 'recommended_cases' in result.data
    assert 'version_info' in result.data
    assert 'ranking_criteria' in result.data
    
    recommended_cases = result.data['recommended_cases']
    assert len(recommended_cases) <= 10  # 不超过限制
    
    # 验证排序：P0 优先级的测试用例应该在前面
    if len(recommended_cases) >= 2:
        first_case = recommended_cases[0]
        assert first_case['metadata']['priority'] == 'P0'
    
    # 验证元数据
    assert result.metadata['total_candidates'] == 4
    assert result.metadata['unique_candidates'] == 4
    assert result.metadata['recommended_count'] == 4
    assert result.metadata['changed_modules_count'] == 2
    assert result.metadata['changed_modules'] == ['用户管理', '权限系统']
    
    # 验证工具调用
    assert mock_search_testcase_tool.execute.call_count == 2


@pytest.mark.asyncio
async def test_execute_missing_project_id(workflow):
    """测试缺少 project_id 参数"""
    version_info = {'changed_modules': ['模块A']}
    context = {}  # 缺少 project_id
    
    # 执行工作流
    result = await workflow.execute(version_info, context)
    
    # 验证结果
    assert result.success is False
    assert "缺少必需的 project_id 参数" in result.error


@pytest.mark.asyncio
async def test_execute_no_context(workflow):
    """测试没有上下文"""
    version_info = {'changed_modules': ['模块A']}
    
    # 执行工作流
    result = await workflow.execute(version_info, None)
    
    # 验证结果
    assert result.success is False
    assert "缺少必需的 project_id 参数" in result.error


@pytest.mark.asyncio
async def test_execute_missing_changed_modules(workflow):
    """测试缺少 changed_modules 参数"""
    version_info = {}  # 缺少 changed_modules
    context = {'project_id': 'test-project-123'}
    
    # 执行工作流
    result = await workflow.execute(version_info, context)
    
    # 验证结果
    assert result.success is False
    assert "缺少必需的 changed_modules 参数" in result.error


@pytest.mark.asyncio
async def test_execute_empty_changed_modules(workflow):
    """测试空的 changed_modules 列表"""
    version_info = {'changed_modules': []}
    context = {'project_id': 'test-project-123'}
    
    # 执行工作流
    result = await workflow.execute(version_info, context)
    
    # 验证结果（应该成功，但返回空列表）
    assert result.success is True
    assert result.data['recommended_cases'] == []
    assert result.metadata['total_candidates'] == 0
    assert result.metadata['recommended_count'] == 0
    assert "没有变更的模块" in result.metadata['warnings']


@pytest.mark.asyncio
async def test_execute_with_priority_filter(workflow, mock_search_testcase_tool):
    """测试使用优先级过滤"""
    version_info = {'changed_modules': ['模块A']}
    context = {
        'project_id': 'test-project-123',
        'priority_filter': 'P0'
    }
    
    # 模拟测试用例搜索结果
    test_cases = [
        {
            'id': 'case1',
            'title': '测试1',
            'score': 0.9,
            'metadata': {'priority': 'P0'}
        }
    ]
    mock_search_testcase_tool.execute.return_value = test_cases
    
    # 执行工作流
    result = await workflow.execute(version_info, context)
    
    # 验证结果
    assert result.success is True
    
    # 验证工具调用时传递了优先级过滤
    mock_search_testcase_tool.execute.assert_called_once()
    call_args = mock_search_testcase_tool.execute.call_args
    assert call_args[1]['priority'] == 'P0'


@pytest.mark.asyncio
async def test_execute_module_search_failure(workflow, mock_search_testcase_tool):
    """测试部分模块搜索失败"""
    version_info = {'changed_modules': ['模块A', '模块B']}
    context = {'project_id': 'test-project-123'}
    
    # 模拟第一个模块成功，第二个模块失败
    test_cases = [
        {
            'id': 'case1',
            'title': '测试1',
            'score': 0.9,
            'metadata': {'priority': 'P0'}
        }
    ]
    mock_search_testcase_tool.execute.side_effect = [
        test_cases,
        Exception("搜索失败")
    ]
    
    # 执行工作流（应该继续执行）
    result = await workflow.execute(version_info, context)
    
    # 验证结果（应该成功，但有警告）
    assert result.success is True
    assert len(result.data['recommended_cases']) == 1
    assert "部分模块检索失败" in result.metadata['warnings'][0]


@pytest.mark.asyncio
async def test_execute_deduplication(workflow, mock_search_testcase_tool):
    """测试去重功能"""
    version_info = {'changed_modules': ['模块A', '模块B']}
    context = {'project_id': 'test-project-123'}
    
    # 模拟两个模块返回相同的测试用例
    duplicate_case = {
        'id': 'case1',
        'title': '共享测试',
        'score': 0.9,
        'metadata': {'priority': 'P0'}
    }
    
    mock_search_testcase_tool.execute.side_effect = [
        [duplicate_case],
        [duplicate_case]  # 重复的测试用例
    ]
    
    # 执行工作流
    result = await workflow.execute(version_info, context)
    
    # 验证结果（应该去重）
    assert result.success is True
    assert result.metadata['total_candidates'] == 2  # 原始数量
    assert result.metadata['unique_candidates'] == 1  # 去重后数量
    assert len(result.data['recommended_cases']) == 1


@pytest.mark.asyncio
async def test_execute_ranking_by_priority(workflow, mock_search_testcase_tool):
    """测试按优先级排序"""
    version_info = {'changed_modules': ['模块A']}
    context = {'project_id': 'test-project-123'}
    
    # 模拟不同优先级的测试用例（乱序）
    test_cases = [
        {
            'id': 'case1',
            'title': '测试1',
            'score': 0.5,
            'metadata': {'priority': 'P2'}
        },
        {
            'id': 'case2',
            'title': '测试2',
            'score': 0.9,
            'metadata': {'priority': 'P0'}
        },
        {
            'id': 'case3',
            'title': '测试3',
            'score': 0.7,
            'metadata': {'priority': 'P1'}
        },
        {
            'id': 'case4',
            'title': '测试4',
            'score': 0.95,
            'metadata': {'priority': 'P0'}
        }
    ]
    mock_search_testcase_tool.execute.return_value = test_cases
    
    # 执行工作流
    result = await workflow.execute(version_info, context)
    
    # 验证结果
    assert result.success is True
    recommended = result.data['recommended_cases']
    
    # 验证排序：P0 应该在前面，且 P0 中分数高的在前
    assert recommended[0]['id'] == 'case4'  # P0, score=0.95
    assert recommended[1]['id'] == 'case2'  # P0, score=0.9
    assert recommended[2]['id'] == 'case3'  # P1, score=0.7
    assert recommended[3]['id'] == 'case1'  # P2, score=0.5


@pytest.mark.asyncio
async def test_execute_limit_results(workflow, mock_search_testcase_tool):
    """测试限制推荐数量"""
    version_info = {'changed_modules': ['模块A']}
    context = {
        'project_id': 'test-project-123',
        'limit': 2  # 只推荐 2 个
    }
    
    # 模拟 5 个测试用例
    test_cases = [
        {'id': f'case{i}', 'title': f'测试{i}', 'score': 0.9 - i*0.1, 'metadata': {'priority': 'P0'}}
        for i in range(5)
    ]
    mock_search_testcase_tool.execute.return_value = test_cases
    
    # 执行工作流
    result = await workflow.execute(version_info, context)
    
    # 验证结果（应该只返回 2 个）
    assert result.success is True
    assert len(result.data['recommended_cases']) == 2
    assert result.metadata['unique_candidates'] == 5
    assert result.metadata['recommended_count'] == 2


@pytest.mark.asyncio
async def test_execute_unexpected_error(workflow, mock_search_testcase_tool):
    """测试意外错误（所有模块检索失败）"""
    version_info = {'changed_modules': ['模块A']}
    context = {'project_id': 'test-project-123'}
    
    # 模拟意外错误
    mock_search_testcase_tool.execute.side_effect = RuntimeError("意外错误")
    
    # 执行工作流
    result = await workflow.execute(version_info, context)
    
    # 验证结果（工作流应该成功，但返回空列表和警告）
    assert result.success is True
    assert len(result.data['recommended_cases']) == 0
    assert "部分模块检索失败" in result.metadata['warnings'][0]


def test_get_ranking_criteria(workflow):
    """测试获取排名标准"""
    criteria = workflow._get_ranking_criteria()
    
    assert 'primary' in criteria
    assert 'secondary' in criteria
    assert 'description' in criteria
    assert '优先级' in criteria['primary']
    assert '相似度分数' in criteria['secondary']
