import json
import asyncio
import os
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv
from tqdm.asyncio import tqdm

load_dotenv()

# Cấu hình Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def generate_qa_batch(text_chunk: str, chunk_id: str, num_pairs: int = 5) -> List[Dict]:
    """
    Sử dụng Google Gemini để tạo các cặp (Question, Expected Answer, Context) từ một đoạn văn bản.
    """
    model = genai.GenerativeModel('gemma-3-27b-it')
    
    prompt = f"""
    Bạn là một chuyên gia đánh giá AI (AI Evaluation Expert). 
    Dựa trên tài liệu dưới đây, hãy tạo ra {num_pairs} cặp câu hỏi và câu trả lời.
    
    Yêu cầu:
    1. Các câu hỏi phải bao gồm nhiều mức độ: Dễ (Fact-check), Trung bình (Reasoning), Khó (Complex Synthesis) và Nghịch lý (Adversarial/Red Teaming).
    2. Mỗi cặp phải bao gồm:
       - Question: Câu hỏi cụ thể.
       - Expected Answer: Câu trả lời chính xác, đầy đủ dựa trên tài liệu.
       - Difficulty: 'easy', 'medium', 'hard', hoặc 'adversarial'.
       - Type: 'fact-check', 'reasoning', 'summarization', hoặc 'adversarial'.
    3. Trả về định dạng JSON list thuần túy.

    Tài liệu:
    \"\"\"{text_chunk}\"\"\"

    Định dạng JSON yêu cầu:
    [
      {{
        "question": "...",
        "expected_answer": "...",
        "difficulty": "...",
        "type": "..."
      }},
      ...
    ]
    """

    try:
        # Gemini call (Gemini SDK is synchronous by default, we wrap in thread for async if needed, 
        # but here we just call it. For a real async experience, use a thread pool.)
        response = await asyncio.to_thread(model.generate_content, prompt)
        
        # Làm sạch output để chỉ lấy JSON
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        data = json.loads(text)
        
        if isinstance(data, dict):
            for key in data:
                if isinstance(data[key], list):
                    qa_pairs = data[key]
                    break
            else:
                qa_pairs = []
        else:
            qa_pairs = data

        # Thêm metadata
        for pair in qa_pairs:
            pair["context"] = text_chunk
            pair["expected_retrieval_ids"] = [chunk_id]
            
        return qa_pairs
    except Exception as e:
        print(f"Error generating QA batch for chunk {chunk_id}: {e}")
        return []

async def main():
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ LỖI: Thiếu GOOGLE_API_KEY trong file .env")
        return

    knowledge_path = "data/knowledge_source.txt"
    if not os.path.exists(knowledge_path):
        print(f"❌ LỖI: Không tìm thấy file {knowledge_path}")
        return

    with open(knowledge_path, "r", encoding="utf-8") as f:
        content = f.read()

    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    
    all_qa_pairs = []
    num_total_needed = 55
    pairs_per_chunk = max(1, num_total_needed // len(paragraphs) + 1)

    print(f"🚀 Bắt đầu tạo {num_total_needed} test cases sử dụng Gemini...")

    tasks = []
    for i, p in enumerate(paragraphs):
        tasks.append(generate_qa_batch(p, f"chunk_{i}", pairs_per_chunk))

    results = await tqdm.gather(*tasks)
    for res in results:
        all_qa_pairs.extend(res)

    all_qa_pairs = all_qa_pairs[:num_total_needed]

    output_path = "data/golden_set.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for pair in all_qa_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    print(f"✅ Hoàn thành! Đã lưu {len(all_qa_pairs)} test cases vào {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
