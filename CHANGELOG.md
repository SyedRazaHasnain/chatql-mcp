# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Centralized version management system
- Removed hardcoded version strings from multiple files

### Added
- `__version__.py` as single source of truth for version information
- `version_manager.py` script for automated version bumping and tagging 
- Centralized version management with git tagging support
- This CHANGELOG.md file to track changes

## [1.0.0] - 2024-01-XX

### Added
- Initial release of Natural Language SQL MCP Server
- Natural language to SQL conversion using OpenAI GPT models
- Support for Microsoft SQL Server, SQL Server Express, and Azure SQL Database
- MCP (Model Context Protocol) integration for AI assistants
- Database schema exploration and query tools
- Built-in query safety validation and result limiting
- Connection pooling and comprehensive error handling
- Professional logging and monitoring capabilities

### Features
- `execute_natural_language_query` - Convert English to SQL and execute
- `execute_direct_sql_query` - Execute SQL with safety validation
- `get_table_information` - Retrieve detailed table schema information
- `list_database_tables` - List all available database tables
- `get_table_sample_data` - Preview sample data from tables

### Security
- Query validation to prevent dangerous operations
- Parameterized queries to prevent SQL injection
- Result limiting to prevent memory exhaustion
- Environment variable based configuration for sensitive data

---

## Release Notes Format

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements 