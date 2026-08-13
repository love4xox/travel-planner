import os
import json
from errors.error_tracker import ErrorTracker

def generate_reports(date_str: str, cities_info: list, places_by_city: dict, tracker: ErrorTracker) -> str:
    os.makedirs("results", exist_ok=True)
    errors = tracker.get_errors()

    md_content = f"# {date_str} 국내 여행 추천 리포트 (복수 지역)\n\n"

    for idx, c in enumerate(cities_info, 1):
        city_name = c.get("city", "정보 없음")
        weather = c.get("weather", "정보 없음")
        reason = c.get("reason", "정보 없음")
        events = c.get("events", [])
        events_text = "\n".join([f"  - {e}" for e in events]) if events else "  - 정보 없음"

        places = places_by_city.get(city_name, [])
        if places:
            places_text = ""
            for p_idx, p in enumerate(places, 1):
                places_text += f"  {p_idx}. **{p['name']}** ({p['category']})\n"
                places_text += f"     - 주소: {p['address']}\n"
                places_text += f"     - 좌표: Lat {p['y']}, Lng {p['x']}\n"
                if p['url']:
                    places_text += f"     - 링크: {p['url']}\n"
        else:
            places_text = "  - 데이터 없음\n"

        md_content += f"## {idx}. {city_name}\n"
        md_content += f"- **추천 이유:** {reason}\n"
        md_content += f"- **날씨 요약:** {weather}\n"
        md_content += f"- **행사/축제:**\n{events_text}\n"
        md_content += f"- **맛집 추천:**\n{places_text}\n"
        md_content += f"- **1일 일정 제안:**\n"
        md_content += f"  - 오전: {city_name} 주요 명소 탐방\n"
        md_content += f"  - 점심: 추천 맛집 방문\n"
        md_content += f"  - 오후: 카페거리 및 지역 문화 공간 방문\n"
        md_content += f"  - 저녁: 지역 특산물 만찬 후 일과 정리\n\n"
        md_content += "---\n\n"

    # 오류 요약
    if errors:
        error_text = "\n".join([f"- [{err['step']}] {err['type']}: {err['message']}" for err in errors])
    else:
        error_text = "- 발생한 오류 없음 (정상 처리 완료)"

    md_content += f"## 오류 요약(errors)\n{error_text}\n"

    md_path = f"results/{date_str}_travel_plan.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    json_data = {
        "recommended_cities_info": cities_info,
        "places_by_city": places_by_city,
        "errors": errors
    }
    json_path = f"results/{date_str}_travel_plan.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    return md_path