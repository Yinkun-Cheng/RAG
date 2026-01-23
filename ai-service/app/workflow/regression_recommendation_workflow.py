"""
回归测试推荐工作流

基于版本变更信息推荐需要执行的回归测试用例。
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseWorkflow, WorkflowError, WorkflowResult
from ..tool.retrieval_tools import SearchTestCaseTool

logger = logging.getLogger(__name__)


class RegressionRecommendationWorkflow(BaseWorkflow):
    """
    回归测试推荐工作流
    
    工作流程：
    1. 获取变更的模块列表
    2. 检索相关的测试用例
    3. 根据优先级和风险排序
    4. 返回推荐的测试用例列表
    """
    
    def __init__(
        self,
        search_testcase_tool: SearchTestCaseTool
    ):
        """
        初始化工作流
        
        Args:
            search_testcase_tool: 测试用例搜索工具
        """
        self.search_testcase_tool = search_testcase_tool
    
    @property
    def name(self) -> str:
        return "regression_recommendation"
    
    @property
    def description(self) -> str:
        return "基于版本变更推荐回归测试用例"
    
    async def execute(
        self, 
        version_info: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        执行回归测试推荐工作流
        
        Args:
            version_info: 版本信息，包含：
                - changed_modules: 变更的模块列表（必需）
                - version_name: 版本名称（可选）
                - change_description: 变更描述（可选）
            context: 上下文信息，包含：
                - project_id: 项目 ID（必需）
                - limit: 推荐数量限制（默认 50）
                - priority_filter: 优先级过滤（可选，如 'P0', 'P1'）
                
        Returns:
            WorkflowResult: 包含推荐的测试用例列表和元数据
        """
        if not context or 'project_id' not in context:
            return WorkflowResult(
                success=False,
                error="缺少必需的 project_id 参数"
            )
        
        if not version_info or 'changed_modules' not in version_info:
            return WorkflowResult(
                success=False,
                error="缺少必需的 changed_modules 参数"
            )
        
        project_id = context['project_id']
        changed_modules = version_info['changed_modules']
        limit = context.get('limit', 50)
        priority_filter = context.get('priority_filter')
        
        warnings = []
        
        try:
            # 步骤 1: 获取变更的模块列表
            logger.info(f"步骤 1: 获取变更模块 (project_id={project_id}, modules={len(changed_modules)})")
            
            if not changed_modules:
                logger.warning("没有变更的模块，返回空推荐列表")
                return WorkflowResult(
                    success=True,
                    data={
                        'recommended_cases': [],
                        'version_info': version_info
                    },
                    metadata={
                        'total_candidates': 0,
                        'recommended_count': 0,
                        'changed_modules_count': 0,
                        'warnings': ["没有变更的模块"]
                    }
                )
            
            # 步骤 2: 检索相关的测试用例
            logger.info("步骤 2: 检索相关测试用例")
            candidate_cases = []
            failed_modules = []
            
            for module in changed_modules:
                try:
                    # 为每个模块搜索测试用例
                    module_cases = await self.search_testcase_tool.execute(
                        query=f"模块:{module}",
                        project_id=project_id,
                        limit=20,  # 每个模块最多 20 个
                        priority=priority_filter
                    )
                    candidate_cases.extend(module_cases)
                    logger.info(f"模块 '{module}' 找到 {len(module_cases)} 个测试用例")
                except Exception as e:
                    logger.warning(f"检索模块 '{module}' 的测试用例失败: {e}")
                    failed_modules.append(module)
            
            if failed_modules:
                warnings.append(f"部分模块检索失败: {', '.join(failed_modules)}")
            
            # 步骤 3: 去重（基于测试用例 ID）
            logger.info("步骤 3: 去重测试用例")
            unique_cases = self._deduplicate_cases(candidate_cases)
            logger.info(f"去重后剩余 {len(unique_cases)} 个测试用例")
            
            # 步骤 4: 根据优先级和风险排序
            logger.info("步骤 4: 排序测试用例")
            ranked_cases = self._rank_cases(unique_cases)
            
            # 步骤 5: 限制推荐数量
            recommended_cases = ranked_cases[:limit]
            logger.info(f"推荐 {len(recommended_cases)} 个测试用例（限制: {limit}）")
            
            # 返回结果
            return WorkflowResult(
                success=True,
                data={
                    'recommended_cases': recommended_cases,
                    'version_info': version_info,
                    'ranking_criteria': self._get_ranking_criteria()
                },
                metadata={
                    'total_candidates': len(candidate_cases),
                    'unique_candidates': len(unique_cases),
                    'recommended_count': len(recommended_cases),
                    'changed_modules_count': len(changed_modules),
                    'changed_modules': changed_modules,
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
    
    def _deduplicate_cases(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        去重测试用例（基于 ID）
        
        Args:
            cases: 测试用例列表
            
        Returns:
            去重后的测试用例列表
        """
        seen_ids = set()
        unique_cases = []
        
        for case in cases:
            case_id = case.get('id')
            if case_id and case_id not in seen_ids:
                seen_ids.add(case_id)
                unique_cases.append(case)
        
        return unique_cases
    
    def _rank_cases(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        根据优先级和风险排序测试用例
        
        排序规则：
        1. 优先级：P0 > P1 > P2 > P3
        2. 相同优先级按分数（score）降序
        
        Args:
            cases: 测试用例列表
            
        Returns:
            排序后的测试用例列表
        """
        # 定义优先级权重
        priority_weights = {
            'P0': 4,
            'P1': 3,
            'P2': 2,
            'P3': 1,
            'p0': 4,
            'p1': 3,
            'p2': 2,
            'p3': 3,
        }
        
        def get_sort_key(case: Dict[str, Any]) -> tuple:
            """获取排序键"""
            # 从 metadata 中获取优先级
            priority = case.get('metadata', {}).get('priority', 'P3')
            priority_weight = priority_weights.get(priority, 0)
            
            # 获取相似度分数
            score = case.get('score', 0.0)
            
            # 返回排序键：优先级权重（降序），分数（降序）
            return (-priority_weight, -score)
        
        # 排序
        sorted_cases = sorted(cases, key=get_sort_key)
        
        return sorted_cases
    
    def _get_ranking_criteria(self) -> Dict[str, Any]:
        """
        获取排名标准说明
        
        Returns:
            排名标准字典
        """
        return {
            'primary': '优先级（P0 > P1 > P2 > P3）',
            'secondary': '相似度分数（降序）',
            'description': '优先推荐高优先级和高相关性的测试用例'
        }
