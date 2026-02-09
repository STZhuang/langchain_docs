# AGENTS.md - LangChain Docs MCP Server

**Generated:** 2025-01-09
**Project Type:** Python MCP Server + Web Crawler
**Package Manager:** uv

## OVERVIEW
MCP server that crawls LangChain Python docs and provides instant search via `query_docs` tool.

## STRUCTURE
```
.
├── src/
│   ├── crawler.py    # crawl4ai-based Mintlify scraper
│   ├── server.py     # FastMCP server with in-memory search
│   ├── config.py     # Shared constants (URL, paths)
│   └── __init__.py   # Package marker
├── tests/
│   └── test_server.py    # Smoke tests
└── data/docs/        # Crawled markdown cache (~150 files)
```

## KEY COMPONENTS

| File | Purpose | Entry Point |
|------|---------|-------------|
| `src/crawler.py` | Scrapes docs.langchain.com/oss/python/ | `uv run src/crawler.py --all` |
| `src/server.py` | MCP server exposing `query_docs` tool | `uv run src/server.py` |
| `src/config.py` | BASE_URL, SITEMAP_URL, DOCS_DIR | Imported by crawler/server |

## WHERE TO LOOK

| Task | Look In | Notes |
|------|---------|-------|
| Change crawl behavior | `src/crawler.py` | Mintlify-specific cleaning logic |
| Modify search ranking | `src/server.py:search_docs()` | Scoring: title(20) > phrase(10) > term(freq) |
| Add MCP tools | `src/server.py` | Use `@mcp.tool()` decorator |
| Update config | `src/config.py` | Centralized constants |
| Run tests | `tests/test_server.py` | `uv run python -m tests.test_server` |

## CONVENTIONS

**Code Style:**
- Python 3.13+ with `uv` package manager
- No explicit linting config (add ruff/black if needed)
- Type hints optional but encouraged for public APIs

**File Organization:**
- `src/` = implementation
- `tests/` = tests (import from `src.`)
- `data/docs/` = auto-generated cache (gitignored)

**Configuration:**
- Constants in `src/config.py` using `pathlib.Path`
- No env vars; all config is code

## ANTI-PATTERNS

**DO NOT:**
- Hardcode URLs/paths in crawler or server (use `config.py`)
- Commit `data/docs/` (already gitignored)
- Run crawler without `--limit` or `--all` (defaults to 300)
- Use `test_server.py` directly (run as module: `python -m tests.test_server`)

**MINTIFLY CRAWLER GOTCHAS:**
- Pages need 2s JS wait for sidebar (`js_wait_sidebar`)
- Must clean: "Copy page", "Skip to main content", "Was this page helpful?"
- URL filter: only `/oss/python/` paths

## COMMANDS

```bash
# Install deps
uv sync

# Install browser for crawler
uv run playwright install chromium

# Crawl all docs
uv run src/crawler.py --all

# Crawl limited (test)
uv run src/crawler.py --limit 50

# Run MCP server
uv run src/server.py

# Test search
uv run python -m tests.test_server
```

## DEPENDENCIES

**Core:**
- `mcp` - FastMCP framework
- `crawl4ai` - Async web crawler
- `playwright` - Browser automation
- `httpx` - HTTP client
- `beautifulsoup4`, `html2text` - HTML parsing

**See:** `pyproject.toml` for full list

## INTEGRATION

MCP clients (Claude Desktop, Cursor) connect via:
```json
{
  "mcpServers": {
    "langchain-docs": {
      "command": "uv",
      "args": ["run", "/absolute/path/src/server.py"]
    }
  }
}
```
