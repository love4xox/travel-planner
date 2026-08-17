import os
import re
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def get_travel_recommendations_json(date_string: str, tracker=None) -> dict:
    """
    Gemini LLM을 호출하여 날짜 기반 추천 도시 및 날씨, 축제 정보를 JSON으로 반환합니다.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        if tracker:
            tracker.add_error("llm_recommendation", "API_KEY_MISSING", "GEMINI_API_KEY가 설정되지 않았습니다.")
        return get_fallback_data()

    client = genai.Client(api_key=api_key)

    prompt = f"""
당신은 전문 한국 여행 가이드입니다.
사용자가 요청한 여행 날짜({date_string})의 계절과 날씨에 가장 적합한 국내 여행지 2~3곳을 추천해 주세요.
(지도 API 검색 품질을 위해 '강원도', '전라남도' 같은 광역 명칭 대신 '강릉시', '경주시', '여수시'처럼 구체적인 시/군 단위 명칭을 사용하세요.)

반드시 아래 JSON 포맷 규칙을 따라 작성하세요:
{{
  "recommended_cities": [
    {{
      "city": "구체적인 시/군 명칭 (예: 경주시, 여수시)",
      "weather": "해당 시기 날씨 요약 1문장",
      "events": ["행사/축제 1", "행사/축제 2"],
      "reason": "추천 근거 2문장"
    }}
  ]
}}
"""

    for attempt in range(1, 3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            raw_text = response.text.strip()
            clean_text = re.sub(r"```json\s*|\s*```", "", raw_text).strip()
            data = json.loads(clean_text)
            
            if "recommended_cities" in data and isinstance(data["recommended_cities"], list):
                return data
            elif "recommended_city" in data:
                return {"recommended_cities": [data]}
            else:
                raise ValueError("JSON 필수 키(recommended_cities)가 누락되었습니다.")
                
        except Exception as e:
            if tracker:
                tracker.add_error("llm_recommendation", "JSON_PARSE_ERROR", f"시도 {attempt} 실패: {str(e)}")
            if attempt == 1:
                prompt += "\n\n[경고]: 이전 출력이 올바른 JSON 규격이 아니었습니다. 반드시 오직 순수한 JSON 포맷으로만 응답하세요."

    return get_fallback_data()

def get_fallback_data() -> dict:
    """파싱 실패 시 예비 보너스 데이터"""
    return {
        "recommended_cities": [
            {
                "city": "강릉시",
                "weather": "해당 시기 온화하고 산책하기 적합한 날씨입니다.",
                "events": ["강릉 커피축제"],
                "reason": "동해 바다와 안목해변 커피거리를 만끽할 수 있는 대표 여행지입니다."
            },
            {
                "city": "속초시",
                "weather": "선선한 바닷바람이 부는 상쾌한 날씨입니다.",
                "events": ["속초 수제맥주 축제"],
                "reason": "설악산 풍경과 아바이마을 등 풍부한 먹거리와 볼거리가 가득합니다."
            }
        ]
    }