# Contributing Guidelines

Thank you for your interest in contributing to this project! This document provides guidelines for contributing.

## Development Workflow

This project follows **Spec-Driven Development (SDD)**:

1. **Type Specs First**: Define Pydantic schemas in `schemas/`
2. **Test Specs Second**: Write pytest tests in `tests/`
3. **Implementation Third**: Implement code that satisfies specs
4. **Validation**: Run mypy + pytest to verify

## Code Standards

### Type Safety
- **100% type hints** required
- Use `typing` module, avoid `Any` when possible
- Pydantic models for data contracts
- mypy strict mode enforced

### Testing
- Write tests **before** implementation (Test Specs)
- Minimum 80% coverage
- Tests mirror source structure
- Use pytest fixtures for reusable test data

### Code Style
- Ruff for formatting and linting
- Max line length: 100
- Google-style docstrings
- Self-documenting code preferred

### File Organization
- One responsibility per file
- Max file size: ~500 lines
- Clear interfaces between modules
- Schemas in `schemas/`, not inline

## Setup Development Environment

```bash
# Backend
cd backend
poetry install
pre-commit install

# Frontend
cd frontend
npm install
```

## Running Tests

```bash
# Backend tests
cd backend
poetry run pytest

# With coverage
poetry run pytest --cov=src --cov-report=html

# Type checking
poetry run mypy src

# Linting
poetry run ruff check src tests
```

## Making Changes

1. **Create a branch**: `git checkout -b feature/your-feature`
2. **Follow SDD**: Write specs → tests → implementation
3. **Run validation**: `make lint type-check test`
4. **Commit**: Use clear commit messages
5. **Push**: Create a pull request

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add hybrid search support
fix: Correct embedding provider selection
docs: Update API documentation
test: Add integration tests for document upload
```

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add tests for new features
4. Ensure type checking passes
5. Request review

## Questions?

Open an issue or start a discussion!
