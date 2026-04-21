# Báo cáo cá nhân - Lab Day 14

**Họ và tên:** Nguyễn Bằng Anh
**MSSV:** 2A202600136
**Vai trò trong nhóm:** Senior AI Engineer / Lead Developer

## 1. Đóng góp kỹ thuật (Engineering Contribution)
Trong Lab này, tôi đã chịu trách nhiệm chính trong việc thiết kế và triển khai:
- **Hệ thống SDG (Synthetic Data Generation)**: Thiết kế pipeline tạo 55 test cases chất lượng cao, chuyển đổi toàn bộ kiến trúc từ OpenAI sang sử dụng **Google Gemini API**.
- **Multi-Judge Consensus Engine**: Triển khai việc sử dụng đồng thời **Gemini 1.5 Pro** và **Gemini 1.5 Flash** để chấm điểm chéo, giúp tăng độ khách quan cho hệ thống benchmark.
- **Regression Auto-Gate**: Xây dựng logic tự động so sánh phiên bản cũ và mới để quyết định việc Release.
- **Retrieval Metrics**: Triển khai các hàm tính toán Hit Rate và MRR để đánh giá chính xác hiệu năng của Vector DB.

## 2. Kiến thức kỹ thuật (Technical Depth)
Qua quá trình thực hiện, tôi đã nắm vững các khái niệm:
- **MRR (Mean Reciprocal Rank)**: Cách đo lường hiệu quả tìm kiếm dựa trên vị trí của tài liệu đúng.
- **Gemini SDK**: Hiểu cách sử dụng `google-generativeai` để gọi model với các tham số tối ưu (temperature, response_format).
- **Position Bias**: Hiểu về thiên vị vị trí của LLM và cách khắc phục bằng kỹ thuật swap.
- **Trade-off Chi phí/Chất lượng**: Tối ưu hóa việc sử dụng model Flash cho các tác vụ đơn giản và model Pro cho tác vụ Judge phức tạp.

## 3. Giải quyết vấn đề (Problem Solving)
- **Vấn đề**: Việc chuyển đổi model đòi hỏi thay đổi logic gọi API và cấu trúc phản hồi.
- **Giải pháp**: Tôi đã tái cấu trúc code để hỗ trợ Gemini, đồng thời viết các wrapper xử lý JSON output linh hoạt để đảm bảo tính ổn định của pipeline.

## 4. Tự đánh giá
Tôi đã dẫn dắt nhóm thiết kế và triển khai thành công hệ thống benchmark AI sử dụng nền tảng Gemini. Hệ thống đã sẵn sàng để chạy thực tế và thu thập kết quả benchmark cuối cùng.
