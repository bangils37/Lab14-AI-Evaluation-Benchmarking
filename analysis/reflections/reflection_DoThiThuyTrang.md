# Báo cáo cá nhân - Lab Day 14

**Họ và tên:** Đỗ Thị Thùy Trang  
**MSSV:** 2A202600041  
**Vai trò trong nhóm:** Quality Assurance / Analyst

## 1. Đóng góp kỹ thuật (Engineering Contribution)
Trong bài lab này, em tập trung vào phần kiểm thử kết quả và phân tích benchmark, cụ thể là:

- Theo dõi và kiểm tra cấu trúc đầu ra của `reports/summary.json` và `reports/benchmark_results.json` sau khi chạy `main.py`.
- Rà soát logic regression trong `main.py`, đặc biệt là phần so sánh `v1` và `v2` để đưa ra quyết định `APPROVE` hay `BLOCK`.
- Hoàn thiện phần `analysis/failure_analysis.md` dựa trên dữ liệu thật từ benchmark thay vì dùng mẫu điền tay.
- Kiểm tra tính nhất quán giữa chỉ số retrieval, điểm judge và trạng thái pass/fail để tìm ra các điểm dễ gây hiểu nhầm khi đọc kết quả.

Em cũng là người tập trung nhiều vào việc biến số liệu thành kết luận có thể hành động được. Thay vì chỉ đọc `avg_score`, em ưu tiên nhìn đồng thời:

- `hit_rate`
- `mrr`
- `agreement_rate`
- phân bố pass/fail theo độ khó

## 2. Kiến thức kỹ thuật (Technical Depth)
Qua phần việc của mình, em hiểu rõ hơn ba nhóm kiến thức chính:

### 2.1. Regression analysis
Em hiểu cách so sánh hai phiên bản agent không chỉ bằng cảm nhận mà bằng delta cụ thể:

- `avg_score`: đo thay đổi về chất lượng
- `avg_latency`: đo thay đổi về hiệu năng
- `hit_rate` và `mrr`: đo thay đổi ở retrieval

Trong repo hiện tại, `v2` cải thiện rõ:

- score tăng từ `2.85` lên `3.47`
- latency giảm từ `0.87s` xuống `0.46s`
- hit rate tăng từ `0.33` lên `0.38`

### 2.2. Quan hệ giữa retrieval và generation
Điều em rút ra rõ nhất là: answer quality và retrieval quality có liên hệ, nhưng không thể thay thế nhau.

Ở benchmark hiện tại:

- chỉ `18` case vừa pass vừa hit đúng top-3
- có tới `20` case vẫn pass dù retrieval miss top-3
- `14/17` fail là retrieval miss top-3

Điều này cho thấy nếu nhóm chỉ nhìn judge score thì sẽ bỏ sót điểm yếu thật sự của hệ thống RAG.

### 2.3. Multi-judge reliability
Benchmark có `20/55` case rơi vào `conflict_status = high`. Em thấy đây là tín hiệu quan trọng:

- multi-judge không chỉ dùng để “lấy trung bình điểm”
- nó còn giúp phát hiện các case mà tiêu chí chấm chưa đủ rõ hoặc câu trả lời của agent nằm ở vùng biên khó đánh giá

Em cũng nhận ra một giới hạn kỹ thuật của repo hiện tại: cost đang được tính theo bảng giá mô phỏng `gpt-4o-mini/gpt-4o`, trong khi lớp judge thực tế lại đang dùng Gemma/Gemini. Vì vậy cost metric hiện phù hợp để so sánh tương đối giữa `v1` và `v2`, nhưng chưa nên xem là chi phí thanh toán thực.

## 3. Giải quyết vấn đề (Problem Solving)
Vấn đề lớn nhất trong phần em phụ trách là làm sao đọc benchmark một cách đúng bản chất, không bị “đánh lừa” bởi số trung bình.

**Vấn đề 1: score tăng nhưng retrieval vẫn thấp.**  
Nếu chỉ nhìn `avg_score = 3.47`, có thể nghĩ agent đã khá tốt. Nhưng khi đối chiếu với `hit_rate = 0.38` và `mrr = 0.26`, em thấy retrieval vẫn là bottleneck rõ ràng. Từ đó em đề xuất failure analysis phải lấy retrieval làm trục chính thay vì chỉ mô tả câu trả lời sai.

**Vấn đề 2: có nhiều case pass dù retrieval miss.**  
Điều này làm việc đọc benchmark dễ bị nhầm. Em giải quyết bằng cách tách riêng bốn nhóm:

- pass + retrieval hit
- pass + retrieval miss
- fail + retrieval hit
- fail + retrieval miss

Nhờ vậy, báo cáo nhóm không còn kết luận quá đơn giản kiểu “pass nghĩa là retrieval tốt”.

**Vấn đề 3: report mẫu ban đầu chưa bám repo thật.**  
Các file report ban đầu còn nhiều placeholder và ví dụ không còn khớp với domain `heart_health`. Em đã chuyển hướng phân tích sang các case fail thật trong `benchmark_results.json`, đặc biệt là các câu hỏi về nguyên nhân nhồi máu cơ tim, phòng ngừa xơ vữa động mạch, và các câu adversarial dạng viết thơ.

## 4. Tự đánh giá
Em đánh giá phần mạnh nhất của mình là khả năng biến log benchmark thành insight có giá trị cho cả nhóm. Em không trực tiếp viết nhiều code lõi như retriever hay agent, nhưng em giúp hệ thống benchmark trở nên “đọc được” và “ra quyết định được”.

Nếu có thêm thời gian, em muốn cải thiện thêm:

- một script tự động phân cụm fail cases thay vì phân tích bán thủ công từ JSON
- một dashboard nhỏ để hiển thị score, hit rate, conflict rate và pass/fail theo difficulty
- đưa cost vào release gate theo dạng ngưỡng mềm, vì hiện tại `v2` được approve dù chi phí proxy tăng mạnh

Em hài lòng với phần đóng góp của mình vì nó phục vụ trực tiếp mục tiêu của lab: không chỉ chạy benchmark, mà phải hiểu được benchmark đang nói gì về hệ thống.
