from langgraph.prebuilt import create_react_agent

from src.prompts import apply_prompt_template
from src.tools import (
    bash_tool,
    browser_tool,
    crawl_tool,
    python_repl_tool,
    tavily_tool,
)

from .llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP

# 基于配置创建智能代理实例
# 研究员代理：使用搜索引擎和爬虫工具
research_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["researcher"]),  # 获取对应类型的LLM
    tools=[tavily_tool, crawl_tool],              # 配置可用工具
    prompt=lambda state: apply_prompt_template("researcher", state),  # 应用提示模板
)

# 代码工程师代理：使用Python解释器和Bash工具
coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["coder"]),      # 获取对应类型的LLM
    tools=[python_repl_tool, bash_tool],          # 配置可用工具
    prompt=lambda state: apply_prompt_template("coder", state),       # 应用提示模板
)

# 浏览器代理：使用浏览器交互工具
browser_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["browser"]),    # 获取对应类型的LLM
    tools=[browser_tool],                         # 配置可用工具
    prompt=lambda state: apply_prompt_template("browser", state),     # 应用提示模板
)
