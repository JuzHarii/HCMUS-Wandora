from __future__ import annotations

import json
import logging
from datetime import date, timedelta
from typing import Any

import httpx

from ..core.config import get_settings

logger = logging.getLogger(__name__)


def _fallback_activities(day_index: int, destination_name: str) -> list[dict[str, Any]]:
    """
    Tạo danh sách các hoạt động du lịch mặc định chuẩn cho từng ngày.

    Công dụng:
    - Khi dịch vụ AI không khả dụng hoặc bị ngắt kết nối, hàm này cung cấp bộ hoạt động
      du lịch mẫu đã được định dạng chuẩn (nhận phòng, ăn uống, tham quan, mua sắm).
    - Giúp hệ thống luôn trả về dữ liệu khả dụng (fail-safe) mà không sụp đổ API.
    =)))
    """
    if day_index == 1:
        return [
            {
                "title": f"Di chuyển đến {destination_name} & Check-in",
                "start_time": "08:00",
                "end_time": "10:00",
                "location_name": f"Khách sạn tại {destination_name}",
                "notes": "Nhận phòng và nghỉ ngơi nhẹ",
                "external_url": None,
                "order_index": 1,
            },
            {
                "title": "Thưởng thức ẩm thực địa phương",
                "start_time": "11:30",
                "end_time": "13:00",
                "location_name": f"Trung tâm {destination_name}",
                "notes": "Khám phá các món ăn đặc sản nổi tiếng",
                "external_url": None,
                "order_index": 2,
            },
            {
                "title": "Tham quan điểm danh thắng nổi tiếng",
                "start_time": "14:30",
                "end_time": "17:00",
                "location_name": f"Điểm tham quan {destination_name}",
                "notes": "Dạo phố và chụp ảnh lưu niệm",
                "external_url": None,
                "order_index": 3,
            },
            {
                "title": "Ăn tối & Dạo phố đêm",
                "start_time": "18:30",
                "end_time": "21:00",
                "location_name": f"Khu phố đêm {destination_name}",
                "notes": "Tận hưởng không khí buổi tối",
                "external_url": None,
                "order_index": 4,
            },
        ]

    return [
        {
            "title": f"Khám phá khu du lịch Ngày {day_index}",
            "start_time": "08:30",
            "end_time": "11:30",
            "location_name": f"Địa điểm du lịch Day {day_index}",
            "notes": "Tham quan trải nghiệm sinh thái / văn hóa",
            "external_url": None,
            "order_index": 1,
        },
        {
            "title": "Ăn trưa và nghỉ ngơi",
            "start_time": "12:00",
            "end_time": "13:30",
            "location_name": "Nhà hàng địa phương",
            "notes": "Nghỉ ngơi lấy sức cho buổi chiều",
            "external_url": None,
            "order_index": 2,
        },
        {
            "title": "Mua sắm quà lưu niệm",
            "start_time": "15:00",
            "end_time": "17:30",
            "location_name": f"Chợ / Trung tâm thương mại {destination_name}",
            "notes": "Mua đồ lưu niệm và đặc sản",
            "external_url": None,
            "order_index": 3,
        },
    ]


def _fallback_draft(
    destination: str | None,
    start_date: date | None,
    end_date: date | None,
    preferences: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Sinh bản nháp lịch trình hoàn chỉnh theo thuật toán tĩnh dự phòng.

    Công dụng:
    - Tính toán số lượng ngày dựa trên start_date và end_date.
    - Duyệt qua từng ngày và ghép các hoạt động từ `_fallback_activities`.
    - Đảm bảo trả về cấu trúc danh sách ngày trùng khớp hoàn toàn với định dạng của AI.
    """
    _ = preferences
    dest_name = destination or "Điểm đến"

    num_days = 3
    if start_date and end_date:
        num_days = (end_date - start_date).days + 1
        if num_days <= 0:
            num_days = 1

    days_draft: list[dict[str, Any]] = []
    current_date = start_date

    for day_idx in range(1, num_days + 1):
        days_draft.append(
            {
                "day_index": day_idx,
                "date_value": current_date.isoformat() if current_date else None,
                "title": f"Ngày {day_idx}: Khám phá {dest_name}",
                "activities": _fallback_activities(day_idx, dest_name),
            }
        )
        if current_date:
            current_date += timedelta(days=1)

    return days_draft


def _safe_parse_json(text: str) -> Any:
    """Trích xuất và parse JSON an toàn, tự động loại bỏ các ký tự markdown fence (```json ... ```)."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return json.loads(cleaned)


def _build_prompt(
    destination: str | None,
    start_date: date | None,
    end_date: date | None,
    preferences: dict[str, Any] | None = None,
    adjustment_instruction: str | None = None,
    existing_itinerary: list[dict[str, Any]] | None = None,
) -> str:
    """
    Xây dựng câu lệnh (prompt) tối ưu gửi cho mô hình ngôn ngữ lớn (LLM).

    Công dụng:
    - Đóng gói thông tin chuyến đi (điểm đến, thời gian, sở thích người dùng).
    - Đính kèm lịch trình hiện tại nếu đang ở chế độ điều chỉnh (adjustment).
    - Ép mô hình trả về đúng cấu trúc JSON mong muốn (Structural JSON Enforcement).
    """
    dest = destination or "Điểm đến phổ biến"
    num_days = 3
    if start_date and end_date:
        num_days = max(1, (end_date - start_date).days + 1)

    pref_str = json.dumps(preferences, ensure_ascii=False) if preferences else "Không có"
    adjust_str = f"\nYêu cầu điều chỉnh từ người dùng: {adjustment_instruction}" if adjustment_instruction else ""
    existing_str = (
        f"\nLịch trình hiện tại của chuyến đi:\n{json.dumps(existing_itinerary, ensure_ascii=False, indent=2)}\nHãy giữ nguyên các điểm tham quan cũ hợp lý và chỉ chỉnh sửa/thêm bớt theo đúng Yêu cầu điều chỉnh."
        if existing_itinerary
        else ""
    )

    return f"""Bạn là chuyên gia tư vấn du lịch thông minh Wandora.
Hãy tạo/cập nhật lịch trình chi tiết cho chuyến đi {dest} trong {num_days} ngày.
Sở thích / Yêu cầu: {pref_str}{existing_str}{adjust_str}

BẮT BUỘC trả về định dạng JSON thuần túy (không dùng markdown block, không giải thích thêm) theo đúng cấu trúc sau:
{{
  "days": [
    {{
      "day_index": 1,
      "title": "Ngày 1: Tiêu đề ngày",
      "activities": [
        {{
          "title": "Tên hoạt động",
          "start_time": "08:00",
          "end_time": "10:00",
          "location_name": "Tên địa điểm",
          "notes": "Ghi chú hoạt động",
          "external_url": null,
          "order_index": 1
        }}
      ]
    }}
  ]
}}
"""


async def _generate_with_gemini(
    destination: str | None,
    start_date: date | None,
    end_date: date | None,
    preferences: dict[str, Any] | None = None,
    adjustment_instruction: str | None = None,
    existing_itinerary: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]] | None:
    """
    Thực hiện cuộc gọi bất đồng bộ (Async Non-blocking Call) tới Gemini REST API.
    """
    settings = get_settings()
    if not settings.gemini_api_key:
        logger.info("Chưa cấu hình GEMINI_API_KEY, tự động chuyển sang chế độ dự phòng (fallback).")
        return None

    prompt = _build_prompt(destination, start_date, end_date, preferences, adjustment_instruction, existing_itinerary)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "response_mime_type": "application/json"},
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text_res = parts[0].get("text", "")
                        parsed = _safe_parse_json(text_res)
                        if isinstance(parsed, dict) and "days" in parsed:
                            return parsed["days"]  # type: ignore[no-any-return]
    except Exception as e:
        logger.warning(f"Lỗi kết nối Gemini API: {e}. Kích hoạt chế độ dự phòng.")

    return None


async def generate_itinerary_draft(
    destination: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    preferences: dict[str, Any] | None = None,
    adjustment_instruction: str | None = None,
    existing_itinerary: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Hàm điều phối chính sinh bản nháp lịch trình bằng AI hoặc dự phòng.
    """
    ai_result = await _generate_with_gemini(
        destination, start_date, end_date, preferences, adjustment_instruction, existing_itinerary
    )
    if ai_result:
        return ai_result
    return _fallback_draft(destination, start_date, end_date, preferences)


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


async def generate_packing_suggestions(
    destination: str | None = None,
    preferences: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Sinh danh sách gợi ý hành lý thông minh bằng Gemini AI (PA3 UC 2.7).
    """
    settings = get_settings()
    if not settings.gemini_api_key:
        return _fallback_packing_suggestions(destination)

    dest = destination or "Điểm du lịch"
    pref_str = json.dumps(preferences, ensure_ascii=False) if preferences else "Không có"

    prompt = f"""Bạn là chuyên gia chuẩn bị hành lý du lịch Wandora.
Hãy tạo danh sách vật dụng cần thiết cho chuyến đi đến {dest}.
Sở thích / Yêu cầu đặc biệt: {pref_str}

BẮT BUỘC trả về định dạng JSON array thuần túy theo đúng cấu trúc sau:
[
  {{
    "name": "Tên vật dụng",
    "quantity": 1,
    "is_shared": false,
    "note": "Ghi chú lưu ý mang theo"
  }}
]
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "response_mime_type": "application/json"},
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text_res = parts[0].get("text", "")
                        parsed = _safe_parse_json(text_res)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            return parsed  # type: ignore[no-any-return]
    except Exception as e:
        logger.warning(f"Lỗi gọi Gemini API sinh hành lý: {e}. Chuyển sang fallback.")

    return _fallback_packing_suggestions(destination)

