# HCMUS-Wandora

Hệ thống lập kế hoạch chuyến đi theo Clean Architecture, xây trên FastAPI, SQLAlchemy, Pydantic và SQLite mặc định. Dự án hỗ trợ các luồng chính: tạo workspace, sinh lịch trình bằng GenAI, xem và chỉnh sửa lịch trình, thêm hoạt động thủ công, và điều chỉnh lịch trình bằng prompt tiếng Việt.

## Yêu Cầu

- Python 3.14+.
- Các thư viện được khai báo trong `requirements.txt`.
- Tùy chọn: `GEMINI_API_KEY` nếu muốn dùng Google Gemini thật, còn không hệ thống sẽ dùng dữ liệu fallback để demo.

## Cài Đặt

1. Tạo và kích hoạt virtual environment.
2. Cài dependencies.
3. Sao chép `.env.example` thành `.env` nếu muốn cấu hình môi trường riêng.

Ví dụ trên Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Cấu Hình

Các biến môi trường chính:

- `ENVIRONMENT`: môi trường chạy ứng dụng.
- `DEBUG`: bật hoặc tắt chế độ debug.
- `DATABASE_URL`: đường dẫn CSDL, mặc định là `sqlite:///./wandora.db`.
- `GEMINI_API_KEY`: khóa Gemini, để trống nếu chỉ muốn dùng fallback.
- `GEMINI_MODEL`: tên model Gemini, mặc định là `gemini-2.0-flash`.

## Chạy Ứng Dụng

Khởi động API bằng Uvicorn:

```powershell
uvicorn main:app --reload
```

Sau khi chạy, kiểm tra nhanh tại:

- `GET /health`
- `http://127.0.0.1:8000/docs`

## Kiểm Thử Demo

Script `demo_test.py` chạy luồng end-to-end gồm tạo workspace, sinh lịch trình, xem timeline, thêm hoạt động thủ công, cập nhật ghi chú và điều chỉnh lịch trình.

```powershell
python demo_test.py
```

## API Chính

### Workspace

- `POST /api/v1/workspaces`: tạo workspace chuyến đi.
- `GET /api/v1/workspaces/{workspace_id}/overview`: lấy tổng quan chuyến đi cho UI 5A/5B.
- `POST /api/v1/workspaces/{workspace_id}/generate-itinerary`: sinh lịch trình tự động.
- `GET /api/v1/workspaces/{workspace_id}/itinerary`: xem lịch trình dạng timeline/map.
- `POST /api/v1/workspaces/{workspace_id}/adjust-itinerary`: điều chỉnh lịch trình bằng prompt tiếng Việt.

### Itinerary

- `POST /api/v1/itineraries/activities`: thêm hoạt động thủ công, tự gắn `is_manual = True`.
- `PUT /api/v1/itineraries/activities/{activity_id}`: cập nhật hoạt động hiện có.

### Chat

- `POST /api/v1/chat/workspaces/{workspace_id}/messages`: ghi nhận tin nhắn của người dùng.

## Cấu Trúc Dự Án

```text
app/
├── api/
├── core/
├── db/
├── models/
├── schemas/
└── services/
main.py
demo_test.py
requirements.txt
.env.example
```

## Ghi Chú Triển Khai

- CSDL khởi tạo tự động khi ứng dụng start.
- Lớp AI có fallback nên demo vẫn chạy được khi chưa cấu hình Gemini.
- File test demo hiện là một script chạy bằng `python demo_test.py`, không phải test framework riêng.
