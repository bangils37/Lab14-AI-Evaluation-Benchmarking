# Báo cáo cá nhân - Lab Day 14

**Họ và tên:** Bùi Trọng Anh
**MSSV:** 2A202600010
**Vai trò trong nhóm:** Data Scientist / Prompt Engineer

## 1. Đóng góp kỹ thuật (Engineering Contribution)
Trong Lab này, tôi đã tập trung vào:
- **Tối ưu hóa Data Source**: Lựa chọn và cấu trúc tài liệu nguồn [knowledge_source.txt](file:///d:/VinUni_AIThucChien/Lab14-AI-Evaluation-Benchmarking/data/knowledge_source.txt) để đảm bảo độ bao phủ các khía cạnh của AI Evaluation.
- **Thiết kế Prompt cho Gemini**: Tinh chỉnh các prompt cho quá trình SDG và Multi-Judge để đạt được kết quả JSON chuẩn xác và ít sai lệch nhất.
- **Phân tích lỗi (Failure Clustering)**: Tham gia vào việc phân loại các trường hợp "Fail" trong benchmark để tìm ra lỗi hệ thống.

## 2. Kiến thức kỹ thuật (Technical Depth)
- **RAGAS Metrics**: Hiểu sâu về cách đo lường Faithfulness và Answer Relevancy mà không cần Ground Truth truyền thống.
- **Gemini API**: Nắm vững cách cấu hình và gọi model Gemini 1.5 Pro/Flash thông qua SDK mới.
- **SDG Diversification**: Hiểu tầm quan trọng của việc có bộ câu hỏi Adversarial để kiểm tra độ bền vững (Robustness) của Agent.

## 3. Giải quyết vấn đề (Problem Solving)
- **Vấn đề**: Các test case ban đầu quá đơn giản, không phản ánh được khả năng suy luận của Agent.
- **Giải pháp**: Tôi đã đề xuất và triển khai bộ tiêu chí đánh giá độ khó, phân tách các câu hỏi thành 4 mức độ: Easy, Medium, Hard và Adversarial.

## 4. Tự đánh giá
Tôi đã hoàn thành tốt vai trò thiết kế dữ liệu và cấu trúc đánh giá. Kết quả cụ thể sẽ được phân tích sâu hơn sau khi hệ thống chạy benchmark trên toàn bộ Golden Dataset.
