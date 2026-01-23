"""
测试用例生成工作流

完整的测试用例自动生成流程，编排所有 Subagent 和 Tool。
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseWorkflow, WorkflowError, WorkflowResult
from ..agent.requirement_analysis_agent import RequirementAnalysisAgent
from ..agent.test_design_agent import TestDesignAgent
from ..agent.quality_review_agent import QualityReviewAgent
from ..tool.retrieval_tools import SearchPRDTool, SearchTestCaseTool
from ..tool.generation_tools import FormatTestCaseTool

logger = logging.getLogger(__name__)


class TestCaseGenerationWorkflow(BaseWorkflow):
    """
    测试用例生成工作流
    
    工作流程：
    1. 检索历史知识（PRD 和测试用例）
    2. 分析需求（RequirementAnalysisAgent）
    3. 设计测试用例（TestDesignAgent）
    4. 质量审查（QualityReviewAgent）
    5. 格式化输出
    """
    
    def __init__(
        self,
        requirement_agent: RequirementAnalysisAgent,
        test_design_agent: TestDesignAgent,
        quality_review_agent: QualityReviewAgent,
        search_prd_tool: SearchPRDTool,
        search_testcase_tool: SearchTestCaseTool,
        format_tool: FormatTestCaseTool
    ):
        """
        初始化工作流
        
        Args:
            requirement_agent: 需求分析 Agent
            test_design_agent: 测试设计 Agent
            quality_review_agent: 质量审查 Agent
            search_prd_tool: PRD 搜索工具
            search_testcase_tool: 测试用例搜索工具
            format_tool: 格式化工具
        """
        self.requirement_agent = requirement_agent
        self.test_design_agent = test_design_agent
        self.quality_review_agent = quality_review_agent
        self.search_prd_tool = search_prd_tool
        self.search_testcase_tool = search_testcase_tool
        self.format_tool = format_tool
    
    @property
    def name(self) -> str:
        return "test_case_generation"
    
    @property
    def description(self) -> str:
        return "自动生成测试用例的完整工作流"
    
    async def execute(
        self, 
        requirement: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        执行测试用例生成工作流
        
        Args:
            requirement: 需求描述
            context: 上下文信息，包含：
                - project_id: 项目 ID（必需）
                - historical_prd_limit: 检索历史 PRD 数量（默认 5）
                - historical_case_limit: 检索历史用例数量（默认 5）
                
        Returns:
            WorkflowResult: 包含生成的测试用例和元数据
        """
        if not context or 'project_id' not in context:
            return WorkflowResult(
                success=False,
                error="缺少必需的 project_id 参数"
            )
        
        project_id = context['project_id']
        errors = []
        warnings = []
        
        try:
            # 步骤 1: 检索历史知识
            logger.info(f"步骤 1: 检索历史知识 (project_id={project_id})")
            historical_prds = []
            historical_cases = []
            
            try:
                prd_limit = context.get('historical_prd_limit', 5)
                historical_prds = await self.search_prd_tool.execute(
                    query=requirement,
                    project_id=project_id,
                    limit=prd_limit
                )
                logger.info(f"检索到 {len(historical_prds)} 个相关 PRD")
            except Exception as e:
                logger.warning(f"检索历史 PRD 失败: {e}")
                warnings.append("无法检索历史 PRD，将继续执行")
            
            try:
                case_limit = context.get('historical_case_limit', 5)
                historical_cases = await self.search_testcase_tool.execute(
                    query=requirement,
                    project_id=project_id,
                    limit=case_limit
                )
                logger.info(f"检索到 {len(historical_cases)} 个相关测试用例")
            except Exception as e:
                logger.warning(f"检索历史测试用例失败: {e}")
                warnings.append("无法检索历史测试用例，将继续执行")
            
            # 步骤 2: 分析需求
            logger.info("步骤 2: 分析需求")
            try:
                analysis_result = await self.requirement_agent.analyze(
                    requirement=requirement,
                    historical_prds=historical_prds
                )
                logger.info(f"需求分析完成: {len(analysis_result.functional_points)} 个功能点")
            except Exception as e:
                logger.error(f"需求分析失败: {e}")
                return WorkflowResult(
                    success=False,
                    error=f"需求分析失败: {str(e)}",
                    metadata={'step': 'requirement_analysis', 'warnings': warnings}
                )
            
            # 步骤 3: 设计测试用例
            logger.info("步骤 3: 设计测试用例")
            try:
                test_designs = await self.test_design_agent.design_tests(
                    analysis=analysis_result,
                    historical_cases=historical_cases
                )
                logger.info(f"测试设计完成: 生成 {len(test_designs)} 个测试用例")
            except Exception as e:
                logger.error(f"测试设计失败: {e}")
                return WorkflowResult(
                    success=False,
                    error=f"测试设计失败: {str(e)}",
                    metadata={
                        'step': 'test_design',
                        'analysis': analysis_result.to_dict(),
                        'warnings': warnings
                    }
                )
            
            # 步骤 4: 质量审查
            logger.info("步骤 4: 质量审查")
            try:
                review_result = await self.quality_review_agent.review(
                    test_cases=test_designs,
                    requirement=requirement,
                    analysis=analysis_result
                )
                logger.info(
                    f"质量审查完成: 覆盖率 {review_result.coverage_score}%, "
                    f"批准 {len(review_result.approved_cases)} 个用例"
                )
            except Exception as e:
                logger.warning(f"质量审查失败: {e}")
                # 质量审查失败时，使用所有测试用例
                from ..agent.quality_review_agent import ReviewResult
                review_result = ReviewResult(
                    coverage_score=0,
                    issues=[],
                    suggestions=[],
                    approved_cases=list(range(len(test_designs))),
                    rejected_cases=[],
                    overall_quality='unknown'
                )
                warnings.append("质量审查失败，已批准所有测试用例")
            
            # 步骤 5: 格式化输出
            logger.info("步骤 5: 格式化输出")
            try:
                # 只格式化批准的测试用例
                approved_designs = [
                    test_designs[i] for i in review_result.approved_cases
                ]
                
                formatted_cases = await self.format_tool.execute(
                    test_cases=approved_designs
                )
                logger.info(f"格式化完成: {len(formatted_cases)} 个测试用例")
            except Exception as e:
                logger.error(f"格式化失败: {e}")
                return WorkflowResult(
                    success=False,
                    error=f"格式化失败: {str(e)}",
                    metadata={
                        'step': 'formatting',
                        'analysis': analysis_result.to_dict(),
                        'review': review_result.to_dict(),
                        'warnings': warnings
                    }
                )
            
            # 返回成功结果
            return WorkflowResult(
                success=True,
                data={
                    'test_cases': formatted_cases,
                    'analysis': analysis_result.to_dict(),
                    'review': review_result.to_dict()
                },
                metadata={
                    'coverage_score': review_result.coverage_score,
                    'total_generated': len(test_designs),
                    'approved_count': len(approved_designs),
                    'rejected_count': len(review_result.rejected_cases),
                    'warnings': warnings,
                    'historical_prds_count': len(historical_prds),
                    'historical_cases_count': len(historical_cases)
                }
            )
            
        except Exception as e:
            logger.exception(f"工作流执行失败: {e}")
            return WorkflowResult(
                success=False,
                error=f"工作流执行失败: {str(e)}",
                metadata={'warnings': warnings}
            )
