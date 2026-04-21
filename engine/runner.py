import asyncio
import time
from typing import List, Dict, Any

class BenchmarkRunner:
    def __init__(self, agent, evaluator, judge):
        self.agent = agent
        self.evaluator = evaluator
        self.judge = judge
        
        # Giá tiền ước tính (USD per 1M tokens)
        self.COST_MODEL = {
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4o": {"input": 2.50, "output": 10.00}
        }

    def _calculate_cost(self, model: str, tokens: int) -> float:
        # Giả định 70% input, 30% output cho đơn giản
        model_rates = self.COST_MODEL.get(model, {"input": 0.5, "output": 1.5})
        avg_rate = (model_rates["input"] * 0.7 + model_rates["output"] * 0.3)
        return (tokens / 1_000_000) * avg_rate

    async def run_single_test(self, test_case: Dict) -> Dict:
        start_time = time.perf_counter()
        
        try:
            # 1. Gọi Agent
            response = await self.agent.query(test_case["question"])
            latency = time.perf_counter() - start_time
            
            # 2. Chạy Multi-Judge
            judge_result = await self.judge.evaluate_multi_judge(
                test_case["question"], 
                response["answer"], 
                test_case["expected_answer"]
            )
            
            # 3. Tính toán cost
            tokens = response.get("metadata", {}).get("tokens_used", 0)
            model = response.get("metadata", {}).get("model", "unknown")
            cost = self._calculate_cost(model, tokens)
            
            return {
                "test_case": test_case["question"],
                "difficulty": test_case.get("difficulty", "unknown"),
                "agent_response": response["answer"],
                "retrieved_ids": response.get("metadata", {}).get("retrieved_ids", []),
                "expected_retrieval_ids": test_case.get("expected_retrieval_ids", []),
                "latency": latency,
                "cost": cost,
                "tokens": tokens,
                "judge": judge_result,
                "status": "fail" if judge_result["final_score"] < 3 else "pass"
            }
        except Exception as e:
            print(f"Error in test case '{test_case['question']}': {e}")
            return {"status": "error", "error": str(e)}

    async def run_all(self, dataset: List[Dict], batch_size: int = 10) -> List[Dict]:
        """
        Chạy tuần tự để giảm số request đồng thời và tránh vượt quota.
        """
        results = []
        total_cases = len(dataset)
        print(f"🚀 Chạy benchmark cho {total_cases} cases (Batch size: {batch_size})...")

        for idx, case in enumerate(dataset, start=1):
            question = case.get("question", "")
            preview = (question[:70] + "...") if len(question) > 70 else question
            print(f"[{idx}/{total_cases}] ▶ Running: {preview}")

            result = await self.run_single_test(case)
            results.append(result)

            status = result.get("status", "unknown")
            latency = result.get("latency")
            if isinstance(latency, (int, float)):
                print(f"[{idx}/{total_cases}] ✓ Done | status={status} | latency={latency:.2f}s")
            else:
                print(f"[{idx}/{total_cases}] ✓ Done | status={status}")

        return results
