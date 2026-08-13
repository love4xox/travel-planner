import os
import requests
from errors.error_tracker import ErrorTracker

def search_places_for_cities(cities_info: list, tracker: ErrorTracker) -> dict:
    """
    여러 추천 도시 각각에 대해 반복문(루프)을 돌며 맛집을 검색합니다.
    """
    kakao_key = os.getenv("KAKAO_REST_API_KEY")
    results = {}

    if not kakao_key:
        tracker.add_error(
            step="place_search",
            error_type="AUTH_ERROR",
            message="KAKAO_REST_API_KEY 환경변수가 설정되지 않았습니다."
        )
        for c in cities_info:
            results[c["city"]] = []
        return results

    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {kakao_key.strip()}"}

    for c in cities_info:
        city_name = c.get("city", "")
        places = []
        params = {"query": f"{city_name} 맛집", "category_group_code": "FD6", "size": 5}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                documents = response.json().get("documents", [])
                for item in documents:
                    places.append({
                        "name": item.get("place_name", "이름 없음"),
                        "address": item.get("road_address_name") or item.get("address_name", "주소 없음"),
                        "category": item.get("category_name", "카테고리 없음"),
                        "url": item.get("place_url", ""),
                        "x": float(item.get("x", 0)),
                        "y": float(item.get("y", 0))
                    })
            else:
                tracker.add_error(
                    step="place_search",
                    error_type="API_ERROR",
                    message=f"[{city_name}] HTTP {response.status_code}"
                )
        except Exception as e:
            tracker.add_error(
                step="place_search",
                error_type="SYSTEM_ERROR",
                message=f"[{city_name}] {e}"
            )

        results[city_name] = places

    return results