# LangChain Python Docs MCP Server

[English](#english) | [中文](#chinese)

---

<a id="english"></a>
## 📖 Project Overview

This is a **Model Context Protocol (MCP)** server designed to let AI assistants (like Claude, Cursor, etc.) query the latest [LangChain Python Documentation](https://docs.langchain.com/oss/python/langchain/overview).

It consists of two main components:
1.  **Smart Crawler**: A `crawl4ai` based crawler that navigates the Mintlify-based documentation site (`docs.langchain.com`), handling dynamic content loading and extracting clean Markdown.
2.  **Fast MCP Server**: A high-performance server that loads the crawled documentation into memory and provides instant, scored search results via the `query_docs` tool.

## 🚀 Features

-   **Sitemap-Based Discovery**: Automatically discovers all pages via `sitemap.xml`, ensuring 100% coverage of the `oss/python` section.
-   **Mintlify Optimized**: Specifically tuned to handle the structure of the new `docs.langchain.com` site, including lazy-loaded sidebars and specific content selectors.
-   **Clean Extraction**: Heuristic cleaning removes "Copy" buttons, navigational footers, and "Skip to content" links.
-   **In-Memory Search**: Preloads all documentation (~150+ files) into RAM for sub-millisecond search latencies.
-   **Relevance Scoring**: Custom ranking algorithm prioritizes Title Matches > Phrase Matches > Term Frequency.

## 🛠️ Installation

### Prerequisites
-   Python 3.10+
-   `uv` (Recommended) or `pip`

### Setup Steps

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd langchain_doc
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    # Or with pip: pip install -r requirements.txt (if generated)
    ```

3.  **Install Browser (for Crawler)**:
    The crawler uses Playwright. You need to install the browser binaries:
    ```bash
    uv run playwright install chromium
    ```

## 🏃‍♂️ Usage

### 1. Crawl the Documentation
Before running the server, you must populate the local data store.

**Full Crawl (Recommended)**:
```bash
uv run src/crawler.py --all
```

**Test Crawl (First 50 pages)**:
```bash
uv run src/crawler.py --limit 50
```

*Data will be saved to `data/docs/*.md`.*

### 2. Verify the Server
Check if the server can find the documents you just crawled:
```bash
uv run test_server.py
```

### 3. Run the Server
To start the MCP server (typically used by an MCP client):
```bash
uv run src/server.py
```

## 🔌 Integration (Clause Desktop / Cursor)

Add this configuration to your MCP settings file (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "langchain-docs": {
      "command": "uv",
      "args": [
        "run",
        "/absolute/path/to/langchain_doc/src/server.py"
      ]
    }
  }
}
```

---

<a id="chinese"></a>
## 📖 项目概览 (Chinese)

这是一个 **Model Context Protocol (MCP)** 服务器，旨在让 AI 助手（如 Claude, Cursor 等）能够通过工具调用查询最新的 [LangChain Python 文档](https://docs.langchain.com/oss/python/langchain/overview)。

核心组件：
1.  **智能爬虫**: 基于 `crawl4ai` 开发，能够处理 Mintlify 架构的动态网页，自动通过 Sitemap 发现页面并提取纯净的 Markdown。
2.  **高速 MCP 服务器**: 将爬取的文档全量加载至内存，通过加权算法提供毫秒级的本地搜索响应。

## 🚀 功能特性

-   **覆盖全**: 利用 `sitemap.xml` 自动发现 `docs.langchain.com/oss/python/` 下的所有文档。
-   **抗干扰**: 针对 Mintlify 页面结构优化，自动去除导航栏、页脚、复制按钮等噪音。
-   **高性能**: 启动时将本地 Markdown 文件预加载到内存，避免运行时磁盘 IO。
-   **搜索优化**: 实现了简单的关键词加权排序（标题匹配 > 短语匹配 > 词频）。

## 🛠️ 安装与配置

### 前置要求
-   Python 3.10+
-   `uv` (推荐)

### 快速开始

1.  **安装依赖**:
    ```bash
    uv sync
    ```

2.  **安装浏览器驱动**:
    ```bash
    uv run playwright install chromium
    ```

3.  **执行爬虫**:
    ```bash
    # 爬取所有文档
    uv run src/crawler.py --all
    ```

4.  **运行测试**:
    ```bash
    uv run test_server.py
    ```

## 🔌 接入配置

在你的 MCP 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "langchain-docs": {
      "command": "uv",
      "args": [
        "run",
        "你的项目绝对路径/src/server.py"
      ]
    }
  }
}
```
