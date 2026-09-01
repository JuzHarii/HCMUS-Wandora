from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.workspace import InviteToken
from .itinerary_service import get_itinerary
from .workspace_service import get_workspace


def create_share_link(db: Session, workspace_id: Any) -> dict[str, Any]:
    """
    Sinh token và đường dẫn chia sẻ liên kết cho chuyến đi (PA3 2.11).

    Công dụng:
    - Kiểm tra workspace tồn tại.
    - Sinh mã ngẫu nhiên bảo mật (UUID token).
    - Lưu vào bảng `invite_tokens`.
    - Trả về đường dẫn chia sẻ cho người dùng ngoài truy cập mà không cần tài khoản.
    """
    _ = get_workspace(db, workspace_id)

    token_str = uuid.uuid4().hex[:16]
    invite_token = InviteToken(workspace_id=str(workspace_id), token=token_str)
    db.add(invite_token)
    db.commit()
    db.refresh(invite_token)

    share_url = f"/api/v1/share/{token_str}"
    return {
        "share_url": share_url,
        "token": token_str,
        "expires_at": invite_token.expires_at,
    }


def get_workspace_by_share_token(db: Session, token: str) -> dict[str, Any]:
    """
    Cho phép truy cập xem lịch trình chuyến đi dạng Read-Only thông qua Token chia sẻ công khai.
    """
    invite_token = db.query(InviteToken).filter(InviteToken.token == token).first()
    if not invite_token:
        raise HTTPException(status_code=404, detail="Liên kết chia sẻ không tồn tại hoặc đã hết hạn")

    return get_itinerary(db, invite_token.workspace_id)


def export_trip_plan(db: Session, workspace_id: Any, export_format: str = "markdown") -> dict[str, Any]:
    """
    Xuất kế hoạch chuyến đi ra dạng chuỗi định dạng Markdown hoặc JSON (PA3 2.11).

    Công dụng:
    - Lấy toàn bộ thông tin chuyến đi và các ngày/hoạt động.
    - Nếu `export_format == "json"`: Đóng gói dưới dạng JSON chuẩn.
    - Nếu `export_format == "markdown"`: Dựng một văn bản Markdown hoàn chỉnh với tiêu đề, danh sách ngày và chi tiết thời gian/địa điểm.
    """
    ws = get_workspace(db, workspace_id)

    # UC 2.14 Draft Guard: chỉ cho phép xuất kế hoạch khi chuyến đi ở trạng thái "Planned"
    if getattr(ws, "status", None) not in ("Planned", "planned"):
        raise HTTPException(
            status_code=403,
            detail="Draft status: Chỉ có thể xuất kế hoạch khi chuyến đi ở trạng thái 'Planned'. Vui lòng xác nhận lịch trình trước.",
        )

    itin = get_itinerary(db, workspace_id)

    fmt_clean = export_format.lower().strip()

    if fmt_clean == "json":
        export_content = json.dumps(
            {
                "workspace_id": ws.id,
                "title": ws.title,
                "destination": ws.destination,
                "start_date": ws.start_date.isoformat() if ws.start_date else None,
                "end_date": ws.end_date.isoformat() if ws.end_date else None,
                "days": [
                    {
                        "day_index": d.day_index,
                        "date": d.date_value.isoformat() if d.date_value else None,
                        "title": d.title,
                        "activities": [
                            {
                                "title": a.title,
                                "start_time": a.start_time.strftime("%H:%M") if a.start_time else None,
                                "end_time": a.end_time.strftime("%H:%M") if a.end_time else None,
                                "location": a.location_name,
                                "notes": a.notes,
                            }
                            for a in d.activities
                        ],
                    }
                    for d in itin["days"]
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    else:
        fmt_clean = "markdown"
        md_lines = [
            f"# Kế hoạch chuyến đi: {ws.title}",
            f"- **Điểm đến**: {ws.destination or 'Chưa xác định'}",
            f"- **Thời gian**: {ws.start_date or 'N/A'} -> {ws.end_date or 'N/A'}",
            "",
            "---",
            "",
        ]

        for d in itin["days"]:
            md_lines.append(f"## {d.title or f'Ngày {d.day_index}'}")
            if d.date_value:
                md_lines.append(f"*Ngày: {d.date_value}*")
            md_lines.append("")

            if not d.activities:
                md_lines.append("_Chưa có hoạt động nào._")
            else:
                for a in d.activities:
                    time_str = ""
                    if a.start_time and a.end_time:
                        time_str = f"[{a.start_time.strftime('%H:%M')} - {a.end_time.strftime('%H:%M')}] "
                    elif a.start_time:
                        time_str = f"[{a.start_time.strftime('%H:%M')}] "

                    loc_str = f" (Địa điểm: {a.location_name})" if a.location_name else ""
                    note_str = f" - *{a.notes}*" if a.notes else ""

                    md_lines.append(f"- **{time_str}{a.title}**{loc_str}{note_str}")
            md_lines.append("")

        export_content = "\n".join(md_lines)

    return {
        "workspace_id": ws.id,
        "title": ws.title,
        "format": fmt_clean,
        "content": export_content,
    }
