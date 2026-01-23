"""
TestEngineerAgent - 主 Agent

模拟高级测试工程师，负责理解用户需求、选择合适的工作流并协调执行。
"""

import logging
import time
import asyncio
from typing import Any, Dict, List, Optional, Type
from enum import Enum

from ..integration.brconnector_client import BRConnectorClient
from ..workflow.base import BaseWorkflow, WorkflowResult
from ..workflow.test_case_generation_workflow import TestCaseGenerationWorkflow
from ..workflow.impact_analysis_workflow import ImpactAnalysisWorkflow
from ..workflow.regression_recommendation_workflow import RegressionRecommendationWorkflow
from ..workflow.test_case_optimization_workflow import TestCaseOptimizationWorkflow

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """任务类型枚举"""
    GENERATE_TEST_CASES = "generate_test_cases"  # 生成测试用例
    IMPACT_ANALYSIS = "impact_analysis"  # 影响分析
    REGRESSION_RECOMMENDATION = "regression_recommendation"  # 回归测试推荐
    TEST_CASE_OPTIMIZATION = "test_case_optimization"  # 测试用例优化
    UNKNOWN = "unknown"  # 未知任务


class AgentResponse:
    """Agent 响应"""
    
    def __init__(
        self,
        success: bool,
        task_type: TaskType,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        初始化 Agent 响应
        
        Args:
            success: 是否成功
            task_type: 任务类型
            data: 响应数据
            error: 错误信息
            metadata: 元数据
        """
        self.success = success
        self.task_type = task_type
        self.data = data or {}
        self.error = error
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'task_type': self.task_type.value,
            'data': self.data,
            'error': self.error,
            'metadata': self.metadata
        }


class TestEngineerAgent:
    """
    测试工程师 Agent
    
    职责：
    - 理解用户输入（需求、变更、问题）
    - 确定任务类型（生成用例 / 影响分析 / 回归推荐 / 用例优化）
    - 选择合适的 Workflow 执行
    - 对最终结果进行质量保证
    """
    
    def __init__(
        self,
        llm_client: BRConnectorClient,
        workflows: Optional[Dict[str, BaseWorkflow]] = None
    ):
        """
        初始化 TestEngineerAgent
        
        Args:
            llm_client: LLM 客户端（BRConnector）
            workflows: 工作流字典 {workflow_name: workflow_instance}
        """
        self.llm_client = llm_client
        self.workflows = workflows or {}
        
        logger.info(f"TestEngineerAgent 初始化完成，注册了 {len(self.workflows)} 个工作流")
        for name in self.workflows.keys():
            logger.info(f"  - {name}")
    
    def register_workflow(self, workflow: BaseWorkflow) -> None:
        """
        注册工作流
        
        Args:
            workflow: 工作流实例
        """
        workflow_name = workflow.name
        if workflow_name in self.workflows:
            logger.warning(f"工作流 '{workflow_name}' 已存在，将被覆盖")
        
        self.workflows[workflow_name] = workflow
        logger.info(f"注册工作流: {workflow_name} - {workflow.description}")
    
    def discover_workflows(self, workflow_instances: List[BaseWorkflow]) -> None:
        """
        自动发现并注册工作流
        
        Args:
            workflow_instances: 工作流实例列表
        """
        logger.info(f"开始自动发现工作流，共 {len(workflow_instances)} 个")
        
        for workflow in workflow_instances:
            self.register_workflow(workflow)
        
        logger.info(f"工作流发现完成，共注册 {len(self.workflows)} 个工作流")
    
    def get_workflow(self, workflow_name: str) -> Optional[BaseWorkflow]:
        """
        获取工作流
        
        Args:
            workflow_name: 工作流名称
            
        Returns:
            工作流实例，如果不存在则返回 None
        """
        return self.workflows.get(workflow_name)
    
    def list_workflows(self) -> List[Dict[str, str]]:
        """
        列出所有已注册的工作流
        
        Returns:
            工作流信息列表
        """
        return [
            {
                'name': name,
                'description': workflow.description
            }
            for name, workflow in self.workflows.items()
        ]
    
    def _quick_classify_by_keywords(self, message: str) -> Optional[TaskType]:
        """
        通过关键词快速分类任务（避免不必要的 LLM 调用）
        
        Args:
            message: 用户消息
            
        Returns:
            任务类型，如果无法通过关键词确定则返回 None
        """
        message_lower = message.lower()
        
        # 生成测试用例的关键词
        generate_keywords = ['生成', '创建', '编写', '设计', 'generate', 'create', 'write', 'design']
        testcase_keywords = ['测试用例', '用例', 'test case', 'testcase']
        
        # 影响分析的关键词
        impact_keywords = ['影响', '变更', '修改', '改动', 'impact', 'change', 'modify', 'affect']
        analysis_keywords = ['分析', 'analysis', 'analyze']
        
        # 回归测试推荐的关键词
        regression_keywords = ['回归', '推荐', 'regression', 'recommend', 'suggest']
        
        # 优化的关键词
        optimization_keywords = ['优化', '补全', '完善', '改进', 'optimize', 'improve', 'enhance', 'supplement']
        
        # 检查生成测试用例
        if any(kw in message_lower for kw in generate_keywords) and \
           any(kw in message_lower for kw in testcase_keywords):
            return TaskType.GENERATE_TEST_CASES
        
        # 检查影响分析
        if any(kw in message_lower for kw in impact_keywords) and \
           any(kw in message_lower for kw in analysis_keywords):
            return TaskType.IMPACT_ANALYSIS
        
        # 检查回归测试推荐
        if any(kw in message_lower for kw in regression_keywords):
            return TaskType.REGRESSION_RECOMMENDATION
        
        # 检查测试用例优化
        if any(kw in message_lower for kw in optimization_keywords) and \
           any(kw in message_lower for kw in testcase_keywords):
            return TaskType.TEST_CASE_OPTIMIZATION
        
        # 无法通过关键词确定
        return None
    
    async def classify_task(self, message: str, context: Dict[str, Any]) -> TaskType:
        """
        分类用户任务
        
        支持：
        1. 关键词快速匹配（快速路径）
        2. LLM 智能分类（准确路径）
        3. 多轮对话上下文理解
        
        Args:
            message: 用户消息
            context: 上下文信息，可包含：
                - conversation_history: 对话历史（用于多轮对话理解）
                - last_task_type: 上一次的任务类型
            
        Returns:
            任务类型
        """
        # 步骤 1: 尝试通过关键词快速分类
        quick_result = self._quick_classify_by_keywords(message)
        if quick_result is not None:
            logger.info(f"通过关键词快速分类: {quick_result.value}")
            return quick_result
        
        # 步骤 2: 使用 LLM 进行智能分类
        logger.info("使用 LLM 进行任务分类")
        
        # 构建上下文信息
        context_info = ""
        if 'conversation_history' in context and context['conversation_history']:
            history = context['conversation_history'][-3:]  # 最近 3 条对话
            context_info = "\n对话历史：\n" + "\n".join([
                f"- {msg['role']}: {msg['content'][:100]}" 
                for msg in history
            ])
        
        if 'last_task_type' in context and context['last_task_type']:
            context_info += f"\n上一次任务类型：{context['last_task_type']}"
        
        # 构建分类 prompt
        classification_prompt = f"""你是一个测试工程师助手。请分析用户的请求，判断任务类型。

用户请求：{message}
{context_info}

任务类型说明：
1. generate_test_cases - 生成测试用例
   - 用户想要创建新的测试用例
   - 关键词：生成、创建、编写、设计测试用例
   - 示例："帮我生成用户登录的测试用例"

2. impact_analysis - 影响分析
   - 用户想要分析需求变更对现有系统的影响
   - 关键词：影响、变更、修改、分析
   - 示例："分析这个需求变更的影响"

3. regression_recommendation - 回归测试推荐
   - 用户想要推荐需要执行的回归测试用例
   - 关键词：回归、推荐、建议
   - 示例："推荐这个版本的回归测试用例"

4. test_case_optimization - 测试用例优化
   - 用户想要优化、补全或改进现有测试用例
   - 关键词：优化、补全、完善、改进
   - 示例："优化现有的登录测试用例"

5. unknown - 未知任务
   - 无法确定任务类型
   - 用于不明确的请求

分析规则：
- 如果用户提到"生成"或"创建"测试用例，选择 generate_test_cases
- 如果用户提到"影响"或"变更分析"，选择 impact_analysis
- 如果用户提到"回归"或"推荐"，选择 regression_recommendation
- 如果用户提到"优化"或"改进"现有用例，选择 test_case_optimization
- 如果无法确定，选择 unknown

请只返回任务类型的英文标识符（如：generate_test_cases），不要返回其他内容。
"""
        
        try:
            response = await self.llm_client.chat(
                messages=[{"role": "user", "content": classification_prompt}],
                max_tokens=50,
                temperature=0.0
            )
            
            task_type_str = response.strip().lower()
            
            # 映射到 TaskType 枚举
            task_type_mapping = {
                'generate_test_cases': TaskType.GENERATE_TEST_CASES,
                'impact_analysis': TaskType.IMPACT_ANALYSIS,
                'regression_recommendation': TaskType.REGRESSION_RECOMMENDATION,
                'test_case_optimization': TaskType.TEST_CASE_OPTIMIZATION,
                'unknown': TaskType.UNKNOWN
            }
            
            task_type = task_type_mapping.get(task_type_str, TaskType.UNKNOWN)
            logger.info(f"LLM 任务分类结果: {task_type.value}")
            
            return task_type
            
        except Exception as e:
            logger.error(f"任务分类失败: {e}")
            # 默认返回生成测试用例任务
            return TaskType.GENERATE_TEST_CASES
    
    def select_workflow(self, task_type: TaskType) -> Optional[BaseWorkflow]:
        """
        根据任务类型选择工作流
        
        Args:
            task_type: 任务类型
            
        Returns:
            工作流实例，如果没有合适的工作流则返回 None
        """
        # 任务类型到工作流名称的映射
        task_to_workflow = {
            TaskType.GENERATE_TEST_CASES: 'test_case_generation',
            TaskType.IMPACT_ANALYSIS: 'impact_analysis',
            TaskType.REGRESSION_RECOMMENDATION: 'regression_recommendation',
            TaskType.TEST_CASE_OPTIMIZATION: 'test_case_optimization'
        }
        
        workflow_name = task_to_workflow.get(task_type)
        if not workflow_name:
            logger.warning(f"未知任务类型: {task_type}")
            return None
        
        workflow = self.get_workflow(workflow_name)
        if not workflow:
            logger.warning(f"未找到工作流: {workflow_name}")
            return None
        
        logger.info(f"选择工作流: {workflow_name} - {workflow.description}")
        return workflow
    
    async def process_request(
        self,
        message: str,
        context: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> AgentResponse:
        """
        处理用户请求
        
        Args:
            message: 用户消息
            context: 上下文信息，包含：
                - project_id: 项目 ID（必需）
                - conversation_id: 对话 ID（可选）
                - timeout: 超时时间（秒，可选，默认 300 秒）
                - 其他工作流所需的参数
            timeout: 超时时间（秒），如果未指定则使用默认值 300 秒
                
        Returns:
            Agent 响应
        """
        # 性能监控：记录开始时间
        start_time = time.time()
        
        # 设置默认超时时间（5 分钟）
        if timeout is None:
            timeout = context.get('timeout', 300.0)
        
        logger.info(f"TestEngineerAgent 开始处理请求: {message[:100]}... (超时: {timeout}秒)")
        
        # 验证必需参数
        if 'project_id' not in context:
            logger.error("缺少必需的 project_id 参数")
            return AgentResponse(
                success=False,
                task_type=TaskType.UNKNOWN,
                error="缺少必需的 project_id 参数",
                metadata={
                    'duration_seconds': time.time() - start_time
                }
            )
        
        try:
            # 使用 asyncio.wait_for 实现超时控制
            response = await asyncio.wait_for(
                self._process_request_internal(message, context, start_time),
                timeout=timeout
            )
            
            # 添加总执行时间到元数据
            total_duration = time.time() - start_time
            response.metadata['total_duration_seconds'] = total_duration
            
            logger.info(f"请求处理完成，总耗时: {total_duration:.2f}秒")
            
            return response
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            logger.error(f"请求处理超时: {duration:.2f}秒 (限制: {timeout}秒)")
            return AgentResponse(
                success=False,
                task_type=TaskType.UNKNOWN,
                error=f"请求处理超时（{timeout}秒），请简化需求或稍后重试",
                metadata={
                    'duration_seconds': duration,
                    'timeout_seconds': timeout,
                    'timeout_error': True
                }
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.exception(f"处理请求时发生异常: {e}")
            return AgentResponse(
                success=False,
                task_type=TaskType.UNKNOWN,
                error=f"处理请求时发生异常: {str(e)}",
                metadata={
                    'duration_seconds': duration,
                    'exception_type': type(e).__name__
                }
            )
    
    async def _process_request_internal(
        self,
        message: str,
        context: Dict[str, Any],
        start_time: float
    ) -> AgentResponse:
        """
        内部请求处理逻辑（用于超时控制）
        
        Args:
            message: 用户消息
            context: 上下文信息
            start_time: 开始时间
            
        Returns:
            Agent 响应
        """
        # 步骤 1: 分类任务
        step_start = time.time()
        logger.info("步骤 1: 分类任务类型")
        task_type = await self.classify_task(message, context)
        step_duration = time.time() - step_start
        logger.info(f"步骤 1 完成，耗时: {step_duration:.2f}秒")
        
        if task_type == TaskType.UNKNOWN:
            logger.warning("无法确定任务类型")
            return AgentResponse(
                success=False,
                task_type=TaskType.UNKNOWN,
                error="无法确定任务类型，请提供更明确的需求描述",
                metadata={
                    'duration_seconds': time.time() - start_time,
                    'classification_duration': step_duration
                }
            )
        
        # 步骤 2: 选择工作流
        step_start = time.time()
        logger.info("步骤 2: 选择合适的工作流")
        workflow = self.select_workflow(task_type)
        step_duration = time.time() - step_start
        logger.info(f"步骤 2 完成，耗时: {step_duration:.2f}秒")
        
        if not workflow:
            logger.error(f"未找到适合任务类型 {task_type} 的工作流")
            return AgentResponse(
                success=False,
                task_type=task_type,
                error=f"未找到适合任务类型 {task_type.value} 的工作流",
                metadata={
                    'duration_seconds': time.time() - start_time,
                    'workflow_selection_duration': step_duration
                }
            )
        
        # 步骤 3: 执行工作流
        step_start = time.time()
        logger.info(f"步骤 3: 执行工作流 {workflow.name}")
        workflow_result = await workflow.execute(message, context)
        step_duration = time.time() - step_start
        logger.info(f"步骤 3 完成，耗时: {step_duration:.2f}秒")
        
        # 步骤 4: 转换结果
        step_start = time.time()
        logger.info("步骤 4: 转换工作流结果为 Agent 响应")
        
        if not workflow_result.success:
            logger.error(f"工作流执行失败: {workflow_result.error}")
            return AgentResponse(
                success=False,
                task_type=task_type,
                error=workflow_result.error,
                metadata={
                    **workflow_result.metadata,
                    'duration_seconds': time.time() - start_time,
                    'workflow_execution_duration': step_duration
                }
            )
        
        # 成功响应
        step_duration = time.time() - step_start
        logger.info(f"步骤 4 完成，耗时: {step_duration:.2f}秒")
        logger.info("请求处理成功")
        
        return AgentResponse(
            success=True,
            task_type=task_type,
            data=workflow_result.data,
            metadata={
                **workflow_result.metadata,
                'workflow_name': workflow.name,
                'workflow_description': workflow.description,
                'duration_seconds': time.time() - start_time,
                'response_formatting_duration': step_duration
            }
        )
    
    async def validate_result(self, result: AgentResponse) -> AgentResponse:
        """
        验证结果质量
        
        Args:
            result: Agent 响应
            
        Returns:
            验证后的 Agent 响应
        """
        # TODO: 实现结果质量验证逻辑
        # 例如：检查测试用例的完整性、覆盖率等
        return result
