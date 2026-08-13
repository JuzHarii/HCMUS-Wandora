"""Tầng tích hợp GenAI và sinh dữ liệu thay thế khi không có API key."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from app.core.config import get_settings
from app.schemas.itinerary import GeneratedItineraryPayload


class AIService:
    """Dịch vụ trừu tượng hóa việc gọi Gemini hoặc tạo dữ liệu dự phòng."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_itinerary_draft(self, workspace: dict[str, object], instruction: str | None = None) -> GeneratedItineraryPayload:
        """Sinh bản nháp lịch trình theo ngữ cảnh chuyến đi."""

        if self.settings.gemini_api_key:
            draft = self._generate_with_gemini(workspace, instruction)
            if draft is not None:
                return draft
        return self._fallback_draft(workspace, instruction)

    def _generate_with_gemini(self, workspace: dict[str, object], instruction: str | None) -> GeneratedItineraryPayload | None:
        """Gọi Gemini nếu thư viện và khóa API đều sẵn sàng."""

        try:
            from google import genai
        except Exception:  # pragma: no cover
            return None

        prompt = self._build_prompt(workspace, instruction)
        client = genai.Client(api_key=self.settings.gemini_api_key)
        response = client.models.generate_content(
            model=self.settings.gemini_model,
            contents=prompt,
        )
        text = getattr(response, "text", None) or ""
        try:
            payload = json.loads(text)
            return GeneratedItineraryPayload.model_validate(payload)
        except Exception:
            return None

    def _fallback_draft(self, workspace: dict[str, object], instruction: str | None) -> GeneratedItineraryPayload:
        """Tạo lịch trình mặc định đủ tốt cho demo và kiểm thử."""

        destination = str(workspace.get("destination") or "Điểm đến")
        start_date = workspace.get("start_date")
        base_date = start_date if isinstance(start_date, (date, datetime)) else None
        days = []
        for day_index, title, summary in [
            (1, f"Khám phá {destination}", "Di chuyển, nhận phòng và làm quen điểm đến."),
            (2, f"Trải nghiệm văn hóa {destination}", "Tham quan các điểm nhấn và thưởng thức ẩm thực địa phương."),
            (3, f"Thư giãn và kết thúc tại {destination}", "Mua sắm nhẹ, ăn trưa và chuẩn bị trở về."),
        ]:
            travel_date = None
            if base_date is not None:
                if isinstance(base_date, datetime):
                    travel_date = (base_date + timedelta(days=day_index - 1)).date()
                else:
                    travel_date = base_date + timedelta(days=day_index - 1)
            days.append(
                {
                    "day_index": day_index,
                    "title": title,
                    "summary": summary if not instruction else f"{summary} Ghi chú điều chỉnh: {instruction}",
                    "travel_date": travel_date,
                    "activities": self._fallback_activities(destination, day_index, instruction),
                }
            )
        return GeneratedItineraryPayload.model_validate({"days": days})

    def _fallback_activities(self, destination: str, day_index: int, instruction: str | None) -> list[dict[str, object]]:
        """Sinh các hoạt động mẫu theo ngày."""

        notes = f"Điều chỉnh theo yêu cầu: {instruction}" if instruction else None
        template = [
            ("08:00", "09:00", "Ăn sáng và khởi hành", "Ẩm thực", f"{destination} - khu trung tâm"),
            ("09:30", "12:00", "Tham quan điểm nổi bật", "Tham quan", f"{destination} - điểm nhấn"),
            ("14:00", "16:30", "Trải nghiệm tự do", "Tự do", f"{destination} - khu trải nghiệm"),
            ("18:00", "20:00", "Ăn tối và nghỉ ngơi", "Ẩm thực", f"{destination} - nhà hàng địa phương"),
        ]
        activities: list[dict[str, object]] = []
        for order, (start_time, end_time, title, activity_type, location_name) in enumerate(template, start=1):
            activities.append(
                {
                    "start_time": start_time,
                    "end_time": end_time,
                    "title": f"{title} ngày {day_index}",
                    "location_name": location_name,
                    "activity_type": activity_type,
                    "notes": notes,
                    "external_url": f"https://www.google.com/maps/search/{destination}",
                }
            )
        return activities

    def _build_prompt(self, workspace: dict[str, object], instruction: str | None) -> str:
        """Xây dựng prompt cấu trúc cho Gemini."""

        payload = {
            "workspace": workspace,
            "instruction": instruction,
            "required_output": "JSON with key days, each day contains day_index, title, summary, travel_date, activities.",
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)
