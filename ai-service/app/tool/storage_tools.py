"""
存储工具

提供测试用例存储能力，通过 Go 后端 API 保存和更新测试用例。
"""

import httpx
from typing import List, Dict, Any, Optional
from .base import BaseTool, ToolError


class SaveTestCaseTool(BaseTool):
    """
    保存测试用例工具。
    
    通过 Go 后端 API 保存测试用例到 PostgreSQL 和 Weaviate，包括：
    - 创建新测试用例
    - 保存测试步骤
    - 自动生成向量并存储
    - 关联 PRD 和模块
    """
    
    def __init__(self, go_backend_url: str):
        """
        初始化保存测试用例工具。
        
        Args:
            go_backend_url: Go 后端 URL（如 http://localhost:8080）
        """
        super().__init__(
            name="save_test_case",
            description="通过 Go 后端 API 保存测试用例"
        )
        self.go_backend_url = go_backend_url.rstrip("/")
    
    async def execute(
        self,
        project_id: str,
        test_case: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行测试用例保存。
        
        Args:
            project_id: 项目 ID
            test_case: 测试用例数据
            **kwargs: 其他参数（如 prd_id, module_id, app_version_id, tag_ids）
            
        Returns:
            保存结果，包含：
            - id: 测试用例 ID
            - title: 测试用例标题
            - created_at: 创建时间
            - version: 版本号
            
        Raises:
            ToolError: 如果保存失败
        """
        try:
            title = test_case.get("title", "Unknown")
            self.logger.info(f"保存测试用例: {title[:50]}...")
            
            # 构建请求数据
            request_data = self._build_request_data(test_case, kwargs)
            
            # 调用 Go 后端 API
            url = f"{self.go_backend_url}/api/v1/projects/{project_id}/testcases"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    error_detail = response.text
                    raise ToolError(
                        tool_name=self.name,
                        message=f"保存测试用例失败: HTTP {response.status_code}",
                        details={"error": error_detail, "url": url}
                    )
                
                result = response.json()
                
                # 提取数据
                if result.get("code") == 0 and "data" in result:
                    saved_case = result["data"]
                    self.logger.info(f"测试用例保存成功: ID={saved_case.get('id')}")
                    return saved_case
                else:
                    raise ToolError(
                        tool_name=self.name,
                        message="保存测试用例失败: 响应格式错误",
                        details={"response": result}
                    )
        
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP 请求失败: {e}")
            raise ToolError(
                tool_name=self.name,
                message=f"保存测试用例失败: {str(e)}",
                details={"error": str(e), "url": url}
            )
        except Exception as e:
            self.logger.error(f"保存测试用例失败: {e}")
            raise ToolError(
                tool_name=self.name,
                message=f"保存测试用例失败: {str(e)}",
                details={"test_case_title": title, "error": str(e)}
            )
    
    def _build_request_data(
        self,
        test_case: Dict[str, Any],
        kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        构建 Go 后端 API 请求数据。
        
        Args:
            test_case: 测试用例数据
            kwargs: 其他参数
            
        Returns:
            请求数据字典
        """
        # 提取测试步骤
        steps = test_case.get("steps", [])
        formatted_steps = []
        
        for step in steps:
            if isinstance(step, dict):
                formatted_steps.append({
                    "step_number": step.get("step_number", 0),
                    "action": step.get("action", ""),
                    "expected_result": step.get("expected", ""),
                    "screenshots": []  # 暂时为空
                })
        
        # 构建请求数据
        request_data = {
            "title": test_case.get("title", ""),
            "preconditions": test_case.get("preconditions", ""),
            "steps": formatted_steps,
            "expected_result": test_case.get("expected_result", ""),
            "priority": test_case.get("priority", "medium"),
            "type": test_case.get("type", "functional"),
            "status": kwargs.get("status", "active"),
        }
        
        # 添加可选字段
        if "prd_id" in kwargs:
            request_data["prd_id"] = kwargs["prd_id"]
        
        if "module_id" in kwargs:
            request_data["module_id"] = kwargs["module_id"]
        
        if "app_version_id" in kwargs:
            request_data["app_version_id"] = kwargs["app_version_id"]
        
        if "tag_ids" in kwargs:
            request_data["tag_ids"] = kwargs["tag_ids"]
        
        if "description" in kwargs:
            request_data["description"] = kwargs["description"]
        
        return request_data


class UpdateTestCaseTool(BaseTool):
    """
    更新测试用例工具。
    
    通过 Go 后端 API 更新现有测试用例，包括：
    - 更新测试用例内容
    - 更新测试步骤
    - 重新生成向量
    - 创建新版本
    """
    
    def __init__(self, go_backend_url: str):
        """
        初始化更新测试用例工具。
        
        Args:
            go_backend_url: Go 后端 URL（如 http://localhost:8080）
        """
        super().__init__(
            name="update_test_case",
            description="通过 Go 后端 API 更新测试用例"
        )
        self.go_backend_url = go_backend_url.rstrip("/")
    
    async def execute(
        self,
        project_id: str,
        test_case_id: str,
        test_case: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行测试用例更新。
        
        Args:
            project_id: 项目 ID
            test_case_id: 测试用例 ID
            test_case: 更新的测试用例数据
            **kwargs: 其他参数（如 change_description）
            
        Returns:
            更新结果，包含：
            - id: 测试用例 ID
            - version: 新版本号
            - updated_at: 更新时间
            
        Raises:
            ToolError: 如果更新失败
        """
        try:
            title = test_case.get("title", "Unknown")
            self.logger.info(f"更新测试用例: {title[:50]}... (ID: {test_case_id})")
            
            # 构建请求数据
            request_data = self._build_request_data(test_case, kwargs)
            
            # 调用 Go 后端 API
            url = f"{self.go_backend_url}/api/v1/projects/{project_id}/testcases/{test_case_id}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.put(
                    url,
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    error_detail = response.text
                    raise ToolError(
                        tool_name=self.name,
                        message=f"更新测试用例失败: HTTP {response.status_code}",
                        details={"error": error_detail, "url": url}
                    )
                
                result = response.json()
                
                # 提取数据
                if result.get("code") == 0 and "data" in result:
                    updated_case = result["data"]
                    self.logger.info(
                        f"测试用例更新成功: ID={test_case_id}, "
                        f"Version={updated_case.get('version')}"
                    )
                    return updated_case
                else:
                    raise ToolError(
                        tool_name=self.name,
                        message="更新测试用例失败: 响应格式错误",
                        details={"response": result}
                    )
        
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP 请求失败: {e}")
            raise ToolError(
                tool_name=self.name,
                message=f"更新测试用例失败: {str(e)}",
                details={"error": str(e), "url": url}
            )
        except Exception as e:
            self.logger.error(f"更新测试用例失败: {e}")
            raise ToolError(
                tool_name=self.name,
                message=f"更新测试用例失败: {str(e)}",
                details={
                    "test_case_id": test_case_id,
                    "test_case_title": title,
                    "error": str(e)
                }
            )
    
    def _build_request_data(
        self,
        test_case: Dict[str, Any],
        kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        构建 Go 后端 API 请求数据。
        
        Args:
            test_case: 测试用例数据
            kwargs: 其他参数
            
        Returns:
            请求数据字典
        """
        # 提取测试步骤
        steps = test_case.get("steps", [])
        formatted_steps = []
        
        for step in steps:
            if isinstance(step, dict):
                formatted_steps.append({
                    "step_number": step.get("step_number", 0),
                    "action": step.get("action", ""),
                    "expected_result": step.get("expected", ""),
                    "screenshots": []  # 暂时为空
                })
        
        # 构建请求数据
        request_data = {
            "title": test_case.get("title", ""),
            "preconditions": test_case.get("preconditions", ""),
            "steps": formatted_steps,
            "expected_result": test_case.get("expected_result", ""),
            "priority": test_case.get("priority", "medium"),
            "type": test_case.get("type", "functional"),
        }
        
        # 添加可选字段
        if "status" in kwargs:
            request_data["status"] = kwargs["status"]
        
        if "change_description" in kwargs:
            request_data["change_description"] = kwargs["change_description"]
        
        if "prd_id" in kwargs:
            request_data["prd_id"] = kwargs["prd_id"]
        
        if "module_id" in kwargs:
            request_data["module_id"] = kwargs["module_id"]
        
        if "app_version_id" in kwargs:
            request_data["app_version_id"] = kwargs["app_version_id"]
        
        if "tag_ids" in kwargs:
            request_data["tag_ids"] = kwargs["tag_ids"]
        
        if "description" in kwargs:
            request_data["description"] = kwargs["description"]
        
        return request_data
