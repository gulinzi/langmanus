"""
LangGraph工作流节点定义模块

包含所有工作流节点的实现，每个节点对应一个特定的功能模块
处理智能体之间的协作流程和状态转换
"""

import logging
import json
from copy import deepcopy
from typing import Literal
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from langgraph.graph import END

# 导入本地模块
from src.agents import research_agent, coder_agent, browser_agent  # 智能体实例
from src.agents.llm import get_llm_by_type  # LLM类型获取工具
from src.config import TEAM_MEMBERS  # 团队成员配置
from src.config.agents import AGENT_LLM_MAP  # 代理与LLM映射配置
from src.prompts.template import apply_prompt_template  # 提示模板应用工具
from src.tools.search import tavily_tool  # 搜索工具
from .types import State, Router  # 类型定义模块

# 初始化日志记录器
logger = logging.getLogger(__name__)

"""
响应格式模板

用于标准化各节点的响应输出格式
占位符：
- {}: 代理名称
- {}: 代理响应内容
"""
RESPONSE_FORMAT = "Response from {}:\n\n<response>\n{}\n</response>\n\n*Please execute the next step.*"


def research_node(state: State) -> Command[Literal["supervisor"]]:
    """
    研究员节点：执行网络搜索与信息收集任务
    
    功能说明：
    1. 调用研究员代理执行搜索任务
    2. 格式化返回结果
    3. 将执行权转交给监督者节点
    
    参数:
        state (State): 当前工作流状态
        
    返回:
        Command[Literal["supervisor"]]: 包含更新状态和跳转指令的命令对象
    """
    logger.info("Research agent starting task")  # 记录任务开始
    result = research_agent.invoke(state)  # 执行研究员代理任务
    logger.info("Research agent completed task")  # 记录任务完成
    logger.debug(f"Research agent response: {result['messages'][-1].content}")  # 调试信息
    
    # 返回状态更新和跳转指令
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "researcher", result["messages"][-1].content  # 格式化响应内容
                    ),
                    name="researcher",  # 消息发送者标识
                )
            ]
        },
        goto="supervisor",  # 下一跳转节点
    )


def code_node(state: State) -> Command[Literal["supervisor"]]:
    """
    程序员节点：执行Python代码生成与执行任务
    
    功能说明：
    1. 调用程序员代理执行代码任务
    2. 格式化返回结果
    3. 将执行权转交给监督者节点
    
    参数:
        state (State): 当前工作流状态
        
    返回:
        Command[Literal["supervisor"]]: 包含更新状态和跳转指令的命令对象
    """
    logger.info("Code agent starting task")  # 记录任务开始
    result = coder_agent.invoke(state)  # 执行程序员代理任务
    logger.info("Code agent completed task")  # 记录任务完成
    logger.debug(f"Code agent response: {result['messages'][-1].content}")  # 调试信息
    
    # 返回状态更新和跳转指令
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "coder", result["messages"][-1].content  # 格式化响应内容
                    ),
                    name="coder",  # 消息发送者标识
                )
            ]
        },
        goto="supervisor",  # 下一跳转节点
    )


def browser_node(state: State) -> Command[Literal["supervisor"]]:
    """
    浏览器节点：执行网页内容解析与交互任务
    
    功能说明：
    1. 调用浏览器代理执行浏览任务
    2. 格式化返回结果
    3. 将执行权转交给监督者节点
    
    参数:
        state (State): 当前工作流状态
        
    返回:
        Command[Literal["supervisor"]]: 包含更新状态和跳转指令的命令对象
    """
    logger.info("Browser agent starting task")  # 记录任务开始
    result = browser_agent.invoke(state)  # 执行浏览器代理任务
    logger.info("Browser agent completed task")  # 记录任务完成
    logger.debug(f"Browser agent response: {result['messages'][-1].content}")  # 调试信息
    
    # 返回状态更新和跳转指令
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "browser", result["messages"][-1].content  # 格式化响应内容
                    ),
                    name="browser",  # 消息发送者标识
                )
            ]
        },
        goto="supervisor",  # 下一跳转节点
    )


def supervisor_node(state: State) -> Command[Literal[*TEAM_MEMBERS, "__end__"]]:
    """
    监督者节点：决策下一执行代理
    
    功能说明：
    1. 应用监督者提示模板
    2. 调用LLM进行决策
    3. 处理决策结果并确定跳转目标
    
    参数:
        state (State): 当前工作流状态
        
    返回:
        Command[Literal[*TEAM_MEMBERS, "__end__"]]: 包含决策结果和跳转指令的命令对象
    """
    logger.info("Supervisor evaluating next action")  # 记录决策开始
    messages = apply_prompt_template("supervisor", state)  # 应用提示模板
    # 调用LLM进行结构化输出
    response = (
        get_llm_by_type(AGENT_LLM_MAP["supervisor"])
        .with_structured_output(Router)
        .invoke(messages)
    )
    goto = response["next"]  # 获取跳转目标
    logger.debug(f"Current state messages: {state['messages']}")  # 调试信息
    logger.debug(f"Supervisor response: {response}")  # 调试信息

    # 处理结束标志
    if goto == "FINISH":
        goto = "__end__"
        logger.info("Workflow completed")  # 记录流程结束
    else:
        logger.info(f"Supervisor delegating to: {goto}")  # 记录分配信息

    # 返回跳转指令和状态更新
    return Command(goto=goto, update={"next": goto})


def planner_node(state: State) -> Command[Literal["supervisor", "__end__"]]:
    """
    规划者节点：生成完整执行计划
    
    功能说明：
    1. 应用规划者提示模板
    2. 根据模式选择LLM类型
    3. 执行搜索预处理（如启用）
    4. 流式生成执行计划
    5. 返回计划结果和跳转指令
    
    参数:
        state (State): 当前工作流状态
        
    返回:
        Command[Literal["supervisor", "__end__"]]: 包含计划结果和跳转指令的命令对象
    """
    logger.info("Planner generating full plan")  # 记录计划生成开始
    messages = apply_prompt_template("planner", state)  # 应用规划者模板
    # 根据模式选择LLM类型
    llm = get_llm_by_type("basic")
    if state.get("deep_thinking_mode"):
        llm = get_llm_by_type("reasoning")
    
    # 处理搜索前置模式
    if state.get("search_before_planning"):
        searched_content = tavily_tool.invoke({"query": state["messages"][-1].content})  # 执行搜索
        messages = deepcopy(messages)  # 深拷贝防止修改原始数据
        # 添加搜索结果到消息内容
        messages[
            -1
        ].content += f"\n\n# Relative Search Results\n\n{json.dumps([{'titile': elem['title'], 'content': elem['content']} for elem in searched_content], ensure_ascii=False)}"

    # 流式生成计划
    stream = llm.stream(messages)
    full_response = ""
    for chunk in stream:
        full_response += chunk.content  # 收集完整响应

    # 调试信息记录
    logger.debug(f"Current state messages: {state['messages']}")
    logger.debug(f"Planner response: {full_response}")

    # 处理代码块包裹
    if full_response.startswith("```json"):
        full_response = full_response.removeprefix("```json")

    if full_response.endswith("```"):
        full_response = full_response.removesuffix("```")

    goto = "supervisor"  # 默认跳转目标
    try:
        json.loads(full_response)  # 验证JSON有效性
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")  # JSON解析失败
        goto = "__end__"

    # 返回状态更新和跳转指令
    return Command(
        update={
            "messages": [HumanMessage(content=full_response, name="planner")],  # 存储生成内容
            "full_plan": full_response,  # 保存完整计划
        },
        goto=goto,  # 确定跳转目标
    )


def coordinator_node(state: State) -> Command[Literal["planner", "__end__"]]:
    """
    协调者节点：与用户交互并决定是否转交给规划者
    
    功能说明：
    1. 应用协调者提示模板
    2. 调用LLM生成响应
    3. 决策是否移交规划者
    
    参数:
        state (State): 当前工作流状态
        
    返回:
        Command[Literal["planner", "__end__"]]: 包含决策结果的命令对象
    """
    logger.info("Coordinator talking.")  # 记录协调者交互
    messages = apply_prompt_template("coordinator", state)  # 应用提示模板
    response = get_llm_by_type(AGENT_LLM_MAP["coordinator"]).invoke(messages)  # 执行LLM调用
    logger.debug(f"Current state messages: {state['messages']}")  # 调试信息
    logger.debug(f"reporter response: {response}")  # 调试信息

    goto = "__end__"  # 默认结束流程
    if "handoff_to_planner" in response.content:
        goto = "planner"  # 检测到规划者移交指令

    return Command(
        goto=goto,  # 返回跳转指令
    )


def reporter_node(state: State) -> Command[Literal["supervisor"]]:
    """
    报告生成节点：编写最终报告
    
    功能说明：
    1. 应用报告者提示模板
    2. 生成结构化报告
    3. 将执行权转交给监督者节点
    
    参数:
        state (State): 当前工作流状态
        
    返回:
        Command[Literal["supervisor"]]: 包含报告内容和跳转指令的命令对象
    """
    logger.info("Reporter write final report")  # 记录报告生成开始
    messages = apply_prompt_template("reporter", state)  # 应用提示模板
    response = get_llm_by_type(AGENT_LLM_MAP["reporter"]).invoke(messages)  # 执行LLM调用
    logger.debug(f"Current state messages: {state['messages']}")  # 调试信息
    logger.debug(f"reporter response: {response}")  # 调试信息

    # 返回状态更新和跳转指令
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format("reporter", response.content),  # 格式化响应
                    name="reporter",  # 消息发送者标识
                )
            ]
        },
        goto="supervisor",  # 下一跳转节点
    )
