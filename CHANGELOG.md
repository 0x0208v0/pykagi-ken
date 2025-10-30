# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2025-10-30

Initial release! Python port of [kagi-ken](https://github.com/czottmann/kagi-ken) v1.2.0 and [kagi-ken-cli](https://github.com/czottmann/kagi-ken-cli) v1.6.0.

### Added

- Search functionality with HTML parsing
- Summarizer functionality with streaming JSON support
- Session token authentication
- CLI tool `pykagi-ken-cli` with `search` and `summarize` commands
- Support for 29 languages in summarization
- Structured JSON output matching Kagi API schemas
- Type hints throughout the codebase
- Async/await support using aiohttp and parsel

### Technical Details

- Python 3.10+ support
- Core dependencies: aiohttp, parsel
- Optional CLI dependency: click
- Development dependencies: ruff
- Faithful port of original Node.js implementation
- Same endpoints and response parsing as kagi-ken v1.2.0

