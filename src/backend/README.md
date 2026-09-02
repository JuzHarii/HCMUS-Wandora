# Wandora Backend (FastAPI Service)

Backend dịch vụ cho ứng dụng lập kế hoạch du lịch thông minh Wandora, xây dựng bằng **FastAPI**, **SQLAlchemy 2.0**, **Alembic**, và tích hợp dịch vụ AI kèm fallback deterministic cho môi trường local/test.

---

## 🚀 Tính năng & PA3 Use-Cases đã hoàn thành

Backend hỗ trợ đầy đủ 11/11 use-cases PA3:

1. **UC 2.1 Trip Creation & Preference Input**: Tạo workspace chuyến đi, lưu điểm đến, ngày đi/về và sở thích du lịch.
2. **UC 2.2 AI Itinerary Generator**: Tự động sinh lịch trình bằng dịch vụ AI bất đồng bộ kèm bộ sinh dự phòng deterministic fallback.
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
├── alembic.ini                     # Cấu hình Alembic migration
├── main.py                         # Entry point ứng dụng
├── requirements.txt                # Thư viện phụ thuộc
└── README.md                       # Tài liệu Backend Runbook
```

---

## 💻 Hướng dẫn Chạy Backend

Các lệnh dưới đây nên chạy từ **repository root** để Alembic, Uvicorn và file `.env` dùng cùng một đường dẫn.

### 1. Clone repository và tạo virtual environment

```powershell
git clone https://github.com/JuzHarii/HCMUS-Wandora.git
cd HCMUS-Wandora
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r src/backend/requirements.txt
```

Nếu repository đã được clone rồi, bắt đầu từ `cd HCMUS-Wandora`. Nếu `py -3.11` không có trên máy, dùng `python -m venv .venv`.

### 2. Cấu hình biến môi trường (`.env`)

Backend đọc file `.env` ở repository root. Tạo file này từ `.env.example`:

```powershell
Copy-Item .env.example .env
```

Với local testing đơn giản, đặt:

```env
DATABASE_URL=sqlite:///./wandora.db
```

Nếu dùng Supabase/PostgreSQL, thay placeholder `DATABASE_URL` trong `.env.example` bằng connection string thật trước khi chạy migration. Cập nhật thêm `JWT_SECRET_KEY` bằng chuỗi ngẫu nhiên ít nhất 32 ký tự. Không dùng production data cho E2E tests.

### 3. Thực thi Database Migration (Alembic)

```powershell
python -m alembic -c src/backend/alembic.ini upgrade heads
```

Repository này có thể có nhiều Alembic heads, vì vậy dùng `upgrade heads` thay vì `upgrade head`.

### 4. Khởi chạy Uvicorn Server

```powershell
python -m uvicorn --app-dir src/backend main:app --reload --port 8000
```

Backend sẵn sàng khi terminal hiển thị `Application startup complete.`

Truy cập tài liệu API tự động:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Database Health Check**: [http://localhost:8000/health/db](http://localhost:8000/health/db)

---

## 🧪 Chạy Kiểm thử

PA5 automated Selenium tests nằm ở `tests/e2e` và cần chạy cả backend + frontend. Xem hướng dẫn chi tiết tại:

- [`../../tests/e2e/README.md`](../../tests/e2e/README.md)

Nếu chỉ muốn kiểm tra backend health sau khi server chạy:

```text
http://localhost:8000/health
http://localhost:8000/health/db
```
