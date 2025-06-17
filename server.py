#!/usr/bin/env python3
"""
Natural Language SQL MCP Server

A Model Context Protocol (MCP) server that provides natural language to SQL
conversion capabilities for SQL Server databases.

Author: Raza Hasnain
Version: 1.0.0
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import mcp.server.stdio
import mcp.types as types

from database_manager import DatabaseManager
from language_processor import LanguageProcessor
from config import Config

# Configure logging
def configure_application_logging(configuration: Config) -> None:
    """Configure comprehensive logging for the application."""
    log_level = getattr(logging, configuration.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr),  # Use stderr to avoid interfering with MCP stdio
        ]
    )

# Initialize configuration and logging
application_config = Config()
configure_application_logging(application_config)
logger = logging.getLogger("natural-language-sql-server")

# Create the server instance
mcp_server = Server(application_config.MCP_SERVER_NAME)

# Global instances (will be initialized in main)
database_manager: Optional[DatabaseManager] = None
language_processor: Optional[LanguageProcessor] = None


@mcp_server.list_tools()
async def list_available_tools() -> List[types.Tool]:
    """List all available tools for natural language SQL operations."""
    return [
        types.Tool(
            name="execute_natural_language_query",
            description="Convert natural language to SQL and execute the query against the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "natural_language_query": {
                        "type": "string",
                        "description": "Natural language query to execute (e.g., 'Show me all customers from New York')"
                    },
                    "include_explanation": {
                        "type": "boolean",
                        "description": "Whether to include explanations and query analysis (default: true)",
                        "default": True
                    }
                },
                "required": ["natural_language_query"]
            }
        ),
        types.Tool(
            name="execute_direct_sql_query",
            description="Execute a direct SQL query against the database with safety validation",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "SQL query to execute"
                    }
                },
                "required": ["sql_query"]
            }
        ),
        types.Tool(
            name="get_table_information",
            description="Get detailed schema information about a specific database table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to get information for"
                    },
                    "schema_name": {
                        "type": "string",
                        "description": "Database schema name (default: 'dbo')",
                        "default": "dbo"
                    }
                },
                "required": ["table_name"]
            }
        ),
        types.Tool(
            name="list_database_tables",
            description="List all tables available in the database with schema information",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_table_sample_data",
            description="Retrieve sample data from a specific table for exploration",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to get sample data from"
                    },
                    "sample_size": {
                        "type": "integer",
                        "description": "Number of sample rows to retrieve (default: 5, max: 20)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    },
                    "schema_name": {
                        "type": "string",
                        "description": "Database schema name (default: 'dbo')",
                        "default": "dbo"
                    }
                },
                "required": ["table_name"]
            }
        )
    ]


@mcp_server.call_tool()
async def handle_tool_execution(
    tool_name: str, 
    tool_arguments: Optional[Dict[str, Any]] = None
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Handle tool execution with comprehensive error handling and logging."""
    try:
        logger.info(f"Executing tool: {tool_name}")
        
        if not tool_arguments:
            tool_arguments = {}
        
        if tool_name == "execute_natural_language_query":
            return await process_natural_language_query(tool_arguments)
        elif tool_name == "execute_direct_sql_query":
            return await process_direct_sql_query(tool_arguments)
        elif tool_name == "get_table_information":
            return await retrieve_table_information(tool_arguments)
        elif tool_name == "list_database_tables":
            return await list_all_database_tables(tool_arguments)
        elif tool_name == "get_table_sample_data":
            return await retrieve_table_sample_data(tool_arguments)
        else:
            error_message = f"Unknown tool: {tool_name}"
            logger.error(error_message)
            return [types.TextContent(type="text", text=f"❌ {error_message}")]
            
    except Exception as exception:
        error_message = f"Error executing tool {tool_name}: {str(exception)}"
        logger.error(error_message, exc_info=True)
        return [types.TextContent(type="text", text=f"❌ {error_message}")]


async def process_natural_language_query(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Process natural language query conversion and execution."""
    natural_language_query = arguments.get("natural_language_query", "").strip()
    include_explanation = arguments.get("include_explanation", True)
    
    if not natural_language_query:
        return [types.TextContent(type="text", text="❌ Error: Natural language query is required")]
    
    try:
        logger.info(f"Processing natural language query: {natural_language_query[:100]}...")
        
        # Get database schema for context
        database_schema_information = database_manager.get_table_schema()
        
        if not database_schema_information.get('success'):
            return [types.TextContent(
                type="text", 
                text=f"❌ Error retrieving database schema: {database_schema_information.get('error')}"
            )]
        
        # Enhance schema with detailed table information
        if database_schema_information.get('tables'):
            detailed_table_schemas = {}
            for table in database_schema_information['tables'][:10]:  # Limit to first 10 tables
                table_schema_name = table.get('TABLE_SCHEMA', 'dbo')
                table_name = table['TABLE_NAME']
                fully_qualified_table_name = f"{table_schema_name}.{table_name}"
                
                table_schema_details = database_manager.get_table_schema(table_name, table_schema_name)
                if table_schema_details.get('success'):
                    detailed_table_schemas[fully_qualified_table_name] = table_schema_details['columns']
                    # Also add without schema for backward compatibility
                    detailed_table_schemas[table_name] = table_schema_details['columns']
            database_schema_information['table_details'] = detailed_table_schemas
        
        # Convert natural language to SQL
        language_processing_result = language_processor.convert_natural_language_to_sql(
            natural_language_query, database_schema_information
        )
        
        if not language_processing_result.get('success'):
            return [types.TextContent(
                type="text", 
                text=f"❌ Error converting query: {language_processing_result.get('error')}"
            )]
        
        generated_sql_query = language_processing_result['sql_query']
        
        # Execute the generated SQL query
        query_execution_result = database_manager.execute_query(generated_sql_query)
        
        # Format comprehensive response
        response_sections = []
        response_sections.append(f"**Natural Language Query:** {natural_language_query}")
        response_sections.append(f"**Generated SQL:**\n```sql\n{generated_sql_query}\n```")
        
        if include_explanation and language_processing_result.get('explanation'):
            response_sections.append(f"**Query Analysis:** {language_processing_result['explanation']}")
        
        if query_execution_result.get('success'):
            if 'data' in query_execution_result:
                record_count = query_execution_result['row_count']
                execution_time = query_execution_result.get('execution_time', 0)
                
                response_sections.append(f"**Results:** Found {record_count} records (executed in {execution_time:.2f}s)")
                
                # Display sample results
                if record_count > 0:
                    sample_data = query_execution_result['data'][:10]  # Limit to 10 records
                    response_sections.append("**Sample Data:**")
                    response_sections.append("```json")
                    response_sections.append(json.dumps(sample_data, indent=2, default=str))
                    response_sections.append("```")
                    
                    if record_count > 10:
                        response_sections.append(f"*(Showing first 10 of {record_count} records)*")
                        
                    if query_execution_result.get('limited'):
                        response_sections.append(f"⚠️ *Results were limited to {application_config.MAX_QUERY_RESULTS} records*")
            else:
                response_sections.append(f"**Result:** {query_execution_result.get('message', 'Query executed successfully')}")
            
            # Add AI suggestions if available
            if language_processing_result.get('suggestions'):
                response_sections.append("**Suggestions:**")
                for suggestion in language_processing_result['suggestions'][:3]:  # Limit suggestions
                    response_sections.append(f"- {suggestion}")
        else:
            response_sections.append(f"❌ **Error:** {query_execution_result.get('error')}")
        
        return [types.TextContent(type="text", text="\n\n".join(response_sections))]
        
    except Exception as exception:
        error_message = f"Unexpected error processing query: {str(exception)}"
        logger.error(error_message, exc_info=True)
        return [types.TextContent(type="text", text=f"❌ {error_message}")]


async def process_direct_sql_query(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Process direct SQL query execution with safety validation."""
    sql_query = arguments.get("sql_query", "").strip()
    
    if not sql_query:
        return [types.TextContent(type="text", text="❌ Error: SQL query is required")]
    
    try:
        logger.info(f"Executing direct SQL query: {sql_query[:100]}...")
        
        # Execute the SQL query
        query_execution_result = database_manager.execute_query(sql_query)
        
        # Format comprehensive response
        response_sections = []
        response_sections.append(f"**SQL Query:**\n```sql\n{sql_query}\n```")
        
        if query_execution_result.get('success'):
            if 'data' in query_execution_result:
                record_count = query_execution_result['row_count']
                execution_time = query_execution_result.get('execution_time', 0)
                
                response_sections.append(f"**Results:** {record_count} records (executed in {execution_time:.2f}s)")
                
                if record_count > 0:
                    # Display results
                    sample_data = query_execution_result['data'][:20]  # Limit to 20 records for direct queries
                    response_sections.append("**Data:**")
                    response_sections.append("```json")
                    response_sections.append(json.dumps(sample_data, indent=2, default=str))
                    response_sections.append("```")
                    
                    if record_count > 20:
                        response_sections.append(f"*(Showing first 20 of {record_count} records)*")
            else:
                response_sections.append(f"**Result:** {query_execution_result.get('message', 'Query executed successfully')}")
        else:
            response_sections.append(f"❌ **Error:** {query_execution_result.get('error')}")
        
        return [types.TextContent(type="text", text="\n\n".join(response_sections))]
        
    except Exception as exception:
        error_message = f"Error executing SQL query: {str(exception)}"
        logger.error(error_message, exc_info=True)
        return [types.TextContent(type="text", text=f"❌ {error_message}")]


async def retrieve_table_information(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Retrieve comprehensive information about a database table."""
    table_name = arguments.get("table_name", "").strip()
    schema_name = arguments.get("schema_name", "dbo").strip()
    
    if not table_name:
        return [types.TextContent(type="text", text="❌ Error: Table name is required")]
    
    try:
        logger.info(f"Retrieving table information for: {schema_name}.{table_name}")
        
        # Get comprehensive table schema
        table_schema_information = database_manager.get_table_schema(table_name, schema_name)
        
        if not table_schema_information.get('success'):
            return [types.TextContent(
                type="text",
                text=f"❌ Error retrieving table information: {table_schema_information.get('error')}"
            )]
        
        # Format comprehensive response
        response_sections = []
        response_sections.append(f"**Table:** {schema_name}.{table_name}")
        
        table_columns = table_schema_information.get('columns', [])
        if table_columns:
            response_sections.append(f"**Columns:** ({len(table_columns)} total)")
            response_sections.append("```")
            for column in table_columns:
                column_name = column['COLUMN_NAME']
                data_type = column['DATA_TYPE']
                nullable_indicator = "NULL" if column['IS_NULLABLE'] == 'YES' else "NOT NULL"
                primary_key_indicator = "🔑 " if column.get('IS_PRIMARY_KEY') else ""
                foreign_key_indicator = "🔗 " if column.get('IS_FOREIGN_KEY') else ""
                
                max_length = column.get('CHARACTER_MAXIMUM_LENGTH', '')
                if max_length:
                    data_type = f"{data_type}({max_length})"
                
                response_sections.append(f"{primary_key_indicator}{foreign_key_indicator}{column_name}: {data_type} {nullable_indicator}")
            response_sections.append("```")
        
        return [types.TextContent(type="text", text="\n".join(response_sections))]
        
    except Exception as exception:
        error_message = f"Error retrieving table information: {str(exception)}"
        logger.error(error_message, exc_info=True)
        return [types.TextContent(type="text", text=f"❌ {error_message}")]


async def list_all_database_tables(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """List all tables available in the database."""
    try:
        logger.info("Listing all database tables")
        
        # Get all database tables
        database_tables_information = database_manager.get_table_schema()
        
        if not database_tables_information.get('success'):
            return [types.TextContent(
                type="text",
                text=f"❌ Error retrieving tables: {database_tables_information.get('error')}"
            )]
        
        available_tables = database_tables_information.get('tables', [])
        
        if not available_tables:
            return [types.TextContent(type="text", text="No tables found in the database.")]
        
        # Format comprehensive response
        response_sections = []
        response_sections.append(f"**Database Tables:** ({len(available_tables)} total)")
        response_sections.append("")
        
        # Group tables by schema
        schema_tables = {}
        for table in available_tables:
            schema_name = table['TABLE_SCHEMA']
            if schema_name not in schema_tables:
                schema_tables[schema_name] = []
            schema_tables[schema_name].append(table['TABLE_NAME'])
        
        for schema_name, table_names in schema_tables.items():
            response_sections.append(f"**Schema: {schema_name}**")
            for table_name in sorted(table_names):
                response_sections.append(f"- {table_name}")
            response_sections.append("")
        
        return [types.TextContent(type="text", text="\n".join(response_sections))]
        
    except Exception as exception:
        error_message = f"Error listing database tables: {str(exception)}"
        logger.error(error_message, exc_info=True)
        return [types.TextContent(type="text", text=f"❌ {error_message}")]


async def retrieve_table_sample_data(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Retrieve sample data from a specified table."""
    table_name = arguments.get("table_name", "").strip()
    sample_size = arguments.get("sample_size", 5)
    schema_name = arguments.get("schema_name", "dbo").strip()
    
    if not table_name:
        return [types.TextContent(type="text", text="❌ Error: Table name is required")]
    
    # Validate and clamp sample size
    sample_size = max(1, min(sample_size, 20))
    
    try:
        logger.info(f"Retrieving sample data from: {schema_name}.{table_name} (sample size: {sample_size})")
        
        # Get sample data
        sample_data_result = database_manager.get_sample_data(table_name, sample_size, schema_name)
        
        if not sample_data_result.get('success'):
            return [types.TextContent(
                type="text",
                text=f"❌ Error retrieving sample data: {sample_data_result.get('error')}"
            )]
        
        # Format comprehensive response
        response_sections = []
        response_sections.append(f"**Sample Data from {schema_name}.{table_name}:**")
        
        sample_records = sample_data_result.get('data', [])
        if sample_records:
            response_sections.append(f"**Records:** {len(sample_records)} of {sample_size} requested")
            response_sections.append("```json")
            response_sections.append(json.dumps(sample_records, indent=2, default=str))
            response_sections.append("```")
        else:
            response_sections.append("No data found in the table.")
        
        return [types.TextContent(type="text", text="\n".join(response_sections))]
        
    except Exception as exception:
        error_message = f"Error retrieving sample data: {str(exception)}"
        logger.error(error_message, exc_info=True)
        return [types.TextContent(type="text", text=f"❌ {error_message}")]


async def initialize_and_run_server():
    """Initialize and run the MCP server with comprehensive setup."""
    global database_manager, language_processor

    logger.info(f"Starting {application_config.MCP_SERVER_NAME} v{application_config.MCP_SERVER_VERSION}")
    
    try:
        # Validate configuration
        if not application_config.validate_configuration():
            logger.error("Configuration validation failed")
            return 1
        
        # Initialize database manager
        logger.info("Initializing database connection...")
        database_manager = DatabaseManager(application_config)
        
        # Test database connection
        connection_test_result = database_manager.test_connection()
        if not connection_test_result.get('success'):
            logger.error(f"Database connection test failed: {connection_test_result.get('error')}")
            return 1
        
        logger.info(f"Database connected successfully: {connection_test_result.get('server_info', {}).get('version', 'Unknown')}")
        
        # Initialize language processor
        logger.info("Initializing natural language processor...")
        language_processor = LanguageProcessor(application_config)
        
        logger.info("MCP server initialized successfully")

        # Run the MCP server via stdio
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=application_config.MCP_SERVER_NAME,
                    server_version=application_config.MCP_SERVER_VERSION,
                    capabilities=mcp_server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
            
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        return 0
    except Exception as exception:
        logger.error(f"Server error: {exception}", exc_info=True)
        return 1
    finally:
        # Cleanup resources
        if database_manager:
            database_manager.close()
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    exit_code = asyncio.run(initialize_and_run_server())
    sys.exit(exit_code) 