"""
환경변수(.env)에서 API 키를 불러오고 검증하는 모듈.

- API 키는 코드에 직접 작성하지 않는다. (보안)
- 필수 키가 없으면 즉시 프로그램 종료 (요구사항 6번)
"""

import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


def get_api_keys():
    """
    환경변수에서 API 키를 읽어온다.
    """
    return {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "KAKAO_REST_API_KEY": os.getenv("KAKAO_REST_API_KEY"),
    }


def validate_api_keys():
    """
    필수 API 키 존재 여부 확인.
    없으면 안내 메시지 출력 후 프로그램 종료.
    """
    keys = get_api_keys()
    missing_keys = [key for key, value in keys.items() if not value]

    if missing_keys:
        print("❌ 필수 API 키가 설정되지 않았습니다:")
        for key in missing_keys:
            print(f"   - {key}")

        print("\n📌 해결 방법:")
        print("   1. 프로젝트 루트에 .env 파일을 생성하세요.")
        print("   2. .env.example 파일을 참고하여 아래처럼 작성하세요.")
        print("      GEMINI_API_KEY=발급받은_키")
        print("      KAKAO_REST_API_KEY=발급받은_키")

        sys.exit(1)

    return keys