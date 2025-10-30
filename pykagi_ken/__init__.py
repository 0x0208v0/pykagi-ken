"""
pykagi-ken: Python library for Kagi.com services

Access Kagi.com search and summarizer using session tokens.

This is a Python port of the kagi-ken ecosystem by Carlo Zottmann.
See https://github.com/czottmann/kagi-ken for the original Node.js implementation.
"""

from pykagi_ken.constants import SUPPORTED_LANGUAGES
from pykagi_ken.search import search
from pykagi_ken.summarize import summarize

__version__ = "0.0.1"

__all__ = [
    "search",
    "summarize",
    "SUPPORTED_LANGUAGES",
]
