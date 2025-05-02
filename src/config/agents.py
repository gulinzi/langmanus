from typing import Literal

"""
LLM能力类型定义模块

定义了系统支持的LLM能力类型，用于约束代理与LLM的映射关系
"""

# 定义LLM能力类型枚举
LLMType = Literal[
    "basic",     # 基础文本理解与生成能力
    "reasoning", # 强化推理与逻辑分析能力
    "vision"     # 视觉内容理解与处理能力
]

"""
代理-LLM映射配置

定义了各个智能代理与LLM能力类型的对应关系，包含以下核心代理：
- 协调者：负责任务分发与协调
- 规划师：进行任务分解与执行规划
- 监督者：进行全局决策与监控
- 研究员：执行网络搜索与信息收集
- 程序员：代码生成与调试
- 浏览器代理：网页内容解析与交互
- 报告生成器：结构化内容生成

注：此配置决定了不同代理使用的LLM类型，影响其核心能力表现
"""
AGENT_LLM_MAP: dict[str, LLMType] = {
    # 协调代理：使用基础能力LLM进行任务调度
    "coordinator": "basic",
    
    # 规划代理：使用推理能力LLM进行任务分解
    "planner": "reasoning",
    
    # 监督代理：使用基础能力LLM进行决策监控
    "supervisor": "basic",
    
    # 研究代理：使用基础能力LLM执行搜索任务
    "researcher": "basic",
    
    # 程序员代理：使用基础能力LLM进行代码生成
    "coder": "basic",
    
    # 浏览器代理：使用视觉能力LLM处理视觉内容
    "browser": "vision",
    
    # 报告生成代理：使用基础能力LLM生成文档
    "reporter": "basic",
}
