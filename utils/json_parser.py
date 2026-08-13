import json
import re

def parse_json_from_response(text: str) -> dict:
    """
    마크다운 코드 블록(```json ...)이 포함된 텍스트에서 순수 JSON만 추출해 파싱합니다.
    """
    clean_text = re.sub(r"```json\s*|\s*```", "", text).strip()
    return json.loads(clean_text)