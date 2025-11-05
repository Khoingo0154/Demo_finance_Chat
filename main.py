"""Main entry point - Chọn chạy Telegram hoặc ADK Web"""
import sys
from config import TELEGRAM_BOT_TOKEN

def main():
    """Main entry point"""
    print("""
Chọn chế độ chạy:
1. Telegram Bot
2. ADK Web Interface
3. Both (Telegram + Web)

""")
    
    choice = input("Nhập lựa chọn (1/2/3): ").strip()
    
    if choice == "1":
        print("\n🚀 Khởi động Telegram Bot...\n")
        from telegram_bot import main as telegram_main
        telegram_main()
    
    elif choice == "2":
        print("\n🚀 Khởi động ADK Web Interface...\n")
        print("Chạy lệnh: adk web")
        print("Hoặc import agent từ agent.py trong code")
    
    elif choice == "3":
        print("\n🚀 Khởi động cả Telegram và Web...\n")
        import asyncio
        import threading
        from telegram_bot import main as telegram_main
        
        # Chạy Telegram bot trong thread riêng
        telegram_thread = threading.Thread(target=telegram_main, daemon=True)
        telegram_thread.start()
        
        print("\n✅ Telegram Bot đang chạy trong background")
        print("📝 Bây giờ bạn có thể chạy: adk web")
        print("\nNhấn Ctrl+C để dừng...")
        
        try:
            telegram_thread.join()
        except KeyboardInterrupt:
            print("\n👋 Đang dừng...")
    
    else:
        print("❌ Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()




