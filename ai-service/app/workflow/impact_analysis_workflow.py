"""
影响分析工作流

分析需求变更对现有测试用例和模块的影响。
"""

import logging
from typing import Any, Dict, Optional

from .base import BaseWorkflow, WorkflowError, WorkflowResult
from ..agent.impact_analysis_agent import ImpactAnalysisAgent
from ..tool.retrieval_tools import SearchPRDTool, SearchTestCaseTool, GetRelatedCasesTool

logger = logging.getLogger(__name__)


class ImpactAnalysisWorkflow(BaseWorkflow):
    """
    影响分析工作流
    
    工作流程：
    1. 检索相关的历史 PRD
    2. 获取相关的测试用例
    3. 调用 ImpactAnalysisAgent 分析影响
    4. 返回影响报告
    """
    
    def __init__(
        self,
        impact_agent: ImpactAnalysisAgent,
        search_prd_tool: SearchPRDTool,
        search_testcase_tool: SearchTestCaseTool,
        get_related_cases_tool: GetRelatedCasesTool
    ):
        """
        初始化工作流
        
        Args:
            impact_agent: 影响分析 Agent
            search_prd_tool: PRD 搜索工具
            search_testcase_tool: 测试用例搜索工具
            get_related_cases_tool: 相关测试用例获取工具
        """
        self.impact_agent = impact_agent
        self.search_prd_tool = search_prd_tool
        self.search_testcase_tool = search_testcase_tool
        self.get_related_cases_tool = get_related_cases_tool
    
    @property
    def name(self) -> str:
        return "impact_analysis"
    
    @property
    def description(self) -> str:
        return "分析需求变更对现有测试用例和模块的影响"
    
    async def execute(
        self, 
        change_description: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        执行影响分析工作流
        
        Args:
            change_description: 变更描述
            context: 上下文信息，包含：
                - project_id: 项目 ID（必需）
                - prd_limit: 检索 PRD 数量（默认 5）
                - case_limit: 检索测试用例数量（默认 10）
                
        Returns:
            WorkflowResult: 包含影响报告和元数据
        """
        if not context or 'project_id' not in context:
            return WorkflowResult(
                success=False,
                error="缺少必需的 project_id 参数"
            )
        
        project_id = context['project_id']
        warnings = []
        
        try:
            # 步骤 1: 检索相关的历史 PRD
            logger.info(f"步骤 1: 检索相关 PRD (project_id={project_id})")
            related_prds = []
            
            try:
                prd_limit = context.get('prd_limit', 5)
                related_prds = await self.search_prd_tool.execute(
                    query=change_description,
                    project_id=project_id,
                    limit=prd_limit
                )
                logger.info(f"检索到 {len(related_prds)} 个相关 PRD")
            except Exception as e:
                logger.warning(f"检索历史 PRD 失败: {e}")
                warnings.append("无法检索历史 PRD，将继续执行")
            
            # 步骤 2: 获取相关的测试用例
            logger.info("步骤 2: 获取相关测试用例")
            existing_test_cases = []
            
            try:
                case_limit = context.get('case_limit', 10)
                # 基于变更描述搜索相关测试用例
                existing_test_cases = await self.search_testcase_tool.execute(
                    query=change_description,
                    project_id=project_id,
                    limit=case_limit
                )
                logger.info(f"检索到 {len(existing_test_cases)} 个相关测试用例")
            except Exception as e:
                logger.warning(f"检索测试用例失败: {e}")
                warnings.append("无法检索测试用例，将继续执行")
            
            # 步骤 3: 调用 ImpactAnalysisAgent 分析影响
            logger.info("步骤 3: 分析变更影响")
            try:
                impact_report = await self.impact_agent.analyze_impact(
                    change_description=change_description,
                    related_prds=related_prds,
                    existing_test_cases=existing_test_cases
                )
                logger.info(
                    f"影响分析完成: 风险等级={impact_report.risk_level}, "
                    f"受影响模块数={len(impact_report.affected_modules)}, "
                    f"受影响测试用例数={len(impact_report.affected_test_cases)}"
                )
            except Exception as e:
                logger.error(f"影响分析失败: {e}")
                return WorkflowResult(
                    success=False,
                    error=f"影响分析失败: {str(e)}",
                    metadata={
                        'step': 'impact_analysis',
                        'warnings': warnings,
                        'related_prds_count': len(related_prds),
                        'existing_cases_count': len(existing_test_cases)
                    }
                )
            
            # 步骤 4: 返回影响报告
            return WorkflowResult(
                success=True,
                data={
                    'impact_report': impact_report.to_dict(),
                    'related_prds': related_prds,
                    'existing_test_cases': existing_test_cases
                },
                metadata={
                    'risk_level': impact_report.risk_level,
                    'change_type': impact_report.change_type,
                    'affected_modules_count': len(impact_report.affected_modules),
                    'affected_cases_count': len(impact_report.affected_test_cases),
                    'warnings': warnings,
                    'related_prds_count': len(related_prds),
                    'existing_cases_count': len(existing_test_cases)
                }
            )
            
        except Exception as e:
            logger.exception(f"工作流执行失败: {e}")
            return WorkflowResult(
                success=False,
                error=f"工作流执行失败: {str(e)}",
                metadata={'warnings': warnings}
            )
