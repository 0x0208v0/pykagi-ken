# AGENTS.md

This file provides guidance to LLM agents when working with code in this repository.

**Note**: This is a Python port of [kagi-ken](https://github.com/czottmann/kagi-ken) v1.2.0 and [kagi-ken-cli](https://github.com/czottmann/kagi-ken-cli) v1.6.0 by Carlo Zottmann.

## Project Overview

pykagi-ken is a Python library and CLI tool that provides programmatic access to Kagi.com services (search and summarizer) using session tokens. It outputs structured JSON matching official API schemas, serving as an alternative to the official Kagi API that requires invite-only API keys.

## Architecture

### Core Structure

- **pykagi_ken/__init__.py**: Main entry point exporting `search`, `summarize`, and `SUPPORTED_LANGUAGES`
- **pykagi_ken/search.py**: Kagi search functionality using HTML parsing with parsel
- **pykagi_ken/summarize.py**: Kagi summarizer functionality using streaming JSON API
- **pykagi_ken/cli.py**: Command-line interface using click
- **pykagi_ken/constants.py**: Shared constants (USER_AGENT, SUPPORTED_LANGUAGES)
- **pykagi_ken/exceptions.py**: Custom exception hierarchy

### Key Design Patterns

#### API Authentication

Both modules use session-based authentication via Cookie headers:

```python
headers = {
    "Cookie": f"kagi_session={token}",
    "User-Agent": USER_AGENT,
}
```

#### Error Handling Strategy

Consistent error handling across both services:

- Parameter validation (type and presence checks)
- Network error detection (connection errors, timeouts)
- HTTP status code handling (401/403 for auth, others for general errors)
- Parsing error recovery with informative messages

#### Search Result Parsing (pykagi_ken/search.py)

HTML parsing strategy using parsel CSS selectors:

- **Main results**: `.search-result` elements → extract URL, title, snippet
- **Grouped results**: `.sr-group .__srgi` elements → extract grouped items
- **Related searches**: `.related-searches a span` elements
- Results use type indicator `t: 0` for search results, `t: 1` for related searches

#### Summarizer Streaming (pykagi_ken/summarize.py)

Handles Kagi's streaming response format:

- **URL summarization**: GET request with query parameters
- **Text summarization**: POST request with form data
- **Stream parsing**: Splits by NUL bytes (`\x00`), extracts final JSON message
- **Output extraction**: `output_data.markdown` → `data.output`

### HTTP Endpoints

- **Search**: `https://kagi.com/html/search?q=${query}` (HTML response)
- **Summarizer**: `https://kagi.com/mother/summary_labs` (streaming JSON)

### Dependencies

- **parsel**: HTML parsing for search results
- **aiohttp**: Async HTTP requests (Python 3.10+ required)
- **click**: CLI framework (optional dependency)

## Development Commands

```bash
# Install dependencies
pip install -e ".[cli,dev]"

# Run CLI
pykagi-ken-cli search "python programming"
pykagi-ken-cli summarize --url "https://example.com"

# Lint and format
ruff check .
ruff format .
```

## Session Token Authentication

Critical for development: Get session tokens from Kagi Settings → Session Link. Extract the `token` value from the URL for use in function calls.

## File Modification Guidelines

### When Modifying Search Logic (pykagi_ken/search.py)

- **HTML selectors**: Update CSS selectors if Kagi changes their HTML structure
- **Result extraction**: Maintain the `{t: 0, url, title, snippet}` format for API compatibility
- **Error handling**: Follow existing pattern of returning `None` for individual parsing failures

### When Modifying Summarizer Logic (pykagi_ken/summarize.py)

- **Stream parsing**: The NUL-byte splitting and "final:" prefix handling is critical for response parsing
- **Request format**: URL vs text requests use different HTTP methods and headers
- **Language validation**: Update `SUPPORTED_LANGUAGES` array if Kagi adds new languages

### Adding New Features

- Follow async/await pattern with type hints
- Add parameter validation at function entry points
- Use consistent error message format
- Export new functions through __init__.py
- Maintain compatibility with official Kagi API response schemas

## Key Implementation Details

- **Async/Await**: Uses Python's async/await throughout with aiohttp
- **Safari User Agent**: Mimics Safari browser for compatibility
- **Session Authentication**: No API keys needed, uses existing Kagi login session
- **Streaming Response**: Summarizer uses Kagi's streaming protocol with NUL-byte delimiters
- **Error Recovery**: Graceful degradation when parsing individual results fails

