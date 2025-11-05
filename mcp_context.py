"""MCP (Model Context Protocol) - Quản lý context conversation"""
import json
from datetime import datetime
from typing import Dict
from redis_client import redis_client

class MCPContext:
    """Quản lý context và state của conversation"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.context = {
            "user_preferences": {},
            "conversation_history": [],
            "active_stocks": [],
            "last_queries": []
        }
    
    def add_message(self, role: str, content: str):
        """Thêm message vào context"""
        self.context["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.context["conversation_history"]) > 10:
            self.context["conversation_history"] = self.context["conversation_history"][-10:]
    
    def add_stock_to_context(self, symbol: str, data: Dict):
        """Thêm cổ phiếu vào active context"""
        stock_info = {
            "symbol": symbol,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.context["active_stocks"].append(stock_info)
        if len(self.context["active_stocks"]) > 5:
            self.context["active_stocks"] = self.context["active_stocks"][-5:]
    
    def get_context_summary(self) -> str:
        """Lấy tóm tắt context hiện tại"""
        summary = []
        if self.context["active_stocks"]:
            summary.append("Cổ phiếu đang theo dõi:")
            for stock in self.context["active_stocks"][-3:]:
                summary.append(f"  - {stock['symbol']}")
        return "\n".join(summary) if summary else "Chưa có cổ phiếu trong context"
    
    def save_to_redis(self):
        """Lưu context vào Redis"""
        if redis_client:
            key = f"mcp:context:{self.session_id}"
            redis_client.set(key, json.dumps(self.context), ex=7*24*60*60)
    
    @staticmethod
    def load_from_redis(session_id: str):
        """Load context từ Redis"""
        if redis_client:
            key = f"mcp:context:{session_id}"
            data = redis_client.get(key)
            if data:
                context = MCPContext(session_id)
                context.context = json.loads(data)
                return context
        return MCPContext(session_id)
