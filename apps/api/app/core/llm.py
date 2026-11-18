import json
import httpx
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.logging import logger


class GeminiClient:
    """
    Lightweight async client for Google Gemini REST API using httpx.
    Automatically falls back to a deterministic structured generator when
    GEMINI_API_KEY is not configured or when running in mock/test mode.
    """

    MODEL_NAME = "gemini-2.5-flash"
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    async def generate_structured_itinerary(
        self,
        prompt: str,
        context: Dict[str, Any],
    ) -> tuple[List[Dict[str, Any]], bool, str]:
        """
        Generates a list of itinerary days with nested activities.
        Returns: (itinerary_days_list, model_invoked_bool, model_identifier_str)
        """
        api_key = settings.gemini_api_key.strip() if settings.gemini_api_key else ""
        if not api_key or settings.provider_mode == "mock" or settings.roamly_env == "test":
            return self._fallback_itinerary(context), False, "deterministic-fallback"

        url = f"{self.BASE_URL}/{self.MODEL_NAME}:generateContent"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "responseMimeType": "application/json",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    params={"key": api_key},
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

            candidates = data.get("candidates", [])
            if not candidates:
                logger.warning("Gemini returned no candidates; using fallback itinerary.")
                return self._fallback_itinerary(context), False, "deterministic-fallback"

            raw_text = (
                candidates[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "{}")
            )
            parsed = json.loads(raw_text)
            days = parsed.get("days", parsed if isinstance(parsed, list) else [])
            if not days:
                return self._fallback_itinerary(context), False, "deterministic-fallback"

            return days, True, self.MODEL_NAME
        except Exception as exc:
            logger.warning(f"Gemini API call failed ({exc}); falling back to deterministic itinerary.")
            return self._fallback_itinerary(context), False, "deterministic-fallback"

    @staticmethod
    def _fallback_itinerary(context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Deterministic fallback generator when offline or no API key is configured."""
        city = context.get("destination_city", "Destination")
        country = context.get("destination_country", "")
        start_str = context.get("start_date", date.today().isoformat())
        end_str = context.get("end_date", start_str)
        lat = float(context.get("latitude", 48.8566))
        lon = float(context.get("longitude", 2.3522))
        currency = context.get("currency", "USD")

        start_dt = date.fromisoformat(str(start_str))
        end_dt = date.fromisoformat(str(end_str))
        num_days = max(1, min((end_dt - start_dt).days + 1, 14))
        weather_list = context.get("weather_summary", [])

        themes = [
            f"Historic Heart & Iconic Landmarks of {city}",
            f"Cultural Gems, Museums & Local Neighborhoods in {city}",
            f"Scenic Views, Parks & Culinary Tasting in {city}",
            f"Artisan Markets & Hidden Corners of {city}",
            f"Waterfront Strolls & Farewell Evening in {city}",
        ]

        days_output: List[Dict[str, Any]] = []
        for idx in range(num_days):
            current_date = start_dt + timedelta(days=idx)
            day_num = idx + 1
            theme = themes[idx % len(themes)]
            weather_info = weather_list[idx] if idx < len(weather_list) else {
                "weather_condition": "Partly cloudy",
                "temp_max_celsius": 22.0,
                "temp_min_celsius": 14.0,
                "precipitation_probability": 15,
            }

            days_output.append(
                {
                    "day_number": day_num,
                    "date": current_date.isoformat(),
                    "theme_title": theme,
                    "weather_summary": weather_info,
                    "activities": [
                        {
                            "name": f"Morning Walking Tour of {city} Old Town",
                            "category": "sightseeing",
                            "description": f"Guided walk exploring the historic center of {city}, {country}.",
                            "start_time": "09:30",
                            "end_time": "12:00",
                            "duration_minutes": 150,
                            "location_name": f"{city} Historic Center",
                            "latitude": round(lat + 0.005 * (idx + 1), 4),
                            "longitude": round(lon + 0.005 * (idx + 1), 4),
                            "estimated_cost": {"amount": 25.0, "currency": currency},
                            "booking_required": False,
                            "order_index": 0,
                        },
                        {
                            "name": f"Traditional {city} Lunch & Market Visit",
                            "category": "dining",
                            "description": f"Sample regional specialties at a popular local market in {city}.",
                            "start_time": "12:30",
                            "end_time": "14:00",
                            "duration_minutes": 90,
                            "location_name": f"{city} Central Market",
                            "latitude": round(lat - 0.004 * (idx + 1), 4),
                            "longitude": round(lon + 0.003 * (idx + 1), 4),
                            "estimated_cost": {"amount": 35.0, "currency": currency},
                            "booking_required": False,
                            "order_index": 1,
                        },
                        {
                            "name": f"Afternoon Cultural Museum & Landmark Experience",
                            "category": "culture",
                            "description": f"Explore flagship art and history exhibits in {city}.",
                            "start_time": "15:00",
                            "end_time": "17:30",
                            "duration_minutes": 150,
                            "location_name": f"{city} National Museum",
                            "latitude": round(lat + 0.008 * (idx + 1), 4),
                            "longitude": round(lon - 0.006 * (idx + 1), 4),
                            "estimated_cost": {"amount": 30.0, "currency": currency},
                            "booking_required": True,
                            "order_index": 2,
                        },
                    ],
                }
            )

        return days_output
