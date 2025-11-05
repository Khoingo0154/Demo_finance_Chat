import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN
from agent_simple import StockAgentMCP

stock_agent = StockAgentMCP()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Xin chào! Tôi là Stock AI Agent. Hỏi tôi về cổ phiếu!")

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
    print("🤖 Đang khởi động Telegram Bot...")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot đã sẵn sàng!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()