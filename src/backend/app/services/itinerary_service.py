from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any

from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.orm import Session

from ..core.time_utils import parse_date_safe, parse_time_safe
from ..models.itinerary import ItineraryActivity, ItineraryDay
from ..models.workspace import Workspace
from ..schemas.itinerary import ItineraryActivityCreate, ItineraryActivityUpdate
from . import ai_service
from .workspace_service import get_workspace


def get_itinerary(db: Session, workspace_id: int) -> dict[str, Any]:
    """
    Truy vấn toàn bộ cây lịch trình (gồm danh sách các ngày và các hoạt động) của workspace.

    Công dụng:
    - Kiểm tra sự tồn tại của workspace.
    - Truy vấn danh sách `ItineraryDay` sắp xếp tăng dần theo `day_index`.
    - Trả về đối tượng dict tương thích với `ItineraryResponse` schema.
    """
    _ = get_workspace(db, workspace_id)  # Xác thực workspace có tồn tại hay không

    days = (
        db.query(ItineraryDay)
        .filter(ItineraryDay.workspace_id == workspace_id)
        .order_by(ItineraryDay.day_index.asc())
        .all()
    )

    return {"workspace_id": workspace_id, "days": days}


def _persist_generated_itinerary(
    db: Session,
    workspace_id: int,
    days_data: list[dict[str, Any]],
    keep_manual: bool = True,
) -> dict[str, Any]:
    """
    Lưu trữ danh sách lịch trình (Days & Activities) vào CSDL trong 1 Transaction nguyên tử (Atomic Transaction).

    Công dụng & Cơ chế hoạt động:
    - Đảm bảo tính toàn vẹn dữ liệu (Sprint 2 requirement):
      + Nếu `keep_manual=True`: Chỉ xóa các hoạt động do AI sinh ra (`is_manual == False`),
        bảo tồn toàn bộ hoạt động thủ công mà người dùng đã tự thêm trước đó (`is_manual == True`).
      + Nếu `keep_manual=False`: Xóa toàn bộ lịch trình cũ để tái thiết lập từ đầu.
    - Duyệt qua từng ngày trong `days_data`, tìm hoặc tạo đối tượng `ItineraryDay`.
    - Thêm danh sách `ItineraryActivity` tương ứng với mỗi ngày.
    - Toàn bộ thao tác thực hiện trong một khối try/except:
      + Thành công: Gọi `db.commit()` để ghi nhận toàn bộ vào CSDL.
      + Thất bại: Tự động gọi `db.rollback()` để hủy bỏ mọi thay đổi dở dang, ngăn ngừa dữ liệu rác.
    """
    ws = get_workspace(db, workspace_id)
    ws.status = "Planned"


    try:
        if keep_manual:
            # Lấy tất cả các ngày hiện có trong workspace
            existing_days = db.query(ItineraryDay).filter(ItineraryDay.workspace_id == workspace_id).all()
            for day in existing_days:
                # Chỉ xóa các hoạt động do AI tạo ra (is_manual == False)
                db.query(ItineraryActivity).filter(
                    ItineraryActivity.day_id == day.id, ItineraryActivity.is_manual == False
                ).delete(synchronize_session=False)
        else:
            # Xóa sạch toàn bộ ngày và hoạt động
            db.query(ItineraryDay).filter(ItineraryDay.workspace_id == workspace_id).delete(synchronize_session=False)

        # Thêm mới các ngày và hoạt động từ danh sách days_data
        for d_data in days_data:
            day_idx = d_data.get("day_index", 1)
            day_title = d_data.get("title", f"Ngày {day_idx}")

            # Định dạng ngày date_value
            date_val = parse_date_safe(d_data.get("date_value"))
            if not date_val and ws.start_date:
                date_val = ws.start_date + timedelta(days=day_idx - 1)

            # Tìm ngày đã tồn tại hoặc tạo mới
            day_obj = (
                db.query(ItineraryDay)
                .filter(ItineraryDay.workspace_id == workspace_id, ItineraryDay.day_index == day_idx)
                .first()
            )
            if not day_obj:
                day_obj = ItineraryDay(
                    workspace_id=workspace_id,
                    day_index=day_idx,
                    date_value=date_val,
                    title=day_title,
                )
                db.add(day_obj)
                db.flush()  # Sinh ID tự động cho day_obj

            activities_list = d_data.get("activities", [])
            for idx, act_data in enumerate(activities_list, start=1):
                s_time = parse_time_safe(act_data.get("start_time"))
                e_time = parse_time_safe(act_data.get("end_time"))
                order_idx = act_data.get("order_index", idx)

                act_obj = ItineraryActivity(
                    day_id=day_obj.id,
                    title=act_data.get("title", "Hoạt động"),
                    start_time=s_time,
                    end_time=e_time,
                    location_name=act_data.get("location_name"),
                    notes=act_data.get("notes"),
                    external_url=act_data.get("external_url"),
                    is_manual=False,  # Đánh dấu do AI sinh ra
                    order_index=order_idx,
                )
                db.add(act_obj)

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu lịch trình vào CSDL: {str(e)}") from e

    return get_itinerary(db, workspace_id)


async def generate_itinerary_draft(db: Session, workspace_id: int, force_regenerate: bool = False) -> dict[str, Any]:
    """
    Sinh bản nháp lịch trình mới hoặc trả về lịch trình hiện có.

    Công dụng & Cơ chế hoạt động:
    - Nếu đã có lịch trình trong CSDL và `force_regenerate == False`: Trả về ngay lịch trình hiện có
      mà không tốn tài nguyên gọi lại Gemini AI (Tối ưu hóa hiệu năng & giảm chi phí API).
    - Nếu `force_regenerate == True` hoặc chưa có lịch trình:
      + Đọc thông tin destination, start_date, end_date và preferences từ workspace.
      + Gọi `ai_service.generate_itinerary_draft` để sinh danh sách ngày/hoạt động.
      + Lưu vào CSDL thông qua `_persist_generated_itinerary`.
    """
    ws = get_workspace(db, workspace_id)

    # Đã có lịch trình và không yêu cầu sinh lại bắt buộc
    existing_days = db.query(ItineraryDay).filter(ItineraryDay.workspace_id == workspace_id).all()
    if existing_days and not force_regenerate:
        return get_itinerary(db, workspace_id)

    preferences = json.loads(ws.preferences_json) if ws.preferences_json else {}

    days_data = await ai_service.generate_itinerary_draft(
        destination=ws.destination,
        start_date=ws.start_date,
        end_date=ws.end_date,
        preferences=preferences,
    )

    return _persist_generated_itinerary(db, workspace_id, days_data, keep_manual=True)


async def adjust_itinerary(db: Session, workspace_id: int, instruction: str) -> dict[str, Any]:
    """
    Điều chỉnh lịch trình hiện tại dựa trên câu lệnh hướng dẫn của người dùng (ví dụ: "thêm hoạt động mua sắm chiều ngày 2").

    Công dụng:
    - Truy vấn lịch trình hiện có làm ngữ cảnh cho AI.
    - Truyền hướng dẫn điều chỉnh `instruction` và `existing_itinerary` sang `ai_service`.
    - Sinh lại lịch trình mới phù hợp với yêu cầu điều chỉnh.
    - Cập nhật CSDL và giữ nguyên các hoạt động do người dùng tự thêm (`keep_manual=True`).
    """
    ws = get_workspace(db, workspace_id)
    preferences = json.loads(ws.preferences_json) if ws.preferences_json else {}

    # Lấy lịch trình hiện tại làm ngữ cảnh cho AI
    current_itin = get_itinerary(db, workspace_id)
    existing_days_data = []
    for day in current_itin.get("days", []):
        existing_days_data.append({
            "day_index": day.day_index,
            "title": day.title,
            "activities": [
                {
                    "title": act.title,
                    "start_time": act.start_time,
                    "end_time": act.end_time,
                    "location_name": act.location_name,
                    "notes": act.notes,
                    "is_manual": act.is_manual,
                }
                for act in day.activities
            ]
        })

    days_data = await ai_service.generate_itinerary_draft(
        destination=ws.destination,
        start_date=ws.start_date,
        end_date=ws.end_date,
        preferences=preferences,
        adjustment_instruction=instruction,
        existing_itinerary=existing_days_data,
    )

    return _persist_generated_itinerary(db, workspace_id, days_data, keep_manual=True)



def add_activity(db: Session, payload: ItineraryActivityCreate) -> ItineraryActivity:
    """
    Thêm một hoạt động mới do người dùng tự nhập thủ công.

    Công dụng & Cơ chế hardening:
    - Bắt buộc gắn cờ `is_manual = True` (Sprint 2 Requirement) để phân biệt với các hoạt động do AI tự động sinh.
    - Tự động liên kết hoặc khởi tạo `ItineraryDay` tương ứng nếu truyền `(workspace_id, day_index)` thay vì `day_id`.
    - Chuyển đổi thời gian an toàn (`parse_time_safe`) tránh các lỗi định dạng chuỗi.
    """
    day_id = payload.day_id

    if not day_id:
        if payload.workspace_id and payload.day_index:
            day_obj = (
                db.query(ItineraryDay)
                .filter(
                    ItineraryDay.workspace_id == payload.workspace_id,
                    ItineraryDay.day_index == payload.day_index,
                )
                .first()
            )
            if not day_obj:
                day_obj = ItineraryDay(
                    workspace_id=payload.workspace_id,
                    day_index=payload.day_index,
                    title=f"Ngày {payload.day_index}",
                )
                db.add(day_obj)
                db.flush()
            day_id = day_obj.id
        else:
            raise HTTPException(status_code=422, detail="Cần cung cấp day_id hoặc bộ (workspace_id, day_index)")

    day_obj = db.query(ItineraryDay).filter(ItineraryDay.id == day_id).first()
    if not day_obj:
        raise HTTPException(status_code=404, detail="Không tìm thấy ngày trong lịch trình (Itinerary Day not found)")

    activity = ItineraryActivity(
        day_id=day_id,
        title=payload.title,
        start_time=parse_time_safe(payload.start_time),
        end_time=parse_time_safe(payload.end_time),
        location_name=payload.location_name,
        notes=payload.notes,
        external_url=payload.external_url,
        is_manual=True,  # Yêu cầu Sprint 2: Cưỡng chế is_manual = True
        order_index=payload.order_index,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def update_activity(db: Session, activity_id: int, payload: ItineraryActivityUpdate) -> ItineraryActivity:
    """
    Cập nhật thông tin chi tiết của một hoạt động đã tồn tại.

    Công dụng:
    - Tìm hoạt động theo `activity_id`, ném lỗi 404 nếu không tìm thấy.
    - Cập nhật các trường được truyền tới (title, start_time, end_time, location_name, notes, external_url, order_index).
    """
    act = db.query(ItineraryActivity).filter(ItineraryActivity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="Không tìm thấy hoạt động (Activity not found)")

    if payload.title is not None:
        act.title = payload.title
    if payload.start_time is not None:
        act.start_time = parse_time_safe(payload.start_time)
    if payload.end_time is not None:
        act.end_time = parse_time_safe(payload.end_time)
    if payload.location_name is not None:
        act.location_name = payload.location_name
    if payload.notes is not None:
        act.notes = payload.notes
    if payload.external_url is not None:
        act.external_url = payload.external_url
    if payload.order_index is not None:
        act.order_index = payload.order_index

    db.commit()
    db.refresh(act)
    return act
