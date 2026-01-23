"""
验证工具单元测试

测试 ValidateCoverageTool、CheckDuplicationTool 和 CheckQualityTool 的功能。
"""

import pytest
from app.tool.validation_tools import (
    ValidateCoverageTool,
    CheckDuplicationTool,
    CheckQualityTool,
)


# ============================================================================
# ValidateCoverageTool 测试
# ============================================================================

@pytest.mark.asyncio
async def test_validate_coverage_tool_full_coverage():
    """测试完全覆盖的情况"""
    tool = ValidateCoverageTool()
    
    # 准备需求分析
    requirement_analysis = {
        "functional_points": ["用户登录", "密码验证", "会话管理"],
        "exception_conditions": ["密码错误", "账户锁定"],
        "constraints": ["密码长度", "登录超时"]
    }
    
    # 准备测试用例（完全覆盖）
    test_cases = [
        {
            "title": "测试用户登录成功",
            "type": "functional",
            "preconditions": "用户已注册",
            "steps": [],
            "expected_result": "登录成功"
        },
        {
            "title": "测试密码验证功能",
            "type": "functional",
            "preconditions": "用户存在",
            "steps": [],
            "expected_result": "验证通过"
        },
        {
            "title": "测试会话管理",
            "type": "functional",
            "preconditions": "用户已登录",
            "steps": [],
            "expected_result": "会话有效"
        },
        {
            "title": "测试密码错误处理",
            "type": "exception",
            "preconditions": "用户存在",
            "steps": [],
            "expected_result": "提示错误"
        },
        {
            "title": "测试账户锁定",
            "type": "exception",
            "preconditions": "多次失败",
            "steps": [],
            "expected_result": "账户锁定"
        },
        {
            "title": "测试密码长度边界",
            "type": "boundary",
            "preconditions": "准备测试数据",
            "steps": [],
            "expected_result": "符合要求"
        },
        {
            "title": "测试登录超时",
            "type": "boundary",
            "preconditions": "设置超时",
            "steps": [],
            "expected_result": "超时处理"
        }
    ]
    
    # 执行验证
    report = await tool.execute(
        test_cases=test_cases,
        requirement_analysis=requirement_analysis
    )
    
    # 验证结果
    assert report["overall_score"] >= 90  # 完全覆盖应该接近 100
    assert report["functional_coverage"] == 100.0
    assert report["exception_coverage"] == 100.0
    assert report["boundary_coverage"] == 100.0
    assert len(report["covered_points"]) == 3
    assert len(report["uncovered_points"]) == 0


@pytest.mark.asyncio
async def test_validate_coverage_tool_partial_coverage():
    """测试部分覆盖的情况"""
    tool = ValidateCoverageTool()
    
    # 准备需求分析
    requirement_analysis = {
        "functional_points": ["用户登录", "密码验证", "会话管理", "注销功能"],
        "exception_conditions": ["密码错误", "账户锁定"],
        "constraints": ["密码长度"]
    }
    
    # 准备测试用例（部分覆盖）
    test_cases = [
        {
            "title": "测试用户登录",
            "type": "functional",
            "preconditions": "",
            "steps": [],
            "expected_result": ""
        },
        {
            "title": "测试密码错误",
            "type": "exception",
            "preconditions": "",
            "steps": [],
            "expected_result": ""
        }
    ]
    
    # 执行验证
    report = await tool.execute(
        test_cases=test_cases,
        requirement_analysis=requirement_analysis
    )
    
    # 验证结果
    assert report["overall_score"] < 100
    assert report["functional_coverage"] < 100  # 只覆盖了部分功能点
    assert len(report["uncovered_points"]) > 0


@pytest.mark.asyncio
async def test_validate_coverage_tool_empty_cases():
    """测试空测试用例列表"""
    tool = ValidateCoverageTool()
    
    requirement_analysis = {
        "functional_points": ["功能1", "功能2"],
        "exception_conditions": [],
        "constraints": []
    }
    
    # 执行验证
    report = await tool.execute(
        test_cases=[],
        requirement_analysis=requirement_analysis
    )
    
    # 验证结果
    assert report["overall_score"] == 0
    assert report["functional_coverage"] == 0
    assert len(report["uncovered_points"]) == 2


# ============================================================================
# CheckDuplicationTool 测试
# ============================================================================

@pytest.mark.asyncio
async def test_check_duplication_tool_no_duplicates():
    """测试无重复的情况"""
    tool = CheckDuplicationTool(similarity_threshold=0.85)
    
    # 准备完全不同的测试用例
    test_cases = [
        {
            "title": "测试用户登录",
            "steps": [{"action": "打开登录页面", "expected": "显示表单"}],
            "expected_result": "登录成功"
        },
        {
            "title": "测试密码重置",
            "steps": [{"action": "点击忘记密码", "expected": "发送邮件"}],
            "expected_result": "重置成功"
        },
        {
            "title": "测试用户注册",
            "steps": [{"action": "填写注册表单", "expected": "提交成功"}],
            "expected_result": "注册完成"
        }
    ]
    
    # 执行检测
    report = await tool.execute(test_cases=test_cases)
    
    # 验证结果
    assert len(report["duplicate_pairs"]) == 0
    assert report["duplicate_count"] == 0
    assert report["unique_count"] == 3
    assert report["duplication_rate"] == 0


@pytest.mark.asyncio
async def test_check_duplication_tool_with_duplicates():
    """测试有重复的情况"""
    tool = CheckDuplicationTool(similarity_threshold=0.85)
    
    # 准备包含重复的测试用例
    test_cases = [
        {
            "title": "测试用户登录功能",
            "steps": [{"action": "输入用户名密码", "expected": "登录成功"}],
            "expected_result": "用户成功登录系统"
        },
        {
            "title": "测试用户登录功能",  # 几乎相同
            "steps": [{"action": "输入用户名密码", "expected": "登录成功"}],
            "expected_result": "用户成功登录系统"
        },
        {
            "title": "测试密码重置",
            "steps": [{"action": "点击忘记密码", "expected": "发送邮件"}],
            "expected_result": "重置成功"
        }
    ]
    
    # 执行检测
    report = await tool.execute(test_cases=test_cases)
    
    # 验证结果
    assert len(report["duplicate_pairs"]) >= 1  # 至少发现一对重复
    assert report["duplicate_count"] >= 2  # 至少 2 个用例重复
    assert report["duplication_rate"] > 0


@pytest.mark.asyncio
async def test_check_duplication_tool_custom_threshold():
    """测试自定义相似度阈值"""
    tool = CheckDuplicationTool(similarity_threshold=0.5)  # 较低的阈值
    
    test_cases = [
        {
            "title": "测试登录",
            "steps": [],
            "expected_result": "成功"
        },
        {
            "title": "测试注册",
            "steps": [],
            "expected_result": "完成"
        }
    ]
    
    # 使用更高的阈值
    report = await tool.execute(
        test_cases=test_cases,
        similarity_threshold=0.9
    )
    
    # 验证结果：高阈值下应该没有重复
    assert len(report["duplicate_pairs"]) == 0


# ============================================================================
# CheckQualityTool 测试
# ============================================================================

@pytest.mark.asyncio
async def test_check_quality_tool_perfect_case():
    """测试完美的测试用例"""
    tool = CheckQualityTool()
    
    # 准备高质量测试用例
    test_case = {
        "title": "测试用户登录功能",
        "preconditions": "用户已注册且账户未被锁定",
        "steps": [
            {
                "step_number": 1,
                "action": "打开登录页面",
                "expected": "显示登录表单"
            },
            {
                "step_number": 2,
                "action": "输入正确的用户名和密码",
                "expected": "输入框显示内容"
            },
            {
                "step_number": 3,
                "action": "点击登录按钮",
                "expected": "跳转到首页"
            }
        ],
        "expected_result": "用户成功登录并跳转到首页",
        "priority": "high",
        "type": "functional"
    }
    
    # 执行检查
    issues = await tool.execute(test_case=test_case)
    
    # 验证结果：应该只有一个 info 级别的问题（标题格式建议）或没有问题
    assert len(issues) <= 1
    if len(issues) == 1:
        # 可能是 info 或 warning 级别
        assert issues[0]["severity"] in ["info", "warning"]


@pytest.mark.asyncio
async def test_check_quality_tool_poor_case():
    """测试质量差的测试用例"""
    tool = CheckQualityTool()
    
    # 准备低质量测试用例
    test_case = {
        "title": "测试",  # 标题过短
        "preconditions": "",  # 缺少前置条件
        "steps": [  # 只有一个步骤
            {
                "step_number": 1,
                "action": "",  # 缺少操作
                "expected": ""  # 缺少预期
            }
        ],
        "expected_result": "成功",  # 预期结果过于模糊
        "priority": "invalid",  # 无效优先级
        "type": "unknown"  # 无效类型
    }
    
    # 执行检查
    issues = await tool.execute(test_case=test_case)
    
    # 验证结果：应该发现多个问题
    assert len(issues) >= 5
    
    # 检查是否包含关键问题
    issue_rules = [issue["rule"] for issue in issues]
    assert "title_length" in issue_rules
    assert "missing_preconditions" in issue_rules
    assert "insufficient_steps" in issue_rules
    assert "vague_expected_result" in issue_rules


@pytest.mark.asyncio
async def test_check_quality_tool_missing_step_details():
    """测试步骤缺少详情的情况"""
    tool = CheckQualityTool()
    
    test_case = {
        "title": "测试用户登录功能",
        "preconditions": "用户已注册",
        "steps": [
            {
                "step_number": 1,
                "action": "打开页面",
                "expected": ""  # 缺少预期
            },
            {
                "step_number": 2,
                "action": "",  # 缺少操作
                "expected": "显示结果"
            }
        ],
        "expected_result": "登录成功",
        "priority": "high",
        "type": "functional"
    }
    
    # 执行检查
    issues = await tool.execute(test_case=test_case)
    
    # 验证结果：应该发现步骤相关的问题
    step_issues = [
        issue for issue in issues 
        if "step" in issue["rule"]
    ]
    assert len(step_issues) >= 2  # 至少 2 个步骤问题


@pytest.mark.asyncio
async def test_check_quality_tool_valid_priority_and_type():
    """测试有效的优先级和类型"""
    tool = CheckQualityTool()
    
    test_case = {
        "title": "测试用户登录功能",
        "preconditions": "用户已注册且账户未被锁定",
        "steps": [
            {"step_number": 1, "action": "操作1", "expected": "预期1"},
            {"step_number": 2, "action": "操作2", "expected": "预期2"}
        ],
        "expected_result": "用户成功登录系统",
        "priority": "high",  # 有效优先级
        "type": "functional"  # 有效类型
    }
    
    # 执行检查
    issues = await tool.execute(test_case=test_case)
    
    # 验证结果：不应该有优先级或类型相关的问题
    priority_issues = [
        issue for issue in issues 
        if issue["rule"] in ["invalid_priority", "invalid_type"]
    ]
    assert len(priority_issues) == 0
