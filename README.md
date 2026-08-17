# ✈️ AI 기반 맞춤형 여행 일정 및 맛집 추천 시스템 (Travel Planner)

Google Gemini LLM과 Kakao Local REST API를 연계하여, 사용자가 입력한 여행 날짜에 맞춰 최적의 여행지와 계절 축제 정보를 추천받고 주변 맛집 정보를 자동으로 수집·제공하는 자동화 CLI 파이프라인 프로그램입니다.

---

## 🎯 과제 목표 및 핵심 기술 개념

1. **REST API 요청/응답 구조 및 HTTP 메서드 (GET vs POST)**
   - **Request/Response**: 클라이언트의 인증 헤더(API Key), 파라미터를 담은 요청에 대해 서버가 상태 코드(200, 400, 403 등)와 JSON 응답 본문을 반환하는 구조를 이해하고 구현합니다.
   - **GET vs POST**: 장소 정보를 단순히 조회하는 카카오 API는 `GET` 방식을 사용하고, 긴 프롬프트와 옵션을 전달하여 새로운 추천을 생성하는 Gemini API는 `POST` 방식을 사용합니다.

2. **LLM 출력의 JSON 구조화 및 데이터 파이프라인 연계**
   - 비정형 자연어 텍스트 대신 `JSON Schema`를 강제하여 `recommended_cities` 형태의 정형 데이터를 수신합니다.
   - 파싱된 도시명(`city`)을 카카오 로컬 검색 API의 입력 파라미터(`query`)로 동적 전달하여 끊김 없는 데이터 파이프라인을 완성합니다.

3. **외부 API 예외 처리 및 에러 트래킹**
   - 인증 실패, 쿼터 제한(429), 네트워크 장애, JSON 파싱 실패 등 외부 API 통신 중 발생 가능한 오류에 대비해 `ErrorTracker` 및 Fallback 데이터를 설계하여 프로그램 안정성을 확보합니다.

4. **API 키 환경변수(`.env`) 관리 및 보안**
   - 소스 코드 하드코딩을 방지하고 `python-dotenv`를 통해 로컬 환경변수로 키를 관리하며, `.gitignore`를 통해 저장소 유출을 방지합니다.

---

## 📂 프로젝트 구조 (Project Structure)

```text
travel-planner/
├── config/
│   ├── __init__.py
│   └── settings.py             # 환경변수 로드 및 API 키 유효성 검증
├── errors/
│   ├── __init__.py
│   └── error_tracker.py        # API 장애 및 런타임 에러 추적/로깅
├── results/                    # 실행 날짜별 JSON 및 MD 결과물 저장소
├── services/
│   ├── __init__.py
│   ├── gemini_service.py       # Google Gemini LLM 여행지 추천 연동
│   ├── kakao_service.py        # Kakao Local REST API 맛집 검색 통신
│   └── report_generator.py     # 최종 마크다운 리포트 생성
├── utils/
│   ├── __init__.py
│   ├── file_writer.py          # 파일 저장 유틸
│   ├── json_parser.py          # JSON 역직렬화 및 텍스트 정제
│   ├── logger.py               # 콘솔 로깅 유틸
│   └── validator.py            # CLI 날짜 포맷(YYYY-MM-DD) 유효성 검증
├── .env                        # API 키 보관 파일 (Git 추적 제외)
├── .env.example                # 환경변수 예시 템플릿
├── .gitignore                  # Git 제외 설정 파일
├── main.py                     # CLI 인자 파싱 및 파이프라인 실행 메인 파일
├── README.md                   # 프로젝트 문서
└── requirements.txt            # 필수 의존성 패키지 목록
```

---

## ⚙️ 사전 설정 및 실행 방법
1. **API 키 발급 및 .env 파일 생성**
- 프로젝트 루트 디렉토리에 .env 파일을 생성하고 발급받은 API 키를 입력합니다.

```text
GEMINI_API_KEY=your_gemini_api_key_here
KAKAO_REST_API_KEY=your_kakao_rest_api_key_here
```

⚠️ 필수 보안 수칙:
- Kakao Developers 콘솔의 [제품 설정] > [카카오맵] 메뉴에서 사용 설정(ON) 상태를 반드시 확인해야 합니다.
- .gitignore에 .env를 등록하여 GitHub 등 공개 저장소에 키가 커밋되지 않도록 관리합니다.

2. **필수 라이브러리 설치**
- pip install -r requirements.txt 또는 직접 설치

```text
pip install python-dotenv google-genai requests
```

3. **CLI 실행 명령어**
- YYYY-MM-DD 형식으로 원하는 여행 날짜를 지정하여 실행
```text
python main.py -date "2026-03-15"
```

---

## 🛠️ 기능 구현 및 문제 해결 (Troubleshooting)
1. **CLI 인터페이스 및 입력값 검증 (main.py, utils/validator.py)**
- **구현 내용**: argparse 모듈로 -date "YYYY-MM-DD" 인자를 수신하고 정규식 포맷 검증 수행.
- **발생 오류**: 초기 실행 시 python 인터프리터 명령어 누락으로 인한 실행 불가 오류가 발생하였으며, CLI 파라미터 규칙(-date)과 다른 --date 입력 및 인자 설정 불일치로 인해 argparse 필수 인자 누락 에러 발생.
- **조치**: python main.py -date ... 정규 명령어로 실행하고 argparse 파서 규칙을 단일 대시(-date)로 통일하여 해결.

2. **Gemini LLM 1차 추천 연동 (services/gemini_service.py)**
- **구현 내용**: 추천 도시, 계절 날씨, 행사 축제, 추천 사유를 갖는 JSON 구조화 데이터 생성.
- **발생 오류**: services/gemini_service.py 20번째 줄 client 선언부의 들여쓰기 공백 불일치(IndentationError)와 더불어, 지원이 종료되었거나 명칭이 변경되어 유효하지 않은 비표준 모델명(gemini-2.5-flash) 호출로 인해 Google API 서버로부터 404 NOT_FOUND 오류가 연달아 반환됨.
- **조치**: 코드 들여쓰기 라인을 재정렬하고, 공식 지원 최신 모델명으로 코드를 수정하여 정상 통신 확보.

3. **Kakao Local REST API 맛집 검색 연동 (services/kakao_service.py)**
- **구현 내용**: Gemini가 반환한 도시명을 전달받아 상위 5개 맛집(상호, 주소, 카테고리, URL, 좌표) 조회.
- **발생 오류**: 카카오 로컬 서비스 비활성화로 인한 403 NotAuthorizedError (disabled OPEN_MAP_AND_LOCAL service) 발생.
- **조치**: Kakao Developers 콘솔의 [제품 설정] > [카카오맵] 사용 설정을 'ON'으로 활성화하여 일간 무료 쿼터 권한 확보.

4. **에러 트래커 개발 및 안정적인 예외 처리 (errors/error_tracker.py)**
- **구현 내용**: API 통신 에러 및 파싱 실패 시 ErrorTracker에 기록하고 Fallback 데이터로 안전 전환.
- **발생 오류**: 에러 수집 모듈 작성 중 def get_errors((self)) -> list: 선언부의 괄호 중복으로 인한 SyntaxError 발생.
- **조치**: def get_errors(self) -> list: 형태로 괄호를 올바르게 수정하여 모듈 정상 임포트 완료.

---

## 🎁 보너스 과제 구현 (Bonus Features)
**복수 지역 추천 및 다중 파이프라인 확장**
- 1차 추천 JSON 스키마를 recommended_cities 배열(2~3개 도시)로 확장.
- 반복문(for)을 통해 각 도시별 카카오 맛집 API를 순차 호출하고, 최종 리포트에 지역별로 체계적으로 분리 정리.

**파일 기반 결과 캐싱 (Result Caching)**
- 동일한 -date로 재실행 시, results/ 폴더 내 기존 원본 JSON(YYYY-MM-DD_travel_plan.json) 존재 여부를 확인.
- 캐시가 존재하면 외부 API 중복 호출을 건너뛰고 기존 데이터를 로드하여 실행 속도 최적화 및 API 쿼터 절약.

---

## 📄 결과물 저장 (Output)
- 프로그램 실행 완료 시 results/ 디렉토리에 2종의 결과 파일이 자동 생성됩니다.
- results/YYYY-MM-DD_travel_plan.json: 원본 데이터, 맛집 목록 및 errors 목록을 포함한 정형 데이터
- results/YYYY-MM-DD_travel_plan.md: 서식이 적용된 최종 여행 계획서 마크다운 리포트

---

## 💡 학습 성과 및 느낀 점 (Key Learnings)
🔗 **이종(異種) API 간 데이터 파이프라인 연계 및 정형화(JSON) 체득**
- LLM의 줄글 응답 대신 정형화된 JSON 스키마 출력을 강제하는 법을 익혔습니다.
- AI가 추출한 도시명을 컴퓨터가 파싱하여 곧바로 카카오 지도 API의 검색 파라미터로 넘겨주는 자동화 흐름(End-to-End 파이프라인)을 구현하며 서비스 간 데이터 연계 원리를 배웠습니다.

🛡️ **외부 API 장애 대응 원칙과 방어적 프로그래밍(Fallback) 습득**
- 권한 에러(403), 모델 에러(404), 문법 오류 등 실제 통신 장애 상황을 해결해 보았습니다.
- 에러 발생 시 프로그램이 멈추지 않도록 ErrorTracker로 기록하고 비상용 예비 데이터(Fallback)로 안전하게 전환하여 최종 결과물 작성을 완주시키는 예외 처리 기법을 체득했습니다.

🔒 **환경변수 보안 관리와 캐싱을 통한 성능 최적화**
- API 키를 코드에 노출하지 않고 .env 및 .gitignore를 통해 격리 관리하는 실무 보안 규칙을 익혔습니다.
- 이미 실행했던 날짜의 결과를 재활용하는 파일 기반 캐싱(Caching)을 적용하여 불필요한 API 호출 비용과 할당량을 아끼고 응답 속도를 최적화하는 감각을 길렀습니다.