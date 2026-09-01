"""OpenAI integration and deterministic itinerary fallback."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
import json
import logging
from typing import Any, Literal

import httpx

from app.core.config import get_settings
from app.schemas.itinerary import GeneratedItineraryPayload

logger = logging.getLogger(__name__)

GenerationSource = Literal["openai", "fallback"]


@dataclass(frozen=True)
class GenerationResult:
    draft: GeneratedItineraryPayload
    source: GenerationSource


def _fallback_activities(day_index: int, destination_name: str) -> list[dict[str, Any]]:
    """Tạo danh sách các hoạt động du lịch mặc định chuẩn cho từng ngày."""
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
    """Sinh bản nháp lịch trình hoàn chỉnh theo thuật toán tĩnh dự phòng."""
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
                "travel_date": current_date.isoformat() if current_date else None,
                "title": f"Ngày {day_idx}: Khám phá {dest_name}",
                "activities": _fallback_activities(day_idx, dest_name),
            }
        )
        if current_date:
            current_date += timedelta(days=1)

    return days_draft


def _safe_parse_json(text: str) -> Any:
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

QUAN TRỌNG:
1. ĐỊA ĐIỂM CỤ THỂ: BẮT BUỘC chỉ được gợi ý các địa điểm, quán ăn, điểm tham quan CỤ THỂ và CÓ THẬT (VD: "Bánh Khọt Gốc Vú Sữa", "Bảo tàng Chứng tích Chiến tranh"). Tuyệt đối KHÔNG sử dụng các cụm từ chung chung như "Thưởng thức ẩm thực địa phương", "Ăn sáng địa phương", "Tham quan điểm nổi tiếng".
2. GOOGLE MAPS LINK: Thuộc tính `external_url` PHẢI là link tìm kiếm Google Maps chính xác của địa điểm đó (VD: "https://www.google.com/maps/search/?api=1&query=Tên+Địa+Điểm").

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


async def _generate_with_openai(
    destination: str | None,
    start_date: date | None,
    end_date: date | None,
    preferences: dict[str, Any] | None = None,
    adjustment_instruction: str | None = None,
    existing_itinerary: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]] | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    prompt = _build_prompt(destination, start_date, end_date, preferences, adjustment_instruction, existing_itinerary)
    url = "https://api.openai.com/v1/chat/completions"

    payload = {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": "You are a helpful travel planning assistant that responds in JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
    }
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    parsed = _safe_parse_json(content)
                    if isinstance(parsed, dict) and "days" in parsed:
                        return parsed["days"]
            else:
                logger.error(f"OpenAI API Error: {response.status_code} - {response.text}")
    except Exception as e:
        logger.warning(f"Lỗi kết nối OpenAI API: {e}. Kích hoạt chế độ dự phòng.")

    return None


async def generate_itinerary_draft(
    destination: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    preferences: dict[str, Any] | None = None,
    adjustment_instruction: str | None = None,
    existing_itinerary: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    ai_result = await _generate_with_openai(
        destination, start_date, end_date, preferences, adjustment_instruction, existing_itinerary
    )
    if ai_result:
        return ai_result
    return _fallback_draft(destination, start_date, end_date, preferences)


def _fallback_packing_suggestions(destination: str | None) -> list[dict[str, Any]]:
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
    settings = get_settings()
    if not settings.openai_api_key:
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

    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": "You are a helpful travel planning assistant that responds in JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    parsed = _safe_parse_json(content)
                    if isinstance(parsed, dict) and "items" in parsed: # If the array was wrapped
                        return parsed["items"]
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return parsed
    except Exception as e:
        logger.warning(f"Lỗi gọi OpenAI API sinh hành lý: {e}. Chuyển sang fallback.")

    return _fallback_packing_suggestions(destination)


class AIService:
    """Create structured itinerary drafts through OpenAI, with a safe fallback."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_itinerary_draft(self, workspace: dict[str, object], instruction: str | None = None) -> GenerationResult:
        if self.settings.openai_api_key:
            draft = self._generate_with_openai(workspace, instruction)
            if draft is not None:
                return GenerationResult(draft=draft, source="openai")
        return GenerationResult(draft=self._fallback_draft(workspace, instruction), source="fallback")

    def _generate_with_openai(self, workspace: dict[str, object], instruction: str | None) -> GeneratedItineraryPayload | None:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": self.settings.openai_model,
                "messages": [
                    {"role": "system", "content": self._build_prompt(workspace, instruction)}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.7,
            }
            headers = {
                "Authorization": f"Bearer {self.settings.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            # Using httpx synchronously since this method is called from synchronous code
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if content:
                        parsed = _safe_parse_json(content)
                        return GeneratedItineraryPayload.model_validate(parsed)
                else:
                    logger.error(f"OpenAI API Error: {response.status_code} - {response.text}")
                    
            return None
        except Exception as exc:
            logger.warning("OpenAI itinerary generation failed; using fallback. error=%s", type(exc).__name__)
            return None

    def _fallback_draft(self, workspace: dict[str, object], instruction: str | None) -> GeneratedItineraryPayload:
        destination = str(workspace.get("destination") or "Destination")
        dates = self._trip_dates(workspace)
        days = []
        for day_index, travel_date in enumerate(dates, start=1):
            days.append(
                {
                    "day_index": day_index,
                    "title": f"Explore {destination} — Day {day_index}",
                    "summary": "A flexible, saved starting point for your group." if not instruction else f"Adjusted for: {instruction}",
                    "travel_date": travel_date.isoformat() if travel_date else None,
                    "activities": self._fallback_activities(destination, day_index, instruction),
                }
            )
        return GeneratedItineraryPayload.model_validate({"days": days})

    def _fallback_activities(self, destination: str, day_index: int, instruction: str | None) -> list[dict[str, object]]:
        notes = f"Adjusted for: {instruction}" if instruction else None
        template = [
            ("08:00", "09:00", "Breakfast and departure", "Food"),
            ("09:30", "12:00", "Visit a local highlight", "Sightseeing"),
            ("14:00", "16:30", "Flexible local experience", "Leisure"),
            ("18:00", "20:00", "Dinner and evening break", "Food"),
        ]
        return [
            {
                "start_time": start_time,
                "end_time": end_time,
                "title": f"{title} — Day {day_index}",
                "location_name": f"{destination} city center",
                "activity_type": activity_type,
                "notes": notes,
                "external_url": f"https://www.google.com/maps/search/{destination}",
            }
            for start_time, end_time, title, activity_type in template
        ]

    def _trip_dates(self, workspace: dict[str, object]) -> list[date | None]:
        start_date = self._to_date(workspace.get("start_date"))
        end_date = self._to_date(workspace.get("end_date"))
        if start_date is None or end_date is None:
            return [start_date]
        return [start_date + timedelta(days=offset) for offset in range((end_date - start_date).days + 1)]

    def _to_date(self, value: object) -> date | None:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            return date.fromisoformat(value)
        return None

    def _build_prompt(self, workspace: dict[str, object], instruction: str | None) -> str:
        payload = {
            "workspace": workspace,
            "instruction": instruction,
        }
        
        system_instruction = """
Bạn là chuyên gia tư vấn du lịch thông minh Wandora. Dưới đây là thông tin chuyến đi dạng JSON.
QUAN TRỌNG:
1. ĐỊA ĐIỂM CỤ THỂ: BẮT BUỘC chỉ được gợi ý các địa điểm, quán ăn, điểm tham quan CỤ THỂ và CÓ THẬT (VD: "Bánh Khọt Gốc Vú Sữa", "Bảo tàng Chứng tích Chiến tranh"). Tuyệt đối KHÔNG sử dụng các cụm từ chung chung như "Thưởng thức ẩm thực địa phương", "Ăn sáng địa phương", "Tham quan điểm nổi tiếng".
2. GOOGLE MAPS LINK: Thuộc tính `external_url` PHẢI là link tìm kiếm Google Maps chính xác của địa điểm đó (VD: "https://www.google.com/maps/search/?api=1&query=Tên+Địa+Điểm").

BẮT BUỘC trả về định dạng JSON theo đúng cấu trúc sau:
{
  "days": [
    {
      "day_index": 1,
      "title": "Ngày 1: Tiêu đề",
      "summary": "Tóm tắt ngắn gọn",
      "travel_date": "2024-01-01",
      "activities": [
        {
          "title": "Tên hoạt động",
          "start_time": "08:00",
          "end_time": "10:00",
          "location_name": "Tên địa điểm",
          "notes": "Ghi chú hoạt động",
          "external_url": "https://www.google.com/maps/search/?api=1&query=..."
        }
      ]
    }
  ]
}
"""
        return system_instruction + "\nJSON INPUT:\n" + json.dumps(payload, ensure_ascii=False, indent=2, default=str)
