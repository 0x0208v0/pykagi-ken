"""
Kagi search functionality.

Ported from kagi-ken/src/search.js (https://github.com/czottmann/kagi-ken)
"""

from typing import Any
from typing import Optional

import aiohttp
from parsel import Selector

from pykagi_ken.constants import USER_AGENT
from pykagi_ken.exceptions import AuthenticationError
from pykagi_ken.exceptions import NetworkError
from pykagi_ken.exceptions import ParsingError
from pykagi_ken.exceptions import ValidationError


async def search(
    query: str, token: str, limit: int = 10
) -> dict[str, list[dict[str, Any]]]:
    """
    Performs a search on Kagi.com and returns structured results.

    Args:
        query: Search query string
        token: Kagi session token
        limit: Maximum number of search results to return (default: 10)

    Returns:
        Dictionary containing 'data' array with search results and related searches.
        Format matches Kagi Search API schema:
        {
            "data": [
                {"t": 0, "url": "...", "title": "...", "snippet": "..."},  # Search result
                {"t": 1, "list": ["...", "..."]}  # Related searches
            ]
        }

    Raises:
        ValidationError: If query or token is invalid
        AuthenticationError: If session token is invalid (401/403)
        NetworkError: If network request fails
        ParsingError: If HTML parsing fails

    Example:
        >>> results = await search("python programming", session_token)
        >>> for item in results["data"]:
        ...     if item["t"] == 0:  # Search result
        ...         print(item["title"], item["url"])
        ...     elif item["t"] == 1:  # Related searches
        ...         print("Related:", item["list"])
    """
    # Validate inputs
    if not query or not isinstance(query, str):
        raise ValidationError("Query must be a non-empty string")
    if not token or not isinstance(token, str):
        raise ValidationError("Token must be a non-empty string")
    if not isinstance(limit, int) or limit < 1:
        raise ValidationError("Limit must be a positive integer")

    # Prepare request
    url = "https://kagi.com/html/search"
    params = {"q": query}
    headers = {
        "User-Agent": USER_AGENT,
        "Cookie": f"kagi_session={token}",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                # Check for authentication errors
                if response.status in (401, 403):
                    raise AuthenticationError(
                        "Authentication failed. Please check your session token."
                    )

                # Check for other HTTP errors
                if response.status != 200:
                    raise NetworkError(
                        f"HTTP request failed with status {response.status}"
                    )

                html = await response.text()

    except aiohttp.ClientError as e:
        raise NetworkError(f"Network request failed: {e}") from e

    # Parse HTML and extract results
    try:
        return _parse_search_results(html, limit)
    except Exception as e:
        raise ParsingError(f"Failed to parse search results: {e}") from e


def _parse_search_results(html: str, limit: int) -> dict[str, list[dict[str, Any]]]:
    """
    Parses HTML search results and extracts structured data.

    Args:
        html: HTML content from Kagi search page
        limit: Maximum number of results to extract

    Returns:
        Dictionary with 'data' array containing search results and related searches
    """
    selector = Selector(text=html)
    data: list[dict[str, Any]] = []

    # Extract main search results
    result_count = 0
    for element in selector.css(".search-result"):
        if result_count >= limit:
            break

        result = _extract_search_result(element)
        if result:
            data.append(result)
            result_count += 1

    # Extract grouped results (if any)
    for group in selector.css(".sr-group"):
        for element in group.css(".__srgi"):
            if result_count >= limit:
                break

            result = _extract_grouped_result(element)
            if result:
                data.append(result)
                result_count += 1

    # Extract related searches
    related = _extract_related_searches(selector)
    if related:
        data.append(related)

    return {"data": data}


def _extract_search_result(element: Selector) -> Optional[dict[str, Any]]:
    """
    Extracts a single search result from HTML element.

    Args:
        element: Selector for a .search-result element

    Returns:
        Dictionary with t=0, url, title, snippet or None if extraction fails
    """
    try:
        # Extract title and URL
        title_link = element.css(".__sri_title_link::attr(href)").get()
        title_text = element.css(".__sri_title_link::text").get()

        if not title_link or not title_text:
            return None

        # Extract snippet
        snippet = element.css(".__sri-desc::text").get()
        if not snippet:
            snippet = ""

        return {
            "t": 0,  # Type: search result
            "url": title_link.strip(),
            "title": title_text.strip(),
            "snippet": snippet.strip(),
        }
    except Exception:
        return None


def _extract_grouped_result(element: Selector) -> Optional[dict[str, Any]]:
    """
    Extracts a single grouped search result from HTML element.

    Args:
        element: Selector for a .__srgi element

    Returns:
        Dictionary with t=0, url, title, snippet or None if extraction fails
    """
    try:
        # Extract title and URL from grouped result
        title_link = element.css("a::attr(href)").get()
        title_text = element.css("a::text").get()

        if not title_link or not title_text:
            return None

        # Grouped results typically don't have snippets
        return {
            "t": 0,  # Type: search result
            "url": title_link.strip(),
            "title": title_text.strip(),
            "snippet": "",
        }
    except Exception:
        return None


def _extract_related_searches(selector: Selector) -> Optional[dict[str, Any]]:
    """
    Extracts related search suggestions.

    Args:
        selector: Selector for the entire page

    Returns:
        Dictionary with t=1 and list of related searches, or None if none found
    """
    try:
        related_list = []
        for element in selector.css(".related-searches a span::text"):
            text = element.get()
            if text:
                related_list.append(text.strip())

        if related_list:
            return {
                "t": 1,  # Type: related searches
                "list": related_list,
            }
        return None
    except Exception:
        return None
