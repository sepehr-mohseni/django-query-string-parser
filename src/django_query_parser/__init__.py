"""
Django Query Parser - Convert query strings into Django Q objects
"""

from .parser import DjangoQueryParser, QueryTranslator

__version__ = "0.1.0"
__all__ = ["DjangoQueryParser", "QueryTranslator"]
