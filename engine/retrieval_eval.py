from typing import List, Dict
import numpy as np

class RetrievalEvaluator:
    """
    Chuyên gia đánh giá hiệu năng của Vector DB / Retrieval Stage.
    """
    def __init__(self):
        pass

    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        """
        Tính toán xem ít nhất 1 trong expected_ids có nằm trong top_k của retrieved_ids không.
        """
        if not expected_ids or not retrieved_ids:
            return 0.0
            
        top_retrieved = retrieved_ids[:top_k]
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        """
        Tính Mean Reciprocal Rank.
        Tìm vị trí đầu tiên của một expected_id trong retrieved_ids.
        MRR = 1 / position (vị trí 1-indexed). Nếu không thấy thì là 0.
        """
        if not expected_ids or not retrieved_ids:
            return 0.0

        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)
        return 0.0

    async def evaluate_batch(self, results: List[Dict]) -> Dict:
        """
        Chạy eval cho toàn bộ kết quả benchmark.
        Mỗi result cần có 'test_case' chứa 'expected_retrieval_ids' 
        và 'agent_response' chứa 'retrieved_ids'.
        """
        hit_rates = []
        mrrs = []
        
        for res in results:
            expected = res.get("expected_retrieval_ids", [])
            retrieved = res.get("retrieved_ids", [])
            
            hit_rates.append(self.calculate_hit_rate(expected, retrieved))
            mrrs.append(self.calculate_mrr(expected, retrieved))
            
        return {
            "avg_hit_rate": float(np.mean(hit_rates)) if hit_rates else 0.0,
            "avg_mrr": float(np.mean(mrrs)) if mrrs else 0.0,
            "total_evaluated": len(results)
        }
