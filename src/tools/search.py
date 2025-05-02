"""
搜索工具模块

集成Tavily搜索服务并提供带日志记录的搜索工具实例
"""

import logging
# 导入LangChain社区版Tavily搜索工具
from langchain_community.tools.tavily_search import TavilySearchResults
# 导入搜索结果数量配置
from src.config import TAVILY_MAX_RESULTS
# 导入本地日志装饰器工具
from .decorators import create_logged_tool

# 初始化模块日志记录器
logger = logging.getLogger(__name__)  # 获取当前模块日志实例

"""
Tavily搜索工具初始化

通过create_logged_tool装饰器增强基础TavilySearchResults工具
生成带完整日志记录功能的搜索工具类
"""
# 创建带日志功能的Tavily搜索工具类
LoggedTavilySearch = create_logged_tool(TavilySearchResults)

"""
Tavily搜索工具实例

预配置的搜索工具实例，包含以下核心参数：
- name: 工具名称标识
- max_results: 搜索结果最大返回数量（基于系统配置）
"""
# 实例化带日志的搜索工具
tavily_tool = LoggedTavilySearch(name="tavily_search", max_results=TAVILY_MAX_RESULTS)
