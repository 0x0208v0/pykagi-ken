# pykagi-ken

A lightweight Python library and CLI tool providing programmatic access to Kagi.com services using session tokens:

- **Search**: Searches Kagi.com and returns structured JSON data matching Kagi's official search API schema
- **Summarizer**: Uses Kagi's Summarizer to create summaries from URLs or text content

Unlike the official Kagi API which requires API access, this package uses your existing Kagi session to access both search and summarization features programmatically.

_"Kagi-ken"_ is a portmanteau of _"Kagi"_ (the service) and _"token"_.

## Why?

The [Kagi API](https://help.kagi.com/kagi/api/overview.html) requires a separate API key, which are invite-only at the moment. If you already have a Kagi subscription and want to programmatically access Kagi's services from your applications, this package provides an alternative by:

- Using your existing Kagi session token (no additional API costs)
- Parsing Kagi's HTML search results into structured JSON (matching official API format)
- Accessing Kagi's Summarizer for URL and text summarization
- Providing both a Python library API and a CLI interface

## Installation

```bash
pip install pykagi-ken[cli]
```

## Usage

```python
import asyncio
from pykagi_ken import search, summarize, SUPPORTED_LANGUAGES

async def main():
    token = "YOUR_KAGI_SESSION_TOKEN"

    # Search example
    search_results = await search("steve jobs", token)
    print(search_results)

    # Summarize URL example
    url_summary = await summarize(
        "https://en.wikipedia.org/wiki/Steve_Jobs",
        token,
        summary_type="summary",
        target_language="EN",
        is_url=True
    )
    print(url_summary)

    # Summarize text example
    text_summary = await summarize(
        "Long article content...",
        token,
        summary_type="takeaway",
        target_language="DE",
        is_url=False
    )
    print(text_summary)

asyncio.run(main())
```

## CLI Usage

```bash
# Set your session token once
echo "YOUR_KAGI_SESSION_TOKEN" > ~/.kagi_session_token

# Search and get JSON results
pykagi-ken-cli search "steve jobs"

# Summarize a URL (default: type=summary, language=EN)
pykagi-ken-cli summarize --url "https://en.wikipedia.org/wiki/Steve_Jobs"

# Summarize text with custom options
pykagi-ken-cli summarize --text "Long article content..." --type takeaway --language DE

# Pass token directly for any command
pykagi-ken-cli search "steve jobs" --token YOUR_KAGI_SESSION_TOKEN
pykagi-ken-cli summarize --url "https://example.com" --token YOUR_KAGI_SESSION_TOKEN
```

## API

### `search(query, token)`

Performs a search on Kagi.com and returns structured results.

**Parameters:**

- `query` (string) - Search query to execute
- `token` (string) - Kagi session token

**Returns:** Promise resolving to object with `data` array containing search results and related searches.

**Example:**

```python
results = await search("javascript frameworks", token)
# Returns: {"data": [{"t": 0, "url": "...", "title": "...", "snippet": "..."}, ...]}
```

### `summarize(input, token, summary_type, target_language, is_url)`

Performs a summarization request on Kagi.com and returns the summary.

**Parameters:**

- `input` (string) - URL or text content to summarize
- `token` (string) - Kagi session token
- `summary_type` (string) - Summary type: 'summary' or 'takeaway' (default: 'summary')
- `target_language` (string) - Target language code (default: 'EN')
- `is_url` (boolean) - Whether input is a URL (True) or text (False)

**Returns:** Promise resolving to object with `data.output` containing the markdown summary.

**Example:**

```python
summary = await summarize(
    "https://example.com/article",
    token,
    summary_type="summary",
    target_language="EN",
    is_url=True
)
# Returns: {"data": {"output": "# Summary\n\n..."}}
```

### `SUPPORTED_LANGUAGES`

Array of supported language codes for summarization: `['BG', 'CS', 'DA', 'DE', 'EL', 'EN', 'ES', 'ET', 'FI', 'FR', 'HU', 'ID', 'IT', 'JA', 'KO', 'LT', 'LV', 'NB', 'NL', 'PL', 'PT', 'RO', 'RU', 'SK', 'SL', 'SV', 'TR', 'UK', 'ZH', 'ZH-HANT']`

## JSON Output Formats

### Search Results

Results match the [Kagi Search API schema](https://help.kagi.com/kagi/api/search.html#objects) in a simplified form:

- **Search Results** (`t: 0`): Web search results with `url`, `title`, `snippet`
- **Related Searches** (`t: 1`): Suggested search terms in `list` array

```json
{
  "data": [
    {
      "t": 0,
      "url": "https://en.wikipedia.org/wiki/Steve_Jobs",
      "title": "Steve Jobs - Wikipedia",
      "snippet": "Steven Paul Jobs (February 24, 1955 – October 5, 2011) was an American businessman..."
    },
    {
      "t": 1,
      "list": ["steve jobs death", "steve jobs quotes", "steve jobs film"]
    }
  ]
}
```

### Summarizer Results

Results match the [Kagi Summarizer API schema](https://help.kagi.com/kagi/api/summarizer.html#objects) in a simplified form:

```json
{
  "data": {
    "output": "# Summary\n\nSteve Jobs was an American entrepreneur and inventor who co-founded Apple Inc..."
  }
}
```

## Authentication

Get your Kagi session token:

1. Visit [Kagi Settings](https://kagi.com/settings/user_details) in your browser
2. Copy the **Session Link**
3. Extract the `token` value from the link
4. Use that value as your session token in function calls

> **Warning**
>
> **Security Note**: Keep your session token private. It provides access to your Kagi account.

## Error Handling

Both functions throw errors for:

- Invalid or missing parameters
- Network connectivity issues
- Invalid or expired session tokens
- Parsing failures

```python
try:
    results = await search("query", "invalid-token")
except Exception as error:
    print(f"Search failed: {error}")
    # Possible errors: "Invalid or expired session token", "Network error: Unable to connect to Kagi"
```

## Author

Python port by 0x0208v0, https://github.com/0x0208v0/pykagi-ken

This project is a Python port of [kagi-ken](https://github.com/czottmann/kagi-ken) v1.2.0 and [kagi-ken-cli](https://github.com/czottmann/kagi-ken-cli) v1.6.0 by Carlo Zottmann.

This project is neither affiliated with nor endorsed by Kagi. We're just very happy customers.

## Related Projects

- [czottmann/kagi-ken](https://github.com/czottmann/kagi-ken) - Original Node.js library
- [czottmann/kagi-ken-cli](https://github.com/czottmann/kagi-ken-cli) - Original Node.js CLI tool
- [czottmann/kagi-ken-mcp](https://github.com/czottmann/kagi-ken-mcp) - MCP server using kagi-ken

---

## Technical Details

- **Architecture**: Async/await with clean functional API
- **Search**: Uses Kagi's `/html/search` endpoint for server-side rendered results (HTML parsing)
- **Summarizer**: Uses Kagi's `/mother/summary_labs` endpoint with streaming JSON responses
- **Authentication**: Session token via Cookie header (caller must provide token)
- **Error Handling**: Network errors, invalid tokens, parsing failures, stream processing
- **User Agent**: Mimics Safari browser for compatibility
- **Dependencies**: `aiohttp` for HTTP requests, `parsel` for HTML parsing, `click` for CLI
