import os
import json
import re
from google import genai
from google.genai import types
from errors.error_tracker import ErrorTracker

def get_travel_recommendations_json(date_string: str, tracker: ErrorTracker) -> dict:
    """
    Gemini API를 호출하여 2~3개 추천 지역 정보를 JSON으로 가져옵니다.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    prompt = f"""
    당신은 전문 한국 여행 가이드입니다.
    사용자가 요청한 여행 날짜({date_string})에 어울리는 국내 여행지 2~3곳을 추천해 주세요.

    반드시 아래 JSON 포맷 규칙을 따라 작성하세요:
    {{
      "recommended_cities": [
        {{
          "city": "도시명 (예: 제주)",
          "weather": "해당 시기 날씨 요약 1문장",
          "events": ["행사/축제 1", "행사/축제 2"],
          "reason": "추천 근거 2문장"
        }},
        {{
          "city": "도시명 (예: 강릉)",
          "weather": "해당 시기 날씨 요약 1문장",
          "events": ["행사/축제 1"],
          "reason": "추천 근거 2문장"
        }}
      ]
    }}
    """

    for attempt in range(1, 3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            raw_text = response.text.strip()
            clean_json_str = re.sub(r"```json\s*|\s*```", "", raw_text).strip()
            data = json.loads(clean_json_str)
            
            if "recommended_cities" in data and isinstance(data["recommended_cities"], list):
                return data
            else:
                raise ValueError("JSON 필수 키(recommended_cities) 누락")

        except Exception as e:
            if attempt == 1:
                prompt += "\n\n[경고]: 유효한 JSON 포맷으로 recommended_cities 배열을 포함하세요."
            else:
                tracker.add_error(
                    step="llm_recommendation",
                    error_type="JSON_PARSE_ERROR",
                    message=f"LLM 파싱 최종 실패: {e}"
                )

    # 파싱 실패 시 예비 보너스 데이터 (복수 도시)
    return {
        "recommended_cities": [
            {
                "city": "강릉",
                "weather": "해당 시기 온화하고 산책하기 적합한 날씨입니다.",
                "events": ["강릉 커피축제"],
                "reason": "동해 바다와 안목해변 커피거리를 만끽할 수 있는 대표 여행지입니다."
            },
            {
                "city": "속초",
                "weather": "선선한 바닷바람이 부는 상쾌한 날씨입니다.",
                "events": ["속초 수제맥주 축제"],
                "reason": "설악산 풍경과 아바이마을 등 풍부한 먹거리와 볼거리가 가득합니다."
            }
        ]
    }