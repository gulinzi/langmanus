"""
Python代码执行工具模块

提供安全执行Python代码的能力，支持数据分析和计算任务
集成REPL环境和日志记录功能，支持异常捕获与错误反馈
"""

import logging
from typing import Annotated  # 类型注解支持
# 导入LangChain核心工具
from langchain_core.tools import tool  # 工具装饰器
from langchain_experimental.utilities import PythonREPL  # Python代码执行环境
# 导入本地装饰器
from .decorators import log_io  # 输入输出日志装饰器

"""
初始化REPL执行环境

创建Python代码执行沙箱实例
配置日志记录器
"""
repl = PythonREPL()  # 创建REPL实例
logger = logging.getLogger(__name__)  # 获取当前模块日志实例


@tool
@log_io
def python_repl_tool(
    code: Annotated[
        str, "需要执行的Python代码，用于数据分析或计算"
    ],
):
    """
    Python代码执行工具
    
    功能：
    1. 安全执行提供的Python代码
    2. 支持数据分析和数学计算
    3. 捕获并处理执行异常
    4. 返回格式化的执行结果
    
    参数:
        code (Annotated[str, "需要执行的Python代码"]): 待执行的代码字符串
        
    返回:
        str: 代码执行结果或错误信息
        
    注意事项：
    - 需要显式使用print()输出结果
    - 捕获所有基础异常并返回错误详情
    """
    logger.info("正在执行Python代码")  # 记录代码执行开始
    
    try:
        # 执行Python代码
        result = repl.run(code)  # 运行代码并获取结果
        logger.info("代码执行成功")  # 记录成功信息
        
    except BaseException as e:
        # 异常处理逻辑
        error_msg = f"代码执行失败，错误信息: {repr(e)}"  # 构建错误信息
        logger.error(error_msg)  # 记录错误日志
        return error_msg  # 返回错误信息
    
    # 构建执行结果字符串
    result_str = (
        f"代码执行成功：\n"
        f"```python\n{code}\n```\n"
        f"标准输出：{result}"
    )
    
    return result_str  # 返回格式化结果
