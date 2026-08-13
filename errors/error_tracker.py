class ErrorTracker:
    """
    프로그램 수행 중 발생하는 단계별 오류(LLM, 지도 API 등)를 
    중앙에서 기록하고 관리하는 추적기 클래스.
    """
    def __init__(self):
        self._errors = []

    def add_error(self, step: str, error_type: str, message: str):
        """오류 항목을 추가합니다."""
        self._errors.append({
            "step": step,
            "type": error_type,
            "message": message
        })

    def get_errors(self) -> list:
        """기록된 모든 오류 목록을 반환합니다."""
        return self._errors

    def has_errors(self) -> bool:
        """오류 존재 여부를 반환합니다."""
        return len(self._errors) > 0

    def clear(self):
        """기록된 오류 초기화"""
        self._errors = []