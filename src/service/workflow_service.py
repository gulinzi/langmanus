"""
工作流服务模块

提供异步代理工作流的执行与事件流处理功能
包含唯一标识生成、日志配置和多智能体协作流程处理
"""

import logging
from src.config import TEAM_MEMBERS  # 团队成员配置
from src.graph import build_graph  # 工作流图构建工具
from langchain_community.adapters.openai import convert_message_to_dict  # 消息格式转换工具
import uuid  # 通用唯一标识符生成模块

"""
日志系统配置

设置基础日志格式与输出级别
格式：时间戳 - 模块名 - 日志级别 - 日志内容
"""
logging.basicConfig(
    level=logging.INFO,  # 默认日志级别：INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志输出格式
)


def enable_debug_logging():
    """
    启用调试日志模式
    
    功能：
    将src模块的日志级别提升至DEBUG级别
    用于获取更详细的执行过程信息
    """
    logging.getLogger("src").setLevel(logging.DEBUG)  # 设置源码调试级别日志


# 初始化模块日志记录器
logger = logging.getLogger(__name__)  # 获取当前模块日志实例

# Create the graph
graph = build_graph()

# Cache for coordinator messages
coordinator_cache = []
MAX_CACHE_SIZE = 2


async def run_agent_workflow(
    user_input_messages: list,
    debug: bool = False,
    deep_thinking_mode: bool = False,
    search_before_planning: bool = False,
):
    """
    异步执行代理工作流
    
    功能说明：
    1. 接收用户输入消息并初始化工作流
    2. 根据配置启用调试日志
    3. 生成唯一工作流ID
    4. 管理代理间消息缓存
    5. 处理工作流事件流
    
    参数:
        user_input_messages (list): 用户请求消息列表
        debug (bool): 是否启用调试日志
        deep_thinking_mode (bool): 是否启用深度思考模式
        search_before_planning (bool): 是否在规划前执行搜索
        
    返回:
        异步生成器：逐步产出工作流事件数据
    """
    if not user_input_messages:
        raise ValueError("输入消息列表不能为空")  # 输入校验

    if debug:
        enable_debug_logging()  # 启用调试日志模式

    logger.info(f"启动工作流，用户输入: {user_input_messages}")  # 记录工作流启动

    workflow_id = str(uuid.uuid4())  # 生成唯一工作流标识

    """
    流式处理代理列表
    
    包含所有团队成员代理及规划者和协调者
    用于识别需要流式处理的代理节点
    """
    streaming_llm_agents = [*TEAM_MEMBERS, "planner", "coordinator"]

    # 每次工作流启动时重置协调者缓存
    global coordinator_cache
    coordinator_cache = []  # 清空历史缓存
    global is_handoff_case
    is_handoff_case = False  # 重置移交案例标识

    """
    执行图模型事件流处理
    
    事件处理流程：
    1. 初始化工作流状态
    2. 流式处理图模型事件
    3. 解析事件类型与数据
    4. 生成标准化事件流输出
    
    参数说明：
    - TEAM_MEMBERS: 团队成员列表（常量）
    - messages: 用户输入消息（运行时变量）
    - deep_thinking_mode: 深度思考模式开关（运行时变量）
    - search_before_planning: 规划前搜索开关（运行时变量）
    """
    async for event in graph.astream_events(
        {
            # 常量配置
            "TEAM_MEMBERS": TEAM_MEMBERS,
            # 运行时变量
            "messages": user_input_messages,  # 用户输入消息
            "deep_thinking_mode": deep_thinking_mode,  # 深度思考模式
            "search_before_planning": search_before_planning,  # 搜索前置模式
        },
        version="v2",  # 使用v2版本事件流
    ):
        # 提取事件关键属性
        kind = event.get("event")  # 事件类型
        data = event.get("data")  # 事件数据
        name = event.get("name")  # 代理名称
        metadata = event.get("metadata")  # 事件元数据
        
        # 解析节点名称
        node = (
            ""  # 默认空字符串
            if (metadata.get("checkpoint_ns") is None)  # 检查点命名空间
            else metadata.get("checkpoint_ns").split(":")[0]  # 取第一个命名空间
        )
        
        # 解析图执行步骤
        langgraph_step = (
            ""  # 默认空字符串
            if (metadata.get("langgraph_step") is None)  # 获取执行步骤
            else str(metadata["langgraph_step"])  # 转换为字符串
        )
        
        # 提取运行ID
        run_id = "" if (event.get("run_id") is None) else str(event["run_id"])  # 运行时唯一标识

        # 处理链启动事件
        if kind == "on_chain_start" and name in streaming_llm_agents:
            if name == "planner":  # 当规划者启动时
                yield {
                    "event": "start_of_workflow",  # 工作流开始事件
                    "data": {  # 事件数据
                        "workflow_id": workflow_id,  # 工作流唯一标识
                        "input": user_input_messages,  # 初始输入消息
                    },
                }
            # 代理启动事件
            ydata = {
                "event": "start_of_agent",  # 代理开始事件
                "data": {
                    "agent_name": name,  # 代理名称
                    "agent_id": f"{workflow_id}_{name}_{langgraph_step}",  # 代理唯一ID
                },
            }
        
        # 处理链结束事件
        elif kind == "on_chain_end" and name in streaming_llm_agents:
            # 代理结束事件
            ydata = {
                "event": "end_of_agent",  # 代理结束事件
                "data": {
                    "agent_name": name,  # 代理名称
                    "agent_id": f"{workflow_id}_{name}_{langgraph_step}",  # 代理唯一ID
                },
            }
        
        # 处理LLM模型启动事件
        elif kind == "on_chat_model_start" and node in streaming_llm_agents:
            # LLM启动事件
            ydata = {
                "event": "start_of_llm",  # LLM开始事件
                "data": {"agent_name": node},  # 相关代理名称
            }
        
        # 处理LLM模型结束事件
        elif kind == "on_chat_model_end" and node in streaming_llm_agents:
            # LLM结束事件
            ydata = {
                "event": "end_of_llm",  # LLM结束事件
                "data": {"agent_name": node},  # 相关代理名称
            }
        elif kind == "on_chat_model_stream" and node in streaming_llm_agents:
            """处理流式LLM输出事件"""
            content = data["chunk"].content  # 获取原始内容
            
            # 处理空消息情况
            if content is None or content == "":
                if not data["chunk"].additional_kwargs.get("reasoning_content"):
                    # 忽略空消息
                    continue
                
                # 生成推理内容事件
                ydata = {
                    "event": "message",  # 消息事件
                    "data": {
                        "message_id": data["chunk"].id,  # 消息唯一标识
                        "delta": {
                            "reasoning_content": (  # 推理内容
                                data["chunk"].additional_kwargs["reasoning_content"]
                            )
                        },
                    },
                }
            
            # 处理普通内容
            else:
                # 处理协调者代理的特殊逻辑
                if node == "coordinator":
                    # 缓存管理
                    if len(coordinator_cache) < MAX_CACHE_SIZE:
                        coordinator_cache.append(content)  # 添加到缓存
                        cached_content = "".join(coordinator_cache)  # 合并缓存内容
                        
                        # 检测转交案例
                        if cached_content.startswith("handoff"):
                            is_handoff_case = True  # 标记转交案例
                            continue  # 跳过当前内容
                    
                        # 缓存未满时继续收集
                        if len(coordinator_cache) < MAX_CACHE_SIZE:
                            continue
                    
                    # 生成缓存消息
                    ydata = {
                        "event": "message",  # 消息事件
                        "data": {
                            "message_id": data["chunk"].id,  # 消息唯一标识
                            "delta": {"content": cached_content},  # 缓存内容
                        },
                    }
                
                # 处理其他代理消息
                elif not is_handoff_case:
                    # 直接发送消息
                    ydata = {
                        "event": "message",  # 消息事件
                        "data": {
                            "message_id": data["chunk"].id,  # 消息唯一标识
                            "delta": {"content": content},  # 原始内容
                        },
                    }
                
                # 默认发送消息
                else:
                    # 其他情况直接发送消息
                    ydata = {
                        "event": "message",  # 消息事件
                        "data": {
                            "message_id": data["chunk"].id,  # 消息唯一标识
                            "delta": {"content": content},  # 原始内容
                        },
                    }
        # 处理工具调用事件
        elif kind == "on_tool_start" and node in TEAM_MEMBERS:
            """工具调用开始"""
            ydata = {
                "event": "tool_call",  # 工具调用事件
                "data": {
                    "tool_call_id": f"{workflow_id}_{node}_{name}_{run_id}",  # 调用ID
                    "tool_name": name,  # 工具名称
                    "tool_input": data.get("input"),  # 工具输入参数
                },
            }
        
        # 处理工具调用结束事件
        elif kind == "on_tool_end" and node in TEAM_MEMBERS:
            """工具调用结果"""
            ydata = {
                "event": "tool_call_result",  # 工具调用结果事件
                "data": {
                    "tool_call_id": f"{workflow_id}_{node}_{name}_{run_id}",  # 调用ID
                    "tool_name": name,  # 工具名称
                    "tool_result": data["output"].content if data.get("output") else "",  # 工具结果
                },
            }
        else:
            continue
        yield ydata

    # 处理转交案例结束
    if is_handoff_case:
        """生成工作流结束事件"""
        yield {
            "event": "end_of_workflow",  # 工作流结束事件
            "data": {
                "workflow_id": workflow_id,  # 工作流唯一标识
                "messages": [  # 最终消息列表
                    convert_message_to_dict(msg)  # 转换消息格式
                    for msg in data["output"].get("messages", [])  # 获取输出消息
                ],
            },
        }
