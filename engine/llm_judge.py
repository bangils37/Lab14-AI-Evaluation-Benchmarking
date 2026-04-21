import asyncio
import os
import json
from typing import Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMJudge:
    def __init__(self, model_a: str = "gemma-3-4b-it", model_b: str = "gemma-3-27b-it"):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model_a_name = model_a
        self.model_b_name = model_b
        
        self.rubrics = {
            "accuracy": "Chấm điểm từ 1-5 dựa trên độ chính xác so với Ground Truth. 5: Hoàn hảo, 1: Hoàn toàn sai hoặc Hallucination.",
            "tone": "Chấm điểm từ 1-5 dựa trên sự chuyên nghiệp, lịch sự và phù hợp của ngôn ngữ.",
            "completeness": "Chấm điểm từ 1-5 dựa trên việc câu trả lời có bao quát hết các ý chính trong Ground Truth không."
        }

    def _normalize_score(self, payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict):
            return payload

        if isinstance(payload, list) and payload:
            first_item = payload[0]
            if isinstance(first_item, dict):
                return first_item

        raise ValueError(f"Unexpected judge payload type: {type(payload).__name__}")

    async def _call_judge(self, model_name: str, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        Bạn là một giám khảo chấm điểm câu trả lời của AI. 
        Hãy đánh giá câu trả lời dựa trên Ground Truth (Sự thật gốc).

        Câu hỏi: {question}
        Ground Truth: {ground_truth}
        AI Answer: {answer}

        Tiêu chí chấm điểm (Rubrics):
        1. Accuracy: {self.rubrics['accuracy']}
        2. Tone: {self.rubrics['tone']}
        3. Completeness: {self.rubrics['completeness']}

        Trả về đúng MỘT JSON object thuần túy, không bọc trong list:
        {{
            "accuracy": <score 1-5>,
            "tone": <score 1-5>,
            "completeness": <score 1-5>,
            "reasoning": "<Giải thích ngắn gọn lý do chấm điểm>"
        }}
        """
        try:
            response = await asyncio.to_thread(model.generate_content, prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            parsed = json.loads(text)
            return self._normalize_score(parsed)
        except Exception as e:
            print(f"Error calling judge {model_name}: {e}")
            return {"accuracy": 1, "tone": 1, "completeness": 1, "reasoning": "Error in judging."}

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        """
        EXPERT TASK: Gọi ít nhất 2 model Gemini.
        """
        score_a = await self._call_judge(self.model_a_name, question, answer, ground_truth)
        score_b = await self._call_judge(self.model_b_name, question, answer, ground_truth)
        
        final_accuracy = (score_a["accuracy"] + score_b["accuracy"]) / 2
        
        diff = abs(score_a["accuracy"] - score_b["accuracy"])
        agreement = max(0, 1.0 - (diff / 4.0)) 
        
        final_score = final_accuracy
        if diff > 1:
            # Ưu tiên Gemini Pro hơn Flash
            final_score = (score_a["accuracy"] * 0.7) + (score_b["accuracy"] * 0.3)

        return {
            "final_score": round(final_score, 2),
            "agreement_rate": round(agreement, 2),
            "individual_scores": {
                self.model_a_name: score_a,
                self.model_b_name: score_b
            },
            "conflict_status": "high" if diff > 1 else "low"
        }
