"""
检索工具

提供 PRD 文档和测试用例的向量检索能力。
通过调用 Go 后端的搜索 API 实现，复用现有的智能搜索和重排功能。
"""

from typing import List, Dict, Any, Optional
import httpx
from .base import BaseTool, ToolError


class SearchPRDTool(BaseTool):
    """
    搜索 PRD 文档工具。
    
    通过调用 Go 后端的搜索 API 来查找相关的 PRD 文档。
    复用 Go 后端的向量检索、混合检索和智能重排功能。
    """
    
    def __init__(self, backend_url: str):
        """
        初始化 PRD 搜索工具。
        
        Args:
            backend_url: Go 后端的基础 URL（例如：http://localhost:8080）
        """
        super().__init__(
            name="search_prd",
            description="在 PRD 文档库中搜索相关文档"
        )
        self.backend_url = backend_url.rstrip("/")  # 移除末尾的斜杠
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def execute(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.7,
        project_id: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        执行 PRD 文档搜索。
        
        Args:
            query: 搜索查询文本
            limit: 返回结果数量限制
            threshold: 相似度阈值（0-1）
            project_id: 项目 ID（必需）
            **kwargs: 其他参数
            
        Returns:
            PRD 文档列表，每个文档包含标题、内容、相似度等信息
            
        Raises:
            ToolError: 如果搜索失败
        """
        try:
            if not project_id:
                raise ToolError(
                    tool_name=self.name,
                    message="project_id 是必需参数",
                    details={"query": query}
                )
            
            self.logger.info(f"搜索 PRD 文档: query='{query}', limit={limit}, project_id={project_id}")
            
            # 构建搜索请求
            search_request = {
                "query": query,
                "type": "prd",  # 只搜索 PRD
                "limit": limit,
                "score_threshold": threshold,
            }
            
            # 调用 Go 后端搜索 API
            url = f"{self.backend_url}/api/v1/projects/{project_id}/search"
            response = await self.http_client.post(url, json=search_request)
            
            # 检查响应状态
            if response.status_code != 200:
                raise ToolError(
                    tool_name=self.name,
                    message=f"Go 后端搜索 API 返回错误: {response.status_code}",
                    details={
                        "query": query,
                        "status_code": response.status_code,
                        "response": response.text
                    }
                )
            
            # 解析响应
            result = response.json()
            if result.get("code") != 200:
                raise ToolError(
                    tool_name=self.name,
                    message=f"搜索失败: {result.get('message', 'Unknown error')}",
                    details={"query": query, "result": result}
                )
            
            # 提取搜索结果
            search_response = result.get("data", {})
            results = search_response.get("results", [])
            
            # 转换为工具期望的格式
            formatted_results = []
            for item in results:
                formatted_results.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "content": item.get("content"),
                    "score": item.get("score"),
                    "metadata": item.get("metadata", {}),
                })
            
            self.logger.info(f"找到 {len(formatted_results)} 个相关 PRD 文档")
            return formatted_results
        
        except ToolError:
            raise
        except Exception as e:
            self.logger.error(f"PRD 搜索失败: {e}")
            raise ToolError(
                tool_name=self.name,
                message=f"搜索 PRD 文档失败: {str(e)}",
                details={"query": query, "error": str(e)}
            )
    
    async def close(self):
        """关闭 HTTP 客户端连接"""
        await self.http_client.aclose()


class SearchTestCaseTool(BaseTool):
    """
    搜索测试用例工具。
    
    通过调用 Go 后端的搜索 API 来查找相关的测试用例。
    复用 Go 后端的向量检索、混合检索和智能重排功能。
    """
    
    def __init__(self, backend_url: str):
        """
        初始化测试用例搜索工具。
        
        Args:
            backend_url: Go 后端的基础 URL（例如：http://localhost:8080）
        """
        super().__init__(
            name="search_test_case",
            description="在测试用例库中搜索相关测试用例"
        )
        self.backend_url = backend_url.rstrip("/")
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def execute(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
        project_id: Optional[str] = None,
        priority: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        执行测试用例搜索。
        
        Args:
            query: 搜索查询文本
            limit: 返回结果数量限制
            threshold: 相似度阈值（0-1）
            project_id: 项目 ID（必需）
            priority: 可选的优先级过滤（P0, P1, P2, P3）
            **kwargs: 其他参数
            
        Returns:
            测试用例列表，每个用例包含标题、步骤、预期结果等信息
            
        Raises:
            ToolError: 如果搜索失败
        """
        try:
            if not project_id:
                raise ToolError(
                    tool_name=self.name,
                    message="project_id 是必需参数",
                    details={"query": query}
                )
            
            self.logger.info(f"搜索测试用例: query='{query}', limit={limit}, project_id={project_id}")
            
            # 构建搜索请求
            search_request = {
                "query": query,
                "type": "testcase",  # 只搜索测试用例
                "limit": limit,
                "score_threshold": threshold,
            }
            
            # 调用 Go 后端搜索 API
            url = f"{self.backend_url}/api/v1/projects/{project_id}/search"
            response = await self.http_client.post(url, json=search_request)
            
            # 检查响应状态
            if response.status_code != 200:
                raise ToolError(
                    tool_name=self.name,
                    message=f"Go 后端搜索 API 返回错误: {response.status_code}",
                    details={
                        "query": query,
                        "status_code": response.status_code,
                        "response": response.text
                    }
                )
            
            # 解析响应
            result = response.json()
            if result.get("code") != 200:
                raise ToolError(
                    tool_name=self.name,
                    message=f"搜索失败: {result.get('message', 'Unknown error')}",
                    details={"query": query, "result": result}
                )
            
            # 提取搜索结果
            search_response = result.get("data", {})
            results = search_response.get("results", [])
            
            # 转换为工具期望的格式，并应用优先级过滤
            formatted_results = []
            for item in results:
                # 如果指定了优先级过滤，则只返回匹配的结果
                if priority:
                    item_priority = item.get("metadata", {}).get("priority")
                    if item_priority != priority:
                        continue
                
                formatted_results.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "content": item.get("content"),
                    "score": item.get("score"),
                    "metadata": item.get("metadata", {}),
                })
            
            self.logger.info(f"找到 {len(formatted_results)} 个相关测试用例")
            return formatted_results
        
        except ToolError:
            raise
        except Exception as e:
            self.logger.error(f"测试用例搜索失败: {e}")
            raise ToolError(
                tool_name=self.name,
                message=f"搜索测试用例失败: {str(e)}",
                details={"query": query, "error": str(e)}
            )
    
    async def close(self):
        """关闭 HTTP 客户端连接"""
        await self.http_client.aclose()


class GetRelatedCasesTool(BaseTool):
    """
    获取相关测试用例工具。
    
    基于给定的测试用例，通过调用 Go 后端的推荐 API 查找相关的其他测试用例。
    """
    
    def __init__(self, backend_url: str):
        """
        初始化相关测试用例获取工具。
        
        Args:
            backend_url: Go 后端的基础 URL（例如：http://localhost:8080）
        """
        super().__init__(
            name="get_related_cases",
            description="获取与指定测试用例相关的其他测试用例"
        )
        self.backend_url = backend_url.rstrip("/")
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def execute(
        self,
        test_case_id: str,
        project_id: str,
        limit: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        执行相关测试用例查询。
        
        Args:
            test_case_id: 测试用例 ID
            project_id: 项目 ID（必需）
            limit: 返回结果数量限制
            **kwargs: 其他参数
            
        Returns:
            相关测试用例列表
            
        Raises:
            ToolError: 如果查询失败
        """
        try:
            if not project_id:
                raise ToolError(
                    tool_name=self.name,
                    message="project_id 是必需参数",
                    details={"test_case_id": test_case_id}
                )
            
            self.logger.info(f"查找与测试用例 {test_case_id} 相关的用例")
            
            # 调用 Go 后端推荐 API
            url = f"{self.backend_url}/api/v1/projects/{project_id}/testcases/{test_case_id}/recommendations"
            params = {"limit": limit}
            response = await self.http_client.get(url, params=params)
            
            # 检查响应状态
            if response.status_code != 200:
                raise ToolError(
                    tool_name=self.name,
                    message=f"Go 后端推荐 API 返回错误: {response.status_code}",
                    details={
                        "test_case_id": test_case_id,
                        "status_code": response.status_code,
                        "response": response.text
                    }
                )
            
            # 解析响应
            result = response.json()
            if result.get("code") != 200:
                raise ToolError(
                    tool_name=self.name,
                    message=f"获取推荐失败: {result.get('message', 'Unknown error')}",
                    details={"test_case_id": test_case_id, "result": result}
                )
            
            # 提取推荐结果
            recommendation_response = result.get("data", {})
            results = recommendation_response.get("results", [])
            
            # 转换为工具期望的格式
            formatted_results = []
            for item in results:
                formatted_results.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "content": item.get("content"),
                    "score": item.get("score"),
                    "metadata": item.get("metadata", {}),
                })
            
            self.logger.info(f"找到 {len(formatted_results)} 个相关测试用例")
            return formatted_results
        
        except ToolError:
            raise
        except Exception as e:
            self.logger.error(f"查找相关测试用例失败: {e}")
            raise ToolError(
                tool_name=self.name,
                message=f"获取相关测试用例失败: {str(e)}",
                details={"test_case_id": test_case_id, "error": str(e)}
            )
    
    async def close(self):
        """关闭 HTTP 客户端连接"""
        await self.http_client.aclose()
