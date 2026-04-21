import asyncio
import random
from typing import List, Dict

class MainAgent:
    """
    RAG Agent mô phỏng để benchmark.
    Hỗ trợ 2 phiên bản: 'v1' (base) và 'v2' (optimized).
    """
    def __init__(self, version: str = "v1"):
        self.name = f"SupportAgent-{version}"
        self.version = version

    async def query(self, question: str) -> Dict:
        """
        Mô phỏng quy trình RAG:
        1. Retrieval: Tìm kiếm context.
        2. Generation: Sinh câu trả lời.
        """
        # Giả lập độ trễ
        latency = 0.4 if self.version == "v2" else 0.8
        await asyncio.sleep(latency) 
        
        # Giả lập Retrieval logic
        # Trong thực tế, đây sẽ là gọi Vector DB
        retrieved_ids = ["chunk_0", "chunk_1", "chunk_2"]
        if self.version == "v1":
            # V1 thi thoảng lấy sai chunk hoặc thiếu chunk
            if random.random() > 0.7:
                retrieved_ids = ["chunk_99", "chunk_100"] 
        else:
            # V2 retrieval ổn định hơn
            if random.random() > 0.95:
                retrieved_ids = ["chunk_99"]

        # Giả lập Generation
        answer_quality = "tốt" if self.version == "v2" else "trung bình"
        
        return {
            "answer": f"[{self.name}] Dựa trên tài liệu hệ thống, tôi xin trả lời câu hỏi: '{question}'. "
                      f"Đây là câu trả lời chất lượng {answer_quality}.",
            "metadata": {
                "model": "gpt-4o-mini" if self.version == "v1" else "gpt-4o",
                "tokens_used": random.randint(100, 300),
                "retrieved_ids": retrieved_ids,
                "version": self.version,
                "latency": latency
            }
        }

if __name__ == "__main__":
    async def test():
        agent = MainAgent(version="v2")
        resp = await agent.query("Làm thế nào để đo lường MRR?")
        print(resp)
    asyncio.run(test())
