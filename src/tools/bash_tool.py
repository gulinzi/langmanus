"""
Bash命令执行工具模块

提供安全执行系统命令的能力，包含详细的错误处理和日志记录
"""

import logging
import subprocess
from typing import Annotated
from langchain_core.tools import tool  # LangChain工具装饰器
from .decorators import log_io  # 输入输出日志装饰器

# 初始化日志记录器
logger = logging.getLogger(__name__)  # 获取当前模块日志实例


@tool
@log_io
def bash_tool(
    cmd: Annotated[str, "需要执行的Bash命令"],
):
    """
    系统命令执行工具
    
    功能：
    1. 安全地执行指定的Bash命令
    2. 返回标准输出结果
    3. 捕获并处理异常情况
    
    参数:
        cmd (Annotated[str, "需要执行的Bash命令"]): 目标系统命令字符串
    
    返回:
        str: 命令执行输出或错误信息
    
    异常处理：
    - CalledProcessError: 命令执行失败时返回详细错误信息
    - 其他异常：捕获所有非预期错误并返回友好提示
    """
    logger.info(f"正在执行Bash命令: {cmd}")  # 记录命令执行日志
    
    try:
        # 执行系统命令并捕获输出
        result = subprocess.run(
            cmd,  # 待执行的命令
            shell=True,  # 启用shell执行
            check=True,  # 检查返回码
            text=True,  # 返回文本格式
            capture_output=True  # 捕获标准输出和错误
        )
        # 返回命令执行的标准输出
        return result.stdout
        
    except subprocess.CalledProcessError as e:
        # 处理命令执行失败情况
        error_message = (
            f"命令执行失败，退出码 {e.returncode}\n"
            f"标准输出: {e.stdout}\n"
            f"错误输出: {e.stderr}"
        )
        logger.error(error_message)  # 记录错误日志
        return error_message  # 返回错误详情
        
    except Exception as e:
        # 处理其他意外情况
        error_message = f"执行命令时发生错误: {str(e)}"
        logger.error(error_message)  # 记录错误日志
        return error_message  # 返回错误详情


if __name__ == "__main__":
    """模块自测试入口"""
    print(bash_tool.invoke("ls -all"))  # 测试bash命令执行功能
