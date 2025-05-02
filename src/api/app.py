"""
FastAPI application for LangManus.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
import asyncio
from typing import AsyncGenerator, Dict, List, Any

from src.graph import build_graph
from src.config import TEAM_MEMBERS
from src.service.workflow_service import run_agent_workflow

# Configure logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LangManus API",
    description="API for LangManus LangGraph-based agent workflow",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create the graph
graph = build_graph()


class ContentItem(BaseModel):
    """内容项模型：用于描述消息中的多媒体内容元素"""
    type: str = Field(..., description="内容类型标识（文本、图片等）")
    text: Optional[str] = Field(None, description="当类型为'text'时的文本内容")
    image_url: Optional[str] = Field(
        None, description="当类型为'image'时的图片资源地址"
    )


class ChatMessage(BaseModel):
    """聊天消息模型：定义单条消息的结构"""
    role: str = Field(..., description="消息发送方角色（用户或助手）")
    content: Union[str, List[ContentItem]] = Field(
        ..., description="消息内容，可以是纯文本或多媒体内容列表"
    )


class ChatRequest(BaseModel):
    """聊天请求模型：定义客户端请求的数据结构"""
    messages: List[ChatMessage] = Field(..., description="完整的对话历史记录")
    debug: Optional[bool] = Field(False, description="是否启用调试日志模式")
    deep_thinking_mode: Optional[bool] = Field(
        False, description="是否启用深度思考模式"
    )
    search_before_planning: Optional[bool] = Field(
        False, description="是否在规划前执行搜索操作"
    )


@app.post("/api/chat/stream")
async def chat_endpoint(request: ChatRequest, req: Request):
    """
    流式聊天接口端点：处理LangGraph工作流的请求
    
    参数:
        request: 客户端发送的聊天请求数据
        req: FastAPI请求对象用于检查连接状态
    
    返回:
        事件流响应对象
    """
    try:
        # 将Pydantic模型转换为字典格式并标准化内容结构
        messages = []
        for msg in request.messages:
            message_dict = {"role": msg.role}  # 初始化基础消息结构
            
            # 处理两种内容形式：纯文本或内容项列表
            if isinstance(msg.content, str):
                message_dict["content"] = msg.content  # 直接使用纯文本
            else:
                # 对于多媒体内容列表进行格式转换
                content_items = []
                for item in msg.content:
                    if item.type == "text" and item.text:
                        # 添加文本内容项
                        content_items.append({"type": "text", "text": item.text})
                    elif item.type == "image" and item.image_url:
                        # 添加图片内容项
                        content_items.append(
                            {"type": "image", "image_url": item.image_url}
                        )
                message_dict["content"] = content_items  # 存储标准化内容
                
            messages.append(message_dict)  # 添加到最终消息列表

        async def event_generator():
            """事件生成器：异步处理工作流事件并生成流式响应"""
            try:
                # 执行代理工作流处理
                async for event in run_agent_workflow(
                    messages,  # 标准化后的消息
                    request.debug,  # 调试模式标志
                    request.deep_thinking_mode,  # 深度思考模式
                    request.search_before_planning,  # 搜索前置模式
                ):
                    # 实时检查客户端连接状态
                    if await req.is_disconnected():
                        logger.info("检测到客户端断开连接，终止工作流")
                        break
                    # 生成事件流数据包
                    yield {
                        "event": event["event"],  # 事件类型
                        "data": json.dumps(event["data"], ensure_ascii=False),  # 序列化数据
                    }
            except asyncio.CancelledError:
                logger.info("流处理任务被取消")
                raise

        return EventSourceResponse(  # 返回SSE响应
            event_generator(),  # 事件流生成器
            media_type="text/event-stream",  # 指定媒体类型
            sep="\n",  # 使用换行符分隔事件
        )
    except Exception as e:
        logger.error(f"聊天端点异常: {e}")  # 记录错误日志
        raise HTTPException(status_code=500, detail=str(e))  # 抛出HTTP异常
