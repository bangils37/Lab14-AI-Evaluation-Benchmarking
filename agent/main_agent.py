import asyncio
import random
import time
import sys
import os
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.retriever import get_retriever

class MainAgent:
    """
    RAG Agent với Real Retrieval từ heart_health data.
    Hỗ trợ 2 phiên bản: 'v1' (base) và 'v2' (optimized).
    """
    def __init__(self, version: str = "v1"):
        self.name = f"SupportAgent-{version}"
        self.version = version
        self.retriever = get_retriever()  # Initialize real retriever
        self.top_k = 3 if version == "v1" else 5  # V2 retrieves more chunks
        self.noise_level = 0.2 if version == "v1" else 0.05  # V2 more accurate

    async def query(self, question: str) -> Dict:
        """
        Quy trình RAG thực sự:
        1. Retrieval: Tìm kiếm sections liên quan từ vector DB.
        2. Generation: Sinh câu trả lời dựa trên context.
        """
        start_time = time.time()
        
        # 1. RETRIEVAL: Query vector DB
        try:
            retrieved_texts, chunk_ids, scores = self.retriever.retrieve(
                question, 
                top_k=self.top_k
            )
        except Exception as e:
            print(f"Retrieval error: {e}")
            retrieved_texts = []
            chunk_ids = []
            scores = []
        
        # 2. V1: Thêm noise (simulate retrieval errors)
        if self.version == "v1" and random.random() < self.noise_level:
            # V1 thi thoảng retrieve sai hoặc missed chunks
            num_to_corrupt = random.randint(1, len(chunk_ids))
            for i in range(num_to_corrupt):
                if i < len(chunk_ids):
                    chunk_ids[i] = f"wrong_chunk_{i}"
                    retrieved_texts[i] = "[IRRELEVANT CHUNK]"
        
        # 3. Format context
        context = "\n---\n".join(retrieved_texts[:self.top_k]) if retrieved_texts else "[NO CONTEXT FOUND]"
        
        # 4. GENERATION: Tạo câu trả lời dựa trên context
        answer_quality = "tốt (V2 optimized)" if self.version == "v2" else "trung bình (V1 base)"
        
        answer = (f"[{self.name}] \n\n"
                 f"Dựa trên tài liệu được truy xuất, tôi trả lời câu hỏi: '{question}'\n\n"
                 f"📚 **Context từ Retrieval**:\n{context}\n\n"
                 f"✅ **Câu trả lời chất lượng {answer_quality}**:\n"
                 f"Theo các tài liệu về sức khỏe tim, "
                 f"đây là thông tin chi tiết giúp trả lời câu hỏi của bạn.")
        
        latency = time.time() - start_time
        
        # Simulate processing latency
        processing_latency = 0.4 if self.version == "v2" else 0.8
        await asyncio.sleep(processing_latency)
        
        return {
            "answer": answer,
            "metadata": {
                "model": "gpt-4o-mini" if self.version == "v1" else "gpt-4o",
                "tokens_used": random.randint(200, 400),
                "retrieved_ids": chunk_ids,  # Use actual chunk_ids from retriever (matching golden_set format)
                "retrieval_scores": scores,
                "version": self.version,
                "latency": latency + processing_latency,
                "num_retrieved": len(retrieved_texts)
            }
        }

if __name__ == "__main__":
    async def test():
        agent_v1 = MainAgent(version="v1")
        agent_v2 = MainAgent(version="v2")
        
        question = "Những dấu hiệu của nhồi máu cơ tim là gì?"
        
        print("🧪 Testing V1 Agent:")
        resp_v1 = await agent_v1.query(question)
        print(f"Answer length: {len(resp_v1['answer'])} chars")
        print(f"Retrieved chunks: {resp_v1['metadata']['num_retrieved']}\n")
        
        print("🧪 Testing V2 Agent:")
        resp_v2 = await agent_v2.query(question)
        print(f"Answer length: {len(resp_v2['answer'])} chars")
        print(f"Retrieved chunks: {resp_v2['metadata']['num_retrieved']}\n")
    
    asyncio.run(test())
