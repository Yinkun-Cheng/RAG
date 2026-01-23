# AI测试工程智能系统设计说明书（Claude可读版）

本文档用于指导 Claude 协助开发一个基于 RAG + Agent + Workflows + Tools 架构的测试工程智能系统。本系统是在现有《测试用例知识库管理系统（RAG）》基础上的智能升级，目标是让系统不仅能检索知识，还能理解需求、推理测试点、自动生成高质量测试用例，并融入真实测试工程流程。

---

## 一、系统总体目标

将当前的结构化测试知识库系统升级为：

> 一个具备“理解 + 推理 + 决策 + 执行”能力的测试工程智能体系统。

核心目标包括：

* 自动根据新需求生成高质量测试用例
* 基于历史 PRD / 用例进行推理与复用
* 支持影响分析、回归推荐、用例补全等智能能力
* 架构可扩展、可演进、可平台化

---

## 二、系统总体架构（逻辑分层）

系统采用五层逻辑架构：

1. 接口层（UI / API / Dify）
2. 智能决策层（Agent / Subagent）
3. 能力编排层（Workflows）
4. 能力执行层（Tools）
5. 知识与数据层（PostgreSQL + Weaviate）

Claude 主要参与第 2～4 层的逻辑实现与协助推理。

---

## 三、Agent 体系设计

### 3.1 主 Agent：TestEngineerAgent

角色定位：模拟一名高级测试工程师，负责整体任务理解、决策与协调。

职责：

* 理解用户输入（需求、变更、问题）
* 判断任务类型（生成用例 / 影响分析 / 回归推荐 / 用例补全等）
* 选择合适的 Workflow 执行
* 判断是否需要调用 Subagent
* 对最终结果进行质量兜底

---

### 3.2 Subagent 设计（按真实测试岗位拆分）

#### RequirementAnalysisAgent（需求分析专家）

职责：

* 从自然语言需求中提取：功能点、业务规则、输入输出、约束条件、异常条件

#### TestDesignAgent（测试设计专家）

职责：

* 根据功能点生成：主流程、异常流、边界值、组合场景、安全/性能测试点

#### QualityReviewAgent（质量审查专家）

职责：

* 对生成用例进行覆盖度检查、结构完整性检查、重复检测、规范性校验

说明：

* Subagent 不是不同模型，而是同一模型通过不同 Prompt 角色运行

---

## 四、Tool 体系设计（原子能力层）

Tool 是系统中最小的可执行能力单元，负责具体操作。

### 4.1 检索类 Tool

* SearchPRDTool：按语义/条件检索 PRD
* SearchTestCaseTool：按语义/条件检索测试用例
* GetRelatedCasesTool：获取某 PRD 关联用例

### 4.2 理解类 Tool

* ParseRequirementTool：将自然语言需求结构化
* ExtractTestPointsTool：从需求中提取测试点

### 4.3 生成类 Tool

* GenerateTestCaseTool：根据测试点生成测试用例
* FormatTestCaseTool：将生成结果格式化为系统标准结构

### 4.4 校验类 Tool

* ValidateCoverageTool：检查测试覆盖度
* CheckDuplicationTool：检测重复用例
* CheckQualityTool：执行质量规则校验

### 4.5 存储类 Tool

* SaveTestCaseTool：保存新用例
* UpdateTestCaseTool：更新已有用例

---

## 五、Workflows 体系设计（业务能力组合层）

Workflow 是由多个 Subagent 和 Tool 组合而成的完整业务流程编排，直接面向业务目标。

### 5.1 Workflow：测试用例自动生成（核心能力）

内部调用：

* 检索 Tool（历史 PRD / 用例）
* 需求解析 Tool
* 测试点提取 Tool
* 用例生成 Tool
* 用例格式化 Tool
* 质量校验 Tool

目标输出：

* 一组结构完整、覆盖充分、可直接执行的测试用例

---

### 5.2 Workflow：影响分析

内部调用：

* PRD 检索 Tool
* 用例关联 Tool
* 变更差异分析 Tool
* 影响范围输出 Tool

目标输出：

* 需求变更影响的功能模块与测试用例清单

---

### 5.3 Workflow：回归测试推荐

内部调用：

* 历史用例检索 Tool
* 模块关联 Tool
* 版本变更分析 Tool
* 推荐排序 Tool

目标输出：

* 本次版本最优回归测试用例集合

---

### 5.4 Workflow：测试用例补全 / 优化

内部调用：

* 用例质量校验 Tool
* 缺失测试点识别 Tool
* 用例补全生成 Tool

目标输出：

* 对现有测试用例的补充与优化建议

---

## 六、Workflow 设计（系统执行流程）

以“测试用例自动生成”Workflow 为例：

1. 用户输入新需求
2. TestEngineerAgent 接收任务
3. 判断任务类型为“测试用例生成”
4. 调用对应 Skill
5. Skill 内部依次执行：

   * 检索历史知识
   * 解析新需求
   * 提取测试点
   * 生成测试用例
   * 质量校验
   * 格式化输出
6. 返回结果给用户，并支持保存到系统

---

## 七、数据与模块边界（与现有项目结构对齐）

建议新增模块结构如下：

internal/ai/

* agent/        → Agent 与 Subagent
* workflow/     → Workflows 业务流程编排层
* tool/         → Tool 原子能力层
* prompt/       → Prompt 模板管理

现有模块（rag、repository、service）可作为 Tool 的底层实现直接复用。

---

## 八、Prompt 设计原则（供 Claude 使用）

1. 每个 Agent / Subagent 使用独立角色 Prompt
2. 每个 Workflow 有明确目标、输入、输出约束
3. 所有输出尽量结构化（JSON / 表格 / 模板格式）
4. 优先可解释性，其次是完整性，再其次是简洁性

---

## 九、系统演进路线

阶段 1：单 Agent + 单 Workflow（测试用例生成）
阶段 2：引入 Subagent + 质量评分机制
阶段 3：平台化、多模型支持、MCP 接入

---

## 十、工程级总结

本系统不是简单的 RAG 问答系统，而是一个面向测试工程领域的智能决策平台。通过 Agent 架构、技能编排与结构化知识体系的融合，实现从“需求输入”到“高质量测试用例输出”的自动化闭环，推动测试管理从工具化走向智能化。

---

（本文件可直接提供给 Claude 作为系统设计与开发协助上下文使用）
