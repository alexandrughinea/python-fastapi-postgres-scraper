# Contributing to FastAPI PostgreSQL Web Scraper

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## Code Style and Quality

This project follows standard Python code style guidelines with some specific tooling:

### Linting and Formatting Tools

- **Black**: For code formatting
- **isort**: For sorting imports
- **Flake8**: For code linting
- **mypy**: For static type checking

### Setting Up Development Environment

1. Clone the repository
2. Install development dependencies:

```bash
pip install black flake8 isort mypy pre-commit
```

3. Install pre-commit hooks:

```bash
pre-commit install
```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality before committing. The hooks will:

- Format code with Black
- Sort imports with isort
- Run Flake8 linting
- Perform type checking with mypy
- Check for common issues (trailing whitespace, file endings, etc.)

If a hook fails, the commit will be aborted. Fix the issues and try again.

### GitHub Actions Workflow

A GitHub Actions workflow is set up to run these checks automatically on pull requests and pushes to the main branch. The workflow:

1. Runs on any push or pull request to main/master that modifies Python files
2. Installs the necessary dependencies
3. Runs Black, Flake8, isort, and mypy
4. Reports any issues in the GitHub interface

### Running Checks Manually

You can run the checks manually with the following commands:

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/

# Type check
mypy --ignore-missing-imports app/
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all tests pass and linting is clean
5. Submit a pull request

Your pull request will be reviewed, and you may be asked to make changes before it is merged.

## Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub. Please include:

- A clear description of the issue or feature
- Steps to reproduce (for bugs)
- Expected behavior
- Actual behavior
- Any relevant logs or screenshots

Thank you for contributing!
