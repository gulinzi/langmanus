"""
网页爬取工具模块

提供通过URL获取可读内容的功能，集成Crawler类实现核心爬取逻辑
支持返回结构化消息格式，包含爬取结果或错误信息
"""

import logging
from typing import Annotated  # 类型注解支持

# 导入LangChain组件
from langchain_core.messages import HumanMessage  # 人类消息类型
from langchain_core.tools import tool  # 工具装饰器
from .decorators import log_io  # 输入输出日志装饰器

# 导入本地模块
from src.crawler import Crawler  # 网页爬虫核心类

# 初始化模块日志记录器
logger = logging.getLogger(__name__)


@tool
@log_io
def crawl_tool(
    url: Annotated[str, "需要爬取的URL地址"],
) -> HumanMessage:
    """
    URL内容爬取工具
    
    功能：
    1. 接收目标URL参数
    2. 使用Crawler类执行爬取操作
    3. 返回结构化消息格式的结果
    4. 捕获并处理异常情况
    
    参数:
        url (Annotated[str, "需要爬取的URL地址"]): 目标网页地址
        
    返回:
        HumanMessage: 包含爬取结果的结构化消息对象
        
    异常处理：
    - BaseException: 捕获所有基础异常并返回错误信息
    """
    try:
        # 创建爬虫实例
        crawler = Crawler()
        
        # 执行网页爬取
        article = crawler.crawl(url)
        
        # 构建并返回结构化消息
        return {"role": "user", "content": article.to_message()}
        
    except BaseException as e:
        # 异常处理逻辑
        error_msg = f"网页爬取失败，错误信息: {repr(e)}"  # 构建错误信息
        logger.error(error_msg)  # 记录错误日志
        return error_msg  # 返回错误信息
