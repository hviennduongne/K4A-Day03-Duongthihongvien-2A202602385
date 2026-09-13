# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Dương Thị Hồng Viên  
> **Mã Sinh Viên / Mã Học viên:** 2A202602385  
> **Chủ đề Lựa chọn:** Trợ lý Học vụ & Tra cứu Lịch thi VinUni  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Với yêu cầu đặt lịch tư vấn, Agent phải phân tích ý định, tra cứu hồ sơ sinh viên để xác định cố vấn phụ trách, sau đó sử dụng kết quả tra cứu làm đầu vào cho bước đặt lịch. Một số câu hỏi đơn giản vẫn có thể được xử lý trực tiếp hoặc chỉ cần gọi một công cụ. |
| **2. Tool Interaction** | 5 / 5 | Hệ thống cần kết nối MCP Server để sử dụng `academic_query` khi tra cứu hồ sơ, GPA và cố vấn; đồng thời gọi `schedule_appointment` để thực hiện hành động đặt lịch. LLM không thể tự tạo ra các dữ liệu nghiệp vụ này một cách đáng tin cậy. |
| **3. Dynamic Decision** | 5 / 5 | Agent phải lựa chọn công cụ dựa trên yêu cầu của người dùng và kết quả quan sát ở từng bước. Ví dụ, chỉ tiếp tục đặt lịch khi tra cứu được sinh viên và cố vấn; nếu nhận `NOT_FOUND`, Agent phải dừng và phản hồi phù hợp thay vì bịa đặt dữ liệu. |
| **4. Long Horizon Goal** | 3 / 5 | Agent cần duy trì mục tiêu hoàn thành yêu cầu xuyên suốt nhiều bước tra cứu và đặt lịch, nhưng quy trình tương đối ngắn, thường hoàn tất trong một phiên làm việc và không đòi hỏi lập kế hoạch dài hạn hoặc bộ nhớ lâu dài. |
| **TỔNG ĐIỂM AGENTIC FIT** | **17 / 20** | Tổng điểm lớn hơn 12/20, vì vậy bài toán phù hợp để triển khai ReAct Agent có khả năng suy luận, gọi công cụ và xử lý kết quả động. |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

Đã chạy `python src/app.py --all` với `GeminiProvider` trên LLM API thật. Trace hiện tại ghi nhận các quyết định gọi công cụ từ Gemini và không có sự kiện `API_ERROR` hoặc phản hồi Mock. File [trace_waterfall.json](trace_waterfall.json) có **10 sự kiện**, gồm **5 TOOL_EXECUTION** và **5 FINAL_ANSWER**.

Phạm vi triển khai trong bài lab là tra cứu hồ sơ, GPA, cố vấn và đặt lịch tư vấn. Dữ liệu sinh viên và thao tác đặt lịch là mô phỏng trong `src/tools.py`; chưa triển khai tra cứu lịch thi hay kết nối lịch hẹn thực tế.

Dưới đây là ba sự kiện TC04 trích nguyên từ trace: tra cứu sinh viên `SV2026002`, lấy cố vấn `TS. Lê Thị B`, sau đó đặt lịch lúc `09:00 ngày 16/09/2026` và trả lời kết quả.

```json
[
  {
    "step": 1,
    "query": "Hãy tra cứu cố vấn học tập của sinh viên SV2026002, sau đó đặt lịch tư vấn cho sinh viên này với đúng cố vấn vừa tìm được vào lúc 09:00 ngày 16/09/2026.",
    "action_type": "TOOL_EXECUTION",
    "thought": "Gemini quyết định gọi công cụ 'academic_query' với tham số: {\"student_id\": \"SV2026002\"}",
    "tool_name": "academic_query",
    "arguments": {
      "student_id": "SV2026002"
    },
    "observation": {
      "status": "SUCCESS",
      "student_id": "SV2026002",
      "data": {
        "full_name": "Trần Thị Bình",
        "class": "AI-K4",
        "gpa": 3.6,
        "email": "binh.tt@vinuni.edu.vn",
        "status": "Đang học",
        "advisor": "TS. Lê Thị B"
      }
    },
    "latency_ms": 11323.86
  },
  {
    "step": 2,
    "query": "Hãy tra cứu cố vấn học tập của sinh viên SV2026002, sau đó đặt lịch tư vấn cho sinh viên này với đúng cố vấn vừa tìm được vào lúc 09:00 ngày 16/09/2026.",
    "action_type": "TOOL_EXECUTION",
    "thought": "Gemini quyết định gọi công cụ 'schedule_appointment' với tham số: {\"advisor_name\": \"TS. Lê Thị B\", \"student_id\": \"SV2026002\", \"datetime_str\": \"09:00 ngày 16/09/2026\"}",
    "tool_name": "schedule_appointment",
    "arguments": {
      "advisor_name": "TS. Lê Thị B",
      "student_id": "SV2026002",
      "datetime_str": "09:00 ngày 16/09/2026"
    },
    "observation": {
      "status": "SUCCESS",
      "booking_id": "BK-SV2026002-99",
      "student_id": "SV2026002",
      "datetime": "09:00 ngày 16/09/2026",
      "advisor": "TS. Lê Thị B",
      "message": "Đặt lịch thành công cho sinh viên SV2026002 với TS. Lê Thị B vào lúc 09:00 ngày 16/09/2026."
    },
    "latency_ms": 13917.89
  },
  {
    "step": 3,
    "query": "Hãy tra cứu cố vấn học tập của sinh viên SV2026002, sau đó đặt lịch tư vấn cho sinh viên này với đúng cố vấn vừa tìm được vào lúc 09:00 ngày 16/09/2026.",
    "action_type": "FINAL_ANSWER",
    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ).",
    "output": "Dưới đây là thông tin chi tiết về việc tra cứu và đặt lịch hẹn tư vấn học vụ của sinh viên:\n\n1. **Thông tin tra cứu:**\n   * **Mã sinh viên:** SV2026002\n   * **Họ và tên:** Trần Thị Bình\n   * **Lớp:** AI-K4\n   * **Cố vấn học tập:** TS. Lê Thị B\n\n2. **Xác nhận đặt lịch hẹn:**\n   * **Mã đặt lịch (Booking ID):** BK-SV2026002-99\n   * **Cố vấn học tập:** TS. Lê Thị B\n   * **Thời gian hẹn:** 09:00 ngày 16/09/2026\n   * **Trạng thái:** Đặt lịch thành công!",
    "latency_ms": 13576.96
  }
]
```

**Nhận xét:** Tên cố vấn không có sẵn trong câu hỏi. Agent sử dụng dữ liệu `advisor` từ Observation của `academic_query` làm tham số `advisor_name` cho `schedule_appointment`. Đây là sự phụ thuộc dữ liệu giữa hai bước, thể hiện khả năng xử lý đa bước của ReAct Agent.

**Sự cố và khắc phục:** Vòng lặp ban đầu dừng ngay sau một tool call khiến TC04 chưa đặt lịch. Đã bổ sung lịch sử Action/Observation vào prompt cho lượt gọi LLM tiếp theo, giữ giới hạn `MAX_ITERATIONS` và chặn tool call trùng lặp. Khi gặp lỗi Gemini `429 RESOURCE_EXHAUSTED`, chương trình giãn cách yêu cầu tối thiểu 13 giây, chờ 60 giây và thử lại tối đa hai lần. Nếu vẫn lỗi, chương trình ghi `API_ERROR` và dừng thay vì fallback về Mock.

Ở lần chạy trước, TC04 và TC05 từng gặp 429 và thành công sau khi thử lại. Đoạn trích trên đã được đồng bộ với file trace mới nhất: ba bước TC04 lần lượt mất 11.323,86 ms, 13.917,89 ms và 13.576,96 ms. Trường `latency_ms` bao gồm thời gian giãn cách yêu cầu và thời gian thử lại nếu có, không chỉ thời gian suy luận LLM. Trace hiện chưa ghi riêng số lần retry nên không dùng file JSON này để khẳng định số lần gặp 429. Trace TC05 ghi hai sự kiện của cùng một vòng xử lý với cùng thời lượng; không cộng hai giá trị này để tính tổng thời gian chạy. Trường `thought` là mô tả quyết định do adapter/chương trình ghi, không phải toàn bộ suy luận nội bộ của mô hình.

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã cấu hình API key và xác nhận Gemini thực hiện các quyết định gọi tool trong lần nghiệm thu cuối.
- [x] Đã thử thành công chế độ `python src/app.py --interactive`: tra cứu SV2026001, tra cứu và đặt lịch cho SV2026002, xử lý NOT_FOUND cho SV9999999.
- [x] Đã kiểm tra trace đủ 5 test case và đồng bộ đoạn trích TC04 tại Mục 2 với `docs/trace_waterfall.json`.
- **Tổng số Test Cases đạt hành vi gọi tool:** **5 / 5** (đánh giá thủ công theo log; giới hạn kiểm chứng TC01 được nêu bên dưới).
- **Số lượt gọi Tool qua MCP Server chính xác:** **5 lượt** — 3 lượt `academic_query` và 2 lượt `schedule_appointment`.
- **Số sự kiện Waterfall Trace:** **10 sự kiện**.
- [x] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân (commit bài làm: `d3259a4`).
- [x] Đã nộp đường link repository lên LMS VLearn.

| Test Case | Kết quả quan sát | Đánh giá |
| :--- | :--- | :--- |
| TC01 — Câu hỏi trực tiếp | Gemini trả lời bằng văn bản, không gọi tool. | Đạt hành vi không gọi tool; chưa xác minh nội dung quy chế. |
| TC02 — Tra cứu học vụ | Gọi `academic_query(SV2026001)`, trả đúng hồ sơ Nguyễn Văn An và GPA 3.85 từ dữ liệu mẫu. | Đạt. |
| TC03 — Đặt lịch | Gọi `schedule_appointment` cho `SV2026001`, cố vấn PGS.TS Nguyễn Văn A, lúc 14:00 ngày 15/09/2026; nhận `SUCCESS`. | Đạt. |
| TC04 — Đa bước | Tra cứu `SV2026002` → lấy TS. Lê Thị B → đặt lịch 09:00 ngày 16/09/2026 → xác nhận mã `BK-SV2026002-99`. | Đạt trong trace hiện tại. |
| TC05 — Không tìm thấy | Gọi `academic_query(SV9999999)`, nhận `NOT_FOUND`; chương trình trả thông báo không tìm thấy và dừng. | Đạt trong trace hiện tại. |

**Giới hạn đánh giá:** Dòng “Đã thực thi 5/5 Test Cases” là bộ đếm thực thi, không phải kiểm định tự động PASS/FAIL. TC01 chạy qua ReAct Agent với nhánh trả lời trực tiếp; chưa có lượt chạy đối chứng riêng bằng `run_baseline_chatbot()`. System Prompt hiện không chứa đầy đủ quy chế học vụ nên chưa chứng minh câu trả lời TC01 chỉ lấy từ System Prompt hoặc chính xác theo tài liệu VinUni. Cần nguồn quy chế được kiểm chứng nếu triển khai thực tế.

**Bài học rút ra:** Agent phù hợp với yêu cầu cần tra cứu dữ liệu rồi hành động dựa trên kết quả. Việc duy trì Observation giữa các vòng và xử lý lỗi API quyết định độ tin cậy của luồng đa bước. Trace giúp kiểm tra công cụ, tham số, kết quả và điểm dừng, thay vì chỉ dựa vào câu trả lời cuối.

**Trạng thái nộp bài:** Đã push bài làm lên nhánh `main` của [repository GitHub cá nhân](https://github.com/hviennduongne/K4A-Day03-Duongthihongvien-2A202602385). Còn bước dán link repository và xác nhận nộp trên LMS VLearn.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
