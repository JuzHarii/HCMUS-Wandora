# TỔNG QUAN TÀI LIỆU HƯỚNG DẪN KIẾN TRÚC, CÁC HÀM VÀ 11 USE CASES (BACKEND WANDORA)

> **Ghi chú nội bộ:** Tài liệu này tổng hợp toàn bộ **11 Use Cases (UC 2.1 -> UC 2.11)** theo đúng chuẩn yêu cầu kỹ thuật PA3, cùng các **File API**, **File Service** và **Công dụng cụ thể của từng Hàm** trong hệ thống backend của Wandora.

---

## 📋 1. BẢNG MAPPING 11 USE CASES (PA3) -> FILE API -> FILE SERVICE -> CÁC HÀM XỬ LÝ

| UC Code | Tên Use Case (Kịch bản sử dụng) | Endpoint / File API | File Service phụ trách | Các hàm chính được thực thi |
|---|---|---|---|---|
| **UC 2.1** | **Trip Creation & Preference Input**<br>*(Tạo chuyến đi & Nhập sở thích)* | workspaces.py | workspace_service.py | `create_workspace`, `list_workspaces`, `get_workspace`, `get_trip_overview` |
| **UC 2.2** | **AI Itinerary Generator**<br>*(Tự động sinh lịch trình bằng AI)* | workspaces.py<br>itineraries.py | itinerary_service.py<br>ai_service.py | `generate_itinerary_draft`, `_persist_generated_itinerary`, `_generate_with_gemini`, `_fallback_draft` |
| **UC 2.3** | **AI Itinerary Adjustment**<br>*(Điều chỉnh lịch trình bằng AI)* | workspaces.py | itinerary_service.py<br>ai_service.py | `adjust_itinerary`, `generate_itinerary_draft` (AI) |
| **UC 2.4** | **Manual Places & External Links**<br>*(Thêm/Sửa điểm du lịch & link ngoài)* | itineraries.py | itinerary_service.py | `add_activity` (cưỡng chế `is_manual=True`), `update_activity`, `get_itinerary` |
| **UC 2.5** | **Group Collaboration**<br>*(Mời & Cộng tác nhóm)* | collaboration.py | collaboration_service.py | `invite_member`, `list_members`, `remove_member` |
| **UC 2.6** | **Role & Permission Management**<br>*(Quản lý phân quyền Owner/Editor/Viewer)* | collaboration.py | collaboration_service.py | `update_member_role`, `list_members` |
| **UC 2.7** | **AI Packing Suggestions**<br>*(Gợi ý danh sách hành lý bằng AI)* | packing.py | packing_service.py | `generate_packing_suggestions` |
| **UC 2.8** | **Shared Luggage Planning**<br>*(Quản lý & Phân công hành lý dùng chung)* | packing.py | packing_service.py | `list_packing_items`, `add_packing_item`, `update_packing_item`, `assign_or_toggle_item`, `delete_packing_item` |
| **UC 2.9** | **Manual Place Note Input**<br>*(Ghi chú & Đánh giá cá nhân cho địa điểm)* | reviews.py | review_service.py | `create_or_update_review`, `list_workspace_reviews` |
| **UC 2.10**| **Place Ratings & Reviews**<br>*(Chấm điểm sao & Nhận xét địa điểm)* | reviews.py | review_service.py | `create_or_update_review`, `list_workspace_reviews` |
| **UC 2.11**| **Share or Export Trip Plan**<br>*(Chia sẻ link công khai & Xuất file)* | share.py | share_service.py | `create_share_link`, `get_workspace_by_share_token`, `export_trip_plan` |

---

## 🔍 2. CHI TIẾT CÔNG DỤNG VÀ LUỒNG CHẠY CỦA TOÀN BỘ 11 USE CASES

### 🔹 UC 2.1: Trip Creation & Preference Input (Tạo Chuyến Đi & Nhập Sở Thích)
* **Mục tiêu:** Cho phép người dùng tạo một chuyến đi mới, cung cấp điểm đến, ngày bắt đầu, ngày kết thúc và tùy chọn sở thích (JSON).
* **File API:** workspaces.py
* **File Service:** workspace_service.py
* **Các hàm liên quan:**
  * `create_workspace(db, payload)`: Tạo record `Workspace` mới vào CSDL với tiêu đề, điểm đến, thời gian và sở thích dạng JSON (`preferences_json`).
  * `list_workspaces(db, skip, limit)`: Lấy danh sách tất cả các chuyến đi hiện có.
  * `get_workspace(db, workspace_id)`: Kiểm tra sự tồn tại và lấy chi tiết chuyến đi.
  * `get_trip_overview(db, workspace_id)`: Tổng hợp các con số tổng quan (số ngày, số hoạt động, số thành viên, số lượng hành lý).

---

### 🔹 UC 2.2: AI Itinerary Generator (Tự Động Sinh Lịch Trình Bằng AI)
* **Mục tiêu:** Tự động sinh ra bản nháp lịch trình hoàn chỉnh phân chia theo từng ngày và mốc thời gian.
* **File API:** workspaces.py
* **File Service:** itinerary_service.py & ai_service.py
* **Các hàm liên quan:**
  * `ai_service._generate_with_gemini(...)`: Gửi yêu cầu Async HTTP tới Gemini API để tạo danh sách ngày và hoạt động dưới dạng JSON.
  * `ai_service._fallback_draft(...)`: Bộ sinh dự phòng tĩnh (rule-based) nếu không có API key hoặc kết nối AI thất bại.
  * `itinerary_service.generate_itinerary_draft(db, workspace_id, force_regenerate)`: Kích hoạt AI tạo bản nháp và gọi `_persist_generated_itinerary`.
  * `itinerary_service._persist_generated_itinerary(...)`: Ghi dữ liệu ngày (`ItineraryDay`) và hoạt động (`ItineraryActivity`) vào CSDL trong một **Atomic Transaction**.

---

### 🔹 UC 2.3: AI Itinerary Adjustment (Điều Chỉnh Lịch Trình Bằng Câu Lệnh AI)
* **Mục tiêu:** Nhận hướng dẫn thay đổi từ người dùng (vd: "Muốn tham quan chợ đêm vào tối Ngày 2") để AI cập nhật lại lịch trình.
* **File API:** workspaces.py (`POST /workspaces/{id}/adjust-itinerary`)
* **File Service:** itinerary_service.py & ai_service.py
* **Các hàm liên quan:**
  * `itinerary_service.adjust_itinerary(db, workspace_id, instruction)`: Đóng gói câu lệnh chỉ dẫn của người dùng, gọi `ai_service.generate_itinerary_draft` kèm yêu cầu điều chỉnh.
  * `itinerary_service._persist_generated_itinerary(db, workspace_id, days_data, keep_manual=True)`: Lưu lại lịch trình mới nhưng **giữ nguyên toàn bộ các hoạt động do người dùng tự thêm thủ công** (`is_manual=True`).

---

### 🔹 UC 2.4: Manual Places & External Links (Thêm/Sửa Điểm Du Lịch Thủ Công)
* **Mục tiêu:** Người dùng tự thêm hoặc chỉnh sửa thủ công điểm tham quan, giờ giấc, địa chỉ, liên kết bên ngoài (Google Maps, v.v.).
* **File API:** itineraries.py
* **File Service:** itinerary_service.py
* **Các hàm liên quan:**
  * `add_activity(db, payload)`: Thêm một hoạt động thủ công vào 1 ngày trong lịch trình (bắt buộc đánh dấu `is_manual=True`).
  * `update_activity(db, activity_id, payload)`: Cập nhật tiêu đề, khung giờ, địa điểm, ghi chú hoặc URL liên kết ngoài.
  * `get_itinerary(db, workspace_id)`: Truy vấn toàn bộ lịch trình hiển thị trên giao diện.

---

### 🔹 UC 2.5: Group Collaboration (Mời & Cộng Tác Nhóm)
* **Mục tiêu:** Mời bạn bè cùng tham gia vào chuyến đi để xem và cập nhật kế hoạch.
* **File API:** collaboration.py
* **File Service:** collaboration_service.py
* **Các hàm liên quan:**
  * `invite_member(db, workspace_id, email, role)`: Mời thành viên mới gia nhập chuyến đi qua email.
  * `list_members(db, workspace_id)`: Xem danh sách tất cả các thành viên hiện tại trong chuyến đi.
  * `remove_member(db, workspace_id, user_id)`: Xóa một thành viên ra khỏi không gian chuyến đi.

---

### 🔹 UC 2.6: Role & Permission Management (Phân Quyền Thành Viên)
* **Mục tiêu:** Quản lý quyền hạn của từng thành viên (`owner` - Chủ sở hữu, `editor` - Người chỉnh sửa, `viewer` - Người chỉ xem).
* **File API:** collaboration.py (`PUT /{workspace_id}/members/{user_id}`)
* **File Service:** collaboration_service.py
* **Các hàm liên quan:**
  * `update_member_role(db, workspace_id, user_id, new_role)`: Cập nhật vai trò/quyền hạn của một thành viên trong CSDL.

---

### 🔹 UC 2.7: AI Packing Suggestions (AI Gợi Ý Danh Sách Hành Lý)
* **Mục tiêu:** Phân tích điểm đến và thời gian chuyến đi để AI đề xuất danh sách đồ dùng cá nhân, giấy tờ, thuốc men cần mang theo.
* **File API:** packing.py (`POST /workspaces/{id}/packing/suggestions`)
* **File Service:** packing_service.py
* **Các hàm liên quan:**
  * `generate_packing_suggestions(db, workspace_id)`: Tự động phân tích profile chuyến đi và tạo các món đồ mẫu theo từng danh mục (Giấy tờ, Quần áo, Đồ cá nhân).

---

### 🔹 UC 2.8: Shared Luggage Planning (Chuẩn Bị Hành Lý Dùng Chung)
* **Mục tiêu:** Quản lý danh sách đồ dùng chung (vd: lều trại, máy ảnh), phân công thành viên chịu trách nhiệm và tích chọn khi đã chuẩn bị xong.
* **File API:** packing.py
* **File Service:** packing_service.py
* **Các hàm liên quan:**
  * `list_packing_items(db, workspace_id)`: Lấy toàn bộ danh sách món đồ trong hành lý.
  * `add_packing_item(db, workspace_id, payload)`: Thêm một vật dụng mới.
  * `update_packing_item(db, item_id, payload)`: Cập nhật tên món đồ, số lượng, danh mục.
  * `assign_or_toggle_item(db, item_id, user_id, is_checked)`: Phân công người chịu trách nhiệm hoặc đánh dấu hoàn thành (`is_checked=True`).
  * `delete_packing_item(db, item_id)`: Xóa món đồ khỏi danh sách.

---

### 🔹 UC 2.9: Manual Place Note Input (Ghi Chú & Đánh Giá Cá Nhân Địa Điểm)
* **Mục tiêu:** Đính kèm ghi chú, mẹo nhỏ hoặc lưu ý cá nhân cho từng điểm đến trong chuyến đi.
* **File API:** reviews.py & itineraries.py
* **File Service:** review_service.py
* **Các hàm liên quan:**
  * `create_or_update_review(db, workspace_id, payload)`: Lưu thông tin ghi chú/nhận xét của người dùng cho một địa điểm.
  * `list_workspace_reviews(db, workspace_id, place_name)`: Xem các ghi chú địa điểm trong workspace.

---

### 🔹 UC 2.10: Place Ratings & Reviews (Chấm Điểm Sao & Nhận Xét Địa Điểm)
* **Mục tiêu:** Cho phép các thành viên chấm điểm sao (1 - 5 stars) và viết đánh giá kinh nghiệm cho các địa điểm tham quan / ăn uống.
* **File API:** reviews.py
* **File Service:** review_service.py
* **Các hàm liên quan:**
  * `create_or_update_review(db, workspace_id, payload)`: Tạo mới hoặc cập nhật điểm đánh giá (`rating`) và bài viết nhận xét (`comment`).
  * `list_workspace_reviews(db, workspace_id, place_name)`: Lấy danh sách bài đánh giá đã lưu trong workspace.

---

### 🔹 UC 2.11: Share or Export Trip Plan (Chia Sẻ & Xuất Kế Hoạch Chuyến Đi)
* **Mục tiêu:** Tạo đường dẫn chia sẻ xem trực tuyến cho người ngoài không cần tài khoản, hoặc xuất kế hoạch ra file Markdown/JSON.
* **File API:** share.py
* **File Service:** share_service.py
* **Các hàm liên quan:**
  * `create_share_link(db, workspace_id)`: Sinh token chia sẻ công khai ngẫu nhiên và lưu vào CSDL.
  * `get_workspace_by_share_token(db, token)`: Tra cứu toàn bộ lịch trình chuyến đi thông qua token chia sẻ mà không cần đăng nhập.
  * `export_trip_plan(db, workspace_id, export_format)`: Tổng hợp dữ liệu chuyến đi và chuyển đổi sang định dạng văn bản **Markdown** đẹp mắt hoặc file **JSON** để tải xuống.
