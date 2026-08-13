"""
Script kiểm thử tự động tập trung 2 use case:
1. Tạo lịch trình tự động qua GenAI (UC-05)
2. Xem & chỉnh sửa lịch trình (UC-08)
"""

import sys

# Đảm bảo hiển thị Tiếng Việt trên Terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient

from app.db.session import init_db
from main import app


init_db()
client = TestClient(app)


def print_step_header(step_number: int, title: str):
    """In tiêu đề từng giai đoạn kiểm thử."""

    print("\n" + "=" * 70)
    print(f" BƯỚC {step_number}: {title}")
    print("=" * 70)


def run_core_tests():
    print("\n" + "🚀" * 30)
    print(" KHỞI CHẠY TEST 2 USE CASE: TẠO & CHỈNH SỬA LỊCH TRÌNH")
    print("🚀" * 30)

    print_step_header(1, "Khởi tạo workspace chuyến đi")
    workspace_payload = {
        "title": "Chuyến đi Đà Nẵng, Hội An & Huế Summer 2026",
        "destination": "Đà Nẵng",
        "description": "Hành trình khám phá di sản và ẩm thực Miền Trung",
        "start_date": "2026-06-01",
        "end_date": "2026-06-04",
        "budget": 900,
        "travel_style": "Văn hóa & Ẩm thực",
        "group_size": 6,
        "notes": "Chỉ kiểm thử 2 use case cốt lõi: tạo và chỉnh lịch trình.",
    }

    res = client.post("/api/v1/workspaces", json=workspace_payload)
    assert res.status_code == 201, f"Tạo workspace thất bại: {res.text}"
    workspace_data = res.json()
    workspace_id = workspace_data.get("workspace_id") or workspace_data.get("id")

    print(f"✅ Workspace đã được tạo: {workspace_id}")
    print(f"   Tên chuyến đi: {workspace_data.get('title')}")
    print(f"   Thời gian: {workspace_data.get('start_date')} -> {workspace_data.get('end_date')}")

    print_step_header(2, "Tạo lịch trình tự động bằng GenAI (UC-05)")
    res = client.post(f"/api/v1/workspaces/{workspace_id}/generate-itinerary")
    assert res.status_code == 200, f"Sinh lịch trình thất bại: {res.text}"
    itinerary = res.json()

    print("✅ Đã sinh lịch trình tự động thành công")
    print(f"   Số ngày trong lịch trình: {len(itinerary.get('days', []))}")

    print("\n📌 Xem lịch trình dạng timeline:")
    first_day = None
    for day in itinerary.get("days", []):
        day_id = day.get("id")
        if first_day is None:
            first_day = day
        print(f"\n   - Ngày {day.get('day_index')}: {day.get('title')}")
        for activity in day.get("activities", []):
            print(
                f"      • {activity.get('start_time')} - {activity.get('end_time')} | "
                f"{activity.get('title')} (@ {activity.get('location_name')})"
            )

    print_step_header(3, "Chỉnh sửa lịch trình (UC-08)")
    assert first_day is not None, "Không có ngày nào trong lịch trình để chỉnh sửa"
    first_activity = first_day["activities"][0]
    act_id = first_activity.get("id")

    update_payload = {
        "start_time": "08:30",
        "end_time": "11:30",
        "notes": "⭐ ĐÃ SỬA: Nhóm tập trung lúc 8h15 trước sảnh khách sạn",
    }
    res = client.put(f"/api/v1/itineraries/activities/{act_id}", json=update_payload)
    assert res.status_code == 200, f"Cập nhật hoạt động thất bại: {res.text}"
    updated_act = res.json()

    print("✅ Đã sửa hoạt động thủ công thành công")
    print(f"   Tên hoạt động: {updated_act.get('title')}")
    print(f"   Khung giờ mới: {updated_act.get('start_time')} - {updated_act.get('end_time')}")
    print(f"   Ghi chú mới: {updated_act.get('notes')}")

    adjust_payload = {
        "prompt": "Thay điểm tham quan bảo tàng bằng hoạt động bãi biển và bổ sung địa điểm ăn tối chay",
    }
    print(f"\n   🤖 Gửi lệnh AI Prompt: '{adjust_payload['prompt']}'")
    res = client.post(f"/api/v1/workspaces/{workspace_id}/adjust-itinerary", json=adjust_payload)
    assert res.status_code == 200, f"Điều chỉnh lịch trình thất bại: {res.text}"

    adjusted_itinerary = res.json()
    print("✅ AI đã điều chỉnh lịch trình thành công")
    print(f"   Số ngày sau điều chỉnh: {len(adjusted_itinerary.get('days', []))}")

    print("\n" + "=" * 70)
    print(" 🎉 HOÀN THÀNH TEST 2 USE CASE: TẠO & CHỈNH SỬA LỊCH TRÌNH")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_core_tests()
