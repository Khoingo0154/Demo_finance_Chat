import json
from datetime import datetime
from google import genai
from google.genai import types
from mcp_context import MCPContext
from rag_system import StockRAG
from redis_client import redis_client
from config import GEMINI_API_KEY

class StockAgentMCP:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = "gemini-2.0-flash-exp"
        self.rag = StockRAG()
        self.sessions = {}
        print("✅ Agent khởi tạo thành công")
    
    def get_session(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "mcp_context": MCPContext.load_from_redis(session_id),
                "created_at": datetime.now().isoformat()
            }
        return self.sessions[session_id]
    
    def query(self, user_message: str, session_id: str) -> str:
        try:
            # Build prompt
            prompt = f"""Bạn là trợ lý AI về chứng khoán.
            
User hỏi: {user_message}

Hãy trả lời ngắn gọn bằng tiếng Việt."""
            
            # Call Gemini
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text if response.text else "Xin lỗi, tôi không thể trả lời."
            
        except Exception as e:
            print(f"Error: {e}")
            return f"Lỗi: {str(e)}"
    
    def _save_conversation(self, session_id: str, user_message: str, agent_response: str):
        pass  # Skip for now