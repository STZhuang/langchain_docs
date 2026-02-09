"""Shared project configuration constants."""

from pathlib import Path

BASE_URL = "https://docs.langchain.com/oss/python/langchain/overview"
SITEMAP_URL = "https://docs.langchain.com/sitemap.xml"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "data" / "docs"
