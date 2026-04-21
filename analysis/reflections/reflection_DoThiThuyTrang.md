# Báo cáo cá nhân - Lab Day 14

**Họ và tên:** Đỗ Thị Thùy Trang
**MSSV:** 2A202600041
**Vai trò trong nhóm:** Quality Assurance / Analyst

## 1. Đóng góp kỹ thuật (Engineering Contribution)
Trong dự án này, tôi đã phụ trách các phần:
- **Xây dựng Regression Gate**: Thiết kế logic so sánh V1 và V2 trong `main.py`, thiết lập các ngưỡng Threshold để quyết định "Release" hoặc "Rollback".
- **Phân tích 5 Whys**: Trực tiếp thực hiện phân tích nguyên nhân gốc rễ cho các case thất bại trong file [failure_analysis.md](file:///d:/VinUni_AIThucChien/Lab14-AI-Evaluation-Benchmarking/analysis/failure_analysis.md).
- **Validation Pipeline**: Chạy script `check_lab.py` và debug các lỗi định dạng báo cáo để đảm bảo bài nộp chuẩn 100%.

## 2. Kiến thức kỹ thuật (Technical Depth)
- **Regression Analysis**: Hiểu cách đánh giá sự thay đổi hiệu năng giữa các phiên bản Agent thông qua Delta Analysis.
- **Hit Rate & MRR**: Nắm rõ cách tính toán và ý nghĩa của việc đo lường độ chính xác tìm kiếm đối với chất lượng tổng thể của RAG.
- **Cost Analysis**: Theo dõi và báo cáo chi phí tiêu thụ token của Gemini để tối ưu hóa ngân sách dự án.

## 3. Giải quyết vấn đề (Problem Solving)
- **Vấn đề**: Cần một cách trực quan để báo cáo kết quả so sánh V1 vs V2 cho nhóm.
- **Giải pháp**: Tôi đã thiết kế cấu trúc JSON cho `summary.json` để bao quát toàn bộ lịch sử chạy, giúp việc so sánh Delta trở nên dễ dàng và tự động.

## 4. Tự đánh giá
Tôi đã thiết lập đầy đủ quy trình và tiêu chí đánh giá. Các báo cáo phân tích định lượng (summary.json) sẽ được hoàn thiện ngay sau khi nhận được kết quả từ pipeline benchmark.
