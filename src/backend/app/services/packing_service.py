from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.packing import PackingItem, PackingListEntry
from ..models.user import User
from ..schemas.packing import PackingItemCreate, PackingItemUpdate
from . import ai_service
from .workspace_service import get_workspace


def _fallback_packing_suggestions(destination: str | None) -> list[dict[str, Any]]:
    """Tạo danh sách đồ dùng gợi ý tĩnh khi không gọi được AI."""
    dest = destination or "Địa điểm du lịch"
    return [
        {"name": "Giấy tờ tùy thân & Căn cước công dân", "quantity": 1, "is_shared": False, "note": "Mang bản chính"},
        {"name": "Vé xe / Vé máy bay & Đặt phòng khách sạn", "quantity": 1, "is_shared": True, "note": "In bản giấy hoặc lưu điện thoại"},
        {"name": f"Trang phục phù hợp với {dest}", "quantity": 3, "is_shared": False, "note": "Quần áo nhẹ và thoải mái"},
        {"name": "Bộ vệ sinh cá nhân & Bàn chải", "quantity": 1, "is_shared": False, "note": "Tuýp nhỏ tiện mang theo"},
        {"name": "Sạc dự phòng & Dây sạc điện thoại", "quantity": 1, "is_shared": True, "note": "Sạc đầy trước khi đi"},
        {"name": "Thuốc cá nhân & Băng cá nhân", "quantity": 1, "is_shared": True, "note": "Thuốc tiêu hóa và hạ sốt"},
    ]


async def generate_packing_suggestions(db: Session, workspace_id: int) -> list[dict[str, Any]]:
    """
    Sinh danh sách gợi ý hành lý tự động dựa trên địa điểm du lịch và sở thích bằng Gemini AI (PA3 2.7).

    Công dụng:
    - Đọc thông tin workspace.
    - Gọi Gemini AI thông qua `ai_service` (hoặc dự phòng fallback nếu mất mạng/thiếu API key).
    - Lưu trực tiếp các món đồ được gợi ý vào bảng `packing_items` của CSDL nếu chưa tồn tại.
    """
    ws = get_workspace(db, workspace_id)
    preferences = json.loads(ws.preferences_json) if ws.preferences_json else {}

    # Gọi AI sinh danh sách hành lý
    items_data = await ai_service.generate_packing_suggestions(destination=ws.destination, preferences=preferences)

    created_items = []
    for item in items_data:
        item_name = item.get("name", "Vật dụng cần mang")
        existing = (
            db.query(PackingItem)
            .filter(PackingItem.workspace_id == workspace_id, PackingItem.name == item_name)
            .first()
        )
        if not existing:
            p_obj = PackingItem(
                workspace_id=workspace_id,
                name=item_name,
                quantity=item.get("quantity", 1),
                is_shared=bool(item.get("is_shared", False)),
                note=item.get("note"),
            )
            db.add(p_obj)
            created_items.append(p_obj)

    db.commit()
    for item_obj in created_items:
        db.refresh(item_obj)

    return (
        db.query(PackingItem)
        .filter(PackingItem.workspace_id == workspace_id)
        .all()
    )



def add_packing_item(db: Session, workspace_id: int, payload: PackingItemCreate) -> dict[str, Any]:
    """Thêm đồ dùng thủ công vào danh sách hành lý."""
    _ = get_workspace(db, workspace_id)

    item = PackingItem(
        workspace_id=workspace_id,
        name=payload.name,
        quantity=payload.quantity,
        is_shared=payload.is_shared,
        note=payload.note,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return get_packing_item_detail(db, item.id)


def list_packing_items(db: Session, workspace_id: int) -> list[dict[str, Any]]:
    """Lấy danh sách vật dụng hành lý kèm thông tin người phân công và trạng thái hoàn thành."""
    _ = get_workspace(db, workspace_id)

    items = (
        db.query(PackingItem)
        .filter(PackingItem.workspace_id == workspace_id)
        .order_by(PackingItem.created_at.asc())
        .all()
    )

    result = []
    for item in items:
        result.append(get_packing_item_detail(db, item.id))
    return result


def get_packing_item_detail(db: Session, item_id: int) -> dict[str, Any]:
    """Chi tiết 1 vật dụng hành lý kèm danh sách người phân công."""
    item = db.query(PackingItem).filter(PackingItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy vật dụng hành lý")

    entries = db.query(PackingListEntry).filter(PackingListEntry.packing_item_id == item.id).all()
    assignments = []
    for entry in entries:
        user = db.query(User).filter(User.id == entry.user_id).first()
        assignments.append(
            {
                "id": entry.id,
                "packing_item_id": entry.packing_item_id,
                "user_id": entry.user_id,
                "user_email": user.email if user else None,
                "user_full_name": user.full_name if user else None,
                "is_checked": entry.is_checked,
            }
        )

    return {
        "id": item.id,
        "workspace_id": item.workspace_id,
        "name": item.name,
        "quantity": item.quantity,
        "is_shared": item.is_shared,
        "note": item.note,
        "created_at": item.created_at,
        "assignments": assignments,
    }


def update_packing_item(db: Session, item_id: int, payload: PackingItemUpdate) -> dict[str, Any]:
    """Cập nhật thông tin vật dụng hành lý."""
    item = db.query(PackingItem).filter(PackingItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy vật dụng hành lý")

    if payload.name is not None:
        item.name = payload.name
    if payload.quantity is not None:
        item.quantity = payload.quantity
    if payload.is_shared is not None:
        item.is_shared = payload.is_shared
    if payload.note is not None:
        item.note = payload.note

    db.commit()
    return get_packing_item_detail(db, item_id)


def assign_or_toggle_item(db: Session, item_id: int, user_id: int, is_checked: bool = False) -> dict[str, Any]:
    """Phân công vật dụng hành lý cho thành viên chuẩn bị hoặc đánh dấu đã hoàn thành (PA3 2.8)."""
    item = db.query(PackingItem).filter(PackingItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy vật dụng hành lý")

    # Đảm bảo user tồn tại để thỏa mãn ràng buộc khóa ngoại SQLite
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, email=f"user{user_id}@wandora.app", full_name=f"User {user_id}")
        db.add(user)
        db.flush()

    entry = (
        db.query(PackingListEntry)
        .filter(PackingListEntry.packing_item_id == item_id, PackingListEntry.user_id == user_id)
        .first()
    )
    if not entry:
        entry = PackingListEntry(packing_item_id=item_id, user_id=user_id, is_checked=is_checked)
        db.add(entry)
    else:
        entry.is_checked = is_checked

    db.commit()
    return get_packing_item_detail(db, item_id)


def delete_packing_item(db: Session, item_id: int) -> dict[str, str]:
    """Xóa vật dụng khỏi danh sách hành lý."""
    item = db.query(PackingItem).filter(PackingItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy vật dụng hành lý")

    db.delete(item)
    db.commit()
    return {"detail": "Đã xóa vật dụng hành lý thành công"}
