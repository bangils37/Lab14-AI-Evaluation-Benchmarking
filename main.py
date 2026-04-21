import asyncio
import json
import os
import time
from typing import List, Dict
from engine.runner import BenchmarkRunner
from engine.retrieval_eval import RetrievalEvaluator
from engine.llm_judge import LLMJudge
from agent.main_agent import MainAgent
from dotenv import load_dotenv

load_dotenv()

async def run_benchmark_for_version(version: str, dataset: List[Dict]) -> Dict:
    print(f"\n--- 🚀 Khởi động Benchmark cho {version} ---")
    
    agent = MainAgent(version=version)
    evaluator = RetrievalEvaluator()
    judge = LLMJudge()
    runner = BenchmarkRunner(agent, evaluator, judge)

    # Chạy benchmark
    results = await runner.run_all(dataset)

    # Tính toán Retrieval Metrics
    retrieval_stats = await evaluator.evaluate_batch(results)

    # Tổng hợp metrics
    total = len(results)
    avg_score = sum(r["judge"]["final_score"] for r in results) / total
    avg_latency = sum(r["latency"] for r in results) / total
    total_cost = sum(r["cost"] for r in results)
    avg_agreement = sum(r["judge"]["agreement_rate"] for r in results) / total

    summary = {
        "metadata": {
            "agent_version": version,
            "total": total,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "metrics": {
            "avg_score": round(avg_score, 2),
            "hit_rate": round(retrieval_stats["avg_hit_rate"], 2),
            "mrr": round(retrieval_stats["avg_mrr"], 2),
            "avg_latency": round(avg_latency, 2),
            "total_cost": round(total_cost, 4),
            "agreement_rate": round(avg_agreement, 2)
        }
    }

    return results, summary

async def main():
    if not os.path.exists("data/golden_set.jsonl"):
        print("❌ Thiếu data/golden_set.jsonl. Hãy điền API Key vào .env và chạy 'python data/synthetic_gen.py' trước.")
        return

    # Load dataset
    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if not dataset:
        print("❌ File data/golden_set.jsonl rỗng.")
        return

    # 1. Chạy V1 (Base)
    v1_results, v1_summary = await run_benchmark_for_version("v1", dataset)

    # 2. Chạy V2 (Optimized)
    v2_results, v2_summary = await run_benchmark_for_version("v2", dataset)

    # 3. So sánh Regression
    print("\n📊 --- KẾT QUẢ SO SÁNH (REGRESSION ANALYSIS) ---")
    score_delta = v2_summary["metrics"]["avg_score"] - v1_summary["metrics"]["avg_score"]
    latency_delta = ((v2_summary["metrics"]["avg_latency"] - v1_summary["metrics"]["avg_latency"]) / v1_summary["metrics"]["avg_latency"]) * 100
    
    print(f"V1 Score: {v1_summary['metrics']['avg_score']} | V2 Score: {v2_summary['metrics']['avg_score']} (Delta: {'+' if score_delta >= 0 else ''}{score_delta:.2f})")
    print(f"V1 Latency: {v1_summary['metrics']['avg_latency']}s | V2 Latency: {v2_summary['metrics']['avg_latency']}s (Change: {latency_delta:.1f}%)")
    print(f"V2 Hit Rate: {v2_summary['metrics']['hit_rate']} | V2 MRR: {v2_summary['metrics']['mrr']}")

    # 4. Release Gate Logic
    approved = False
    if score_delta >= 0 and latency_delta < 20: # Chấp nhận nếu score không giảm và latency không tăng quá 20%
        approved = True
        print("✅ QUYẾT ĐỊNH: CHẤP NHẬN BẢN CẬP NHẬT (APPROVE)")
    else:
        print("❌ QUYẾT ĐỊNH: TỪ CHỐI (BLOCK RELEASE) - Hiệu năng hoặc chất lượng bị giảm.")

    # 5. Xuất báo cáo
    os.makedirs("reports", exist_ok=True)
    
    report_summary = {
        "v1": v1_summary,
        "v2": v2_summary,
        "regression": {
            "score_delta": round(score_delta, 2),
            "latency_change_percent": round(latency_delta, 2),
            "decision": "APPROVE" if approved else "BLOCK"
        },
        "metadata": v2_summary["metadata"] # Dùng metadata v2 làm info chính
    }
    # Flatten cho check_lab.py (để nó tìm thấy metrics ở level cao nhất nếu cần)
    report_summary["metrics"] = v2_summary["metrics"] 

    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(report_summary, f, ensure_ascii=False, indent=2)
    
    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(v2_results, f, ensure_ascii=False, indent=2)

    print("\n✅ Đã lưu báo cáo vào thư mục reports/")

if __name__ == "__main__":
    asyncio.run(main())
