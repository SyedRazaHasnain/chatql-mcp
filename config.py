"""
Configuration module for Natural Language SQL MCP Server.

This module handles environment variable loading and configuration management
for database connections, API keys, and server settings.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Configuration class for the Natural Language SQL MCP Server."""
    
    # Database Configuration
    DB_SERVER: str = os.getenv('DB_SERVER', 'localhost\\SQLEXPRESS')
    DB_DATABASE: str = os.getenv('DB_DATABASE', '')
    DB_USERNAME: str = os.getenv('DB_USERNAME', '')  # Empty for Windows Auth
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')  # Empty for Windows Auth
    DB_DRIVER: str = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4')
    OPENAI_MAX_TOKENS: int = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
    
    # MCP Server Configuration
    MCP_SERVER_NAME: str = os.getenv('MCP_SERVER_NAME', 'natural-language-sql-server')
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Query Configuration
    MAX_QUERY_RESULTS: int = int(os.getenv('MAX_QUERY_RESULTS', '100'))
    QUERY_TIMEOUT: int = int(os.getenv('QUERY_TIMEOUT', '30'))  # seconds
    
    # Security Configuration
    SELECT_ONLY_MODE: bool = os.getenv('SELECT_ONLY_MODE', 'false').lower() == 'true'
    ALLOW_MODE_TOGGLE: bool = os.getenv('ALLOW_MODE_TOGGLE', 'true').lower() == 'true'
    
    @property
    def connection_string(self) -> str:
        """
        Generate the database connection string.
        
        Returns:
            str: SQLAlchemy connection string for SQL Server
            
        Raises:
            ValueError: If required database configuration is missing
        """
        if not self.DB_SERVER:
            raise ValueError("DB_SERVER is required")
        if not self.DB_DATABASE:
            raise ValueError("DB_DATABASE is required")
        
        # Build connection string based on authentication method
        if self.DB_USERNAME and self.DB_PASSWORD:
            # SQL Server authentication
            logger.info("Using SQL Server authentication")
            return (
                f"mssql+pyodbc://{self.DB_USERNAME}:{self.DB_PASSWORD}@"
                f"{self.DB_SERVER}/{self.DB_DATABASE}?"
                f"driver={self.DB_DRIVER.replace(' ', '+')}"
            )
        else:
            # Windows authentication (trusted connection)
            logger.info("Using Windows authentication")
            return (
                f"mssql+pyodbc://@{self.DB_SERVER}/{self.DB_DATABASE}?"
                f"driver={self.DB_DRIVER.replace(' ', '+')}&trusted_connection=yes"
            )
    
    @classmethod
    def validate_configuration(cls) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        config = cls()
        errors = []
        
        # Check required database configuration
        if not config.DB_SERVER:
            errors.append("DB_SERVER is required")
        if not config.DB_DATABASE:
            errors.append("DB_DATABASE is required")
        if not config.DB_DRIVER:
            errors.append("DB_DRIVER is required")
        
        # Check OpenAI configuration
        if not config.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set - natural language processing will be disabled")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False
        
        return True
    
    def __repr__(self) -> str:
        """Safe representation of config (excludes sensitive data)."""
        return (
            f"Config(server={self.DB_SERVER}, database={self.DB_DATABASE}, "
            f"driver={self.DB_DRIVER}, has_openai_key={bool(self.OPENAI_API_KEY)})"
        ) 