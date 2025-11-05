# """Cấu hình cho Stock Agent"""
# import os
# from dotenv import load_dotenv
# load_dotenv()
# # API Keys
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
# ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "your-alpha-vantage-key")
# TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your-telegram-bot-token")

# # Redis Configuration
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
# REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# # RAG Configuration
# EMBEDDING_DIM = 384
# TOP_K_RESULTS = 5

# # Cache TTL (seconds)
# STOCK_DATA_TTL = 3600  # 1 hour
# CONVERSATION_TTL = 7 * 24 * 60 * 60  # 7 days
# CONTEXT_TTL = 7 * 24 * 60 * 60  # 7 days


# print(GEMINI_API_KEY,"||" , ALPHA_VANTAGE_API_KEY,"||", TELEGRAM_BOT_TOKEN)



#_________________________________________________________________________________________________________________________
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "your-alpha-vantage-key")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your-telegram-bot-token")

# Debug flag
DEBUG = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# RAG Configuration
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

# Cache TTL (seconds)
STOCK_DATA_TTL = int(os.getenv("STOCK_DATA_TTL", "3600"))  # 1 hour
CONVERSATION_TTL = int(os.getenv("CONVERSATION_TTL", str(7 * 24 * 60 * 60)))  # 7 days
CONTEXT_TTL = int(os.getenv("CONTEXT_TTL", str(7 * 24 * 60 * 60)))  # 7 days

# NOTE: Avoid printing secrets here. If DEBUG, you can print a masked summary.
if DEBUG:
    print("DEBUG mode on. TELEGRAM_BOT_TOKEN set?", TELEGRAM_BOT_TOKEN != "your-telegram-bot-token")


# # Hướng dẫn ngắn
# - Thay thế các file tương ứng trong dự án với nội dung trên.
# - Cài dependencies: `pip install -r requirements.txt` (bổ sung `python-dotenv`, `google-adk` nếu cần).
# - Thiết lập `.env` với `TELEGRAM_BOT_TOKEN`, `ALPHA_VANTAGE_API_KEY`, v.v.
# - Chạy `python main.py` hoặc `python telegram_bot.py` để test Telegram bot.

# Nếu bạn muốn, mình có thể tiếp tục:
# - Viết unit tests cho các module
# - Tạo mock LLM để test end-to-end
# - Hướng dẫn deploy (Docker + systemd)

# Trong config.py
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

