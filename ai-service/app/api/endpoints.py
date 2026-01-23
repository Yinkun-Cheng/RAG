"""
API Endpoints - AI Test Assistant

提供测试用例生成和对话的 API 端点
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json
import asyncio

from app.agent.test_engineer_agent import TestEngineerAgent, TaskType
from app.agent.conversation_manager import ConversationManager
from app.integration.brconnector_client import BRConnectorClient
from app.workflow.test_case_generation_workflow import TestCaseGenerationWorkflow
from app.workflow.impact_analysis_workflow import ImpactAnalysisWorkflow
from app.workflow.regression_recommendation_workflow import RegressionRecommendationWorkflow
from app.workflow.test_case_optimization_workflow import TestCaseOptimizationWorkflow
from app.agent.requirement_analysis_agent import RequirementAnalysisAgent
from app.agent.test_design_agent import TestDesignAgent
from app.agent.quality_review_agent import QualityReviewAgent
from app.agent.impact_analysis_agent import ImpactAnalysisAgent
from app.tool.retrieval_tools import SearchPRDTool, SearchTestCaseTool, GetRelatedCasesTool
from app.tool.generation_tools import FormatTestCaseTool
from app.tool.validation_tools import CheckQualityTool, ValidateCoverageTool
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class GenerateRequest(BaseModel):
    """测试用例生成请求"""
    message: str = Field(..., description="用户需求描述")
    project_id: str = Field(..., description="项目 ID")
    conversation_id: Optional[str] = Field(None, description="对话 ID（可选）")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="额外上下文")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "用户登录功能需求：支持用户名密码登录，需要验证码",
                "project_id": 1,
                "conversation_id": "conv-123",
                "context": {}
            }
        }


class GenerateResponse(BaseModel):
    """测试用例生成响应"""
    success: bool = Field(..., description="是否成功")
    task_type: str = Field(..., description="任务类型")
    conversation_id: Optional[str] = Field(None, description="对话 ID")
    test_cases: Optional[list] = Field(None, description="生成的测试用例")
    analysis: Optional[Dict[str, Any]] = Field(None, description="需求分析结果")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    error: Optional[str] = Field(None, description="错误信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "task_type": "GENERATE_TEST_CASES",
                "conversation_id": "conv-123",
                "test_cases": [
                    {
                        "title": "验证用户名密码登录成功",
                        "preconditions": "用户已注册",
                        "steps": [
                            {"step_number": 1, "action": "输入用户名", "expected": "用户名输入框显示输入内容"},
                            {"step_number": 2, "action": "输入密码", "expected": "密码输入框显示掩码"},
                            {"step_number": 3, "action": "点击登录按钮", "expected": "跳转到首页"}
                        ],
                        "expected_result": "用户成功登录系统",
                        "priority": "P0",
                        "type": "functional"
                    }
                ],
                "metadata": {
                    "coverage_score": 85,
                    "total_generated": 5,
                    "approved_count": 5
                }
            }
        }


class ChatStreamRequest(BaseModel):
    """流式对话请求"""
    message: str = Field(..., description="用户消息")
    project_id: str = Field(..., description="项目 ID")
    conversation_id: Optional[str] = Field(None, description="对话 ID（可选）")
    stream: bool = Field(True, description="是否流式传输")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "帮我分析一下用户登录功能的测试点",
                "project_id": 1,
                "conversation_id": "conv-123",
                "stream": True
            }
        }


# ============================================================================
# Global Instances (Singleton Pattern)
# ============================================================================

# 这些实例在应用启动时初始化
_agent: Optional[TestEngineerAgent] = None
_conversation_manager: Optional[ConversationManager] = None
_br_client: Optional[BRConnectorClient] = None


def get_agent() -> TestEngineerAgent:
    """获取 TestEngineerAgent 实例（单例）"""
    global _agent
    
    if _agent is None:
        logger.info("初始化 TestEngineerAgent...")
        
        # 初始化 BRConnector 客户端
        br_client = BRConnectorClient(
            api_key=settings.BRCONNECTOR_API_KEY,
            base_url=settings.BRCONNECTOR_BASE_URL,
            model=settings.BRCONNECTOR_MODEL
        )
        
        # 初始化 Subagents
        requirement_agent = RequirementAnalysisAgent(br_client)
        test_design_agent = TestDesignAgent(br_client)
        quality_review_agent = QualityReviewAgent(br_client)
        impact_analysis_agent = ImpactAnalysisAgent(br_client)
        
        # 初始化 Tools
        search_prd_tool = SearchPRDTool(backend_url=settings.GO_BACKEND_URL)
        search_testcase_tool = SearchTestCaseTool(backend_url=settings.GO_BACKEND_URL)
        get_related_cases_tool = GetRelatedCasesTool(backend_url=settings.GO_BACKEND_URL)
        format_testcase_tool = FormatTestCaseTool()
        check_quality_tool = CheckQualityTool()
        validate_coverage_tool = ValidateCoverageTool()
        
        # 初始化 Workflows
        test_case_generation_workflow = TestCaseGenerationWorkflow(
            requirement_agent=requirement_agent,
            test_design_agent=test_design_agent,
            quality_review_agent=quality_review_agent,
            search_prd_tool=search_prd_tool,
            search_testcase_tool=search_testcase_tool,
            format_tool=format_testcase_tool
        )
        
        impact_analysis_workflow = ImpactAnalysisWorkflow(
            impact_agent=impact_analysis_agent,
            search_prd_tool=search_prd_tool,
            search_testcase_tool=search_testcase_tool,
            get_related_cases_tool=get_related_cases_tool
        )
        
        regression_recommendation_workflow = RegressionRecommendationWorkflow(
            search_testcase_tool=search_testcase_tool
        )
        
        test_case_optimization_workflow = TestCaseOptimizationWorkflow(
            search_testcase_tool=search_testcase_tool,
            search_prd_tool=search_prd_tool,
            validate_coverage_tool=validate_coverage_tool,
            check_quality_tool=check_quality_tool,
            requirement_analysis_agent=requirement_agent,
            test_design_agent=test_design_agent,
            format_testcase_tool=format_testcase_tool
        )
        
        # 创建 TestEngineerAgent
        _agent = TestEngineerAgent(br_client)
        
        # 注册 Workflows
        _agent.register_workflow(test_case_generation_workflow)
        _agent.register_workflow(impact_analysis_workflow)
        _agent.register_workflow(regression_recommendation_workflow)
        _agent.register_workflow(test_case_optimization_workflow)
        
        logger.info("TestEngineerAgent 初始化完成")
    
    return _agent


def get_conversation_manager() -> ConversationManager:
    """获取 ConversationManager 实例（单例）"""
    global _conversation_manager
    
    if _conversation_manager is None:
        logger.info("初始化 ConversationManager...")
        _conversation_manager = ConversationManager(default_window_size=10)
        logger.info("ConversationManager 初始化完成")
    
    return _conversation_manager


def get_br_client() -> BRConnectorClient:
    """获取 BRConnectorClient 实例（单例）"""
    global _br_client
    
    if _br_client is None:
        logger.info("初始化 BRConnectorClient...")
        _br_client = BRConnectorClient(
            api_key=settings.BRCONNECTOR_API_KEY,
            base_url=settings.BRCONNECTOR_BASE_URL,
            model=settings.BRCONNECTOR_MODEL
        )
        logger.info("BRConnectorClient 初始化完成")
    
    return _br_client


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/generate", response_model=GenerateResponse)
async def generate_test_cases(request: GenerateRequest) -> GenerateResponse:
    """
    生成测试用例端点
    
    基于用户需求描述，使用 AI 生成测试用例。
    支持多种任务类型：测试用例生成、影响分析、回归推荐、用例优化。
    
    Args:
        request: 生成请求，包含需求描述、项目 ID 等
        
    Returns:
        GenerateResponse: 生成结果，包含测试用例、分析结果等
        
    Raises:
        HTTPException: 当请求参数无效或处理失败时
    """
    try:
        logger.info(f"收到测试用例生成请求: project_id={request.project_id}, message={request.message[:50]}...")
        
        # 获取 Agent 和 ConversationManager
        agent = get_agent()
        conversation_manager = get_conversation_manager()
        
        # 创建或获取对话
        conversation_id = request.conversation_id or f"conv-{request.project_id}-{asyncio.get_event_loop().time()}"
        conversation = conversation_manager.get_or_create_conversation(
            conversation_id=conversation_id,
            project_id=str(request.project_id)
        )
        
        # 添加用户消息到对话历史
        conversation_manager.add_message(
            conversation_id=conversation_id,
            role='user',
            content=request.message
        )
        
        # 准备上下文
        context = request.context or {}
        context['project_id'] = request.project_id
        context['conversation_history'] = conversation_manager.get_context(conversation_id)
        
        # 调用 Agent 处理请求
        logger.info(f"调用 TestEngineerAgent 处理请求...")
        agent_response = await agent.process_request(
            message=request.message,
            context=context
        )
        
        # 添加 AI 响应到对话历史
        response_content = json.dumps(agent_response.to_dict(), ensure_ascii=False)
        conversation_manager.add_message(
            conversation_id=conversation_id,
            role='assistant',
            content=response_content
        )
        
        # 构建响应
        if agent_response.success:
            logger.info(f"请求处理成功: task_type={agent_response.task_type}")
            return GenerateResponse(
                success=True,
                task_type=agent_response.task_type.value,
                conversation_id=conversation_id,
                test_cases=agent_response.result.get('test_cases') if agent_response.result else None,
                analysis=agent_response.result.get('analysis') if agent_response.result else None,
                metadata=agent_response.metadata
            )
        else:
            logger.error(f"请求处理失败: {agent_response.error}")
            return GenerateResponse(
                success=False,
                task_type=agent_response.task_type.value if agent_response.task_type else "UNKNOWN",
                conversation_id=conversation_id,
                error=agent_response.error,
                metadata=agent_response.metadata
            )
            
    except ValueError as e:
        logger.error(f"参数验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(request: ChatStreamRequest):
    """
    流式对话端点（SSE）
    
    使用 Server-Sent Events (SSE) 流式传输 AI 响应。
    适用于需要实时显示 AI 生成过程的场景。
    
    Args:
        request: 对话请求，包含消息、项目 ID 等
        
    Returns:
        StreamingResponse: SSE 流式响应
        
    Raises:
        HTTPException: 当请求参数无效或处理失败时
    """
    try:
        logger.info(f"收到流式对话请求: project_id={request.project_id}, message={request.message[:50]}...")
        
        # 获取 BRConnector 客户端和 ConversationManager
        br_client = get_br_client()
        conversation_manager = get_conversation_manager()
        
        # 创建或获取对话
        conversation_id = request.conversation_id or f"conv-{request.project_id}-{asyncio.get_event_loop().time()}"
        conversation = conversation_manager.get_or_create_conversation(
            conversation_id=conversation_id,
            project_id=str(request.project_id)
        )
        
        # 添加用户消息到对话历史
        conversation_manager.add_message(
            conversation_id=conversation_id,
            role='user',
            content=request.message
        )
        
        # 获取对话上下文
        conversation_history = conversation_manager.get_context(conversation_id)
        
        async def event_generator():
            """SSE 事件生成器"""
            try:
                # 发送开始事件
                yield f"data: {json.dumps({'type': 'start', 'conversation_id': conversation_id}, ensure_ascii=False)}\n\n"
                
                # 准备消息（包含对话历史）
                messages = conversation_history + [
                    {'role': 'user', 'content': request.message}
                ]
                
                # 流式调用 BRConnector
                full_response = ""
                async for chunk in br_client.chat_stream(messages=messages):
                    if chunk:
                        full_response += chunk
                        # 发送内容块
                        yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"
                
                # 添加完整响应到对话历史
                conversation_manager.add_message(
                    conversation_id=conversation_id,
                    role='assistant',
                    content=full_response
                )
                
                # 发送完成事件
                yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id}, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                logger.error(f"流式传输时发生错误: {str(e)}", exc_info=True)
                # 发送错误事件
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用 nginx 缓冲
            }
        )
        
    except ValueError as e:
        logger.error(f"参数验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"处理流式请求时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")


@router.get("/conversations")
async def list_conversations(project_id: Optional[str] = None):
    """
    列出对话
    
    获取所有对话或特定项目的对话列表。
    
    Args:
        project_id: 项目 ID（可选），如果指定则只返回该项目的对话
        
    Returns:
        对话列表
    """
    try:
        conversation_manager = get_conversation_manager()
        
        conversations = conversation_manager.list_conversations(
            project_id=str(project_id) if project_id else None
        )
        
        return {
            "success": True,
            "conversations": [
                {
                    "conversation_id": conv.conversation_id,
                    "project_id": conv.project_id,
                    "message_count": len(conv.messages),
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                }
                for conv in conversations
            ],
            "total": len(conversations)
        }
        
    except Exception as e:
        logger.error(f"列出对话时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    删除对话
    
    删除指定的对话及其所有消息。
    
    Args:
        conversation_id: 对话 ID
        
    Returns:
        删除结果
    """
    try:
        conversation_manager = get_conversation_manager()
        
        success = conversation_manager.delete_conversation(conversation_id)
        
        if success:
            return {
                "success": True,
                "message": f"对话 {conversation_id} 已删除"
            }
        else:
            raise HTTPException(status_code=404, detail=f"对话 {conversation_id} 不存在")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除对话时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")
