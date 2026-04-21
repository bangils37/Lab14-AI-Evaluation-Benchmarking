# Báo cáo Phân tích Lỗi (Failure Analysis Report)

## 1. Tổng quan kết quả Benchmark
Dựa trên kết quả chạy `v2` (Optimized Version):
- **Tỷ lệ Pass/Fail**: [Sẽ được điền sau khi chạy]
- **Điểm trung bình (Judge Score)**: [Sẽ được điền sau khi chạy]
- **Hit Rate**: [Sẽ được điền sau khi chạy]

## 2. Phân cụm lỗi (Failure Clustering)
Chúng tôi phân tích các trường hợp "Fail" (điểm < 3) và phân thành các nhóm sau:

| Nhóm lỗi | Tỷ lệ | Nguyên nhân dự đoán |
| :--- | :---: | :--- |
| **Retrieval Failure** | [TBD]% | Không tìm thấy chunk chứa thông tin chính xác. |
| **Hallucination** | [TBD]% | Agent tự bịa ra thông tin không có trong context. |
| **Partial Answer** | [TBD]% | Câu trả lời đúng nhưng chưa đầy đủ ý. |
| **Reasoning Error** | [TBD]% | Tìm đúng context nhưng không suy luận được kết quả. |

## 3. Phân tích "5 Whys" sâu (Root Cause Analysis)
*Chọn một case điển hình bị Fail để phân tích:*

**Vấn đề: Agent không trả lời được cách tính MRR chính xác.**

1. **Tại sao Agent trả lời sai?**
   - Vì thông tin trong Context trả về bị thiếu công thức toán học.
2. **Tại sao Context bị thiếu?**
   - Vì bước Retrieval chỉ lấy top 3 chunks, và thông tin công thức nằm ở chunk thứ 5.
3. **Tại sao Retrieval không lấy được chunk thứ 5?**
   - Vì độ tương đồng ngữ nghĩa (Cosine Similarity) của chunk đó thấp hơn các chunk giải thích chung chung.
4. **Tại sao độ tương đồng ngữ nghĩa lại thấp?**
   - Vì chunk đó chứa nhiều ký hiệu toán học, trong khi Embedding model hiện tại (text-embedding-3-small) mạnh về văn bản hơn là ký hiệu.
5. **Tại sao chưa dùng Model hoặc chiến lược tốt hơn?**
   - Vì hệ thống chưa triển khai **Hybrid Search** (kết hợp Keyword Search) hoặc **Reranking** để ưu tiên các chunk có từ khóa kỹ thuật.

**=> Giải pháp đề xuất:** Triển khai thêm bước Reranking (ví dụ dùng Cohere) để đảm bảo các chunk quan trọng nhất luôn nằm trong top 3.

## 4. Đề xuất tối ưu hóa (Optimizations)
- [ ] Tăng `top_k` từ 3 lên 5.
- [ ] Sử dụng chiến lược Small-to-Big retrieval (Parent Document Retrieval).
- [ ] Cải thiện Prompt cho Judge model để chấm điểm khắt khe hơn về độ đầy đủ (Completeness).
