# Wandora Backend (FastAPI Service)

Backend dịch vụ cho ứng dụng lập kế hoạch du lịch thông minh Wandora, xây dựng bằng **FastAPI**, **SQLAlchemy 2.0**, **Alembic**, và tích hợp **Google Gemini AI**.

---

## 🚀 Tính năng & PA3 Use-Cases đã hoàn thành

Backend hỗ trợ đầy đủ 11/11 use-cases PA3:

1. **UC 2.1 Trip Creation & Preference Input**: Tạo workspace chuyến đi, lưu điểm đến, ngày đi/về và sở thích du lịch.
2. **UC 2.2 AI Itinerary Generator**: Tự động sinh lịch trình bằng Gemini AI (`gemini-1.5-flash`) bất đồng bộ kèm bộ sinh dự phòng (fallback).
3. **UC 2.3 AI Itinerary Adjustment**: Điều chỉnh lịch trình theo câu lệnh hướng dẫn của người dùng.
4. **UC 2.4 Manual Places & External Links**: Thêm/sửa địa điểm thủ công (`is_manual=True`), liên kết ngoài và ghi chú.
5. **UC 2.5 Group Collaboration**: Mời thành viên qua Email, xem danh sách và xóa thành viên khỏi chuyến đi.
6. **UC 2.6 Role & Permission Management**: Phân quyền vai trò người dùng (`owner`, `editor`, `viewer`, `member`).
7. **UC 2.7 AI Packing Suggestions**: Gợi ý danh sách đồ dùng hành lý phù hợp với điểm đến và thời gian chuyến đi.
8. **UC 2.8 Shared Luggage Planning**: Phân công người chuẩn bị đồ dùng hành lý dùng chung và tích cờ hoàn thành.
9. **UC 2.9 Manual Place Note Input**: Đính kèm ghi chú chi tiết cho từng địa điểm / hoạt động trong lịch trình.
10. **UC 2.10 Place Ratings & Reviews**: Đánh giá 1-5 sao và nhận xét địa điểm du lịch trong nhóm.
11. **UC 2.11 Share or Export Trip Plan**: Sinh link chia sẻ công khai xem Read-Only qua Token và Xuất kế hoạch ra dạng file **JSON** hoặc **Markdown**.

---

## 🛠️ Cấu trúc thư mục (`src/backend`)

```text
src/backend/
├── app/
│   ├── api/
│   │   ├── deps.py                 # Dependency helpers (DB session)
│   │   ├── router.py               # Tổng hợp tất cả API routers v1
│   │   └── v1/                     # Các endpoints API v1 (workspaces, itineraries, chat, collaboration, packing, reviews, share)
│   ├── core/
│   │   ├── config.py               # Cấu hình Pydantic BaseSettings & .env
│   │   ├── security.py             # Bảo mật
│   │   └── time_utils.py           # Bộ parser thời gian ISO 8601 & HH:MM safe
│   ├── db/
│   │   ├── base.py                 # SQLAlchemy DeclarativeBase
│   │   ├── init_db.py              # Hàm khởi tạo bảng CSDL
│   │   └── session.py              # Engine & SessionLocal (bật SQLite foreign_keys=ON)
│   ├── models/                     # Các mô hình dữ liệu SQLAlchemy (Workspace, Itinerary, User, Chat, Packing, Review)
│   ├── schemas/                    # Pydantic Schemas cho Request/Response validation
│   └── services/                   # Logic nghiệp vụ (ai_service, workspace_service, itinerary_service, collaboration_service, packing_service, review_service, share_service)
├── migrations/                     # Kịch bản Alembic DB migration
├── tests/                          # Bộ kiểm thử tự động pytest (11/11 tests pass)
├── alembic.ini                     # Cấu hình Alembic migration
├── main.py                         # Entry point ứng dụng
├── requirements.txt                # Thư viện phụ thuộc
└── README.md                       # Tài liệu Backend Runbook
```

---

## 💻 Hướng dẫn Chạy & Phát triển

### 1. Cài đặt môi trường

```bash
cd src/backend
pip install -r requirements.txt
```

### 2. Cấu hình biến môi trường (`.env`)

Tạo file `.env` từ `.env.example`:

```env
APP_NAME="Wandora Backend"
DEBUG=True
DATABASE_URL="sqlite:///./wandora.db"
GEMINI_API_KEY="your_gemini_api_key_here"
GEMINI_MODEL="gemini-1.5-flash"
```

*(Nếu không có `GEMINI_API_KEY`, ứng dụng sẽ tự động sử dụng bộ sinh dữ liệu dự phòng deterministic fallback mượt mà).*

### 3. Thực thi Database Migration (Alembic)

```bash
alembic upgrade head
```

### 4. Khởi chạy Uvicorn Server

```bash
uvicorn app.main:app --reload --port 8000
```

Truy cập tài liệu API tự động:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Chạy Kiểm thử Tự động (Pytest)

Chạy bộ kiểm thử tự động toàn bộ 11/11 use-cases:

```bash
pytest -v
```

Kết quả mong đợi:
```text
tests/test_chat.py::test_chat_flow PASSED
tests/test_collaboration.py::test_collaboration_flow PASSED
tests/test_health.py::test_health_endpoint PASSED
tests/test_integrity.py::test_sqlite_foreign_keys_cascade PASSED
tests/test_integrity.py::test_unique_constraint_workspace_day_index PASSED
tests/test_integrity.py::test_parse_time_safe_utils PASSED
tests/test_itineraries.py::test_itinerary_lifecycle_and_hardening PASSED
tests/test_packing.py::test_packing_and_luggage_planning PASSED
tests/test_reviews.py::test_place_reviews PASSED
tests/test_share.py::test_share_and_export_flow PASSED
tests/test_workspaces.py::test_create_and_get_workspace PASSED

11 passed in 0.26s
```
