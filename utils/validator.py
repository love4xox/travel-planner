import re

def validate_date(date_string: str) -> bool:
    """
    입력된 날짜 문자열이 YYYY-MM-DD 형식에 맞는지 검증합니다.
    """
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    return bool(re.match(pattern, date_string))