# Báo cáo cá nhân - Lab Day 14

**Họ và tên:** Nguyễn Bằng Anh  
**MSSV:** 2A202600136  
**Vai trò trong nhóm:** Senior AI Engineer / Lead Developer

## 1. Đóng góp kỹ thuật (Engineering Contribution)
Trong bài lab này, em đóng vai trò dẫn dắt phần kiến trúc benchmark và các module lõi của hệ thống. Những phần em tập trung nhiều nhất gồm:

- Xây dựng retriever trong `engine/retriever.py` để đọc toàn bộ dữ liệu từ `data/heart_health`, chunk theo section markdown, tạo embedding bằng `SentenceTransformer(all-MiniLM-L6-v2)` và truy vấn bằng cosine similarity.
- Thiết kế `MainAgent` trong `agent/main_agent.py` với hai phiên bản:
  - `v1`: top-k thấp hơn và có noise mô phỏng retrieval yếu
  - `v2`: top-k cao hơn, ít noise hơn và latency xử lý tốt hơn
- Triển khai `RetrievalEvaluator` trong `engine/retrieval_eval.py` để tính `Hit Rate` và `MRR`.
- Triển khai `LLMJudge` trong `engine/llm_judge.py` dùng hai judge model `gemma-3-4b-it` và `gemma-3-27b-it`, có tính `agreement_rate` và cơ chế xử lý xung đột điểm số.
- Tổ chức toàn bộ pipeline benchmark trong `main.py` và `engine/runner.py`, bao gồm chạy V1/V2, tổng hợp metrics và tự động đưa ra quyết định release gate.

Điểm em quan tâm nhất không chỉ là “chạy được”, mà là làm sao để các thành phần của benchmark liên kết đúng với nhau: chunking trong retriever phải khớp với chunking trong dữ liệu sinh ra, metric retrieval phải được đưa vào summary, và kết quả cuối phải đủ rõ để nhóm phân tích được nguyên nhân lỗi.

## 2. Kiến thức kỹ thuật (Technical Depth)
Qua quá trình xây dựng hệ thống, em hiểu sâu hơn một số khái niệm cốt lõi:

### 2.1. Retrieval metrics
`Hit Rate` và `MRR` không thay thế nhau:

- `Hit Rate` cho biết hệ thống có đưa đúng chunk vào top-k hay không
- `MRR` cho biết chunk đúng nằm ở vị trí cao hay thấp

Trong bài lab này, `v2` đạt `hit_rate = 0.38` và `mrr = 0.26`, cho thấy retriever có cải thiện so với `v1` nhưng vẫn chưa đủ mạnh cho câu hỏi hard/adversarial.

### 2.2. Multi-judge consensus
Em hiểu rõ hơn việc dùng nhiều judge model không phải để “làm đẹp benchmark”, mà để đo độ ổn định của phép chấm. Ở repo hiện tại:

- hai judge hoạt động song song
- nếu chênh lệch accuracy lớn hơn `1`, hệ thống dùng weighted score thay vì trung bình thuần

Cách làm này giúp benchmark thực tế hơn nhiều so với việc chỉ tin vào một model judge duy nhất.

### 2.3. Trade-off giữa chất lượng, tốc độ và chi phí
`v2` tốt hơn `v1` về điểm và latency, nhưng cost proxy cũng tăng mạnh. Em rút ra một bài học quan trọng: release gate trong hệ thống thực tế nên xem đồng thời ít nhất ba chiều:

- quality
- latency
- cost

Trong repo này, gate mới chặn theo score và latency. Đây là hợp lý cho bản lab đầu tiên, nhưng chưa đủ cho một production benchmark đầy đủ.

## 3. Giải quyết vấn đề (Problem Solving)
Em gặp ba vấn đề kỹ thuật đáng nhớ nhất:

**Vấn đề 1: đồng bộ chunking giữa dữ liệu và retriever.**  
Ban đầu nếu mỗi thành phần chunk theo một cách khác nhau thì `expected_retrieval_ids` sẽ không đáng tin. Em giải quyết bằng cách thống nhất chiến lược section-based chunking cho cả `synthetic_gen.py` và `engine/retriever.py`.

**Vấn đề 2: benchmark cần mô phỏng được cải tiến giữa hai phiên bản agent.**  
Nếu `v1` và `v2` gần như giống nhau, regression analysis sẽ không có ý nghĩa. Em giải quyết bằng cách điều chỉnh:

- `top_k`
- mức noise retrieval
- processing latency

Nhờ đó, `v2` thực sự thể hiện cải thiện định lượng thay vì chỉ khác tên phiên bản.

**Vấn đề 3: quality score không phản ánh đầy đủ vấn đề retrieval.**  
Khi đọc `benchmark_results.json`, em nhận ra có nhiều case pass dù retrieval miss top-3. Điều này làm em thay đổi cách nhìn hệ thống: không thể coi judge score là chỉ số duy nhất. Vì vậy em đưa retrieval metrics thành một phần bắt buộc của summary và của quyết định phân tích lỗi.

## 4. Tự đánh giá
Em đánh giá phần đóng góp của mình nằm ở lớp kiến trúc và tính nhất quán của toàn bộ pipeline benchmark. Em không chỉ viết từng module riêng lẻ, mà cố gắng làm cho chúng ghép lại thành một hệ thống có thể:

- sinh dữ liệu
- truy xuất
- chấm điểm
- so sánh phiên bản
- xuất báo cáo

Nếu có thêm thời gian, em muốn nâng cấp hệ thống theo ba hướng:

- thay dense retrieval thuần bằng hybrid retrieval + reranking
- cải thiện generation của agent để thật sự tổng hợp câu trả lời thay vì dùng template tương đối cố định
- chuẩn hóa cost accounting theo model thực tế đang dùng, thay vì dùng bảng giá proxy

Nhìn chung, em hài lòng với phần việc mình đảm nhiệm vì repo hiện tại đã thể hiện được tinh thần của một “AI Evaluation Factory”: có dữ liệu, có metric, có release gate, có failure analysis, và có đủ tín hiệu để nhóm tiếp tục tối ưu trong vòng sau.
