# Báo cáo cá nhân - Lab Day 14

**Họ và tên:** Bùi Trọng Anh  
**MSSV:** 2A202600010  
**Vai trò trong nhóm:** Data Scientist / Prompt Engineer

## 1. Đóng góp kỹ thuật (Engineering Contribution)
Trong bài lab này, em tập trung vào lớp dữ liệu đánh giá và pipeline sinh test case. Các phần em phụ trách chính gồm:

- Chuẩn hóa knowledge source sang thư mục `data/heart_health` gồm 5 tài liệu markdown về tim mạch, thay cho cách đọc một file văn bản đơn lẻ.
- Điều chỉnh `data/synthetic_gen.py` để chunk theo section dựa trên heading markdown, giúp `chunk_id` của dữ liệu sinh ra khớp với `chunk_id` trong retriever.
- Thiết kế lại prompt sinh dữ liệu để bộ golden set không chỉ có câu hỏi factual mà còn có `hard cases` theo `HARD_CASES_GUIDE.md` như prompt injection, goal hijacking, out-of-context, ambiguous, multi-turn và correction.
- Tối ưu pipeline SDG để giảm quota tiêu thụ khi gọi Gemini/Gemma: giảm concurrency, rút gọn context, chọn số chunk đủ dùng, và thêm retry theo `retry_delay`.

Kết quả là bộ `golden_set.jsonl` hiện tại có `55` test case với phân bố đủ 4 độ khó:

- `15` easy
- `14` medium
- `14` hard
- `12` adversarial

## 2. Kiến thức kỹ thuật (Technical Depth)
Qua phần việc của mình, em học được nhiều bài học thực tế về thiết kế data cho evaluation:

- Chất lượng benchmark không chỉ nằm ở số lượng test case, mà nằm ở việc test case có ép được hệ thống lộ điểm yếu hay không.
- Với RAG, việc đồng bộ giữa `synthetic_gen.py` và `engine/retriever.py` là rất quan trọng. Nếu dữ liệu sinh ra dùng một kiểu chunking còn retriever dùng kiểu khác, `expected_retrieval_ids` sẽ mất giá trị.
- Prompt cho SDG cần vừa chặt vừa tiết kiệm token. Trong free tier, giới hạn không chỉ là số request mà còn là `input tokens per minute`, nên prompt engineering cũng là một bài toán cost engineering.
- Adversarial cases cần được thiết kế có chủ đích. Nếu chỉ hỏi factual question, benchmark sẽ không đo được khả năng từ chối đúng, xin làm rõ, hay giữ đúng phạm vi nhiệm vụ của agent.

Một điểm em thấy rất đáng giá là bộ data hiện tại đã thực sự tạo áp lực lên hệ thống: nhóm `hard` và `adversarial` có tỉ lệ fail cao hơn hẳn, cho thấy dữ liệu không bị “quá dễ”.

## 3. Giải quyết vấn đề (Problem Solving)
Trong quá trình làm, em gặp ba vấn đề chính:

**Vấn đề 1: dữ liệu nguồn ban đầu chưa phù hợp cho retrieval evaluation.**  
Ban đầu script sinh dữ liệu đọc từ `knowledge_source.txt`, trong khi retriever thực tế lại đang lấy dữ liệu từ `data/heart_health`. Điều này làm benchmark dễ bị lệch ground truth. Em đã sửa lại generator để đọc trực tiếp từ thư mục `heart_health` và sinh `chunk_id` theo format `heart_health_xx_section_y`.

**Vấn đề 2: chunk theo paragraph làm câu hỏi sinh ra bị rời ý.**  
Nếu chunk quá nhỏ, model thường tạo câu hỏi dựa trên mẩu thông tin cục bộ, khó ra được các câu reasoning hoặc adversarial chất lượng. Em chuyển sang chunk theo section và đưa cả tiêu đề tài liệu lẫn tiêu đề mục vào context để tăng tính mạch lạc.

**Vấn đề 3: gặp rate limit khi sinh dữ liệu.**  
Script ban đầu gọi rất nhiều request song song nên vượt quota free tier. Em đã tối ưu theo hướng:

- chỉ chọn số chunk đủ dùng
- tăng số câu hỏi trên mỗi request
- giảm concurrency xuống `1`
- cắt ngắn context
- thêm backoff và retry theo thông báo từ API

Đây là một kinh nghiệm rất thực tế: với pipeline evaluation, muốn hệ thống chạy được ổn định thì phải tối ưu cả “độ khó dữ liệu” lẫn “chi phí sinh dữ liệu”.

## 4. Tự đánh giá
Em đánh giá phần đóng góp của mình mạnh nhất ở chỗ biến bộ dữ liệu từ một tập câu hỏi minh họa thành một golden set có giá trị kiểm thử thực sự. Em không chỉ thêm số lượng case, mà cố gắng làm cho dataset phản ánh đúng yêu cầu rubric: có retrieval ground truth, có hard cases, và có khả năng làm lộ điểm yếu của agent.

Nếu có thêm thời gian, em muốn cải thiện hai điểm:

- thêm bước kiểm tra tự động chất lượng từng test case sau khi sinh ra để loại bớt case yếu hoặc trùng ý
- chuẩn hóa taxonomy của trường `type` để tránh trường hợp dataset sinh ra thêm nhãn mới như `ambiguous` hoặc `out-of-context` mà benchmark hiện chưa tận dụng trực tiếp

Nhìn chung, em hài lòng với phần việc mình phụ trách vì nó tác động trực tiếp đến chất lượng toàn bộ benchmark: dữ liệu tốt thì mới đánh giá được agent một cách đáng tin cậy.
