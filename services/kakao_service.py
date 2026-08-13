import os
import requests
from errors.error_tracker import ErrorTracker

def search_places_by_keyword(keyword: str, tracker: ErrorTracker, category: str = "FD6", size: int = 5) -> list:
    """
    Kakao Local API로 맛집을 검색합니다.
    오류가 발생하거나 결과가 0건이어도 중단 없이 에러를 기록하고 빈 리스트를 반환합니다.
    """
    places = []
    kakao_key = os.getenv("KAKAO_REST_API_KEY")

    if not kakao_key:
        tracker.add_error(
            step="place_search",
            error_type="AUTH_ERROR",
            message="KAKAO_REST_API_KEY 환경변수가 설정되지 않았습니다."
        )
        return places

    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {kakao_key.strip()}"}
    params = {"query": f"{keyword} 맛집", "category_group_code": category, "size": size}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        
        # 인증 오류 (401/403)
        if response.status_code in [401, 403]:
            print(f"    - 지도 API 오류: 인증 실패({response.status_code}). '데이터 없음'으로 처리합니다.")
            tracker.add_error(
                step="place_search",
                error_type="AUTH_ERROR",
                message=f"HTTP {response.status_code}"
            )
            return places
            
        elif response.status_code != 200:
            tracker.add_error(
                step="place_search",
                error_type="API_ERROR",
                message=f"HTTP {response.status_code}"
            )
            return places

        data = response.json()
        documents = data.get("documents", [])
        
        # 검색 결과 0건
        if not documents:
            print("    - 검색 결과 0건 (데이터 없음 처리)")
            tracker.add_error(
                step="place_search",
                error_type="EMPTY_RESULT",
                message=f"0 results for query={keyword} 맛집"
            )
            return places

        for item in documents:
            places.append({
                "name": item.get("place_name", "이름 없음"),
                "address": item.get("road_address_name") or item.get("address_name", "주소 없음"),
                "category": item.get("category_name", "카테고리 없음"),
                "url": item.get("place_url", ""),
                "x": float(item.get("x", 0)), # 경도 (lng)
                "y": float(item.get("y", 0))  # 위도 (lat)
            })

    except Exception as e:
        tracker.add_error(
            step="place_search",
            error_type="SYSTEM_ERROR",
            message=str(e)
        )

    return places