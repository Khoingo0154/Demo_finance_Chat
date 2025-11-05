import json
import logging
import asyncio
import inspect
import uuid
from datetime import datetime

from mcp_context import MCPContext
from rag_system import StockRAG
from redis_client import redis_client

# Google ADK imports
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.agents.invocation_context import InvocationContext

# -------------------------------------------------------------------------
# Logging setup
# -------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class StockAgentMCP:
    """Stock Agent tích hợp MCP Context + RAG + Google ADK"""

    def __init__(self, base_agent):
        if base_agent is None:
            raise ValueError("base_agent không được None")
        self.base_agent = base_agent
        self.rag = StockRAG()
        self.sessions = {}
        self.session_service = InMemorySessionService()

    # ---------------------------------------------------------------------
    def get_session(self, session_id: str):
        """Lấy hoặc khởi tạo session"""
        if session_id not in self.sessions:
            logger.info(f"🔹 Tạo session mới cho user {session_id}")
            self.sessions[session_id] = {
                "mcp_context": MCPContext.load_from_redis(session_id),
                "created_at": datetime.now().isoformat(),
            }
        return self.sessions[session_id]

    # ---------------------------------------------------------------------
    def query(self, user_message: str, session_id: str) -> str:
        """Xử lý truy vấn người dùng"""
        session = self.get_session(session_id)
        mcp_context = session["mcp_context"]

        # Ghi nhận hội thoại
        mcp_context.add_message("user", user_message)
        rag_context = self.rag.get_relevant_context(user_message)

        enhanced_message = (
            f"[RAG Context]\n{rag_context}\n\n"
            f"[Conversation Context]\n{mcp_context.get_context_summary()}\n\n"
            f"[User Query]\n{user_message}"
        )

        try:
            response_text = self._call_llm_sync(enhanced_message, session_id)
        except Exception as e:
            logger.exception("❌ Lỗi khi gọi base_agent:")
            response_text = f"❌ Lỗi khi gọi mô hình: {e}"

        # Lưu lại hội thoại
        mcp_context.add_message("assistant", str(response_text))
        try:
            mcp_context.save_to_redis()
        except Exception as e:
            logger.warning(f"⚠️ Không thể lưu MCP context: {e}")

        try:
            self._save_conversation(session_id, user_message, str(response_text))
        except Exception as e:
            logger.warning(f"⚠️ Không thể lưu hội thoại: {e}")

        return str(response_text)

    # ---------------------------------------------------------------------
    def _call_llm_sync(self, prompt: str, session_id: str) -> str:
        """Wrapper đồng bộ an toàn"""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            return asyncio.run_coroutine_threadsafe(self._call_llm_async(prompt, session_id), loop).result()
        else:
            return asyncio.run(self._call_llm_async(prompt, session_id))

    # ---------------------------------------------------------------------
    async def _call_llm_async(self, prompt: str, session_id: str) -> str:
        """Gọi Google ADK agent đúng cách với InvocationContext"""
        logger.info("🧠 Gọi run_async() với InvocationContext...")

        try:
            # ✅ Tạo session (phải await)
            session = await self.session_service.create_session(
                app_name="stock_agent_app",
                user_id=session_id
            )

            # ✅ Tạo InvocationContext và gán input
            context = InvocationContext(
                agent=self.base_agent,
                session_service=self.session_service,
                session=session,
                invocation_id=str(uuid.uuid4())
            )
            context.input = prompt  # ✅ Gán input vào context thay vì truyền param

            # ✅ Gọi run_async
            result_gen = self.base_agent.run_async(context)

            if inspect.isasyncgen(result_gen):
                logger.info("📡 Phát hiện async generator → thu output stream")
                collected = ""
                async for chunk in result_gen:
                    if hasattr(chunk, "output_text"):
                        collected += chunk.output_text
                    elif hasattr(chunk, "text"):
                        collected += chunk.text
                    elif isinstance(chunk, str):
                        collected += chunk
                logger.info(f"✅ Nhận được {len(collected)} ký tự phản hồi")
                return collected

        except Exception as e:
            logger.warning(f"⚠️ Lỗi khi run_async(): {e}")

        # 🔄 Fallback nếu run_async lỗi
        logger.info("🔄 Thử generate_content() hoặc __call__() ...")
        try:
            if hasattr(self.base_agent, "generate_content"):
                res = self.base_agent.generate_content(prompt)
                if asyncio.iscoroutine(res):
                    res = await res
                return self._parse_result(res)

            if callable(self.base_agent):
                res = self.base_agent(prompt)
                if asyncio.iscoroutine(res):
                    res = await res
                return self._parse_result(res)
        except Exception as e:
            logger.warning(f"⚠️ generate_content/__call__ failed: {e}")

        available = [m for m in dir(self.base_agent) if not m.startswith("_")]
        raise AttributeError(
            f"❌ Không thể gọi agent. Có thể do:\n"
            f"1️⃣ Model chưa được cấu hình đúng\n"
            f"2️⃣ API key chưa được set\n"
            f"3️⃣ Phiên bản Google ADK không tương thích\n\n"
            f"Debug:\n{available}"
        )

    # ---------------------------------------------------------------------
    def _parse_result(self, result) -> str:
        """Parse kết quả LLM"""
        if hasattr(result, "output_text"):
            return result.output_text
        if hasattr(result, "text"):
            return result.text
        if isinstance(result, dict):
            return result.get("output_text") or result.get("text") or str(result)
        if isinstance(result, str):
            return result
        return str(result)

    # ---------------------------------------------------------------------
    def _save_conversation(self, session_id: str, user_message: str, agent_response: str):
        """Lưu hội thoại vào Redis"""
        if not redis_client:
            return
        key = f"chat:session:{session_id}"
        data = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "agent_response": agent_response,
        }
        redis_client.rpush(key, json.dumps(data))
        redis_client.expire(key, 7 * 24 * 60 * 60)


# -------------------------------------------------------------------------
# Test độc lập
# -------------------------------------------------------------------------
if __name__ == "__main__":
    import os

    os.environ["GOOGLE_GENAI_API_KEY"] = os.getenv("GEMINI_API_KEY", "")
    model_name = "gemini-2.0-flash-exp"

    print(f"\n🧪 Testing model: {model_name}")
    agent_core = LlmAgent(name="stock_agent", model=model_name)
    print("✅ LlmAgent created!")

    stock_agent = StockAgentMCP(agent_core)
    resp = stock_agent.query("Phân tích cổ phiếu FPT hôm nay", "debug")
    print("\n✅ Response:")
    print(resp[:500])




# """Stock Agent với MCP và RAG"""
# import json
# from datetime import datetime
# from google.adk.agents import LlmAgent
# from google.adk import Agent

# from mcp_context import MCPContext
# from rag_system import StockRAG
# from redis_client import redis_client
# from tools import get_stock_quote, get_company_info
# class StockAgentMCP:
#     """Stock Agent với MCP context management và RAG"""
    
#     def __init__(self, base_agent: LlmAgent):
#         self.base_agent = base_agent
#         self.rag = StockRAG()
#         self.sessions = {}  # Dictionary để lưu nhiều sessions
    
#     def get_session(self, session_id: str):
#         """Lấy hoặc tạo session mới"""
#         if session_id not in self.sessions:
#             self.sessions[session_id] = {
#                 "mcp_context": MCPContext.load_from_redis(session_id),
#                 "created_at": datetime.now().isoformat()
#             }
#         return self.sessions[session_id]
    
#     def query(self, user_message: str, session_id: str) -> str:
#         """Query agent với MCP context và RAG enhancement"""
        
#         # Lấy session
#         session = self.get_session(session_id)
#         mcp_context = session["mcp_context"]
        
#         # Thêm message vào MCP context
#         mcp_context.add_message("user", user_message)
        
#         # Lấy relevant context từ RAG
#         rag_context = self.rag.get_relevant_context(user_message)
        
#         # Tạo enhanced prompt với context
#         enhanced_message = f"""
# [Context từ RAG System]
# {rag_context}

# [Conversation Context]
# {mcp_context.get_context_summary()}

# [User Query]
# {user_message}
# """
        
#         # Gọi agent
#         response = self.base_agent.query(enhanced_message)
        
#         # Lưu response vào context
#         mcp_context.add_message("assistant", response)
        
#         # Lưu context vào Redis
#         mcp_context.save_to_redis()
        
#         # Lưu conversation vào Redis
#         self._save_conversation(session_id, user_message, response)
        
#         return response
    
#     def _save_conversation(self, session_id: str, user_message: str, agent_response: str):
#         """Lưu conversation vào Redis"""
#         if not redis_client:
#             return
        
#         conversation_key = f"chat:session:{session_id}"
#         conversation_data = {
#             "timestamp": datetime.now().isoformat(),
#             "user_message": user_message,
#             "agent_response": agent_response
#         }
        
#         redis_client.rpush(conversation_key, json.dumps(conversation_data))
#         redis_client.expire(conversation_key, 7 * 24 * 60 * 60)