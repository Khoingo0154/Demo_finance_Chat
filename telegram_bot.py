# """Telegram Bot integration cho Stock Agent"""
# import asyncio
# from telegram import Update
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# from config import TELEGRAM_BOT_TOKEN, GEMINI_API_KEY
# from agent import StockAgentMCP
# from config import TELEGRAM_BOT_TOKEN
# from agent_simple import StockAgentMCP

# from tools import get_stock_quote, get_company_info, search_similar_stocks
# print(TELEGRAM_BOT_TOKEN)
# stock_agent = StockAgentMCP()

# # Khởi tạo Stock Agent với MCP + RAG
# stock_agent = StockAgentMCP(
#     model_name="gemini-2.0-flash",
#     tools_list=[get_stock_quote, get_company_info, search_similar_stocks]
# )


# async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handler cho /start command"""
#     welcome_message = """
# 👋 Xin chào! Tôi là Stock AI Agent
#     await update.message.reply_text("👋 Xin chào! Tôi là Stock AI Agent. Hỏi tôi về cổ phiếu!")

# 🤖 Tôi có thể giúp bạn:
# • 📊 Tra cứu giá cổ phiếu real-time
# • 🏢 Thông tin chi tiết về công ty
# • 🔍 Tìm cổ phiếu tương tự
# • 💬 Trò chuyện về thị trường chứng khoán

# 💡 Ví dụ:
# - "Giá AAPL bao nhiêu?"
# - "Thông tin về công ty GOOGL"
# - "Tìm cổ phiếu công nghệ tương tự"

# 📝 Commands:
# /start - Bắt đầu
# /help - Hướng dẫn
# /stats - Thống kê session
# /clear - Xóa lịch sử

# Hãy hỏi tôi bất cứ điều gì về cổ phiếu! 🚀
# """
#     await update.message.reply_text(welcome_message)


# async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handler cho /help command"""
#     help_text = """
# 📚 HƯỚNG DẪN SỬ DỤNG

# 🔹 Tra cứu giá cổ phiếu:
#    "Giá AAPL"
#    "Cho tôi biết giá MSFT"
   
# 🔹 Thông tin công ty:
#    "Thông tin về GOOGL"
#    "Công ty TSLA là gì?"
   
# 🔹 Tìm kiếm cổ phiếu:
#    "Tìm cổ phiếu công nghệ"
#    "Cổ phiếu tương tự AAPL"

# 🔹 So sánh:
#    "So sánh AAPL và MSFT"
   
# ⚡ Bot sử dụng:
# • MCP - Nhớ context cuộc trò chuyện
# • RAG - Tìm kiếm thông minh
# • Real-time data từ Alpha Vantage
# """
#     await update.message.reply_text(help_text)


# async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handler cho /stats command"""
#     user_id = str(update.effective_user.id)
#     session = stock_agent.get_session(user_id)
    
#     stats_text = f"""
# 📊 THỐNG KÊ SESSION

# 👤 User ID: {user_id}
# ⏰ Session bắt đầu: {session['created_at']}
# 💬 Số tin nhắn: {len(session['mcp_context'].context['conversation_history'])}
# 📈 Cổ phiếu đã xem: {len(session['mcp_context'].context['active_stocks'])}

# {session['mcp_context'].get_context_summary()}
# """
#     await update.message.reply_text(stats_text)


# async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handler cho /clear command - Xóa lịch sử"""
#     user_id = str(update.effective_user.id)
#     if user_id in stock_agent.sessions:
#         del stock_agent.sessions[user_id]
#     await update.message.reply_text("✅ Đã xóa lịch sử chat và context!")


# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handler cho tin nhắn text"""
#     user_id = str(update.effective_user.id)
#     user_message = update.message.text
    
#     # Gửi typing action
#     await update.message.chat.send_action(action="typing")
    
#     try:
#         # Query agent với session_id là user_id
#         response = stock_agent.query(user_message, session_id=user_id)
        
#         # Gửi response về Telegram
#         await update.message.reply_text(response)
        
#     except Exception as e:
#         error_message = f"❌ Xin lỗi, có lỗi xảy ra:\n{str(e)}"
#         await update.message.reply_text(error_message)
#         await update.message.reply_text(f"❌ Lỗi: {str(e)}")


# async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handler cho errors"""
#     print(f"Update {update} caused error {context.error}")


# def main():
#     """Main function để chạy Telegram bot"""
    
#     # Kiểm tra config
#     if TELEGRAM_BOT_TOKEN == "your-telegram-bot-token":
#         print("❌ Vui lòng cấu hình TELEGRAM_BOT_TOKEN trong .env")
#         return
    
#     print("🤖 Đang khởi động Telegram Bot...")
    
#     # Tạo Application
#     application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
#     # Thêm handlers
#     application.add_handler(CommandHandler("start", start_command))
#     application.add_handler(CommandHandler("help", help_command))
#     application.add_handler(CommandHandler("stats", stats_command))
#     application.add_handler(CommandHandler("clear", clear_command))
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
#     application.add_error_handler(error_handler)
    
#     # Chạy bot
#     print("✅ Telegram Bot đã sẵn sàng!")
#     print("📱 Hãy mở Telegram và chat với bot của bạn!")
#     print("✅ Bot đã sẵn sàng!")
#     application.run_polling(allowed_updates=Update.ALL_TYPES)


# if __name__ == "__main__":
#     main()


#________________________________________________________________________________________________________________________

import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.code_executors import BuiltInCodeExecutor
from google.genai import types
# Đảm bảo import GEMINI_MODEL và TOKEN từ config
from config import TELEGRAM_BOT_TOKEN, GEMINI_MODEL
from agent import StockAgentMCP

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# --- KHỐI KHỞI TẠO AGENT ĐÃ SỬA LỖI ---
# Chỉ khởi tạo MỘT LẦN và xử lý lỗi import

base_agent = None

try:
    # 1. Thử import LlmAgent thật
    from google.adk.agents import LlmAgent  # type: ignore
    
    # 2. Khởi tạo base_agent thật
    logger.info(f"Đang khởi tạo LlmAgent thật với model: {GEMINI_MODEL}")
    base_agent = LlmAgent(name="stock_llm_agent", model=GEMINI_MODEL)

except ImportError:
    logger.warning("Không thể import 'google.adk.agents'. Vui lòng cài đặt: pip install google-adk")
except Exception as e:
    logger.warning(f"Không thể import google.adk.agents: {e}. Sử dụng Mock LlmAgent.")

# Nếu import/khởi tạo thật thất bại, base_agent vẫn là None
if base_agent is None:
    # 3. Định nghĩa Mock LlmAgent
    class LlmAgent:
        def __init__(self, name: str, model: str = "mock-model"):
            self.model = model
            self.name = name
            logger.info(f"Đã khởi tạo Mock LlmAgent (model={self.model})")

        # Định nghĩa __call__ để tương thích với Strategy 2 trong agent.py
        def __call__(self, prompt: str) -> str:
            response = f"🤖 (MOCK RESPONSE for model={self.model})\n---\n{prompt}"
            logger.info(f"Mock LlmAgent: Đang trả về response cho prompt: {prompt[:30]}...")
            return response
            
    # 4. Khởi tạo base_agent giả
    base_agent = LlmAgent(name="stock_llm_agent_mock", model="gemini-mock")

# 5. Khởi tạo StockAgentMCP chỉ MỘT LẦN với base_agent (thật hoặc giả)
stock_agent = StockAgentMCP(base_agent=base_agent, )
logger.info(f"StockAgentMCP đã được khởi tạo với agent type: {type(base_agent)}")
# --- KẾT THÚC KHỐI SỬA LỖI ---


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler cho /start command"""
    welcome_message = (
        "👋 Xin chào! Tôi là Stock AI Agent. Hỏi tôi về cổ phiếu!\n\n"
        "🤖 Tôi có thể giúp bạn:\n"
        "• 📊 Tra cứu giá cổ phiếu real-time\n"
        "• 🏢 Thông tin chi tiết về công ty\n"
        "• 🔍 Tìm cổ phiếu tương tự\n\n"
        "Gợi ý: 'Giá AAPL', 'Thông tin GOOGL', 'Tìm cổ phiếu công nghệ'\n"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler cho /help command"""
    help_text = (
        "📚 HƯỚNG DẪN SỬ DỤNG\n\n"
        "- Tra cứu giá: 'Giá AAPL'\n"
        "- Thông tin công ty: 'Thông tin AAPL'\n"
        "- Xóa lịch sử: /clear\n"
        "- Xem thống kê: /stats"
    )
    await update.message.reply_text(help_text)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler cho /stats command"""
    user_id = str(update.effective_user.id)
    session = stock_agent.get_session(user_id)

    stats_text = (
        f"📊 THỐNG KÊ SESSION\n\n"
        f"👤 User ID: {user_id}\n"
        f"⏰ Session bắt đầu: {session['created_at']}\n"
        f"💬 Số tin nhắn: {len(session['mcp_context'].context['conversation_history'])}\n"
    )
    await update.message.reply_text(stats_text)


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler cho /clear command - Xóa lịch sử"""
    user_id = str(update.effective_user.id)
    if user_id in stock_agent.sessions:
        # Xóa context trong bộ nhớ của agent
        del stock_agent.sessions[user_id]
        # (Lưu ý: context trong Redis sẽ tự hết hạn hoặc bị ghi đè)
    await update.message.reply_text("✅ Đã xóa lịch sử chat và context trong bộ nhớ!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler cho tin nhắn text - chạy query trong executor"""
    if not update.message or not update.message.text:
        return
        
    user_id = str(update.effective_user.id)
    user_message = update.message.text

    # Gửi typing action
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    except Exception as e:
        logger.warning(f"Không thể gửi typing action: {e}")

    loop = asyncio.get_event_loop()

    try:
        # Chạy hàm .query (có chứa I/O) trong một thread riêng
        # để không block event loop chính của Telegram
        response = await loop.run_in_executor(
            None,  # Sử dụng ThreadPoolExecutor mặc định
            stock_agent.query,  # Hàm cần chạy
            user_message,       # Tham số 1 cho
            user_id             # Tham số 2 cho
        )
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.exception("Lỗi nghiêm trọng khi xử lý message")
        await update.message.reply_text(f"❌ Xin lỗi, có lỗi xảy ra khi xử lý: {e}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler cho errors"""
    logger.error("Update %s gây lỗi %s", update, context.error)


def main():
    """Main function để chạy Telegram bot"""
    
    # Kiểm tra config
    if TELEGRAM_BOT_TOKEN == "your-telegram-bot-token" or not TELEGRAM_BOT_TOKEN:
        logger.error("❌ Vui lòng cấu hình TELEGRAM_BOT_TOKEN trong .env")
        return
    
    logger.info("🤖 Đang khởi động Telegram Bot...")
    
    # Tạo Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Thêm handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Chạy bot
    logger.info("✅ Telegram Bot đã sẵn sàng!")
    logger.info("📱 Hãy mở Telegram và chat với bot của bạn!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()