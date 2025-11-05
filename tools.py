# import requests
# from config import ALPHA_VANTAGE_API_KEY
# from rag_system import StockRAG

# rag_system = StockRAG()

# def get_stock_quote(symbol: str) -> str:
#     """[MCP Tool] Lấy thông tin giá cổ phiếu từ Alpha Vantage API"""
#     try:
#         url = "https://www.alphavantage.co/query"
#         params = {
#             "function": "GLOBAL_QUOTE",
#             "symbol": symbol.upper(),
#             "apikey": ALPHA_VANTAGE_API_KEY
#         }
        
#         response = requests.get(url, params=params)
#         data = response.json()
        
#         if "Global Quote" in data and data["Global Quote"]:
#             quote = data["Global Quote"]
            
#             stock_data = {
#                 "symbol": quote.get('01. symbol', symbol),
#                 "price": quote.get('05. price', 'N/A'),
#                 "change": quote.get('09. change', 'N/A'),
#                 "change_percent": quote.get('10. change percent', 'N/A'),
#                 "volume": quote.get('06. volume', 'N/A'),
#                 "trading_day": quote.get('07. latest trading day', 'N/A')
#             }
            
#             rag_system.store_stock_data(symbol.upper(), stock_data)
            
#             result = f"""📊 Cổ phiếu {symbol.upper()}:
# 💰 Giá: ${stock_data['price']}
# 📈 Thay đổi: {stock_data['change']} ({stock_data['change_percent']})
# 📊 Khối lượng: {stock_data['volume']}
# 📅 Ngày: {stock_data['trading_day']}"""
            
#             return result
#         else:
#             return f"❌ Không tìm thấy thông tin cho mã {symbol}."
    
#     except Exception as e:
#         return f"❌ Lỗi: {str(e)}"


# def get_company_info(symbol: str) -> str:
#     """[MCP Tool] Lấy thông tin công ty"""
#     try:
#         url = "https://www.alphavantage.co/query"
#         params = {
#             "function": "OVERVIEW",
#             "symbol": symbol.upper(),
#             "apikey": ALPHA_VANTAGE_API_KEY
#         }
        
#         response = requests.get(url, params=params)
#         data = response.json()
        
#         if "Name" in data:
#             company_data = {
#                 "name": data.get('Name', 'N/A'),
#                 "symbol": data.get('Symbol', symbol),
#                 "sector": data.get('Sector', 'N/A'),
#                 "industry": data.get('Industry', 'N/A'),
#                 "market_cap": data.get('MarketCapitalization', 'N/A')
#             }
            
#             rag_system.store_stock_data(symbol.upper(), company_data)
            
#             result = f"""🏢 Công ty:
# 📌 Tên: {company_data['name']}
# 🔖 Mã: {company_data['symbol']}
# 🏭 Ngành: {company_data['sector']}
# 💼 Lĩnh vực: {company_data['industry']}
# 💎 Vốn hóa: ${company_data['market_cap']}"""
#             return result
#         else:
#             return f"❌ Không tìm thấy thông tin công ty {symbol}"
    
#     except Exception as e:
#         return f"❌ Lỗi: {str(e)}"


# def search_similar_stocks(query: str) -> str:
#     """[MCP Tool] Tìm kiếm cổ phiếu tương tự dùng RAG"""
#     results = rag_system.semantic_search(query, top_k=5)
    
#     if not results:
#         return "❌ Không tìm thấy cổ phiếu phù hợp trong knowledge base."
    
#     response = ["🔍 Cổ phiếu tương tự:"]
#     for i, result in enumerate(results, 1):
#         data = result["data"]
#         response.append(
#             f"\n{i}. {result['symbol']} - {data.get('name', 'N/A')} "
#             f"({result['similarity']:.0%})"
#         )
    
#     return "\n".join(response)

#________________________________________________________________________________________________________________________

import requests
import json
from config import ALPHA_VANTAGE_API_KEY, STOCK_DATA_TTL
from rag_system import StockRAG
from redis_client import redis_client
import time
from functools import wraps
rag_system = StockRAG()


def _cache_get(key: str):
    try:
        if redis_client:
            return redis_client.get(key)
    except Exception:
        pass
    return None


def _cache_set(key: str, value: str, ttl: int):
    try:
        if redis_client:
            redis_client.set(key, value, ex=ttl)
    except Exception:
        pass

def retry_on_rate_limit(max_retries=3, delay=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                result = func(*args, **kwargs)
                if "rate limit" not in result.lower():
                    return result
                if attempt < max_retries - 1:
                    time.sleep(delay)
            return result
        return wrapper
    return decorator

@retry_on_rate_limit()

def get_stock_quote(symbol: str) -> str:
    """Lấy thông tin giá cổ phiếu từ Alpha Vantage API (với timeout và cache)

    FIX: thêm timeout và caching để tránh bị rate-limit và chậm
    """
    key = f"stock:quote:{symbol.upper()}"
    cached = _cache_get(key)
    if cached:
        try:
            data = json.loads(cached)
            # trả dạng text như cũ
            return cached
        except Exception:
            pass

    try:
        url = "https://www.alphavantage.co/query"
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol.upper(), "apikey": ALPHA_VANTAGE_API_KEY}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            stock_data = {
                "symbol": quote.get("01. symbol", symbol),
                "price": quote.get("05. price", "N/A"),
                "change": quote.get("09. change", "N/A"),
                "change_percent": quote.get("10. change percent", "N/A"),
                "volume": quote.get("06. volume", "N/A"),
                "trading_day": quote.get("07. latest trading day", "N/A"),
            }

            rag_system.store_stock_data(symbol.upper(), stock_data)

            result = (
                f"📊 Cổ phiếu {symbol.upper()}:\n"
                f"💰 Giá: ${stock_data['price']}\n"
                f"📈 Thay đổi: {stock_data['change']} ({stock_data['change_percent']})\n"
                f"📊 Khối lượng: {stock_data['volume']}\n"
                f"📅 Ngày: {stock_data['trading_day']}"
            )

            # cache raw json string để tái sử dụng
            _cache_set(key, json.dumps(stock_data), STOCK_DATA_TTL)
            return result
        else:
            return f"❌ Không tìm thấy thông tin cho mã {symbol}."
    except Exception as e:
        return f"❌ Lỗi khi gọi Alpha Vantage: {e}"


def get_company_info(symbol: str) -> str:
    key = f"stock:company:{symbol.upper()}"
    cached = _cache_get(key)
    if cached:
        return cached

    try:
        url = "https://www.alphavantage.co/query"
        params = {"function": "OVERVIEW", "symbol": symbol.upper(), "apikey": ALPHA_VANTAGE_API_KEY}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "Name" in data:
            company_data = {
                "name": data.get("Name", "N/A"),
                "symbol": data.get("Symbol", symbol),
                "sector": data.get("Sector", "N/A"),
                "industry": data.get("Industry", "N/A"),
                "market_cap": data.get("MarketCapitalization", "N/A"),
            }
            rag_system.store_stock_data(symbol.upper(), company_data)

            result = (
                f"🏢 Công ty:\n"
                f"📌 Tên: {company_data['name']}\n"
                f"🔖 Mã: {company_data['symbol']}\n"
                f"🏭 Ngành: {company_data['sector']}\n"
                f"💼 Lĩnh vực: {company_data['industry']}\n"
                f"💎 Vốn hóa: ${company_data['market_cap']}"
            )

            _cache_set(key, result, STOCK_DATA_TTL)
            return result
        else:
            return f"❌ Không tìm thấy thông tin công ty {symbol}"
    except Exception as e:
        return f"❌ Lỗi: {e}"


def search_similar_stocks(query: str) -> str:
    results = rag_system.semantic_search(query, top_k=5)

    if not results:
        return "❌ Không tìm thấy cổ phiếu phù hợp trong knowledge base."

    response = ["🔍 Cổ phiếu tương tự:"]
    for i, result in enumerate(results, 1):
        data = result["data"]
        response.append(f"\n{i}. {result['symbol']} - {data.get('name', 'N/A')} ({result['similarity']:.2f})")

    return "\n".join(response)