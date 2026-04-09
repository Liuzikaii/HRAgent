"""LangChain Agent — HR policy expert powered by DeepSeek + RAG."""

import logging
from typing import AsyncGenerator

from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.config import get_settings
from app.services.rag import retrieve_context

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一位专业的人力资源（HR）智能助手，服务于企业员工和管理者。你的职责是：

1. **准确回答**：基于提供的参考文档内容，准确、专业地回答关于公司政策、员工手册、考勤制度、薪酬福利、请假规定等方面的问题。
2. **引用依据**：回答时尽量引用参考文档中的具体条款或规定，增强回答的可信度。
3. **友好专业**：保持友好、专业的语气，像一位经验丰富的 HR 顾问一样提供帮助。
4. **诚实透明**：如果参考文档中没有相关信息，明确告知用户，并建议他们向 HR 部门进一步咨询。
5. **格式清晰**：使用 Markdown 格式让回答结构清晰、易读。使用列表、加粗等格式增强可读性。

注意事项：
- 不要编造参考文档中没有的信息
- 涉及具体数字（如假期天数、报销金额等）时，务必与参考文档一致
- 对于政策变更或有争议的问题，建议用户联系 HR 部门确认"""


def _get_llm() -> ChatDeepSeek:
    """Create a ChatDeepSeek LLM instance."""
    settings = get_settings()
    return ChatDeepSeek(
        model="deepseek-chat",
        api_key=settings.deepseek_api_key,
        temperature=0.3,
        max_tokens=2048,
    )


def build_messages(
    query: str,
    chat_history: list[dict] | None = None,
) -> list:
    """Build the message list with RAG context and chat history."""
    # Retrieve relevant context from Milvus
    context = retrieve_context(query)

    # Build the user message with context
    if context:
        user_content = f"""请基于以下参考文档内容回答用户的问题。

--- 参考文档 ---
{context}
--- 参考文档结束 ---

用户问题：{query}"""
    else:
        user_content = f"""用户问题：{query}

注意：知识库中暂无相关文档，请根据你的 HR 专业知识尽力回答，并建议用户向 HR 部门确认。"""

    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # Add chat history (last 10 messages for context window management)
    if chat_history:
        for msg in chat_history[-10:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=user_content))
    return messages


async def chat(query: str, chat_history: list[dict] | None = None) -> str:
    """Send a query to the HR Agent and get a response."""
    llm = _get_llm()
    messages = build_messages(query, chat_history)
    response = await llm.ainvoke(messages)
    return response.content


async def chat_stream(query: str, chat_history: list[dict] | None = None) -> AsyncGenerator[str, None]:
    """Stream a response from the HR Agent."""
    llm = _get_llm()
    messages = build_messages(query, chat_history)
    async for chunk in llm.astream(messages):
        if chunk.content:
            yield chunk.content
