"""
Database management module for Natural Language SQL MCP Server.

This module provides database connectivity and query execution capabilities
for SQL Server using SQLAlchemy and pyodbc.
"""

import pyodbc
import pandas as pd
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError, TimeoutError
from sqlalchemy.engine import Engine
from typing import List, Dict, Any, Optional, Union
from config import Config
import logging
import time
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database manager for SQL Server connections and query execution.
    
    Provides methods for connecting to SQL Server, executing queries,
    and retrieving schema information.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the database manager.
        
        Args:
            config: Optional configuration object. If None, uses default Config()
        """
        self.config = config or Config()
        self.engine: Optional[Engine] = None
        self._metadata: Optional[MetaData] = None
        
        # SELECT-only mode state
        self._select_only_mode = self.config.SELECT_ONLY_MODE
        
        self._connect()
    
    def _connect(self) -> None:
        """
        Establish database connection.
        
        Raises:
            ValueError: If configuration is invalid
            SQLAlchemyError: If database connection fails
        """
        try:
            # Validate configuration first
            if not self.config.validate_configuration():
                raise ValueError("Invalid database configuration")
            
            connection_string = self.config.connection_string
            logger.info(f"Connecting to database: {self.config.DB_SERVER}/{self.config.DB_DATABASE}")
            
            # Create engine with connection pooling and timeouts
            self.engine = create_engine(
                connection_string,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=3600,  # Recycle connections after 1 hour
                connect_args={
                    "timeout": self.config.QUERY_TIMEOUT,
                    "autocommit": True
                }
            )
            
            # Test the connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            Connection: SQLAlchemy database connection
            
        Raises:
            SQLAlchemyError: If connection fails
        """
        if not self.engine:
            raise SQLAlchemyError("Database engine not initialized")
        
        connection = None
        try:
            connection = self.engine.connect()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    def set_select_only_mode(self, enabled: bool) -> Dict[str, Any]:
        """
        Enable or disable SELECT-only mode.
        
        Args:
            enabled: True to enable SELECT-only mode, False to allow all operations
            
        Returns:
            Dict containing the operation result
        """
        if not self.config.ALLOW_MODE_TOGGLE:
            return {
                'success': False,
                'error': 'Mode toggle is disabled by configuration'
            }
        
        previous_mode = self._select_only_mode
        self._select_only_mode = enabled
        
        logger.info(f"SELECT-only mode {'enabled' if enabled else 'disabled'}")
        
        return {
            'success': True,
            'message': f"SELECT-only mode {'enabled' if enabled else 'disabled'}",
            'previous_mode': previous_mode,
            'current_mode': enabled
        }
    
    def get_select_only_mode(self) -> Dict[str, Any]:
        """
        Get current SELECT-only mode status.
        
        Returns:
            Dict containing the current mode status
        """
        return {
            'success': True,
            'select_only_mode': self._select_only_mode,
            'can_toggle': self.config.ALLOW_MODE_TOGGLE
        }
    
    def _validate_query_for_select_only_mode(self, query: str) -> Dict[str, Any]:
        """
        Validate query against SELECT-only mode restrictions.
        
        Args:
            query: SQL query string to validate
            
        Returns:
            Dict containing validation result
        """
        if not self._select_only_mode:
            return {'is_valid': True, 'message': 'All operations allowed'}
        
        query_upper = query.strip().upper()
        
        # Only allow SELECT statements in SELECT-only mode
        if not query_upper.startswith('SELECT'):
            return {
                'is_valid': False,
                'message': 'Only SELECT queries are allowed in SELECT-only mode'
            }
        
        # Additional validation for SELECT queries to prevent dangerous operations
        dangerous_keywords = ['DROP', 'TRUNCATE', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return {
                    'is_valid': False,
                    'message': f'SELECT-only mode: Query contains forbidden keyword: {keyword}'
                }
        
        return {'is_valid': True, 'message': 'SELECT query validated'}
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test database connection and return server information.
        
        Returns:
            Dict containing connection test results and server info
        """
        try:
            with self.get_connection() as conn:
                # Test connection with a simple query
                result = conn.execute(text("SELECT @@VERSION as version, @@SERVERNAME as server_name"))
                server_info = dict(result.fetchone())
                
                return {
                    'success': True,
                    'message': 'Database connection successful',
                    'server_info': server_info
                }
                
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def close(self) -> None:
        """Close database connections and cleanup resources."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute SQL query and return results.
        
        Args:
            query: SQL query string
            parameters: Optional query parameters for parameterized queries
            
        Returns:
            Dict containing query results, metadata, and status
        """
        start_time = time.time()
        
        try:
            # Validate query (basic safety checks)
            if not query or not query.strip():
                return {
                    'success': False,
                    'error': 'Empty query provided'
                }
            
            # Check SELECT-only mode first
            select_only_validation = self._validate_query_for_select_only_mode(query)
            if not select_only_validation['is_valid']:
                logger.warning(f"Query blocked by SELECT-only mode: {query[:100]}...")
                return {
                    'success': False,
                    'error': select_only_validation['message']
                }
            
            # Remove potentially dangerous operations for safety (only when not in SELECT-only mode)
            if not self._select_only_mode:
                dangerous_keywords = ['DROP', 'TRUNCATE', 'DELETE FROM', 'ALTER', 'CREATE']
                query_upper = query.upper()
                
                for keyword in dangerous_keywords:
                    if keyword in query_upper and not query_upper.strip().startswith('SELECT'):
                        logger.warning(f"Potentially dangerous query blocked: {query[:100]}...")
                        return {
                            'success': False,
                            'error': f'Query contains potentially dangerous keyword: {keyword}'
                        }
            
            with self.get_connection() as conn:
                # Use parameterized queries if parameters provided
                if parameters:
                    result = conn.execute(text(query), parameters)
                else:
                    result = conn.execute(text(query))
                
                execution_time = time.time() - start_time
                
                # Check if it's a SELECT query
                if query.strip().upper().startswith('SELECT'):
                    columns = list(result.keys())
                    rows = [dict(zip(columns, row)) for row in result.fetchall()]
                    
                    # Limit results to prevent memory issues
                    if len(rows) > self.config.MAX_QUERY_RESULTS:
                        logger.warning(f"Query returned {len(rows)} rows, limiting to {self.config.MAX_QUERY_RESULTS}")
                        rows = rows[:self.config.MAX_QUERY_RESULTS]
                    
                    return {
                        'success': True,
                        'data': rows,
                        'columns': columns,
                        'row_count': len(rows),
                        'query': query,
                        'execution_time': execution_time,
                        'limited': len(rows) == self.config.MAX_QUERY_RESULTS
                    }
                else:
                    # For non-SELECT queries (INSERT, UPDATE, etc.)
                    conn.commit()
                    return {
                        'success': True,
                        'message': f"Query executed successfully. Rows affected: {result.rowcount}",
                        'rows_affected': result.rowcount,
                        'query': query,
                        'execution_time': execution_time
                    }
                    
        except TimeoutError as e:
            return {
                'success': False,
                'error': f'Query timeout after {self.config.QUERY_TIMEOUT} seconds: {str(e)}',
                'query': query
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error executing query: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'query': query
            }
    
    def get_table_schema(self, table_name: Optional[str] = None, schema_name: str = 'dbo') -> Dict[str, Any]:
        """
        Get database schema information.
        
        Args:
            table_name: Optional specific table name to get schema for
            schema_name: Database schema name (default: 'dbo')
            
        Returns:
            Dict containing schema information
        """
        try:
            if table_name:
                # Get specific table schema
                query = """
                SELECT 
                    c.COLUMN_NAME,
                    c.DATA_TYPE,
                    c.IS_NULLABLE,
                    c.COLUMN_DEFAULT,
                    c.CHARACTER_MAXIMUM_LENGTH,
                    c.NUMERIC_PRECISION,
                    c.NUMERIC_SCALE,
                    CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END as IS_PRIMARY_KEY,
                    CASE WHEN fk.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END as IS_FOREIGN_KEY
                FROM INFORMATION_SCHEMA.COLUMNS c
                LEFT JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc 
                    ON c.TABLE_NAME = tc.TABLE_NAME 
                    AND c.TABLE_SCHEMA = tc.TABLE_SCHEMA 
                    AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
                LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE pk 
                    ON c.COLUMN_NAME = pk.COLUMN_NAME 
                    AND c.TABLE_NAME = pk.TABLE_NAME 
                    AND c.TABLE_SCHEMA = pk.TABLE_SCHEMA 
                    AND tc.CONSTRAINT_NAME = pk.CONSTRAINT_NAME
                LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE fk 
                    ON c.COLUMN_NAME = fk.COLUMN_NAME 
                    AND c.TABLE_NAME = fk.TABLE_NAME 
                    AND c.TABLE_SCHEMA = fk.TABLE_SCHEMA
                LEFT JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS fktc 
                    ON fk.CONSTRAINT_NAME = fktc.CONSTRAINT_NAME 
                    AND fktc.CONSTRAINT_TYPE = 'FOREIGN KEY'
                WHERE c.TABLE_NAME = :table_name 
                    AND c.TABLE_SCHEMA = :schema_name
                ORDER BY c.ORDINAL_POSITION
                """
                
                result = self.execute_query(query, {
                    'table_name': table_name,
                    'schema_name': schema_name
                })
                
                if result.get('success'):
                    return {
                        'success': True,
                        'table': table_name,
                        'schema': schema_name,
                        'columns': result['data']
                    }
                else:
                    return result
            else:
                # Get all tables with basic information
                query = """
                SELECT 
                    t.TABLE_SCHEMA,
                    t.TABLE_NAME,
                    t.TABLE_TYPE,
                    ISNULL(ep.value, '') as TABLE_DESCRIPTION
                FROM INFORMATION_SCHEMA.TABLES t
                LEFT JOIN sys.tables st ON t.TABLE_NAME = st.name
                LEFT JOIN sys.extended_properties ep ON st.object_id = ep.major_id 
                    AND ep.minor_id = 0 
                    AND ep.name = 'MS_Description'
                WHERE t.TABLE_TYPE = 'BASE TABLE'
                ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME
                """
                
                result = self.execute_query(query)
                
                if result.get('success'):
                    return {
                        'success': True,
                        'tables': result['data']
                    }
                else:
                    return result
                
        except Exception as e:
            logger.error(f"Error getting table schema: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_sample_data(self, table_name: str, limit: int = 5, schema_name: str = 'dbo') -> Dict[str, Any]:
        """
        Get sample data from a table.
        
        Args:
            table_name: Name of the table
            limit: Number of sample rows to retrieve (default: 5)
            schema_name: Database schema name (default: 'dbo')
            
        Returns:
            Dict containing sample data and metadata
        """
        try:
            # Validate inputs
            if not table_name or not table_name.strip():
                return {
                    'success': False,
                    'error': 'Table name is required'
                }
            
            if limit <= 0 or limit > 100:
                limit = min(max(limit, 1), 100)  # Clamp between 1 and 100
            
            # Sanitize table name (basic validation)
            if not table_name.replace('_', '').replace('-', '').isalnum():
                return {
                    'success': False,
                    'error': 'Invalid table name format'
                }
            
            query = f"SELECT TOP {limit} * FROM [{schema_name}].[{table_name}]"
            return self.execute_query(query)
            
        except Exception as e:
            logger.error(f"Error getting sample data: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the database connection.
        
        Returns:
            Dict with connection test results
        """
        try:
            with self.get_connection() as conn:
                result = conn.execute(text("SELECT @@VERSION as version, GETDATE() as server_time"))
                row = result.fetchone()
                
                return {
                    'success': True,
                    'message': 'Database connection successful',
                    'server_info': {
                        'version': row[0] if row else 'Unknown',
                        'current_time': str(row[1]) if row else 'Unknown'
                    }
                }
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def close(self) -> None:
        """Close the database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed") 