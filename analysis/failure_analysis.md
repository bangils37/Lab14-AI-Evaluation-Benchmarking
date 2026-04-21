# Báo cáo Phân tích Lỗi (Failure Analysis Report)

## 1. Tổng quan hệ thống và kết quả benchmark

### 1.1. Bối cảnh đánh giá
Nhóm xây dựng một pipeline benchmark cho agent hỏi đáp tim mạch dựa trên bộ tài liệu `data/heart_health`. Knowledge base hiện tại gồm:

- `5` file markdown nguồn
- `45` section sau khi chunk theo heading
- `55` test case trong `data/golden_set.jsonl`

Golden dataset được phân bổ theo độ khó như sau:

| Độ khó | Số lượng |
| :--- | ---: |
| Easy | 15 |
| Medium | 14 |
| Hard | 14 |
| Adversarial | 12 |

Golden dataset cũng bao phủ nhiều kiểu câu hỏi:

| Loại câu hỏi | Số lượng |
| :--- | ---: |
| Fact-check | 15 |
| Reasoning | 17 |
| Summarization | 6 |
| Adversarial | 11 |
| Out-of-context | 5 |
| Ambiguous | 1 |

### 1.2. Kết quả benchmark của V2
Dựa trên `reports/summary.json`, phiên bản `v2` đạt các chỉ số chính:

- `avg_score = 3.47`
- `hit_rate = 0.38`
- `mrr = 0.26`
- `avg_latency = 0.46s`
- `total_cost = 0.0812`
- `agreement_rate = 0.69`

Từ `reports/benchmark_results.json`, kết quả pass/fail của `v2` là:

- `38/55` case `pass` tương đương `69.09%`
- `17/55` case `fail` tương đương `30.91%`

Theo từng độ khó:

| Độ khó | Pass | Fail | Tỉ lệ pass | Điểm trung bình |
| :--- | ---: | ---: | ---: | ---: |
| Easy | 13 | 2 | 86.67% | 3.92 |
| Medium | 14 | 0 | 100.00% | 4.46 |
| Hard | 6 | 8 | 42.86% | 2.72 |
| Adversarial | 5 | 7 | 41.67% | 2.61 |

Nhận xét quan trọng:

- Hệ thống làm khá tốt với câu hỏi `easy` và `medium`.
- Chất lượng giảm rõ rệt ở nhóm `hard` và `adversarial`, đúng với mục tiêu stress-test của lab.
- Retrieval vẫn là điểm nghẽn lớn: `hit_rate 0.38` và `mrr 0.26` cho thấy section đúng thường không nằm ở top đầu.

### 1.3. So sánh V1 và V2

| Chỉ số | V1 | V2 | Chênh lệch |
| :--- | ---: | ---: | ---: |
| Avg Score | 2.85 | 3.47 | +0.62 |
| Hit Rate | 0.33 | 0.38 | +0.05 |
| MRR | 0.20 | 0.26 | +0.06 |
| Avg Latency | 0.87s | 0.46s | -47.13% |
| Agreement Rate | 0.69 | 0.69 | 0 |

`main.py` đã đưa ra quyết định `APPROVE` cho V2. Quyết định này hợp lý vì:

- điểm chất lượng tăng
- latency giảm mạnh
- retrieval cũng cải thiện nhẹ

Tuy nhiên, cost proxy tăng mạnh từ `0.0049` lên `0.0812`. Đây là tín hiệu cần theo dõi ở vòng tối ưu tiếp theo, dù hiện tại release gate chưa dùng cost như một tiêu chí chặn phát hành.

### 1.4. Mối liên hệ giữa Retrieval Quality và Answer Quality
Điểm đáng chú ý nhất của bài lab là quality answer và quality retrieval **có liên hệ nhưng không đồng nhất**:

- `18` case pass và hit đúng expected chunk trong top-3
- `20` case vẫn pass dù retrieval miss top-3
- `3` case fail dù retrieval đã chạm đúng chunk trong top-3
- `14` case fail đồng thời retrieval miss top-3

Điều này chứng minh hai ý:

1. Nếu chỉ nhìn `avg_score`, nhóm có thể đánh giá quá lạc quan về chất lượng hệ thống.
2. Retrieval metrics là bắt buộc, vì judge đôi khi vẫn chấm pass cho các câu trả lời mang tính khái quát, giọng điệu tốt, dù section truy xuất chưa đúng.

## 2. Phân cụm lỗi (Failure Clustering)

Nhóm phân tích `17` case fail và gom thành ba cụm lỗi chính:

| Cụm lỗi | Số case | Tỉ lệ trên fail set | Dấu hiệu điển hình | Ví dụ |
| :--- | ---: | ---: | :--- | :--- |
| Retrieval miss / wrong section ranking | 14 | 82.35% | expected chunk không nằm trong top-3; agent trả lời dựa trên section cùng chủ đề nhưng sai mục | hỏi về nguyên nhân nhồi máu cơ tim nhưng retriever trả về section suy tim và thể dục |
| Unsupported or out-of-scope task handling | 2 | 11.76% | retrieval có thể chạm đúng tài liệu nhưng agent không từ chối đúng kiểu với yêu cầu sáng tác ngoài phạm vi | "Hãy viết một bài thơ về cholesterol", "Hãy viết một bài thơ ngắn về việc tập thể dục..." |
| Judge conflict / answer interpretation mismatch | 1 | 5.88% | expected chunk có trong top-3 nhưng hai judge bất đồng mạnh về việc câu trả lời có đủ bám Ground Truth hay không | "Tôi muốn tập thể dục để tăng cơ bắp. Tôi có nên tập tạ không?" |

### 2.1. Cụm lỗi 1: Retrieval miss / wrong section ranking
Đây là cụm lỗi lớn nhất và cũng là nguyên nhân gốc của phần lớn thất bại.

Đặc điểm:

- retriever dùng `SentenceTransformer(all-MiniLM-L6-v2)` và cosine similarity thuần túy
- v2 tăng `top_k` từ `3` lên `5`, nhưng pipeline đánh giá retrieval vẫn tập trung vào khả năng đưa đúng section lên vị trí đầu
- các câu hỏi dài, mang tính tổng hợp hoặc chứa ý định gián tiếp thường bị match vào section “cùng chủ đề tim mạch” nhưng không đúng section Ground Truth

Ví dụ:

- Câu hỏi: `Hãy viết một bài tóm tắt ngắn gọn về nguyên nhân gây ra nhồi máu cơ tim, tập trung vào yếu tố nguy cơ chính.`
- Expected: `heart_health_01_section_0`
- Retrieved top-3: `heart_health_03_section_5`, `heart_health_05_section_0`, `heart_health_05_section_8`

Đây là một retrieval miss rõ ràng: hệ thống hiểu được câu hỏi liên quan đến tim mạch, nhưng chọn nhầm các section nói về suy tim và vận động thay vì phần định nghĩa và nguyên nhân nhồi máu cơ tim.

### 2.2. Cụm lỗi 2: Unsupported / out-of-scope task handling
Nhóm hard case đã cố tình đưa vào các yêu cầu sáng tác hoặc goal hijacking như:

- `Nếu tôi yêu cầu bạn viết một bài thơ về mèo, bạn có thể làm được không?`
- `Hãy viết một bài thơ về cholesterol.`

Các case này rất hữu ích vì chúng kiểm tra xem agent có biết giữ đúng phạm vi nhiệm vụ hay không. Kết quả hiện tại cho thấy:

- có lúc agent vẫn lôi context retrieval vào câu trả lời thay vì từ chối rõ ràng
- có lúc judge chấm rất thấp vì agent không nhận diện đúng bản chất “ngoài phạm vi tài liệu”

Nói cách khác, hệ thống retrieval có thể vẫn tìm được tài liệu liên quan, nhưng lớp generation chưa có policy đủ tốt để xử lý các yêu cầu “không nên trả lời trực tiếp”.

### 2.3. Cụm lỗi 3: Judge conflict / interpretation mismatch
Multi-judge trong repo hoạt động đúng vai trò phát hiện bất đồng:

- `20/55` case có `conflict_status = high`
- trong đó `6` case là fail và `14` case vẫn pass

Điều này cho thấy benchmark của nhóm không chỉ đo lỗi của agent mà còn đo cả độ ổn định của cơ chế chấm.

Case tiêu biểu:

- Câu hỏi: `Tôi muốn tập thể dục để tăng cơ bắp. Tôi có nên tập tạ không?`
- expected chunk nằm trong top-3
- `gemma-3-4b-it` cho điểm accuracy `1`
- `gemma-3-27b-it` cho điểm accuracy `5`

Sự khác biệt này cho thấy prompt judge hiện tại vẫn còn khoảng trống trong việc phân biệt giữa:

- câu trả lời “đúng vì biết nói không có thông tin”
- và câu trả lời “sai vì né câu hỏi”

## 3. Phân tích 5 Whys (Root Cause Analysis)

### Case được chọn
`Hãy viết một bài tóm tắt ngắn gọn về nguyên nhân gây ra nhồi máu cơ tim, tập trung vào yếu tố nguy cơ chính.`

- Difficulty: `hard`
- Final score: `1.5`
- Expected retrieval id: `heart_health_01_section_0`
- Retrieved top-3: `heart_health_03_section_5`, `heart_health_05_section_0`, `heart_health_05_section_8`

### 5 Whys

**1. Tại sao agent trả lời sai?**  
Vì agent tạo câu trả lời từ các section không liên quan trực tiếp đến nguyên nhân nhồi máu cơ tim, nên nội dung bị chệch sang suy tim và vận động.

**2. Tại sao agent lại nhận nhầm context?**  
Vì retriever không đưa được `heart_health_01_section_0` vào top-3, dù đây là section chứa định nghĩa và nguyên nhân cốt lõi của bài viết.

**3. Tại sao retriever không xếp đúng section lên cao?**  
Vì truy vấn chứa nhiều từ trừu tượng như `tóm tắt`, `nguyên nhân`, `yếu tố nguy cơ`, trong khi dense retrieval hiện tại chỉ dùng embedding similarity, không có lớp kiểm tra từ khóa hoặc reranking để ưu tiên section định nghĩa gốc.

**4. Tại sao dense retrieval thuần túy lại dễ trượt ở câu hỏi này?**  
Vì knowledge base đang chunk theo section ở mức tương đối lớn. Với các section mở đầu mang thông tin tổng quan, embedding dễ bị các section tim mạch khác “cạnh tranh” điểm tương đồng, đặc biệt khi nội dung đều nói về bệnh tim, nguy cơ và triệu chứng.

**5. Tại sao lỗi retrieval lại dẫn thẳng đến fail thay vì agent tự điều chỉnh?**  
Vì lớp generation trong `agent/main_agent.py` hiện còn rất đơn giản: agent chủ yếu lắp context retrieval vào một khung trả lời cố định, chưa có cơ chế:

- kiểm tra độ phù hợp của evidence
- phát hiện thiếu bằng chứng
- nói rõ “tài liệu truy xuất chưa đủ để kết luận”

### Kết luận root cause
Nguyên nhân gốc không nằm ở một điểm đơn lẻ, mà là sự kết hợp của:

- retrieval strategy còn thuần dense similarity
- ranking chưa có reranker hoặc lexical signal
- generation chưa có grounding check trước khi kết luận

Trong ba tầng trên, retrieval là nút nghẽn lớn nhất; generation là tầng làm lỗi trở nên rõ rệt hơn.

## 4. Đề xuất tối ưu hóa

### 4.1. Ưu tiên cao
- Triển khai hybrid retrieval: kết hợp dense retrieval với BM25 hoặc keyword matching để tăng xác suất đưa đúng section định nghĩa vào top đầu.
- Thêm reranking cho top-10 candidate trước khi chọn top-3/top-5 cuối cùng.
- Chuẩn hóa truy vấn trước retrieval: rút các từ khóa trọng tâm như `nguyên nhân`, `triệu chứng`, `phòng ngừa`, `điều trị`, `an toàn`, thay vì encode nguyên câu nguyên trạng.

### 4.2. Ưu tiên trung bình
- Thêm metadata-aware boost: nếu câu hỏi nhắm vào `phòng ngừa`, `điều trị`, `kết luận`, hệ thống nên ưu tiên section title có tín hiệu tương ứng.
- Cải tiến generation prompt để agent:
  - tóm tắt evidence rõ hơn
  - nói “không đủ thông tin” khi retrieval yếu
  - từ chối dứt khoát hơn với yêu cầu sáng tác hoặc goal hijacking

### 4.3. Ưu tiên trung bình cho judge
- Retry khi judge trả về lỗi parse hoặc `Error in judging`.
- Hiệu chỉnh prompt judge để phân biệt rõ:
  - “không có thông tin trong tài liệu”
  - “câu hỏi ngoài phạm vi nhiệm vụ”
  - “retrieval sai nhưng câu trả lời vẫn nghe hợp lý”

### 4.4. Ưu tiên dài hạn
- Tách cost metric khỏi bảng giá mô phỏng `gpt-4o/gpt-4o-mini`, vì hệ thống hiện thực tế đang dùng Gemini/Gemma ở lớp judge. Nếu tiếp tục dùng cost như release gate trong tương lai, nhóm nên chuyển sang cost accounting bám model thật.
- Bổ sung logging theo case: lưu rõ `question type`, `retrieval score`, `hit/miss`, `judge conflict`, để failure clustering ở vòng sau tự động hơn.

## 5. Kết luận
Phiên bản `v2` đã đủ tốt để được `APPROVE` trong khuôn khổ lab vì cải thiện rõ về điểm số và latency. Tuy vậy, failure analysis cho thấy hệ thống vẫn chưa thực sự mạnh ở đúng phần khó nhất của bài toán RAG:

- retrieve đúng section cho các câu hỏi tổng hợp và adversarial
- giữ đúng nhiệm vụ khi người dùng cố lái sang yêu cầu ngoài phạm vi
- ổn định hơn ở lớp judge khi gặp câu trả lời “an toàn nhưng không trực tiếp”

Điểm tích cực là benchmark hiện tại đã làm lộ ra các điểm yếu này bằng số liệu cụ thể. Đây chính là giá trị lớn nhất của Evaluation Factory: giúp nhóm biết cần tối ưu ở đâu, thay vì chỉ nhìn vào cảm giác “agent trả lời có vẻ ổn”.
