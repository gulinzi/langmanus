"""
文件管理工具模块

封装文件写入操作，集成日志记录功能
"""

import logging
# 导入LangChain社区文件管理工具
from langchain_community.tools.file_management import WriteFileTool
# 导入本地日志装饰器工具
from .decorators import create_logged_tool

# 初始化模块日志记录器
logger = logging.getLogger(__name__)  # 获取当前模块日志实例

"""
带日志的文件写入工具

通过create_logged_tool装饰器增强WriteFileTool
实现自动输入输出日志记录功能
"""
# 创建带日志功能的文件写入工具类
LoggedWriteFile = create_logged_tool(WriteFileTool)
# 实例化带日志的文件写入工具
write_file_tool = LoggedWriteFile()  # 创建工具实例
