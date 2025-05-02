"""
LangGraph工作流构建模块

基于状态图定义多智能体协作流程，包含协调器、规划器、监督者等核心节点
"""

# 导入LangGraph核心组件
from langgraph.graph import StateGraph, START  # 状态图构建工具及起始节点

# 导入自定义类型定义
from .types import State  # 状态类型定义

# 导入各功能节点
from .nodes import (
    # 协调节点：负责任务分发与流程控制
    coordinator_node,
    
    # 规划节点：进行任务分解与执行计划制定
    planner_node,
    
    # 监督节点：全局决策与质量控制
    supervisor_node,
    
    # 研究节点：网络搜索与信息收集
    research_node,
    
    # 代码节点：代码生成与执行
    code_node,
    
    # 浏览器节点：网页内容解析与交互
    browser_node,
    
    # 报告节点：结构化内容生成
    reporter_node,
)

def build_graph():
    """
    构建完整的代理工作流图
    
    流程说明：
    1. 从协调节点开始任务分发
    2. 根据任务类型路由到相应专业节点
    3. 各节点协作完成任务处理
    4. 最终生成结构化报告
    
    返回:
        编译后的可执行状态图实例
    """
    # 创建状态图构建器
    builder = StateGraph(State)
    
    # 添加初始边：启动工作流
    builder.add_edge(START, "coordinator")  # 起始节点连接协调器
    
    # 添加核心功能节点
    builder.add_node("coordinator", coordinator_node)  # 任务协调中枢
    builder.add_node("planner", planner_node)          # 任务规划专家
    builder.add_node("supervisor", supervisor_node)    # 决策监督者
    builder.add_node("researcher", research_node)      # 信息研究员
    builder.add_node("coder", code_node)              # 代码工程师
    builder.add_node("browser", browser_node)          # 浏览器代理
    builder.add_node("reporter", reporter_node)        # 报告生成器
    
    # 返回编译后的可执行图
    return builder.compile()
