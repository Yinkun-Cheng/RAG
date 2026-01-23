"""
测试用例优化工作流

分析现有测试用例的质量，识别缺失的测试点，并生成补充测试用例。
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseWorkflow, WorkflowError, WorkflowResult
from ..tool.retrieval_tools import SearchTestCaseTool, SearchPRDTool
from ..tool.validation_tools import ValidateCoverageTool, CheckQualityTool
from ..tool.generation_tools import GenerateTestCaseTool, FormatTestCaseTool
from ..agent.requirement_analysis_agent import RequirementAnalysisAgent
from ..agent.test_design_agent import TestDesignAgent

logger = logging.getLogger(__name__)


class TestCaseOptimizationWorkflow(BaseWorkflow):
    """
    测试用例优化工作流
    
    工作流程：
    1. 获取现有测试用例
    2. 质量检查
    3. 识别缺失的测试点
    4. 生成补充测试用例
    5. 返回优化建议和补充用例
    """
    
    def __init__(
        self,
        search_testcase_tool: SearchTestCaseTool,
        search_prd_tool: SearchPRDTool,
        validate_coverage_tool: ValidateCoverageTool,
        check_quality_tool: CheckQualityTool,
        requirement_analysis_agent: RequirementAnalysisAgent,
        test_design_agent: TestDesignAgent,
        format_testcase_tool: FormatTestCaseTool
    ):
        """
        初始化工作流
        
        Args:
            search_testcase_tool: 测试用例搜索工具
            search_prd_tool: PRD 搜索工具
            validate_coverage_tool: 覆盖率验证工具
            check_quality_tool: 质量检查工具
            requirement_analysis_agent: 需求分析 Agent
            test_design_agent: 测试设计 Agent
            format_testcase_tool: 测试用例格式化工具
        """
        self.search_testcase_tool = search_testcase_tool
        self.search_prd_tool = search_prd_tool
        self.validate_coverage_tool = validate_coverage_tool
        self.check_quality_tool = check_quality_tool
        self.requirement_analysis_agent = requirement_analysis_agent
        self.test_design_agent = test_design_agent
        self.format_testcase_tool = format_testcase_tool
    
    @property
    def name(self) -> str:
        return "test_case_optimization"
    
    @property
    def description(self) -> str:
        return "优化和补全现有测试用例"
    
    async def execute(
        self, 
        requirement: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        执行测试用例优化工作流
        
        Args:
            requirement: 需求描述（用于分析现有用例的覆盖情况）
            context: 上下文信息，包含：
                - project_id: 项目 ID（必需）
                - existing_cases: 现有测试用例列表（可选，如果不提供则通过搜索获取）
                - prd_limit: PRD 检索数量限制（默认 5）
                - testcase_limit: 测试用例检索数量限制（默认 10）
                
        Returns:
            WorkflowResult: 包含质量问题、缺失测试点、补充用例和优化建议
        """
        if not context or 'project_id' not in context:
            return WorkflowResult(
                success=False,
                error="缺少必需的 project_id 参数"
            )
        
        if not requirement:
            return WorkflowResult(
                success=False,
                error="缺少必需的 requirement 参数"
            )
        
        project_id = context['project_id']
        prd_limit = context.get('prd_limit', 5)
        testcase_limit = context.get('testcase_limit', 10)
        
        warnings = []
        
        try:
            # 步骤 1: 获取现有测试用例
            logger.info(f"步骤 1: 获取现有测试用例 (project_id={project_id})")
            
            existing_cases = context.get('existing_cases')
            if not existing_cases:
                # 如果没有提供现有用例，通过搜索获取
                try:
                    existing_cases = await self.search_testcase_tool.execute(
                        query=requirement,
                        project_id=project_id,
                        limit=testcase_limit
                    )
                    logger.info(f"通过搜索找到 {len(existing_cases)} 个现有测试用例")
                except Exception as e:
                    logger.warning(f"搜索现有测试用例失败: {e}")
                    warnings.append(f"搜索现有测试用例失败: {str(e)}")
                    existing_cases = []
            
            if not existing_cases:
                logger.warning("没有找到现有测试用例，无法进行优化")
                return WorkflowResult(
                    success=True,
                    data={
                        'quality_issues': [],
                        'missing_points': [],
                        'supplementary_cases': [],
                        'optimization_suggestions': ["没有找到现有测试用例，建议先创建基础测试用例"]
                    },
                    metadata={
                        'existing_cases_count': 0,
                        'quality_issues_count': 0,
                        'missing_points_count': 0,
                        'supplementary_cases_count': 0,
                        'warnings': warnings
                    }
                )
            
            # 步骤 2: 质量检查
            logger.info("步骤 2: 执行质量检查")
            quality_issues = []
            
            for case in existing_cases:
                try:
                    issues = await self.check_quality_tool.execute(case)
                    if issues:
                        quality_issues.extend([
                            {
                                'case_id': case.get('id'),
                                'case_title': case.get('title'),
                                'issues': issues
                            }
                        ])
                except Exception as e:
                    logger.warning(f"质量检查失败 (case_id={case.get('id')}): {e}")
                    warnings.append(f"质量检查失败: {str(e)}")
            
            logger.info(f"发现 {len(quality_issues)} 个测试用例存在质量问题")
            
            # 步骤 3: 检索相关 PRD 并分析需求
            logger.info("步骤 3: 检索相关 PRD 并分析需求")
            
            historical_prds = []
            try:
                historical_prds = await self.search_prd_tool.execute(
                    query=requirement,
                    project_id=project_id,
                    limit=prd_limit
                )
                logger.info(f"检索到 {len(historical_prds)} 个相关 PRD")
            except Exception as e:
                logger.warning(f"检索 PRD 失败: {e}")
                warnings.append(f"检索 PRD 失败: {str(e)}")
            
            # 分析需求
            try:
                analysis_result = await self.requirement_analysis_agent.analyze(
                    requirement=requirement,
                    context={'historical_prds': historical_prds}
                )
                logger.info("需求分析完成")
            except Exception as e:
                logger.error(f"需求分析失败: {e}")
                return WorkflowResult(
                    success=False,
                    error=f"需求分析失败: {str(e)}",
                    metadata={'warnings': warnings}
                )
            
            # 步骤 4: 识别缺失的测试点（覆盖率检查）
            logger.info("步骤 4: 识别缺失的测试点")
            
            try:
                coverage_report = await self.validate_coverage_tool.execute(
                    test_cases=existing_cases,
                    requirement_analysis=analysis_result.to_dict()
                )
                
                missing_points = coverage_report.get('missing_coverage', [])
                logger.info(f"识别到 {len(missing_points)} 个缺失的测试点")
            except Exception as e:
                logger.warning(f"覆盖率检查失败: {e}")
                warnings.append(f"覆盖率检查失败: {str(e)}")
                missing_points = []
            
            # 步骤 5: 生成补充测试用例
            logger.info("步骤 5: 生成补充测试用例")
            
            supplementary_cases = []
            if missing_points:
                try:
                    # 使用测试设计 Agent 生成补充用例
                    test_designs = await self.test_design_agent.design_tests(
                        analysis=analysis_result,
                        context={
                            'historical_cases': existing_cases,
                            'focus_points': missing_points  # 聚焦于缺失的测试点
                        }
                    )
                    
                    # 格式化补充用例
                    supplementary_cases = await self.format_testcase_tool.execute(
                        [tc.to_dict() for tc in test_designs]
                    )
                    
                    logger.info(f"生成 {len(supplementary_cases)} 个补充测试用例")
                except Exception as e:
                    logger.warning(f"生成补充测试用例失败: {e}")
                    warnings.append(f"生成补充测试用例失败: {str(e)}")
            
            # 步骤 6: 生成优化建议
            logger.info("步骤 6: 生成优化建议")
            optimization_suggestions = self._generate_optimization_suggestions(
                quality_issues=quality_issues,
                missing_points=missing_points,
                existing_cases_count=len(existing_cases),
                supplementary_cases_count=len(supplementary_cases)
            )
            
            # 返回结果
            return WorkflowResult(
                success=True,
                data={
                    'quality_issues': quality_issues,
                    'missing_points': missing_points,
                    'supplementary_cases': supplementary_cases,
                    'optimization_suggestions': optimization_suggestions,
                    'requirement_analysis': analysis_result.to_dict(),
                    'coverage_report': coverage_report if 'coverage_report' in locals() else {}
                },
                metadata={
                    'existing_cases_count': len(existing_cases),
                    'quality_issues_count': len(quality_issues),
                    'missing_points_count': len(missing_points),
                    'supplementary_cases_count': len(supplementary_cases),
                    'warnings': warnings
                }
            )
            
        except Exception as e:
            logger.exception(f"工作流执行失败: {e}")
            return WorkflowResult(
                success=False,
                error=f"工作流执行失败: {str(e)}",
                metadata={'warnings': warnings}
            )
    
    def _generate_optimization_suggestions(
        self,
        quality_issues: List[Dict[str, Any]],
        missing_points: List[str],
        existing_cases_count: int,
        supplementary_cases_count: int
    ) -> List[str]:
        """
        生成优化建议
        
        Args:
            quality_issues: 质量问题列表
            missing_points: 缺失的测试点列表
            existing_cases_count: 现有测试用例数量
            supplementary_cases_count: 补充测试用例数量
            
        Returns:
            优化建议列表
        """
        suggestions = []
        
        # 质量问题建议
        if quality_issues:
            suggestions.append(
                f"发现 {len(quality_issues)} 个测试用例存在质量问题，建议修复这些问题以提高测试用例的可维护性和可执行性"
            )
            
            # 统计常见问题
            common_issues = {}
            for qi in quality_issues:
                for issue in qi.get('issues', []):
                    issue_type = issue.split(':')[0] if ':' in issue else issue
                    common_issues[issue_type] = common_issues.get(issue_type, 0) + 1
            
            # 提供针对性建议
            for issue_type, count in sorted(common_issues.items(), key=lambda x: x[1], reverse=True):
                if count >= 2:
                    suggestions.append(f"多个测试用例存在 '{issue_type}' 问题，建议统一修复")
        
        # 覆盖率建议
        if missing_points:
            suggestions.append(
                f"识别到 {len(missing_points)} 个缺失的测试点，建议添加补充测试用例以提高覆盖率"
            )
            
            # 分类缺失点
            functional_missing = [p for p in missing_points if '功能' in p or 'functional' in p.lower()]
            exception_missing = [p for p in missing_points if '异常' in p or 'exception' in p.lower()]
            boundary_missing = [p for p in missing_points if '边界' in p or 'boundary' in p.lower()]
            
            if functional_missing:
                suggestions.append(f"缺少 {len(functional_missing)} 个功能测试点，建议优先补充")
            if exception_missing:
                suggestions.append(f"缺少 {len(exception_missing)} 个异常测试点，建议补充异常处理测试")
            if boundary_missing:
                suggestions.append(f"缺少 {len(boundary_missing)} 个边界值测试点，建议补充边界值测试")
        
        # 补充用例建议
        if supplementary_cases_count > 0:
            suggestions.append(
                f"已生成 {supplementary_cases_count} 个补充测试用例，建议审查后添加到测试套件中"
            )
        
        # 整体建议
        if existing_cases_count < 5:
            suggestions.append("现有测试用例数量较少，建议增加更多测试用例以提高测试覆盖率")
        
        if not quality_issues and not missing_points:
            suggestions.append("现有测试用例质量良好且覆盖率较高，建议保持当前测试策略")
        
        return suggestions
