# Contributing to pykagi-ken

Thank you for your interest in contributing to pykagi-ken! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pykagi-ken.git
   cd pykagi-ken
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Code Quality

We use `ruff` for linting and formatting:

```bash
# Check code quality
ruff check pykagi_ken/

# Auto-fix issues
ruff check --fix pykagi_ken/

# Format code
ruff format pykagi_ken/
```

### Type Checking

The project includes type hints. You can use `mypy` for type checking:

```bash
pip install mypy
mypy pykagi_ken/
```

## Project Structure

```
pykagi-ken/
├── pykagi_ken/           # Main package
│   ├── __init__.py       # Package exports
│   ├── cli.py            # CLI implementation
│   ├── constants.py      # Constants (USER_AGENT, SUPPORTED_LANGUAGES)
│   ├── exceptions.py     # Custom exceptions
│   ├── search.py         # Search functionality
│   ├── summarize.py      # Summarize functionality
│   └── py.typed          # PEP 561 marker
├── examples/             # Usage examples
├── AGENTS.md             # LLM agent guidance
├── README.md             # Main documentation
├── LICENSE               # MIT License
├── CHANGELOG.md          # Version history
└── pyproject.toml        # Package configuration
```

## Coding Guidelines

1. **Follow PEP 8**: Use `ruff format` to ensure consistent formatting
2. **Type hints**: Add type hints to all functions and methods
3. **Docstrings**: Use Google-style docstrings for all public functions
4. **Async/await**: All network operations should use async/await
5. **Error handling**: Use custom exceptions from `exceptions.py`

## Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Run linter**: `ruff check pykagi_ken/`
5. **Format code**: `ruff format pykagi_ken/`
6. **Commit your changes**: `git commit -m "Add your feature"`
7. **Push to your fork**: `git push origin feature/your-feature-name`
8. **Create a Pull Request**

## Pull Request Guidelines

- **Clear description**: Explain what your PR does and why
- **Documentation**: Update README.md if needed
- **Changelog**: Add entry to CHANGELOG.md
- **Code quality**: Ensure all checks pass

## Reporting Issues

When reporting issues, please include:

- **Python version**: `python --version`
- **Package version**: `pykagi-ken --version`
- **Error message**: Full traceback if applicable
- **Steps to reproduce**: Minimal example to reproduce the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened

## Questions?

Feel free to open an issue for questions or discussions!

## License

By contributing to pykagi-ken, you agree that your contributions will be licensed under the MIT License.

## Acknowledgments

This project is a Python port of [kagi-ken](https://github.com/czottmann/kagi-ken) by Carlo Zottmann.

