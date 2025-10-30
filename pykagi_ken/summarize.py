"""
Kagi summarizer functionality.

Ported from kagi-ken/src/summarize.js (https://github.com/czottmann/kagi-ken)
"""

import json

import aiohttp

from pykagi_ken.constants import SUPPORTED_LANGUAGES
from pykagi_ken.constants import USER_AGENT
from pykagi_ken.exceptions import AuthenticationError
from pykagi_ken.exceptions import NetworkError
from pykagi_ken.exceptions import ParsingError
from pykagi_ken.exceptions import ValidationError


async def summarize(
    input_text: str,
    token: str,
    summary_type: str = "summary",
    language: str = "EN",
    is_url: bool = False,
) -> dict[str, dict[str, str]]:
    """
    Performs a summarization request on Kagi.com.

    Args:
        input_text: URL or text content to summarize
        token: Kagi session token
        summary_type: Type of summary - "summary" or "takeaway" (default: "summary")
        language: Target language code (default: "EN")
        is_url: Whether input_text is a URL (True) or plain text (False)

    Returns:
        Dictionary containing summary data:
        {
            "data": {
                "output": "# Summary\\n\\nSummary text in markdown format..."
            }
        }

    Raises:
        ValidationError: If input parameters are invalid
        AuthenticationError: If session token is invalid (401/403)
        NetworkError: If network request fails
        ParsingError: If response parsing fails

    Example:
        >>> # Summarize a URL
        >>> result = await summarize(
        ...     "https://en.wikipedia.org/wiki/Python",
        ...     session_token,
        ...     is_url=True
        ... )
        >>> print(result["data"]["output"])

        >>> # Summarize text
        >>> result = await summarize(
        ...     "Long article text...",
        ...     session_token,
        ...     summary_type="takeaway",
        ...     language="DE"
        ... )
    """
    # Validate inputs
    if not input_text or not isinstance(input_text, str):
        raise ValidationError("Input must be a non-empty string")
    if not token or not isinstance(token, str):
        raise ValidationError("Token must be a non-empty string")
    if summary_type not in ("summary", "takeaway"):
        raise ValidationError('Summary type must be "summary" or "takeaway"')
    # Allow empty string for default language
    if language and language not in SUPPORTED_LANGUAGES:
        raise ValidationError(
            f"Language must be one of: {', '.join(SUPPORTED_LANGUAGES)} or empty string for default"
        )

    # Prepare request
    url = "https://kagi.com/mother/summary_labs"
    headers = {
        "Accept": "application/vnd.kagi.stream",
        "Connection": "keep-alive",
        "Cookie": f"kagi_session={token}",
        "Host": "kagi.com",
        "Pragma": "no-cache",
        "Referer": "https://kagi.com/summarizer",
        "User-Agent": USER_AGENT,
    }

    try:
        async with aiohttp.ClientSession() as session:
            if is_url:
                # URL summarization - GET request with query parameters
                params = {
                    "url": input_text,
                    "stream": "1",
                    "target_language": language,
                    "summary_type": summary_type,
                }
                async with session.get(url, params=params, headers=headers) as response:
                    stream_data = await _handle_response(response)
            else:
                # Text summarization - POST request with form data
                data = aiohttp.FormData()
                data.add_field("text", input_text)
                data.add_field("stream", "1")
                data.add_field("target_language", language)
                data.add_field("summary_type", summary_type)

                async with session.post(url, data=data, headers=headers) as response:
                    stream_data = await _handle_response(response)

    except aiohttp.ClientError as e:
        raise NetworkError(f"Network request failed: {e}") from e

    # Parse streaming response
    try:
        return _parse_streaming_summary(stream_data)
    except Exception as e:
        raise ParsingError(f"Failed to parse summary response: {e}") from e


async def _handle_response(response: aiohttp.ClientResponse) -> str:
    """
    Handles HTTP response and checks for errors.

    Args:
        response: aiohttp response object

    Returns:
        Response text content

    Raises:
        AuthenticationError: If authentication fails
        NetworkError: If HTTP request fails
    """
    # Check for authentication errors
    if response.status in (401, 403):
        raise AuthenticationError(
            "Authentication failed. Please check your session token."
        )

    # Check for other HTTP errors
    if response.status != 200:
        raise NetworkError(f"HTTP request failed with status {response.status}")

    return await response.text()


def _parse_streaming_summary(stream_data: str) -> dict[str, dict[str, str]]:
    """
    Parses streaming summary response.

    The response format is a series of JSON messages separated by NUL bytes (\\x00).
    The final message is prefixed with "final:" and contains the complete summary.

    Args:
        stream_data: Raw streaming response data

    Returns:
        Dictionary with 'data' containing 'output' field with markdown summary

    Raises:
        ParsingError: If parsing fails
    """
    try:
        # Split by NUL bytes and filter empty messages
        messages = [msg.strip() for msg in stream_data.split("\x00") if msg.strip()]

        if not messages:
            raise ParsingError("No messages found in streaming response")

        # Get the last message (should be the final summary)
        last_message = messages[-1]

        # Remove "final:" prefix if present
        if last_message.startswith("final:"):
            last_message = last_message[6:].strip()

        # Parse JSON
        parsed_data = json.loads(last_message)

        # Extract output_data.markdown and return as data.output (matching kagi-ken)
        output = parsed_data.get("output_data", {}).get("markdown", "")
        return {"data": {"output": output}}

    except json.JSONDecodeError as e:
        raise ParsingError(f"Failed to parse JSON: {e}") from e
    except Exception as e:
        raise ParsingError(f"Failed to parse streaming response: {e}") from e
