# Contributing to Natural Language SQL MCP Server

Thank you for your interest in contributing to this project! We welcome contributions from the community.

## How to Contribute

### Reporting Issues

1. Check if the issue already exists in our [Issues](https://github.com/your-username/natural-language-sql-mcp/issues)
2. If not, create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, SQL Server version)

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/natural-language-sql-mcp.git
   cd natural-language-sql-mcp
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code style
   - Add appropriate docstrings and comments
   - Include type hints where applicable

3. **Test your changes**
   ```bash
   python -m pytest  # When tests are added
   python server.py  # Manual testing
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

### Code Standards

- **Python Style**: Follow PEP 8
- **Type Hints**: Use type hints for function parameters and return values
- **Docstrings**: Use Google-style docstrings
- **Error Handling**: Include comprehensive error handling
- **Logging**: Use structured logging with appropriate levels

### Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality (when test framework is added)
3. Ensure all existing tests pass
4. Create a pull request with:
   - Clear title and description
   - Reference to related issues
   - Screenshots/examples if applicable

### Code Review

- All submissions require review
- We may suggest changes, improvements, or alternatives
- Please be patient and responsive to feedback

## Development Guidelines

### Adding New Features

1. **Database Operations**: All database operations should go through `DatabaseManager`
2. **Natural Language Processing**: Extend `LanguageProcessor` for new AI features
3. **MCP Tools**: Add new tools in `server.py` following existing patterns
4. **Configuration**: Add new config options to `config.py` with appropriate defaults

### Security Considerations

- Never commit sensitive data (API keys, passwords, connection strings)
- Validate all user inputs
- Use parameterized queries to prevent SQL injection
- Follow principle of least privilege for database access

### Performance Guidelines

- Cache expensive operations when appropriate
- Limit query results to prevent memory issues
- Use connection pooling for database access
- Consider rate limiting for API calls

## Questions?

Feel free to open an issue for questions or reach out to the maintainers.

Thank you for contributing! 🎉 