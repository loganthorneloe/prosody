# Contributing to Prosody

Thank you for your interest in contributing to Prosody! We welcome contributions from the community and are grateful for any help you can provide.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with the following information:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **System Information**: Your OS version, Python version, and Prosody version
6. **Logs**: Any relevant error messages or logs

### Requesting Features

Feature requests are welcome! Please create an issue with:

1. **Description**: Clear description of the feature
2. **Use Case**: Why this feature would be useful
3. **Implementation Ideas**: Any thoughts on how it could be implemented (optional)

### Submitting Pull Requests

1. **Fork the Repository**: Create your own fork of the project
2. **Create a Branch**: Create a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make Changes**: Implement your changes following our coding standards
4. **Write Tests**: Add tests for new functionality
5. **Test**: Run the test suite to ensure everything works
6. **Commit**: Commit your changes with a clear message
7. **Push**: Push to your fork (`git push origin feature/amazing-feature`)
8. **Pull Request**: Open a pull request with a clear title and description

### Coding Standards

- Follow PEP 8 for Python code style
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused
- Write unit tests for new functionality

### Development Setup

1. Fork and clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Install in development mode: `pip install -e .`

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=src/prosody

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests in parallel
pytest -n auto
```

### Code of Conduct

- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## Questions?

If you have questions, feel free to:
- Open an issue for discussion
- Check existing issues and pull requests
- Read the documentation in the README

Thank you for contributing to Prosody!