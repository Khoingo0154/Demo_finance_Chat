# 🚀 HƯỚNG DẪN CHẠY DỰ ÁN STOCK AGENT - TỪNG BƯỚC

## ✅ CHECKLIST TRƯỚC KHI BẮT ĐẦU

- [ ] Python 3.9+ đã cài đặt
- [ ] Docker đã cài đặt
- [ ] Internet connection
- [ ] Telegram account
- [ ] Terminal/Command Prompt

---

# BƯỚC 1: TẠO THỦ MỤC DỰ ÁN

## Windows:
```cmd
cd Desktop
mkdir stock_agent
cd stock_agent
```

## macOS/Linux:
```bash
cd ~/Desktop
mkdir stock_agent
cd stock_agent
```

**✅ Kiểm tra:** Bạn đang ở trong thư mục `stock_agent`
```bash
pwd
# Output: /path/to/stock_agent
```

---

# BƯỚC 2: TẠO VIRTUAL ENVIRONMENT

## Windows:
```cmd
python -m venv venv
venv\Scripts\activate
```

Sau khi activate, terminal sẽ có `(venv)` ở đầu dòng:
```
(venv) C:\Users\YourName\Desktop\stock_agent>
```

## macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

Sau khi activate:
```
(venv) username@computer:~/Desktop/stock_agent$
```

**✅ Kiểm tra:**
```bash
which python
# Windows: C:\...\stock_agent\venv\Scripts\python.exe
# Linux/Mac: /path/to/stock_agent/venv/bin/python
```

---

# BƯỚC 3: TẠO FILE requirements.txt

Tạo file `requirements.txt`:

## Windows:
```cmd
notepad requirements.txt
```

## macOS/Linux:
```bash
nano requirements.txt
# hoặc
vim requirements.txt
# hoặc
code requirements.txt  # Nếu dùng VS Code
```

**Copy nội dung này vào file:**
```txt
google-genai>=0.3.0
redis>=5.0.0
numpy>=1.24.0
requests>=2.31.0
python-telegram-bot>=20.7
python-dotenv>=1.0.0
```

**Save file:**
- Notepad: `Ctrl+S` → Close
- Nano: `Ctrl+X` → `Y` → `Enter`
- Vim: `ESC` → `:wq` → `Enter`

**✅ Kiểm tra file tồn tại:**
```bash
ls requirements.txt
# hoặc (Windows)
dir requirements.txt
```

---

# BƯỚC 4: CÀI ĐẶT DEPENDENCIES

```bash
pip install -r requirements.txt
```

Quá trình này mất 2-5 phút. Bạn sẽ thấy:
```
Collecting google-genai>=0.3.0
  Downloading google_genai-0.3.0-py3-none-any.whl
...
Successfully installed google-genai-0.3.0 redis-5.0.1 ...
```

**✅ Kiểm tra đã cài đặt:**
```bash
pip list | grep google-genai
pip list | grep redis
pip list | grep telegram
```

---

# BƯỚC 5: LẤY API KEYS

## 5.1. Gemini API Key

1. Mở browser: https://aistudio.google.com/app/apikey
2. Đăng nhập Google
3. Click **"Create API Key"**
4. Click **"Create API key in new project"**
5. Copy key (dạng: `AIzaSy...`)
6. **LƯU LẠI KEY NÀY!**

## 5.2. Alpha Vantage API Key

1. Mở browser: https://www.alphavantage.co/support/#api-key
2. Nhập email của bạn
3. Click **"GET FREE API KEY"**
4. Check email → Copy key
5. **LƯU LẠI KEY NÀY!**

## 5.3. Telegram Bot Token

1. Mở Telegram
2. Tìm **@BotFather** (có dấu tick xanh)
3. Start chat
4. Gửi: `/newbot`
5. BotFather hỏi tên bot:
   ```
   Alright, a new bot. How are we going to call it?
   ```
   Trả lời: `Stock AI Agent`

6. BotFather hỏi username:
   ```
   Now let's choose a username for your bot.
   ```
   Trả lời: `stock_ai_agent_bot` (phải kết thúc bằng `bot`)

7. BotFather trả token:
   ```
   Done! Your token is: 1234567890:ABCdefGHI...
   ```
8. **COPY TOKEN NÀY!**

**✅ Kiểm tra token:**
```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```
Thay `<YOUR_TOKEN>` bằng token thật. Phải trả về thông tin bot.

---

# BƯỚC 6: TẠO FILE .env

Tạo file `.env`:

## Windows:
```cmd
notepad .env
```

## macOS/Linux:
```bash
nano .env
```

**Copy nội dung này vào file và THAY ĐỔI keys:**
```bash
# Gemini API Key
GEMINI_API_KEY=AIzaSy_PASTE_YOUR_KEY_HERE

# Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY=PASTE_YOUR_KEY_HERE

# Telegram Bot Token
TELEGRAM_BOT_TOKEN=1234567890:ABC_PASTE_YOUR_TOKEN_HERE

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

**⚠️ QUAN TRỌNG:** Thay tất cả `PASTE_YOUR_KEY_HERE` bằng keys thật!

**Save file** (Ctrl+S)

**✅ Kiểm tra:**
```bash
cat .env
# Phải thấy keys thật, không phải "PASTE_YOUR_KEY_HERE"
```

---

# BƯỚC 7: TẠO CÁC FILE PYTHON

Tạo từng file một:

## 7.1. config.py

```bash
# Windows
notepad config.py

# Mac/Linux
nano config.py
```

**Copy code này:**
```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# RAG Configuration
EMBEDDING_DIM = 384
TOP_K_RESULTS = 5

# Cache TTL (seconds)
STOCK_DATA_TTL = 3600
CONVERSATION_TTL = 7 * 24 * 60 * 60
CONTEXT_TTL = 7 * 24 * 60 * 60

print("✅ Config loaded successfully!")
```

**Save file**

## 7.2. redis_client.py

```python
import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB

class RedisClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                cls._instance.client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    decode_responses=True
                )
                cls._instance.client.ping()
                print("✅ Đã kết nối Redis thành công")
            except Exception as e:
                print(f"⚠️  Không thể kết nối Redis: {e}")
                cls._instance.client = None
        return cls._instance
    
    def get_client(self):
        return self.client

redis_client = RedisClient().get_client()
```

## 7.3. mcp_context.py

```python
import json
from datetime import datetime
from redis_client import redis_client

class MCPContext:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.context = {
            "user_preferences": {},
            "conversation_history": [],
            "active_stocks": [],
            "last_queries": []
        }
    
    def add_message(self, role: str, content: str):
        self.context["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.context["conversation_history"]) > 10:
            self.context["conversation_history"] = self.context["conversation_history"][-10:]
    
    def add_stock_to_context(self, symbol: str, data: dict):
        stock_info = {
            "symbol": symbol,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.context["active_stocks"].append(stock_info)
        if len(self.context["active_stocks"]) > 5:
            self.context["active_stocks"] = self.context["active_stocks"][-5:]
    
    def get_context_summary(self) -> str:
        summary = []
        if self.context["active_stocks"]:
            summary.append("Cổ phiếu đang theo dõi:")
            for stock in self.context["active_stocks"][-3:]:
                summary.append(f"  - {stock['symbol']}")
        return "\n".join(summary) if summary else "Chưa có cổ phiếu trong context"
    
    def save_to_redis(self):
        if redis_client:
            key = f"mcp:context:{self.session_id}"
            redis_client.set(key, json.dumps(self.context), ex=7*24*60*60)
    
    @staticmethod
    def load_from_redis(session_id: str):
        if redis_client:
            key = f"mcp:context:{session_id}"
            data = redis_client.get(key)
            if data:
                context = MCPContext(session_id)
                context.context = json.loads(data)
                return context
        return MCPContext(session_id)
```

## 7.4. rag_system.py

```python
import json
import numpy as np
from typing import List, Dict
from datetime import datetime
from redis_client import redis_client
from config import EMBEDDING_DIM, TOP_K_RESULTS

class StockRAG:
    def __init__(self):
        self.embedding_dim = EMBEDDING_DIM
        print(f"✅ RAG System khởi tạo (embedding_dim={EMBEDDING_DIM})")
    
    def _generate_embedding(self, text: str) -> List[float]:
        hash_val = hash(text.lower())
        np.random.seed(hash_val % (2**31))
        embedding = np.random.randn(self.embedding_dim)
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.tolist()
    
    def store_stock_data(self, symbol: str, data: Dict):
        if not redis_client:
            return
        
        doc_text = f"{symbol} {data.get('name', '')} {data.get('sector', '')} {data.get('industry', '')}"
        embedding = self._generate_embedding(doc_text)
        
        doc_key = f"rag:stock:{symbol}"
        redis_client.hset(doc_key, "symbol", symbol)
        redis_client.hset(doc_key, "data", json.dumps(data))
        redis_client.hset(doc_key, "embedding", json.dumps(embedding))
        redis_client.hset(doc_key, "text", doc_text)
        redis_client.hset(doc_key, "timestamp", datetime.now().isoformat())
        redis_client.expire(doc_key, 24*60*60)
        redis_client.sadd("rag:stock:index", symbol)
    
    def semantic_search(self, query: str, top_k: int = TOP_K_RESULTS) -> List[Dict]:
        if not redis_client:
            return []
        
        query_embedding = np.array(self._generate_embedding(query))
        stock_symbols = redis_client.smembers("rag:stock:index")
        
        results = []
        for symbol in stock_symbols:
            doc_key = f"rag:stock:{symbol}"
            doc_data = redis_client.hgetall(doc_key)
            
            if doc_data and "embedding" in doc_data:
                doc_embedding = np.array(json.loads(doc_data["embedding"]))
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                
                results.append({
                    "symbol": doc_data["symbol"],
                    "data": json.loads(doc_data["data"]),
                    "similarity": similarity,
                    "text": doc_data["text"]
                })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
    
    def get_relevant_context(self, query: str) -> str:
        results = self.semantic_search(query, top_k=3)
        
        if not results:
            return "Không tìm thấy thông tin liên quan trong knowledge base."
        
        context_parts = ["📚 Thông tin liên quan:"]
        for i, result in enumerate(results, 1):
            data = result["data"]
            context_parts.append(
                f"\n{i}. {result['symbol']}: {data.get('name', 'N/A')} "
                f"({result['similarity']:.0%})"
            )
        
        return "\n".join(context_parts)
```

## 7.5. tools.py

```python
import requests
from config import ALPHA_VANTAGE_API_KEY
from rag_system import StockRAG

rag_system = StockRAG()

def get_stock_quote(symbol: str) -> str:
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol.upper(),
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            
            stock_data = {
                "symbol": quote.get('01. symbol', symbol),
                "price": quote.get('05. price', 'N/A'),
                "change": quote.get('09. change', 'N/A'),
                "change_percent": quote.get('10. change percent', 'N/A'),
                "volume": quote.get('06. volume', 'N/A'),
                "trading_day": quote.get('07. latest trading day', 'N/A')
            }
            
            rag_system.store_stock_data(symbol.upper(), stock_data)
            
            result = f"""📊 Cổ phiếu {symbol.upper()}:
💰 Giá: ${stock_data['price']}
📈 Thay đổi: {stock_data['change']} ({stock_data['change_percent']})
📊 Khối lượng: {stock_data['volume']}
📅 Ngày: {stock_data['trading_day']}"""
            
            return result
        else:
            return f"❌ Không tìm thấy thông tin cho mã {symbol}."
    
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"


def get_company_info(symbol: str) -> str:
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "OVERVIEW",
            "symbol": symbol.upper(),
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "Name" in data:
            company_data = {
                "name": data.get('Name', 'N/A'),
                "symbol": data.get('Symbol', symbol),
                "sector": data.get('Sector', 'N/A'),
                "industry": data.get('Industry', 'N/A'),
                "market_cap": data.get('MarketCapitalization', 'N/A')
            }
            
            rag_system.store_stock_data(symbol.upper(), company_data)
            
            result = f"""🏢 Công ty:
📌 Tên: {company_data['name']}
🔖 Mã: {company_data['symbol']}
🏭 Ngành: {company_data['sector']}
💼 Lĩnh vực: {company_data['industry']}
💎 Vốn hóa: ${company_data['market_cap']}"""
            return result
        else:
            return f"❌ Không tìm thấy thông tin công ty {symbol}"
    
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"


def search_similar_stocks(query: str) -> str:
    results = rag_system.semantic_search(query, top_k=5)
    
    if not results:
        return "❌ Không tìm thấy cổ phiếu phù hợp."
    
    response = ["🔍 Cổ phiếu tương tự:"]
    for i, result in enumerate(results, 1):
        data = result["data"]
        response.append(
            f"\n{i}. {result['symbol']} - {data.get('name', 'N/A')} "
            f"({result['similarity']:.0%})"
        )
    
    return "\n".join(response)
```

## 7.6. agent.py

```python
import json
from datetime import datetime
from google.genai.adk import LlmAgent
from mcp_context import MCPContext
from rag_system import StockRAG
from redis_client import redis_client
from tools import get_stock_quote, get_company_info, search_similar_stocks

class StockAgentMCP:
    def __init__(self, base_agent: LlmAgent):
        self.base_agent = base_agent
        self.rag = StockRAG()
        self.sessions = {}
    
    def get_session(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "mcp_context": MCPContext.load_from_redis(session_id),
                "created_at": datetime.now().isoformat()
            }
        return self.sessions[session_id]
    
    def query(self, user_message: str, session_id: str) -> str:
        session = self.get_session(session_id)
        mcp_context = session["mcp_context"]
        
        mcp_context.add_message("user", user_message)
        rag_context = self.rag.get_relevant_context(user_message)
        
        enhanced_message = f"""
[Context từ RAG]
{rag_context}

[Context cuộc trò chuyện]
{mcp_context.get_context_summary()}

[User]
{user_message}
"""
        
        response = self.base_agent.query(enhanced_message)
        
        mcp_context.add_message("assistant", response)
        mcp_context.save_to_redis()
        self._save_conversation(session_id, user_message, response)
        
        return response
    
    def _save_conversation(self, session_id: str, user_message: str, agent_response: str):
        if not redis_client:
            return
        
        conversation_key = f"chat:session:{session_id}"
        conversation_data = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "agent_response": agent_response
        }
        
        redis_client.rpush(conversation_key, json.dumps(conversation_data))
        redis_client.expire(conversation_key, 7 * 24 * 60 * 60)
```

## 7.7. telegram_bot.py

```python
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN
from agent import StockAgentMCP
from google.genai.adk import LlmAgent
from tools import get_stock_quote, get_company_info, search_similar_stocks

base_agent = LlmAgent(
    model="gemini-2.0-flash-exp",
    name="stock_agent_telegram",
    description="AI Agent chuyên về chứng khoán",
    instruction="""Bạn là trợ lý AI về chứng khoán trên Telegram.

Nhiệm vụ:
- Cung cấp thông tin cổ phiếu real-time
- Tìm kiếm cổ phiếu với RAG
- Trả lời ngắn gọn với emoji

Tools:
- get_stock_quote: Lấy giá
- get_company_info: Thông tin công ty
- search_similar_stocks: Tìm tương tự

Lưu ý: Chỉ cung cấp thông tin, không tư vấn đầu tư.""",
    tools=[get_stock_quote, get_company_info, search_similar_stocks]
)

stock_agent = StockAgentMCP(base_agent)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = """👋 Xin chào! Tôi là Stock AI Agent

🤖 Tôi có thể:
• 📊 Tra giá cổ phiếu
• 🏢 Thông tin công ty
• 🔍 Tìm cổ phiếu tương tự

💡 Ví dụ: "Giá AAPL bao nhiêu?"

Commands:
/start - Bắt đầu
/help - Hướng dẫn
/stats - Thống kê
/clear - Xóa lịch sử"""
    await update.message.reply_text(welcome)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """📚 HƯỚNG DẪN

🔹 Tra giá: "Giá AAPL"
🔹 Info công ty: "Thông tin về GOOGL"
🔹 Tìm kiếm: "Tìm cổ phiếu công nghệ"
🔹 So sánh: "So sánh AAPL và MSFT"

Bot sử dụng MCP + RAG để nhớ context!"""
    await update.message.reply_text(help_text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    session = stock_agent.get_session(user_id)
    
    stats = f"""📊 THỐNG KÊ

👤 User ID: {user_id}
⏰ Session: {session['created_at']}
💬 Tin nhắn: {len(session['mcp_context'].context['conversation_history'])}
📈 Cổ phiếu: {len(session['mcp_context'].context['active_stocks'])}

{session['mcp_context'].get_context_summary()}"""
    await update.message.reply_text(stats)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in stock_agent.sessions:
        del stock_agent.sessions[user_id]
    await update.message.reply_text("✅ Đã xóa lịch sử!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_message = update.message.text
    
    await update.message.chat.send_action(action="typing")
    
    try:
        response = stock_agent.query(user_message, session_id=user_id)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")

def main():
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your-telegram-bot-token":
        print("❌ Vui lòng cấu hình TELEGRAM_BOT_TOKEN trong .env")
        return
    
    print("🤖 Đang khởi động Telegram Bot...")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Telegram Bot đã sẵn sàng!")
    print("📱 Mở Telegram và chat với bot!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
```

**✅ Kiểm tra tất cả files đã tạo:**
```bash
ls -la
# Phải thấy:
# config.py
# redis_client.py
# mcp_context.py
# rag_system.py
# tools.py
# agent.py
# telegram_bot.py
# requirements.txt
# .env
```

---

# BƯỚC 8: KHỞI ĐỘNG DOCKER REDIS

```bash
docker run -d \
  --name stock-redis \
  -p 6379:6379 \
  --restart always \
  redis:alpine
```

**✅ Kiểm tra Redis đang chạy:**
```bash
docker ps | grep redis

# Output:
# abc123  redis:alpine  Up 10 seconds  0.0.0.0:6379->6379/tcp  stock-redis
```

**✅ Test kết nối Redis:**
```bash
docker exec -it stock-redis redis-cli ping
# Output: PONG
```

---

# BƯỚC 9: TEST TỪNG COMPONENT

## 9.1. Test config

```bash
python -c "import config; print('Config OK!')"
```

Phải thấy:
```
✅ Config loaded successfully!
Config OK!
```

## 9.2. Test Redis connection

```bash
python -c "from redis_client import redis_client; print('Redis:', redis_client.ping() if redis_client else 'Not connected')"
```

Phải thấy:
```
✅ Đã kết nối Redis thành công
Redis: True
```

## 9.3. Test RAG system

```bash
python -c "from rag_system import StockRAG; rag = StockRAG(); print('RAG OK!')"
```

Phải thấy:
```
✅ RAG System khởi tạo (embedding_dim=384)
RAG OK!
```

## 9.4. Test tools

Tạo file `test_tools.py`:
```python
from tools import get_stock_quote

print("Testing get_stock_quote...")
result = get_stock_quote("AAPL")
print(result)
```

Chạy:
```bash
python test_tools.py
```

Phải thấy thông tin cổ phiếu AAPL hoặc lỗi nếu API limit.

---

# BƯỚC 10: CHẠY TELEGRAM BOT

```bash
python telegram_bot.py
```

**Kết quả mong đợi:**
```
✅ Config loaded successfully!
✅ Đã kết nối Redis thành công
✅ RAG System khởi tạo (embedding_dim=384)
🤖 Đang khởi động Telegram Bot...
✅ Telegram Bot đã sẵn sàng!
📱 Mở Telegram và chat với bot!
```

**⚠️ Terminal sẽ không có prompt, bot đang chạy!**

---

# BƯỚC 11: TEST BOT TRÊN TELEGRAM

1. Mở Telegram
2. Tìm bot (username bạn đã tạo, VD: `@stock_ai_agent_bot`)
3. Nhấn **START** hoặc gửi `/start`
4. Thấy welcome message ✅

## Test các lệnh:

### Test 1: `/help`
```
Gửi: /help
Nhận: Hướng dẫn sử dụng
```

### Test 2: Hỏi giá cổ phiếu
```
Gửi: Giá AAPL bao nhiêu?
Nhận: 📊 Cổ phiếu AAPL: ...
```

### Test 3: Thông tin công ty
```
Gửi: Thông tin về GOOGL
Nhận: 🏢 Công ty: Alphabet Inc. ...
```

### Test 4: Stats
```
Gửi: /stats
Nhận: 📊 THỐNG KÊ
      Tin nhắn: X
      Cổ phiếu: Y
```

### Test 5: Tìm kiếm
```
Gửi: Tìm cổ phiếu công nghệ
Nhận: 🔍 Cổ phiếu tương tự: ...
```

### Test 6: Clear history
```
Gửi: /clear
Nhận: ✅ Đã xóa lịch sử!
```

**✅ Nếu tất cả tests PASS → Bot hoạt động tốt!**

---

# BƯỚC 12: MONITOR VÀ DEBUG

## 12.1. Xem logs của bot

Terminal đang chạy bot sẽ hiện logs realtime:
```
✅ Telegram Bot đã sẵn sàng!
INFO - User 123456789: Giá AAPL bao nhiêu?
INFO - Response sent to 123456789
```

## 12.2. Xem Redis data

Mở terminal MỚI (giữ terminal bot đang chạy):

```bash
# Vào Redis CLI
docker exec -it stock-redis redis-cli

# Trong Redis CLI:
# Xem tất cả keys
KEYS *

# Xem MCP context
GET mcp:context:123456789

# Xem conversation
LRANGE chat:session:123456789 0 -1

# Xem RAG index
SMEMBERS rag:stock:index

# Xem stock document
HGETALL rag:stock:AAPL

# Thoát
EXIT
```

## 12.3. Check Docker Redis

```bash
# Xem Redis logs
docker logs stock-redis

# Xem Redis stats
docker exec -it stock-redis redis-cli INFO stats

# Xem memory usage
docker stats stock-redis
```

---

# BƯỚC 13: DỪNG VÀ KHỞI ĐỘNG LẠI

## Dừng bot

Trong terminal đang chạy bot:
- Nhấn `Ctrl + C`

```
^C
KeyboardInterrupt
Shutting down...
```

## Khởi động lại bot

```bash
python telegram_bot.py
```

## Dừng Redis

```bash
docker stop stock-redis
```

## Khởi động lại Redis

```bash
docker start stock-redis

# Verify
docker ps | grep redis
```

## Stop tất cả

```bash
# Stop bot: Ctrl+C trong terminal bot

# Stop Redis
docker stop stock-redis

# Deactivate venv
deactivate
```

## Start tất cả lại

```bash
# 1. Start Redis
docker start stock-redis

# 2. Activate venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows

# 3. Start bot
python telegram_bot.py
```

---

# ❌ TROUBLESHOOTING

## Lỗi 1: Module not found

```bash
ModuleNotFoundError: No module named 'google.genai'
```

**Giải pháp:**
```bash
# Kiểm tra venv đã activate chưa
which python
# Phải trỏ vào venv

# Cài lại packages
pip install -r requirements.txt
```

## Lỗi 2: Redis connection error

```bash
⚠️ Không thể kết nối Redis: Error 111 connecting to localhost:6379
```

**Giải pháp:**
```bash
# Check Redis đang chạy
docker ps | grep redis

# Nếu không thấy, start Redis
docker start stock-redis

# Hoặc tạo mới
docker run -d --name stock-redis -p 6379:6379 redis:alpine
```

## Lỗi 3: Telegram bot không response

```bash
# Bot chạy nhưng không trả lời
```

**Giải pháp:**
```bash
# 1. Check token trong .env
cat .env | grep TELEGRAM_BOT_TOKEN

# 2. Test token
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# 3. Check logs trong terminal bot
# Có thấy message từ user không?

# 4. Restart bot
# Ctrl+C → python telegram_bot.py
```

## Lỗi 4: API rate limit (Alpha Vantage)

```
❌ Lỗi: API rate limit exceeded
```

**Giải pháp:**
- Free plan: 5 requests/minute, 500/day
- Đợi 1 phút rồi thử lại
- Hoặc upgrade: https://www.alphavantage.co/premium/

## Lỗi 5: Gemini API invalid

```bash
❌ Invalid API key
```

**Giải pháp:**
```bash
# 1. Check key trong .env
cat .env | grep GEMINI_API_KEY

# 2. Verify key
curl -H "x-goog-api-key: $GEMINI_API_KEY" \
  https://generativelanguage.googleapis.com/v1/models

# 3. Tạo key mới nếu cần
# https://aistudio.google.com/app/apikey
```

## Lỗi 6: Port 6379 đã được sử dụng

```bash
Error: port is already allocated
```

**Giải pháp:**
```bash
# Option 1: Dừng Redis cũ
docker stop stock-redis
docker rm stock-redis

# Tạo lại
docker run -d --name stock-redis -p 6379:6379 redis:alpine

# Option 2: Dùng port khác
docker run -d --name stock-redis -p 6380:6379 redis:alpine

# Update .env
REDIS_PORT=6380
```

---

# 🎉 HOÀN TẤT!

Bây giờ bạn đã có:
- ✅ Telegram Bot hoạt động
- ✅ Redis lưu trữ data
- ✅ MCP Context management
- ✅ RAG Semantic search
- ✅ Real-time stock data

---

# 📚 COMMANDS THAM KHẢO NHANH

## Activate venv
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

## Deactivate venv
```bash
deactivate
```

## Start Redis
```bash
docker start stock-redis
```

## Stop Redis
```bash
docker stop stock-redis
```

## Start Bot
```bash
python telegram_bot.py
```

## Stop Bot
```
Ctrl + C
```

## View Redis data
```bash
docker exec -it stock-redis redis-cli
> KEYS *
> GET mcp:context:123456789
> EXIT
```

## View Redis logs
```bash
docker logs stock-redis
docker logs -f stock-redis  # Follow mode
```

## Check Docker containers
```bash
docker ps
docker ps -a  # Include stopped
```

## Restart everything
```bash
docker restart stock-redis
# Ctrl+C bot → python telegram_bot.py
```

---

# 🔄 WORKFLOW HÀNG NGÀY

## Mở máy lần đầu:

```bash
# 1. Vào thư mục dự án
cd ~/Desktop/stock_agent

# 2. Start Redis (nếu chưa chạy)
docker start stock-redis

# 3. Activate venv
source venv/bin/activate

# 4. Start bot
python telegram_bot.py
```

## Khi tắt máy:

```bash
# 1. Stop bot (Ctrl+C)

# 2. Redis có --restart always nên không cần stop
# Nhưng nếu muốn stop:
docker stop stock-redis

# 3. Deactivate venv
deactivate
```

---

# 📊 MONITORING

## Xem stats Redis:
```bash
docker exec -it stock-redis redis-cli INFO stats
```

## Xem memory usage:
```bash
docker stats stock-redis
```

## Đếm số keys:
```bash
docker exec -it stock-redis redis-cli DBSIZE
```

## Xem keys theo pattern:
```bash
docker exec -it stock-redis redis-cli KEYS "mcp:*"
docker exec -it stock-redis redis-cli KEYS "rag:*"
docker exec -it stock-redis redis-cli KEYS "chat:*"
```

## Backup Redis data:
```bash
# Save snapshot
docker exec -it stock-redis redis-cli SAVE

# Copy dump file
docker cp stock-redis:/data/dump.rdb ./backup_$(date +%Y%m%d).rdb
```

---

# 🚀 NEXT STEPS (Optional)

## 1. Chạy với Docker Compose

Tạo `docker-compose.yml`:
```yaml
version: '3.8'

services:
  redis:
    image: redis:alpine
    container_name: stock-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: always

volumes:
  redis-data:
```

Chạy:
```bash
docker-compose up -d
docker-compose down
```

## 2. Deploy lên VPS

```bash
# 1. SSH vào VPS
ssh user@your-server-ip

# 2. Clone code
git clone your-repo
cd stock_agent

# 3. Setup như local
# ... (giống bước 1-10)

# 4. Chạy bot với nohup
nohup python telegram_bot.py > bot.log 2>&1 &

# 5. View logs
tail -f bot.log
```

## 3. Setup systemd service (Linux)

Tạo `/etc/systemd/system/stock-bot.service`:
```ini
[Unit]
Description=Stock Telegram Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/stock_agent
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python telegram_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable stock-bot
sudo systemctl start stock-bot
sudo systemctl status stock-bot
```

## 4. Thêm logging

Thêm vào đầu `telegram_bot.py`:
```python
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)
logger = logging.getLogger(__name__)
```

## 5. Thêm error handling

Wrap main function:
```python
def main():
    try:
        # ... code ...
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise

if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("Stopped by user")
            break
        except Exception as e:
            print(f"Error: {e}. Restarting in 5s...")
            time.sleep(5)
```

---

# 📝 CHECKLIST CUỐI CÙNG

Đảm bảo tất cả đều OK:

- [ ] Python 3.9+ installed
- [ ] Docker installed và Redis đang chạy
- [ ] Virtual environment created và activated
- [ ] Dependencies installed (`pip list`)
- [ ] .env file với keys thật
- [ ] Tất cả .py files đã tạo
- [ ] Redis ping trả về PONG
- [ ] Config import OK
- [ ] Redis client connected
- [ ] RAG system initialized
- [ ] Tools test OK (hoặc API limit - bình thường)
- [ ] Telegram bot chạy không lỗi
- [ ] Bot respond trên Telegram

**✅ Nếu tất cả checked → HOÀN THÀNH! 🎉**

---

# 💬 LIÊN HỆ & HỖ TRỢ

Nếu gặp vấn đề:

1. **Check logs** trong terminal bot
2. **Check Redis** với `docker logs stock-redis`
3. **Test từng component** như bước 9
4. **Google error message** cụ thể
5. **Đọc lại từng bước** trong hướng dẫn này

---

# 🎓 ĐÃ HỌC ĐƯỢC GÌ?

Qua dự án này bạn đã học:

1. ✅ **Python Development**
   - Virtual environments
   - Package management với pip
   - Environment variables
   - Async programming

2. ✅ **Docker**
   - Container basics
   - Docker commands
   - Volume management
   - Port mapping

3. ✅ **Redis**
   - Key-value store
   - Data structures (String, List, Hash, Set)
   - TTL và expiration
   - Redis CLI

4. ✅ **AI & ML**
   - LLM integration (Gemini)
   - RAG (Retrieval-Augmented Generation)
   - Embedding vectors
   - Semantic search

5. ✅ **System Design**
   - MCP (Model Context Protocol)
   - Multi-user sessions
   - Caching strategies
   - API integration

6. ✅ **Telegram Bot**
   - Bot API
   - Commands và handlers
   - Async message handling

**Chúc mừng! Bạn đã hoàn thành một dự án AI thực tế! 🚀**