"""
FPL Report Package
=================

This package provides tools for analyzing Fantasy Premier League (FPL) data.
"""

__version__ = "1.0.0"
__author__ = "Tom"

# Import main modules for easier access
from .core.fpl_report_app import FPLReportApp
from .exceptions import FPLReportError, APIClientError, DataFetchError, DataProcessingError, ReportGenerationError

__all__ = [
    "FPLReportApp",
    "FPLReportError",
    "APIClientError", 
    "DataFetchError",
    "DataProcessingError",
    "ReportGenerationError"
]