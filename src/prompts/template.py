"""
提示模板处理模块

提供加载和格式化提示模板的核心功能
包含模板加载、占位符替换和系统提示生成等核心方法
"""

import os
import re
from datetime import datetime

from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt.chat_agent_executor import AgentState


def get_prompt_template(prompt_name: str) -> str:
    """
    加载并预处理原始提示模板
    
    功能说明：
    1. 读取指定名称的.md模板文件
    2. 对模板内容进行特殊字符转义处理
    3. 将自定义占位符转换为标准格式
    
    参数:
        prompt_name (str): 提示模板名称（对应.md文件名）
        
    返回:
        str: 处理后的模板字符串
        
    处理流程：
    1. 构建模板文件完整路径
    2. 读取原始模板内容
    3. 双重花括号转义：避免与Python字符串格式化冲突
    4. 自定义占位符转换：将<<VAR>>转换为{VAR}
    """
    # 构建模板文件路径并读取内容
    template = open(os.path.join(os.path.dirname(__file__), f"{prompt_name}.md")).read()
    
    # 对模板中的花括号进行转义处理
    # 避免与Python字符串格式化冲突
    template = template.replace("{", "{{").replace("}", "}}")
    
    # 将自定义占位符<<VAR>>转换为标准格式{VAR}
    # 支持嵌套变量名转换
    template = re.sub(r"<<([^>>]+)>>", r"{\1}", template)
    
    return template


def apply_prompt_template(prompt_name: str, state: AgentState) -> list:
    """
    应用提示模板到当前工作流状态
    
    功能说明：
    1. 加载指定名称的提示模板
    2. 注入当前时间和状态变量
    3. 生成最终的系统提示消息
    
    参数:
        prompt_name (str): 提示模板名称
        state (AgentState): 当前代理工作流状态
        
    返回:
        list: 包含系统提示和历史消息的对话记录
        
    处理流程：
    1. 创建带时间变量的PromptTemplate对象
    2. 注入当前时间和状态变量生成实际提示
    3. 将系统提示与历史消息合并返回
    """
    # 创建带当前时间变量的提示模板
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME"],
        template=get_prompt_template(prompt_name),
    ).format(
        # 格化当前时间戳
        CURRENT_TIME=datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        **state
    )
    
    # 返回组合消息列表
    # 系统提示作为首个系统角色消息
    # 后续接续历史消息
    return [{"role": "system", "content": system_prompt}] + state["messages"]
