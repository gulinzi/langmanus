"""
浏览器交互工具模块

提供基于浏览器的操作功能，支持同步和异步两种执行模式
"""

import asyncio
from pydantic import BaseModel, Field  # 数据模型验证
from typing import Optional, ClassVar, Type  # 类型提示
from langchain.tools import BaseTool  # LangChain基础工具类
from browser_use import AgentHistoryList, Browser, BrowserConfig  # 浏览器使用库
from browser_use import Agent as BrowserAgent  # 浏览器代理类
from src.agents.llm import vl_llm  # 视觉语言模型实例
from src.tools.decorators import create_logged_tool  # 日志装饰器
from src.config import CHROME_INSTANCE_PATH  # Chrome实例路径配置

# 全局浏览器实例
expected_browser = None

"""
初始化浏览器实例

如果配置了Chrome实例路径，创建带配置的浏览器对象
用于复用浏览器会话，保持登录状态等
"""
if CHROME_INSTANCE_PATH:
    expected_browser = Browser(
        config=BrowserConfig(chrome_instance_path=CHROME_INSTANCE_PATH)
    )


class BrowserUseInput(BaseModel):
    """
    浏览器操作输入模型
    
    定义浏览器工具的标准输入格式
    包含一个必需的指令字段，描述需要执行的浏览器操作
    """
    
    instruction: str = Field(..., description="浏览器操作指令，如'访问谷歌搜索浏览器使用库'")  # 中文化指令描述


class BrowserTool(BaseTool):
    """
    浏览器交互工具类
    
    提供同步和异步两种方式操作浏览器
    支持复杂网页交互任务，如导航、点击、表单填写等
    """
    
    name: ClassVar[str] = "browser"  # 工具名称
    args_schema: Type[BaseModel] = BrowserUseInput  # 输入参数模式
    description: ClassVar[str] = (
        "此工具用于与网页浏览器交互。输入应为自然语言描述，如'访问谷歌并搜索LangChain'，或'导航到Reddit查找关于人工智能的热门帖子'。"
    )  # 工具描述中文化

    _agent: Optional[BrowserAgent] = None  # 浏览器代理实例


    def _run(self, instruction: str) -> str:
        """
        同步执行浏览器任务
        
        功能：
        1. 创建浏览器代理实例
        2. 执行同步浏览器操作
        3. 处理异步事件循环
        4. 返回执行结果或错误信息
        
        参数:
            instruction (str): 自然语言描述的浏览器操作指令
            
        返回:
            str: 操作结果或错误描述
        """
        self._agent = BrowserAgent(
            task=instruction,  # 设置当前任务指令
            llm=vl_llm,  # 使用视觉语言模型
            browser=expected_browser,  # 使用预配置浏览器
        )
        
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 执行异步任务并获取结果
                result = loop.run_until_complete(self._agent.run())
                # 返回最终结果（处理历史记录列表）
                return (
                    str(result)
                    if not isinstance(result, AgentHistoryList)
                    else result.final_result
                )
            finally:
                loop.close()  # 确保事件循环正确关闭
        except Exception as e:
            # 捕获并处理所有异常
            return f"执行浏览器任务时发生错误: {str(e)}"


    async def _arun(self, instruction: str) -> str:
        """
        异步执行浏览器任务
        
        功能：
        1. 创建浏览器代理实例
        2. 异步执行浏览器操作
        3. 返回处理结果或错误信息
        
        参数:
            instruction (str): 自然语言描述的浏览器操作指令
            
        返回:
            str: 操作结果或错误描述
        """
        self._agent = BrowserAgent(
            task=instruction,  # 设置当前任务指令
            llm=vl_llm  # 使用视觉语言模型
        )
        
        try:
            # 异步执行任务
            result = await self._agent.run()
            # 返回最终结果（处理历史记录列表）
            return (
                str(result)
                if not isinstance(result, AgentHistoryList)
                else result.final_result
            )
        except Exception as e:
            # 捕获并处理所有异常
            return f"异步执行浏览器任务时发生错误: {str(e)}"


# 应用日志装饰器增强
BrowserTool = create_logged_tool(BrowserTool)
# 创建工具实例
browser_tool = BrowserTool()
