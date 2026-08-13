import os
import json
from errors.error_tracker import ErrorTracker

def generate_reports(date_str: str, city_info: dict, places: list, tracker: ErrorTracker) -> str:
    """
    최종 리포트(.md) 및 원본 데이터(.json)를 results/ 폴더에 저장합니다.
    """
    os.makedirs("results", exist_ok=True)
    errors = tracker.get_errors()

    # 1. 맛집 추천 텍스트
    if places:
        places_text = ""
        for idx, p in enumerate(places, 1):
            places_text += f"{idx}. **{p['name']}** ({p['category']})\n"
            places_text += f"   - 주소: {p['address']}\n"
            places_text += f"   - 좌표: Lat {p['y']}, Lng {p['x']}\n"
            if p['url']:
                places_text += f"   - 링크: {p['url']}\n"
            places_text += "\n"
    else:
        places_text = "- 데이터 없음 (장소 검색 결과 0건 또는 API 오류 발생)\n"

    # 2. 오류 요약 텍스트
    if errors:
        error_text = ""
        for err in errors:
            error_text += f"- [{err['step']}] {err['type']}: {err['message']}\n"
    else:
        error_text = "- 발생한 오류 없음 (정상 처리 완료)\n"

    # 3. 행사/축제 텍스트
    events = city_info.get("events", [])
    events_text = "\n".join([f"- {e}" for e in events]) if events else "- 정보 없음"

    # 4. Markdown 문서 구성
    md_content = f"""# {date_str} 국내 여행 추천 리포트

## 추천 지역
- **{city_info.get('recommended_city', '정보 없음')}**

## 추천 이유
{city_info.get('reason', '정보 없음')}

## 날씨 요약
{city_info.get('weather', '정보 없음')}

## 행사/축제 목록
{events_text}

## 맛집 추천
{places_text.strip()}

## 1일 일정 제안
- **오전:** {city_info.get('recommended_city')} 대표 명소 탐방 및 산책
- **점심:** 추천 지역 맛집 방문
- **오후:** 주요 관광 명소 및 시내 카페 방문
- **저녁:** 지역 특산물 만찬 후 일정 정리

## 오류 요약(errors)
{error_text.strip()}
"""

    md_path = f"results/{date_str}_travel_plan.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 5. 원본 JSON 파일 구성
    json_data = {
        "recommended_city_info": city_info,
        "places": places,
        "errors": errors
    }
    json_path = f"results/{date_str}_travel_plan.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    return md_path