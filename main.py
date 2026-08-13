import os
import json
import argparse
import sys
from utils.validator import validate_date
from config.settings import validate_api_keys
from errors.error_tracker import ErrorTracker
from services.gemini_service import get_travel_recommendations_json
from services.kakao_service import search_places_for_cities
from services.report_generator import generate_reports

def main():
    validate_api_keys()

    parser = argparse.ArgumentParser(
        description="Travel Planner CLI (Bonus Feature Included)",
        usage="python main.py -date \"YYYY-MM-DD\""
    )
    
    parser.add_argument(
        "-date", "--date",
        type=str,
        required=True,
        help="여행 날짜 (YYYY-MM-DD)"
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        parser.print_help()
        sys.exit(1)

    date_str = args.date

    if not validate_date(date_str):
        print("\n❌ [입력 오류] 날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)")
        parser.print_help()
        sys.exit(1)

    cache_json_path = f"results/{date_str}_travel_plan.json"
    tracker = ErrorTracker()

    # 💡 [보너스 과제] 결과 캐싱 검사
    if os.path.exists(cache_json_path):
        print(f"\n⚡ [캐시 발견] '{cache_json_path}' 기존 데이터가 존재합니다. API 호출을 건너뛰고 캐시된 결과를 불러옵니다.")
        with open(cache_json_path, "r", encoding="utf-8") as f:
            cached_data = json.load(f)
        
        cities_info = cached_data.get("recommended_cities_info", [])
        places_by_city = cached_data.get("places_by_city", {})
        
        report_path = generate_reports(date_str, cities_info, places_by_city, tracker)
        print(f"    - 캐시 기반 리포트 재생성 완료: {report_path}\n")
        return

    # [1/3] 복수 도시 추천 (LLM API)
    print(f"\n[1/3] 1차 추천 생성 중(LLM - 복수 지역)...")
    cities_data = get_travel_recommendations_json(date_str, tracker)
    cities_info = cities_data.get("recommended_cities", [])
    city_names = [c["city"] for c in cities_info]
    print(f"    - recommended_cities: {city_names}")

    # [2/3] 지역별 맛집 검색 (지도 API 반복 루프)
    print(f"[2/3] 맛집 검색 중(지도/장소 API 루프)...")
    places_by_city = search_places_for_cities(cities_info, tracker)
    for c_name, p_list in places_by_city.items():
        print(f"    - [{c_name}] 맛집 {len(p_list)}곳 검색 완료")

    # [3/3] 최종 리포트 및 캐시 저장
    print(f"[3/3] 최종 리포트 저장 중...")
    report_path = generate_reports(date_str, cities_info, places_by_city, tracker)

    print(f"\n완료! {report_path} 를 확인하세요.\n")

if __name__ == "__main__":
    main()