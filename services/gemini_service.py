import os
import json
import re
from google import genai
from google.genai import types
from errors.error_tracker import ErrorTracker

def get_travel_recommendation_json(date_string: str, tracker: ErrorTracker) -> dict:
    """
    Gemini API(gemini-2.5-flash)를 호출하여 1차 추천 결과를 JSON으로 받아옵니다.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    prompt = f"""
    당신은 전문 한국 여행 가이드입니다.
    사용자가 요청한 여행 날짜({date_string})에 어울리는 국내 여행지 1곳을 추천해 주세요.

    아래 JSON 포맷 규칙을 정확히 따라 작성해 주세요:
    {{
      "recommended_city": "도시명 (예: 제주, 강릉, 부산, 삼척)",
      "weather": "해당 시기 일반적 날씨 요약 1~2문장",
      "events": ["행사 또는 축제 후보 1", "행사 또는 축제 후보 2"],
      "reason": "추천 근거 2~4문장"
    }}
    """

    for attempt in range(1, 3):
        try:
            # gemini-2.5-flash 모델 사용 및 JSON 응답 강제
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
            
            required_keys = ["recommended_city", "weather", "events", "reason"]
            if all(k in data for k in required_keys):
                return data
            else:
                raise ValueError("JSON 필수 키 누락")

        except Exception as e:
            if attempt == 1:
                prompt += "\n\n[경고]: 유효한 JSON 포맷으로 정확한 키값을 포함하여 응답하세요."
            else:
                tracker.add_error(
                    step="llm_recommendation",
                    error_type="JSON_PARSE_ERROR",
                    message=f"LLM 파싱 최종 실패: {e}"
                )

    # 요청 날짜의 월(Month)을 확인하여 Fallback 예비 데이터 제공
    try:
        month = int(date_string.split("-")[1])
    except Exception:
        month = 8

    if month == 8:
        return {
            "recommended_city": "강원도 강릉시",
            "weather": "8월 중순은 무더운 성수기 여름 날씨로 피서하기에 좋은 시기입니다.",
            "events": ["강릉 경포 해수욕장 축제", "강릉 수제맥주 축제"],
            "reason": "8월 중순은 시원한 동해 바다와 경포대 해수욕장에서 여름 피서를 즐기기에 최고의 여행지입니다."
        }
    else:
        return {
            "recommended_city": "전라남도 광양시",
            "weather": "3월 중순은 온화한 봄바람이 불어오며 꽃놀이하기 좋은 날씨입니다.",
            "events": ["광양 매화축제"],
            "reason": "3월 중순은 매화꽃이 만개하는 시기로, 섬진강변의 아름다운 풍경을 산책하기에 최적의 여행지입니다."
        }