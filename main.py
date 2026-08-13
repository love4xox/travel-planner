import argparse
import sys
from utils.validator import validate_date
from config.settings import validate_api_keys
from errors.error_tracker import ErrorTracker
from services.gemini_service import get_travel_recommendation_json
from services.kakao_service import search_places_by_keyword
from services.report_generator import generate_reports

def main():
    # API 키 존재 여부 확인
    validate_api_keys()

    # CLI 인자 설정
    parser = argparse.ArgumentParser(
        description="Travel Planner CLI",
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

    # 입력 날짜 검증
    if not validate_date(date_str):
        print("\n❌ [입력 오류] 날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)")
        parser.print_help()
        sys.exit(1)

    # 에러 추적 객체 생성
    tracker = ErrorTracker()

    # [1/3] LLM 1차 추천 생성
    print(f"\n[1/3] 1차 추천 생성 중(LLM)...")
    city_info = get_travel_recommendation_json(date_str, tracker)
    rec_city = city_info.get("recommended_city", "정보 없음")
    print(f"    - recommended_city: \"{rec_city}\"")

    # [2/3] 맛집 검색 (지도/장소 API)
    print(f"[2/3] 맛집 검색 중(지도/장소 API)...")
    places = search_places_by_keyword(rec_city, tracker)

    if places:
        print(f"    - 맛집 {len(places)}곳 검색 완료")
    else:
        print("    - 맛집 검색 데이터 없음 (다음 단계로 계속 진행합니다.)")

    # [3/3] 최종 리포트 및 JSON 생성
    print(f"[3/3] 최종 리포트 생성 중(LLM/Report)...")
    report_path = generate_reports(date_str, city_info, places, tracker)
    print(f"    - 리포트 생성 완료")

    print(f"\n완료! {report_path} 를 확인하세요.\n")

if __name__ == "__main__":
    main()