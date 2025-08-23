from typing import Optional, Any

class FPLReportError(Exception):
    """Base exception for FPL Report application"""
    pass

class APIClientError(FPLReportError):
    """Exception raised for API client errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, url: Optional[str] = None) -> None:
        self.message = message
        self.status_code = status_code
        self.url = url
        super().__init__(self.message)

class DataFetchError(FPLReportError):
    """Exception raised when data cannot be fetched"""
    def __init__(self, message: str, source: Optional[str] = None) -> None:
        self.message = message
        self.source = source
        super().__init__(self.message)

class DataProcessingError(FPLReportError):
    """Exception raised during data processing"""
    def __init__(self, message: str, context: Optional[str] = None) -> None:
        self.message = message
        self.context = context
        super().__init__(self.message)

class ReportGenerationError(FPLReportError):
    """Exception raised during report generation"""
    def __init__(self, message: str, report_type: Optional[str] = None) -> None:
        self.message = message
        self.report_type = report_type
        super().__init__(self.message)