# """RAG (Retrieval-Augmented Generation) System"""
# import json
# import numpy as np
# from typing import List, Dict
# from datetime import datetime
# from redis_client import redis_client
# from config import EMBEDDING_DIM, TOP_K_RESULTS

# class StockRAG:
#     """RAG System cho Stock Agent"""
    
#     def __init__(self):
#         self.embedding_dim = EMBEDDING_DIM
    
#     def _generate_embedding(self, text: str) -> List[float]:
#         """Tạo embedding đơn giản"""
#         hash_val = hash(text.lower())
#         np.random.seed(hash_val % (2**31))
#         return np.random.randn(self.embedding_dim).tolist()
    
#     def store_stock_data(self, symbol: str, data: Dict):
#         """Lưu dữ liệu cổ phiếu vào vector store"""
#         if not redis_client:
#             return
        
#         doc_text = f"{symbol} {data.get('name', '')} {data.get('sector', '')} {data.get('industry', '')}"
#         embedding = self._generate_embedding(doc_text)
        
#         doc_key = f"rag:stock:{symbol}"
#         redis_client.hset(doc_key, mapping={
#             "symbol": symbol,
#             "data": json.dumps(data),
#             "embedding": json.dumps(embedding),
#             "text": doc_text,
#             "timestamp": datetime.now().isoformat()
#         })
#         redis_client.expire(doc_key, 24*60*60)
#         redis_client.sadd("rag:stock:index", symbol)
    
#     def semantic_search(self, query: str, top_k: int = TOP_K_RESULTS) -> List[Dict]:
#         """Tìm kiếm semantic trong vector store"""
#         if not redis_client:
#             return []
        
#         query_embedding = self._generate_embedding(query)
#         stock_symbols = redis_client.smembers("rag:stock:index")
        
#         results = []
#         for symbol in stock_symbols:
#             doc_key = f"rag:stock:{symbol}"
#             doc_data = redis_client.hgetall(doc_key)
            
#             if doc_data and "embedding" in doc_data:
#                 doc_embedding = json.loads(doc_data["embedding"])
#                 similarity = self._cosine_similarity(query_embedding, doc_embedding)
                
#                 results.append({
#                     "symbol": doc_data["symbol"],
#                     "data": json.loads(doc_data["data"]),
#                     "similarity": similarity,
#                     "text": doc_data["text"]
#                 })
        
#         results.sort(key=lambda x: x["similarity"], reverse=True)
#         return results[:top_k]
    
#     def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
#         """Tính cosine similarity"""
#         vec1 = np.array(vec1)
#         vec2 = np.array(vec2)
#         return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
    
#     def get_relevant_context(self, query: str) -> str:
#         """Lấy context liên quan cho RAG"""
#         results = self.semantic_search(query, top_k=3)
        
#         if not results:
#             return "Không tìm thấy thông tin liên quan trong knowledge base."
        
#         context_parts = ["Thông tin liên quan từ knowledge base:"]
#         for i, result in enumerate(results, 1):
#             data = result["data"]
#             context_parts.append(
#                 f"\n{i}. {result['symbol']}: {data.get('name', 'N/A')} "
#                 f"(Similarity: {result['similarity']:.2f})"
#             )
        
#         return "\n".join(context_parts)


# ___________________________________________________________________________________________________________--


import json
import hashlib
import numpy as np
from typing import List, Dict
from datetime import datetime
from redis_client import redis_client
from config import EMBEDDING_DIM, TOP_K_RESULTS


class StockRAG:
    def __init__(self):
        self.embedding_dim = EMBEDDING_DIM

    def _generate_embedding(self, text: str) -> List[float]:
        """Tạo embedding giả lập nhưng ổn định: dùng sha256 để tạo seed reproducible.

        FIX: tránh dùng built-in hash() vì Python randomizes hash across processes.
        """
        if not text:
            # trả về vector 0 nếu text rỗng
            return [0.0] * self.embedding_dim

        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        seed = int(digest, 16) % (2 ** 31)
        rng = np.random.RandomState(seed)
        return rng.randn(self.embedding_dim).tolist()

    def store_stock_data(self, symbol: str, data: Dict):
        if not redis_client:
            return

        doc_text = f"{symbol} {data.get('name', '')} {data.get('sector', '')} {data.get('industry', '')}"
        embedding = self._generate_embedding(doc_text)

        doc_key = f"rag:stock:{symbol}"
        redis_client.hset(doc_key, mapping={
            "symbol": symbol,
            "data": json.dumps(data),
            "embedding": json.dumps(embedding),
            "text": doc_text,
            "timestamp": datetime.now().isoformat(),
        })
        redis_client.expire(doc_key, 24 * 60 * 60)
        redis_client.sadd("rag:stock:index", symbol)

    def semantic_search(self, query: str, top_k: int = TOP_K_RESULTS) -> List[Dict]:
        if not redis_client:
            return []

        query_embedding = self._generate_embedding(query)
        stock_symbols = redis_client.smembers("rag:stock:index") or []

        results = []
        for symbol in stock_symbols:
            doc_key = f"rag:stock:{symbol}"
            doc_data = redis_client.hgetall(doc_key)

            if doc_data and "embedding" in doc_data:
                doc_embedding = json.loads(doc_data["embedding"])
                similarity = self._cosine_similarity(query_embedding, doc_embedding)

                results.append({
                    "symbol": doc_data.get("symbol", symbol),
                    "data": json.loads(doc_data.get("data", "{}")),
                    "similarity": similarity,
                    "text": doc_data.get("text", ""),
                })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        v1 = np.array(vec1, dtype=float)
        v2 = np.array(vec2, dtype=float)
        denom = (np.linalg.norm(v1) * np.linalg.norm(v2))
        if denom == 0:
            return 0.0
        return float(np.dot(v1, v2) / denom)

    def get_relevant_context(self, query: str) -> str:
        results = self.semantic_search(query, top_k=3)

        if not results:
            return "Không tìm thấy thông tin liên quan trong knowledge base."

        context_parts = ["Thông tin liên quan từ knowledge base:"]
        for i, result in enumerate(results, 1):
            data = result["data"]
            context_parts.append(
                f"\n{i}. {result['symbol']}: {data.get('name', 'N/A')} (Similarity: {result['similarity']:.2f})"
            )

        return "\n".join(context_parts)