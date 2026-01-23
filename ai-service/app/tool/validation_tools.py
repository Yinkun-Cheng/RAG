"""
验证工具

提供测试用例验证能力，包括覆盖率检查、重复检测和质量验证。
"""

from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher
from .base import BaseTool, ToolError


class ValidateCoverageTool(BaseTool):
    """
    验证覆盖率工具。
    
    检查测试用例对需求分析的覆盖完整性，包括：
    - 功能点覆盖率
    - 异常条件覆盖率
    - 边界值覆盖率
    - 整体覆盖评分
    """
    
    def __init__(self):
        """初始化覆盖率验证工具。"""
        super().__init__(
            name="validate_coverage",
            description="验证测试用例对需求的覆盖完整性"
        )
    
    async def execute(
        self,
        test_cases: List[Dict[str, Any]],
        requirement_analysis: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行覆盖率验证。
        
        Args:
            test_cases: 测试用例列表
            requirement_analysis: 需求分析结果（来自 ParseRequirementTool）
            **kwargs: 其他参数
            
        Returns:
            覆盖率报告，包含：
            - overall_score: 整体覆盖率评分（0-100）
            - functional_coverage: 功能点覆盖率（0-100）
            - exception_coverage: 异常条件覆盖率（0-100）
            - boundary_coverage: 边界值覆盖率（0-100）
            - covered_points: 已覆盖的功能点列表
            - uncovered_points: 未覆盖的功能点列表
            - coverage_details: 详细覆盖信息
            
        Raises:
            ToolError: 如果验证失败
        """
        try:
            self.logger.info(f"验证 {len(test_cases)} 个测试用例的覆盖率")
            
            # 提取需求分析中的关键点
            functional_points = requirement_analysis.get("functional_points", [])
            exception_conditions = requirement_analysis.get("exception_conditions", [])
            constraints = requirement_analysis.get("constraints", [])
            
            # 检查功能点覆盖
            covered_functional = set()
            uncovered_functional = set()
            
            for fp in functional_points:
                is_covered = self._check_point_coverage(fp, test_cases)
                if is_covered:
                    covered_functional.add(fp)
                else:
                    uncovered_functional.add(fp)
            
            # 计算功能点覆盖率
            functional_coverage = (
                len(covered_functional) / max(len(functional_points), 1) * 100
            )
            
            # 检查异常条件覆盖
            exception_test_count = sum(
                1 for tc in test_cases 
                if tc.get("type") == "exception"
            )
            exception_coverage = min(
                exception_test_count / max(len(exception_conditions), 1) * 100,
                100
            )
            
            # 检查边界值覆盖
            boundary_test_count = sum(
                1 for tc in test_cases 
                if tc.get("type") == "boundary"
            )
            # 假设每个约束至少需要一个边界值测试
            boundary_coverage = min(
                boundary_test_count / max(len(constraints), 1) * 100,
                100
            )
            
            # 计算整体覆盖率（加权平均）
            overall_score = (
                functional_coverage * 0.5 +  # 功能点权重 50%
                exception_coverage * 0.3 +   # 异常条件权重 30%
                boundary_coverage * 0.2      # 边界值权重 20%
            )
            
            coverage_report = {
                "overall_score": round(overall_score, 2),
                "functional_coverage": round(functional_coverage, 2),
                "exception_coverage": round(exception_coverage, 2),
                "boundary_coverage": round(boundary_coverage, 2),
                "covered_points": list(covered_functional),
                "uncovered_points": list(uncovered_functional),
                "coverage_details": {
                    "total_functional_points": len(functional_points),
                    "covered_functional_points": len(covered_functional),
                    "total_exception_conditions": len(exception_conditions),
                    "exception_test_cases": exception_test_count,
                    "total_constraints": len(constraints),
                    "boundary_test_cases": boundary_test_count,
                }
            }
            
            self.logger.info(f"覆盖率验证完成，整体评分: {overall_score:.2f}%")
            return coverage_report
        
        except Exception as e:
            self.logger.error(f"覆盖率验证失败: {e}")
            raise ToolError(
                tool_name=self.name,
                message=f"验证覆盖率失败: {str(e)}",
                details={"test_case_count": len(test_cases), "error": str(e)}
            )
    
    def _check_point_coverage(
        self, 
        point: str, 
        test_cases: List[Dict[str, Any]]
    ) -> bool:
        """
        检查某个功能点是否被测试用例覆盖。
        
        Args:
            point: 功能点描述
            test_cases: 测试用例列表
            
        Returns:
            是否被覆盖
        """
        point_lower = point.lower()
        
        # 检查测试用例标题或前置条件中是否包含功能点关键词
        for tc in test_cases:
            title = tc.get("title", "").lower()
            preconditions = tc.get("preconditions", "").lower()
            expected_result = tc.get("expected_result", "").lower()
            
            # 提取功能点的关键词（简单分词）
            keywords = [w for w in point_lower.split() if len(w) > 2]
            
            # 如果标题、前置条件或预期结果中包含关键词，认为已覆盖
            for keyword in keywords:
                if (keyword in title or 
                    keyword in preconditions or 
                    keyword in expected_result):
                    return True
        
        return False


class CheckDuplicationTool(BaseTool):
    """
    检查重复工具。
    
    检测测试用例列表中的重复或高度相似的用例，帮助：
    - 识别冗余测试
    - 提高测试效率
    - 减少维护成本
    """
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        初始化重复检测工具。
        
        Args:
            similarity_threshold: 相似度阈值（0-1），默认 0.85
        """
        super().__init__(
            name="check_duplication",
            description="检测测试用例中的重复或高度相似用例"
        )
        self.similarity_threshold = similarity_threshold
    
    async def execute(
        self,
        test_cases: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行重复检测。
        
        Args:
            test_cases: 测试用例列表
            **kwargs: 其他参数（可包含 similarity_threshold 覆盖默认值）
            
        Returns:
            重复检测报告，包含：
            - duplicate_pairs: 重复用例对列表 [(index1, index2, similarity), ...]
            - duplicate_count: 重复用例数量
            - unique_count: 唯一用例数量
            - duplication_rate: 重复率（0-100）
            
        Raises:
            ToolError: 如果检测失败
        """
        try:
            threshold = kwargs.get("similarity_threshold", self.similarity_threshold)
            self.logger.info(f"检测 {len(test_cases)} 个测试用例的重复情况（阈值: {threshold}）")
            
            duplicate_pairs = []
            
            # 两两比较测试用例
            for i in range(len(test_cases)):
                for j in range(i + 1, len(test_cases)):
                    similarity = self._calculate_similarity(
                        test_cases[i],
                        test_cases[j]
                    )
                    
                    if similarity >= threshold:
                        duplicate_pairs.append((i, j, round(similarity, 3)))
            
            # 计算统计信息
            duplicate_indices = set()
            for i, j, _ in duplicate_pairs:
                duplicate_indices.add(i)
                duplicate_indices.add(j)
            
            duplicate_count = len(duplicate_indices)
            unique_count = len(test_cases) - duplicate_count
            duplication_rate = (
                duplicate_count / max(len(test_cases), 1) * 100
            )
            
            report = {
                "duplicate_pairs": duplicate_pairs,
                "duplicate_count": duplicate_count,
                "unique_count": unique_count,
                "duplication_rate": round(duplication_rate, 2),
                "total_cases": len(test_cases),
            }
            
            self.logger.info(
                f"重复检测完成，发现 {len(duplicate_pairs)} 对重复用例 "
                f"（重复率: {duplication_rate:.2f}%）"
            )
            return report
        
        except Exception as e:
            self.logger.error(f"重复检测失败: {e}")
            raise ToolError(
                tool_name=self.name,
                message=f"检测重复失败: {str(e)}",
                details={"test_case_count": len(test_cases), "error": str(e)}
            )
    
    def _calculate_similarity(
        self,
        tc1: Dict[str, Any],
        tc2: Dict[str, Any]
    ) -> float:
        """
        计算两个测试用例的相似度。
        
        Args:
            tc1: 测试用例 1
            tc2: 测试用例 2
            
        Returns:
            相似度评分（0-1）
        """
        # 比较标题相似度
        title1 = tc1.get("title", "")
        title2 = tc2.get("title", "")
        title_sim = SequenceMatcher(None, title1, title2).ratio()
        
        # 比较步骤相似度
        steps1 = self._extract_steps_text(tc1.get("steps", []))
        steps2 = self._extract_steps_text(tc2.get("steps", []))
        steps_sim = SequenceMatcher(None, steps1, steps2).ratio()
        
        # 比较预期结果相似度
        expected1 = tc1.get("expected_result", "")
        expected2 = tc2.get("expected_result", "")
        expected_sim = SequenceMatcher(None, expected1, expected2).ratio()
        
        # 加权平均（标题 40%，步骤 40%，预期结果 20%）
        similarity = (
            title_sim * 0.4 +
            steps_sim * 0.4 +
            expected_sim * 0.2
        )
        
        return similarity
    
    def _extract_steps_text(self, steps: List[Dict[str, Any]]) -> str:
        """
        从步骤列表中提取文本。
        
        Args:
            steps: 步骤列表
            
        Returns:
            合并的步骤文本
        """
        if not isinstance(steps, list):
            return ""
        
        text_parts = []
        for step in steps:
            if isinstance(step, dict):
                action = step.get("action", "")
                expected = step.get("expected", "")
                text_parts.append(f"{action} {expected}")
        
        return " ".join(text_parts)


class CheckQualityTool(BaseTool):
    """
    检查质量工具。
    
    对测试用例执行质量规则验证，检查：
    - 标题清晰度
    - 前置条件完整性
    - 步骤可执行性
    - 预期结果明确性
    - 命名规范
    """
    
    def __init__(self):
        """初始化质量检查工具。"""
        super().__init__(
            name="check_quality",
            description="执行测试用例质量规则验证"
        )
    
    async def execute(
        self,
        test_case: Dict[str, Any],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        执行质量检查。
        
        Args:
            test_case: 单个测试用例
            **kwargs: 其他参数
            
        Returns:
            质量问题列表，每个问题包含：
            - severity: 严重程度（error/warning/info）
            - rule: 规则名称
            - message: 问题描述
            - field: 相关字段
            
        Raises:
            ToolError: 如果检查失败
        """
        try:
            title = test_case.get("title", "")
            self.logger.info(f"检查测试用例质量: {title[:50]}...")
            
            issues = []
            
            # 规则 1: 标题应该清晰且具体（至少 10 个字符）
            if len(title) < 10:
                issues.append({
                    "severity": "warning",
                    "rule": "title_length",
                    "message": "标题过短，应该更具描述性（至少 10 个字符）",
                    "field": "title"
                })
            
            # 规则 2: 标题应该以"测试"开头
            if not title.startswith("测试") and not title.lower().startswith("test"):
                issues.append({
                    "severity": "info",
                    "rule": "title_format",
                    "message": "建议标题以'测试'开头，更符合命名规范",
                    "field": "title"
                })
            
            # 规则 3: 应该有前置条件
            preconditions = test_case.get("preconditions", "")
            if not preconditions or len(preconditions) < 5:
                issues.append({
                    "severity": "error",
                    "rule": "missing_preconditions",
                    "message": "前置条件缺失或不完整，应明确测试前的准备工作",
                    "field": "preconditions"
                })
            
            # 规则 4: 应该至少有 2 个测试步骤
            steps = test_case.get("steps", [])
            if not isinstance(steps, list) or len(steps) < 2:
                issues.append({
                    "severity": "warning",
                    "rule": "insufficient_steps",
                    "message": "测试步骤过少，建议至少包含 2 个步骤",
                    "field": "steps"
                })
            
            # 规则 5: 每个步骤应该有操作和预期
            for i, step in enumerate(steps):
                if isinstance(step, dict):
                    action = step.get("action", "")
                    expected = step.get("expected", "")
                    
                    if not action:
                        issues.append({
                            "severity": "error",
                            "rule": "missing_step_action",
                            "message": f"步骤 {i+1} 缺少操作描述",
                            "field": f"steps[{i}].action"
                        })
                    
                    if not expected:
                        issues.append({
                            "severity": "warning",
                            "rule": "missing_step_expected",
                            "message": f"步骤 {i+1} 缺少预期结果",
                            "field": f"steps[{i}].expected"
                        })
            
            # 规则 6: 预期结果应该明确且可验证
            expected_result = test_case.get("expected_result", "")
            if not expected_result or len(expected_result) < 10:
                issues.append({
                    "severity": "error",
                    "rule": "vague_expected_result",
                    "message": "预期结果应该明确且可验证（至少 10 个字符）",
                    "field": "expected_result"
                })
            
            # 规则 7: 优先级应该是有效值
            priority = test_case.get("priority", "")
            valid_priorities = ["high", "medium", "low", "高", "中", "低"]
            if priority and priority not in valid_priorities:
                issues.append({
                    "severity": "warning",
                    "rule": "invalid_priority",
                    "message": f"优先级值无效: {priority}，应为 high/medium/low",
                    "field": "priority"
                })
            
            # 规则 8: 测试类型应该是有效值
            test_type = test_case.get("type", "")
            valid_types = ["functional", "boundary", "exception", "功能", "边界", "异常"]
            if test_type and test_type not in valid_types:
                issues.append({
                    "severity": "warning",
                    "rule": "invalid_type",
                    "message": f"测试类型无效: {test_type}，应为 functional/boundary/exception",
                    "field": "type"
                })
            
            self.logger.info(f"质量检查完成，发现 {len(issues)} 个问题")
            return issues
        
        except Exception as e:
            self.logger.error(f"质量检查失败: {e}")
            raise ToolError(
                tool_name=self.name,
                message=f"检查质量失败: {str(e)}",
                details={"test_case_title": test_case.get("title", "Unknown"), "error": str(e)}
            )
