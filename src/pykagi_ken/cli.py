"""
Command-line interface for pykagi-ken.

Ported from kagi-ken-cli (https://github.com/czottmann/kagi-ken-cli)
"""

import asyncio
import json
from pathlib import Path
from typing import Optional

import click

from pykagi_ken import SUPPORTED_LANGUAGES
from pykagi_ken import __version__
from pykagi_ken import search
from pykagi_ken import summarize
from pykagi_ken.exceptions import PyKagiKenError


def _get_token(token_arg: Optional[str]) -> str:
    """
    Resolves session token from argument or file.

    Args:
        token_arg: Token passed via --token flag

    Returns:
        Session token string

    Raises:
        click.ClickException: If token cannot be found
    """
    # Try token argument first
    if token_arg:
        return token_arg

    # Try reading from ~/.kagi_session_token
    token_file = Path.home() / ".kagi_session_token"
    if token_file.exists():
        try:
            return token_file.read_text().strip()
        except Exception as e:
            raise click.ClickException(f"Failed to read token file: {e}") from e

    # No token found
    raise click.ClickException(
        "No session token found. Please provide via --token flag or "
        "save to ~/.kagi_session_token file."
    )


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=__version__, prog_name="pykagi-ken")
def main(ctx):
    """
    pykagi-ken - Python port of kagi-ken

    Access Kagi.com services using session tokens.

    \b
    Commands:
      search      Search Kagi and return JSON results
      summarize   Summarize URL or text content

    \b
    Authentication:
      Get your session token from https://kagi.com/settings/user_details
      Save to ~/.kagi_session_token or use --token flag

    \b
    Examples:
      # Search
      pykagi-ken-cli search "python programming"
      pykagi-ken-cli search "steve jobs" --limit 5

      # Summarize URL
      pykagi-ken-cli summarize --url "https://example.com"

      # Summarize text
      pykagi-ken-cli summarize --text "Long article..." --type takeaway --language DE
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument("query")
@click.option(
    "--token",
    "-t",
    help="Kagi session token (or save to ~/.kagi_session_token)",
)
@click.option(
    "--limit",
    "-l",
    default=10,
    type=int,
    help="Maximum number of results (default: 10)",
)
def search_cmd(query: str, token: Optional[str], limit: int):
    """
    Search Kagi and return JSON results.

    \b
    Examples:
      pykagi-ken-cli search "python programming"
      pykagi-ken-cli search "steve jobs" --limit 5
      pykagi-ken-cli search "rust lang" --token YOUR_TOKEN
    """
    try:
        session_token = _get_token(token)
        results = asyncio.run(search(query, session_token, limit))
        click.echo(json.dumps(results, indent=2, ensure_ascii=False))
    except PyKagiKenError as e:
        raise click.ClickException(str(e)) from e
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {e}") from e


@main.command()
@click.option(
    "--url",
    "-u",
    help="URL to summarize",
)
@click.option(
    "--text",
    "-x",
    help="Text content to summarize",
)
@click.option(
    "--token",
    "-t",
    help="Kagi session token (or save to ~/.kagi_session_token)",
)
@click.option(
    "--type",
    "-y",
    "summary_type",
    default="summary",
    type=click.Choice(["summary", "takeaway"], case_sensitive=False),
    help='Summary type: "summary" or "takeaway" (default: summary)',
)
@click.option(
    "--language",
    "-l",
    default="EN",
    type=click.Choice(SUPPORTED_LANGUAGES, case_sensitive=False),
    help="Target language code (default: EN)",
)
def summarize_cmd(
    url: Optional[str],
    text: Optional[str],
    token: Optional[str],
    summary_type: str,
    language: str,
):
    """
    Summarize URL or text content.

    \b
    Examples:
      # Summarize URL
      pykagi-ken-cli summarize --url "https://en.wikipedia.org/wiki/Python"

      # Summarize text with custom options
      pykagi-ken-cli summarize --text "Long article..." --type takeaway --language DE

      # Use token flag
      pykagi-ken-cli summarize --url "https://example.com" --token YOUR_TOKEN
    """
    # Validate input
    if not url and not text:
        raise click.ClickException("Either --url or --text must be provided")
    if url and text:
        raise click.ClickException("Cannot use both --url and --text")

    try:
        session_token = _get_token(token)
        input_text = url if url else text
        is_url = bool(url)

        result = asyncio.run(
            summarize(
                input_text,
                session_token,
                summary_type=summary_type.lower(),
                language=language.upper(),
                is_url=is_url,
            )
        )
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except PyKagiKenError as e:
        raise click.ClickException(str(e)) from e
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {e}") from e


if __name__ == "__main__":
    main()
