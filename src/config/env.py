"""
环境配置模块

包含系统运行所需的环境变量配置，分为推理型LLM、基础LLM、视觉语言LLM和浏览器实例配置四大模块。
所有配置项优先从环境变量读取，若未设置则使用默认值。
"""

import os
from dotenv import load_dotenv  # 用于加载.env文件中的环境变量

# 加载环境变量配置
# 会自动读取项目根目录下的.env文件
load_dotenv()

"""
推理型LLM配置（适用于复杂逻辑推理任务）

配置参数：
- 模型名称：REASONING_MODEL
- 基础URL：REASONING_BASE_URL
- API密钥：REASONING_API_KEY

默认模型：o1-mini
典型应用场景：数学计算、逻辑推理、复杂问题分析
"""
REASONING_MODEL = os.getenv("REASONING_MODEL", "o1-mini")     # 推理模型服务标识
REASONING_BASE_URL = os.getenv("REASONING_BASE_URL")         # 推理模型API基础地址
REASONING_API_KEY = os.getenv("REASONING_API_KEY")           # 推理模型认证密钥

"""
基础LLM配置（适用于常规文本处理任务）

配置参数：
- 模型名称：BASIC_MODEL
- 基础URL：BASIC_BASE_URL
- API密钥：BASIC_API_KEY

默认模型：gpt-4o
典型应用场景：文本生成、简单对话、数据处理
"""
BASIC_MODEL = os.getenv("BASIC_MODEL", "gpt-4o")             # 基础模型服务标识
BASIC_BASE_URL = os.getenv("BASIC_BASE_URL")                 # 基础模型API基础地址
BASIC_API_KEY = os.getenv("BASIC_API_KEY")                   # 基础模型认证密钥

"""
视觉语言LLM配置（适用于视觉内容理解任务）

配置参数：
- 模型名称：VL_MODEL
- 基础URL：VL_BASE_URL
- API密钥：VL_API_KEY

默认模型：gpt-4o
典型应用场景：图像识别、图表分析、多媒体内容处理
"""
VL_MODEL = os.getenv("VL_MODEL", "gpt-4o")                   # 视觉模型服务标识
VL_BASE_URL = os.getenv("VL_BASE_URL")                       # 视觉模型API基础地址
VL_API_KEY = os.getenv("VL_API_KEY")                         # 视觉模型认证密钥

"""
浏览器实例配置

配置参数：
- 实例路径：CHROME_INSTANCE_PATH

典型应用场景：无头浏览器操作、网页自动化测试、DOM解析
"""
CHROME_INSTANCE_PATH = os.getenv("CHROME_INSTANCE_PATH")    # Chrome实例工作路径配置
