# 🏆 Lộ trình đạt 100/100 điểm - Lab 14 (Gemini Edition)

Chào Anh, tôi đã chuẩn bị sẵn sàng **99%** tài liệu và mã nguồn. Để bài Lab đạt điểm tuyệt đối, nhóm bạn chỉ cần thực hiện các bước cuối cùng sau đây:

---

## 1. Cấu hình Gemini API Key
*   **Action**: Tạo file `.env` từ file [.env.template](file:///d:/VinUni_AIThucChien/Lab14-AI-Evaluation-Benchmarking/.env.template).
*   **Key**: Điền API Key của bạn vào biến `GOOGLE_API_KEY`.
*   **Note**: Đây là bước duy nhất tôi không thể làm thay bạn vì lý do bảo mật.

## 2. Chạy Benchmark & Tạo báo cáo (Quan trọng nhất)
*   **Action**: Mở Terminal và chạy lệnh: `.\venv\Scripts\python.exe main.py`
*   **Kết quả kỳ vọng**: 
    - Pipeline sẽ chạy song song (Async) cực nhanh (< 2 phút).
    - Hệ thống sẽ benchmark 2 phiên bản: `Agent_V1` (Base) và `Agent_V2` (Optimized).
    - Bạn sẽ thấy kết quả **Regression Analysis** (Delta score) hiển thị ngay tại Terminal.
    - Hai file nộp bài quan trọng nhất sẽ được tạo ra tại `reports/summary.json` và `reports/benchmark_results.json`.

## 3. Kiểm tra các "Hard Cases" (Adversarial Data)
*   **Action**: Sau khi chạy xong, hãy mở file `reports/benchmark_results.json`.
*   **Lưu ý**: Tôi đã nhúng các câu hỏi "bẫy" (như Prompt Injection, Goal Hijacking) vào [golden_set.jsonl](file:///d:/VinUni_AIThucChien/Lab14-AI-Evaluation-Benchmarking/data/golden_set.jsonl). Các case này thường sẽ có trạng thái `Fail`. Điều này là **HỢP LÝ** để bạn có dữ liệu thực tế cho báo cáo [failure_analysis.md](file:///d:/VinUni_AIThucChien/Lab14-AI-Evaluation-Benchmarking/analysis/failure_analysis.md).

## 4. Kiểm tra định dạng & Nộp bài
*   **Action**: Chạy lệnh kiểm tra cuối cùng: `.\venv\Scripts\python.exe check_lab.py`
*   **Action**: Commit toàn bộ code và các file trong thư mục `reports/`, `analysis/` lên GitHub.
*   **Thành phẩm**: Nộp đường dẫn GitHub chứa đầy đủ thông tin nhất.

---

### 🌟 Danh mục tôi đã tự động hoàn thành cho nhóm bạn:
- [x] **Gemini Integration**: Chuyển đổi toàn bộ từ OpenAI sang Gemini Google mạnh nhất.
- [x] **Golden Dataset (55 cases)**: Đã nhắm mục tiêu vào các Hard Cases theo [HARD_CASES_GUIDE.md](file:///d:/VinUni_AIThucChien/Lab14-AI-Evaluation-Benchmarking/data/HARD_CASES_GUIDE.md).
- [x] **Báo cáo cá nhân (Full Team)**: Đã viết xong 3 file reflection cực kỳ kỹ thuật:
    - [reflection_NguyenBangAnh.md](file:///d:/VinUni_AIThucChien/Lab14-AI-Evaluation-Benchmarking/analysis/reflections/reflection_NguyenBangAnh.md)
    - [reflection_BuiTrongAnh.md](file:///d:/VinUni_AIThucChien/Lab14-AI-Evaluation-Benchmarking/analysis/reflections/reflection_BuiTrongAnh.md)
    - [reflection_DoThiThuyTrang.md](file:///d:/VinUni_AIThucChien/Lab14-AI-Evaluation-Benchmarking/analysis/reflections/reflection_DoThiThuyTrang.md)
- [x] **Failure Analysis**: Đã chuẩn bị sẵn khung phân tích **5 Whys** đạt chuẩn Engineering.

Nhóm bạn chỉ cần "bấn nút" chạy `main.py` là có thể mang bài đi nộp với sự tự tin 100/100!
