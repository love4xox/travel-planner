import os
import json
import re
from google import genai
from errors.error_tracker import ErrorTracker

def get_travel_recommendation_json(date_string: str, tracker: ErrorTracker) -> dict:
    """
    Gemini API를 호출하여 1차 추천 결과를 JSON으로 받아옵니다.
    파싱 실패 시 최대 1회 재시도합니다.
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    당신은 전문 한국 여행 가이드입니다.
    사용자가 요청한 여행 날짜({date_string})에 어울리는 국내 여행지 1곳을 추천해 주세요.

    반드시 다른 설명 없이 아래 JSON 포맷으로만 응답하세요:
    {{
      "recommended_city": "도시명 (예: 제주, 강릉, 광양)",
      "weather": "해당 시기 일반적 날씨 요약 1~2문장",
      "events": ["행사 또는 축제 후보 1", "행사 또는 축제 후보 2"],
      "reason": "추천 근거 2~4문장"
    }}
    """

    for attempt in range(1, 3):  # 최초 1회 + 재시도 1회 (최대 2회)
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            raw_text = response.text.strip()
            clean_json_str = re.sub(r"```json\s*|\s*```", "", raw_text).strip()
            data = json.loads(clean_json_str)
            
            required_keys = ["recommended_city", "weather", "events", "reason"]
            if all(k in data for k in required_keys):
                return data
            else:
                raise ValueError("JSON에 필수 키가 누락되었습니다.")

        except Exception as e:
            if attempt == 1:
                prompt += "\n\n[경고]: 이전 응답이 유효한 JSON 포맷이 아니었습니다. 반드시 오직 순수한 JSON 객체만 반환해 주세요."
            else:
                tracker.add_error(
                    step="llm_recommendation",
                    error_type="JSON_PARSE_ERROR",
                    message=f"최대 재시도(1회) 초과 후 파싱 실패: {e}"
                )

    # 파싱 최종 실패 시 Fallback 기본 데이터 제공
    return {
        "recommended_city": "강릉",
        "weather": "날씨 정보를 불러오지 못했습니다.",
        "events": [],
        "reason": "LLM 응답 파싱 실패로 기본 추천 지역이 설정되었습니다."
    }