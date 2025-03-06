# Contributing to DataPipe Analytics

Thank you for considering contributing to DataPipe Analytics! This document outlines the process for contributing to the project and provides guidelines to help you get started.

## 🌟 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## 🚀 How Can I Contribute?

### 🐛 Reporting Bugs

Bugs are tracked as [GitHub issues](https://github.com/javid912/datapipe-analytics/issues). Before creating a bug report, please check if the issue has already been reported. When creating a bug report, please include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Describe the behavior you observed and what you expected to see
- Include screenshots if possible
- Include details about your environment (OS, Docker version, etc.)

### 💡 Suggesting Enhancements

Enhancement suggestions are also tracked as GitHub issues. When creating an enhancement suggestion:

- Use a clear and descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful to most users
- Include mockups or examples if applicable

### 📝 Documentation Improvements

Documentation is crucial for this project. If you find any part of the documentation that could be improved:

- Identify which part of the documentation needs improvement
- Suggest clear and concise changes
- Submit a pull request with your improvements

### 🔧 Pull Requests

Here's the process for submitting a pull request:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure your changes don't break existing functionality
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 💻 Development Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Make (optional, for using Makefile commands)
- Alpha Vantage API key (for data extraction)

### Local Development

1. Clone your fork of the repository
```bash
git clone https://github.com/YOUR_USERNAME/datapipe-analytics.git
cd datapipe-analytics
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install development dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Copy the example environment file and configure your API key
```bash
cp .env.example .env
# Edit .env and add your Alpha Vantage API key
```

5. Start the services
```bash
# For standard hardware:
docker-compose up -d

# For older or resource-constrained hardware:
docker-compose -f docker-compose-minimal.yml up -d
```

## 🧪 Testing

Before submitting a pull request, please run the tests to ensure your changes don't break existing functionality:

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests (requires Docker)
pytest tests/integration/

# Run dbt tests
cd dbt && dbt test
```

## 📊 Style Guidelines

### Python Code

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints where appropriate
- Write docstrings for all functions, classes, and modules
- Use meaningful variable and function names

### SQL Code

- Use uppercase for SQL keywords (SELECT, FROM, WHERE, etc.)
- Use snake_case for table and column names
- Include comments for complex queries
- Follow the project's SQL style guide in `docs/sql_style_guide.md`

### Documentation

- Use Markdown for documentation
- Include examples where appropriate
- Keep documentation up-to-date with code changes
- Use clear and concise language

## 🏆 Recognition

Contributors will be recognized in the project's README and in the GitHub repository's contributors list. We value all contributions, whether they're bug fixes, feature additions, or documentation improvements.

## 📝 License

By contributing to DataPipe Analytics, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

## 🙏 Thank You!

Thank you for contributing to DataPipe Analytics! Your efforts help make this project better for everyone. 