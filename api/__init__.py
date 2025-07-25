"""
Soccer Analytics API

A flexible abstraction layer that provides natural language querying
capabilities over soccer data analysis functions.
"""

from .main_api import SoccerAnalyticsAPI
from .query_processor import QueryProcessor
from .analysis_router import AnalysisRouter
from .response_formatter import ResponseFormatter

__all__ = [
    'SoccerAnalyticsAPI',
    'QueryProcessor', 
    'AnalysisRouter',
    'ResponseFormatter'
]

__version__ = '1.0.0'