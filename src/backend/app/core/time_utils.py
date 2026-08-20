from datetime import date, datetime, time


def parse_time_safe(val: str | time | None) -> time | None:
    """
    Chuyển đổi an toàn các định dạng chuỗi thời gian ("HH:MM" hoặc "HH:MM:SS") thành đối tượng `datetime.time`.

    Công dụng:
    - Tránh các ngoại lệ ngắt đột ngột (Unhandled Exception) khi người dùng truyền chuỗi sai định dạng.
    - Hỗ trợ cả hai định dạng `HH:MM` và `HH:MM:SS`.
    - Trả về `None` nếu chuỗi không hợp lệ thay vì làm ngắt ứng dụng.
    """
    if val is None:
        return None
    if isinstance(val, time):
        return val
    if not isinstance(val, str):
        return None
    val_clean = val.strip()
    if not val_clean:
        return None

    parts = val_clean.split(":")
    if len(parts) >= 2:
        try:
            hour = int(parts[0])
            minute = int(parts[1])
            second = int(parts[2]) if len(parts) > 2 else 0
            if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59:
                return time(hour, minute, second)
        except ValueError:
            pass
    return None


def format_time_safe(val: time | None) -> str | None:
    """
    Chuyển đổi đối tượng `datetime.time` thành chuỗi định dạng tiêu chuẩn "HH:MM".

    Công dụng:
    - Đảm bảo tính đồng nhất định dạng dữ liệu trả về cho phía Frontend.
    """
    if val is None:
        return None
    return val.strftime("%H:%M")


def parse_date_safe(val: str | date | None) -> date | None:
    """
    Chuyển đổi an toàn chuỗi ngày ISO 8601 ("YYYY-MM-DD") hoặc đối tượng `datetime` thành `datetime.date`.

    Công dụng:
    - Xử lý các đầu vào ngày linh hoạt từ request API hoặc từ phản hồi AI.
    - Ngăn chặn lỗi timezone shift (UTC+7) bằng cách chỉ lưu trữ thuần túy giá trị Ngày (`date`).
    """
    if val is None:
        return None
    if isinstance(val, date):
        return val
    if isinstance(val, datetime):
        return val.date()
    if not isinstance(val, str):
        return None
    val_clean = val.strip()
    if not val_clean:
        return None

    try:
        return date.fromisoformat(val_clean)
    except ValueError:
        return None
