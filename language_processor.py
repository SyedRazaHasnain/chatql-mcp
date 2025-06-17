"""
Natural Language Processing module for SQL query generation.

This module provides natural language to SQL conversion capabilities
using OpenAI's GPT models with enhanced context awareness and validation.
"""

import openai
from typing import Dict, Any, List, Optional, Tuple
from config import Config
import re
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LanguageProcessor:
    """
    Professional natural language processor for converting English queries to SQL.
    
    Uses OpenAI's GPT models to understand natural language queries and
    generate appropriate SQL statements with context from database schema.
    """
    
    def __init__(self, configuration: Optional[Config] = None):
        """
        Initialize the natural language processor.
        
        Args:
            configuration: Optional configuration object. If None, uses default Config()
        """
        self.configuration = configuration or Config()
        
        # Set up OpenAI client
        if self.configuration.OPENAI_API_KEY:
            openai.api_key = self.configuration.OPENAI_API_KEY
            logger.info("OpenAI API key configured successfully")
        else:
            logger.warning("No OpenAI API key provided. Natural language processing will be limited.")
        
        # Cache for schema information to reduce API calls
        self.database_schema_cache = {}
        
        # Common SQL patterns and aliases for pattern recognition
        self.sql_pattern_dictionary = {
            'top_records': r'(top|first|last)\s+(\d+)',
            'order_by_clause': r'(sorted|ordered)\s+by',
            'group_by_clause': r'(grouped|group)\s+by',
            'date_range_filter': r'(between|from|since|before|after)',
            'aggregate_functions': r'(sum|total|average|avg|count|maximum|max|minimum|min)',
        }
    
    def convert_natural_language_to_sql(self, natural_language_query: str, database_schema_information: Dict[str, Any], 
                    query_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convert natural language query to SQL with enhanced capabilities.
        
        Args:
            natural_language_query: The natural language query to convert
            database_schema_information: Database schema information for context
            query_context: Optional context (previous queries, user preferences, etc.)
            
        Returns:
            Dict containing conversion results, SQL query, and metadata
        """
        
        if not self.configuration.OPENAI_API_KEY:
            return {
                'success': False,
                'error': 'OpenAI API key not configured for natural language processing'
            }
        
        try:
            # Analyze query intent and structure
            query_analysis_result = self._analyze_natural_language_intent(natural_language_query)
            
            # Build enhanced schema context for AI processing
            enhanced_schema_context = self._build_comprehensive_schema_context(
                database_schema_information, query_analysis_result
            )
            
            # Generate SQL with retry mechanism for better reliability
            sql_generation_result = self._generate_sql_with_intelligent_retry(
                natural_language_query, 
                enhanced_schema_context, 
                query_analysis_result,
                query_context
            )
            
            if sql_generation_result['success']:
                # Validate and optimize the generated SQL
                sql_validation_result = self._validate_and_optimize_generated_sql(
                    sql_generation_result['sql_query'], 
                    database_schema_information
                )
                
                return {
                    'success': True,
                    'sql_query': sql_validation_result['query'],
                    'natural_query': natural_language_query,
                    'query_type': query_analysis_result['query_type'],
                    'confidence_score': sql_generation_result.get('confidence', 0.8),
                    'explanation': sql_generation_result.get('explanation', ''),
                    'warnings': sql_validation_result.get('warnings', []),
                    'suggestions': self._generate_intelligent_query_suggestions(
                        natural_language_query, database_schema_information
                    )
                }
            else:
                return sql_generation_result
            
        except Exception as exception:
            logger.error(f"Error in convert_natural_language_to_sql: {str(exception)}")
            return {
                'success': False,
                'error': f"Failed to convert natural language to SQL: {str(exception)}",
                'natural_query': natural_language_query
            }
    
    def _analyze_natural_language_intent(self, natural_language_query: str) -> Dict[str, Any]:
        """Analyze the intent and structure of the natural language query."""
        query_lowercase = natural_language_query.lower()
        
        intent_analysis = {
            'query_type': 'SELECT',  # default assumption
            'has_aggregation': False,
            'has_grouping': False,
            'has_ordering': False,
            'has_limit': False,
            'has_joins': False,
            'has_date_filter': False,
            'detected_entities': [],
            'filter_conditions': [],
            'special_features': []
        }
        
        # Detect query operation type
        if any(word in query_lowercase for word in ['insert', 'add', 'create new']):
            intent_analysis['query_type'] = 'INSERT'
        elif any(word in query_lowercase for word in ['update', 'modify', 'change', 'set']):
            intent_analysis['query_type'] = 'UPDATE'
        elif any(word in query_lowercase for word in ['delete', 'remove', 'drop']):
            intent_analysis['query_type'] = 'DELETE'
        
        # Detect SQL features and patterns
        if re.search(self.sql_pattern_dictionary['aggregate_functions'], query_lowercase):
            intent_analysis['has_aggregation'] = True
        
        if re.search(self.sql_pattern_dictionary['group_by_clause'], query_lowercase):
            intent_analysis['has_grouping'] = True
        
        if re.search(self.sql_pattern_dictionary['order_by_clause'], query_lowercase):
            intent_analysis['has_ordering'] = True
        
        if re.search(self.sql_pattern_dictionary['top_records'], query_lowercase):
            intent_analysis['has_limit'] = True
        
        if re.search(self.sql_pattern_dictionary['date_range_filter'], query_lowercase):
            intent_analysis['has_date_filter'] = True
        
        # Detect potential table joins
        if any(word in query_lowercase for word in ['with', 'and their', 'including', 'along with', 'join']):
            intent_analysis['has_joins'] = True
        
        return intent_analysis
    
    def _build_comprehensive_schema_context(self, database_schema_information: Dict[str, Any], 
                                     query_analysis_result: Dict[str, Any]) -> str:
        """Build an enhanced schema context with intelligent filtering."""
        context_sections = []
        
        # Add query type specific instructions
        context_sections.append(f"Query Operation Type: {query_analysis_result['query_type']}")
        
        if 'tables' in database_schema_information:
            # Filter and prioritize tables based on query analysis
            relevant_tables = self._identify_relevant_tables(
                database_schema_information.get('tables', []),
                query_analysis_result
            )
            
            context_sections.append("\nMost Relevant Database Tables:")
            for table in relevant_tables[:10]:  # Limit to top 10 most relevant
                context_sections.append(f"- {table['TABLE_NAME']}")
        
        if 'table_details' in database_schema_information:
            context_sections.append("\nDetailed Schema Information:")
            
            # Prioritize tables that seem most relevant to the query
            for table_name, column_details in database_schema_information['table_details'].items():
                if self._is_table_contextually_relevant(table_name, query_analysis_result):
                    context_sections.append(f"\nTable: {table_name}")
                    
                    # Group columns by type for better AI context
                    primary_key_columns = []
                    regular_data_columns = []
                    
                    for column in column_details:
                        formatted_column_info = self._format_column_information(column)
                        
                        if column.get('is_primary_key') or column.get('is_foreign_key'):
                            primary_key_columns.append(formatted_column_info)
                        else:
                            regular_data_columns.append(formatted_column_info)
                    
                    if primary_key_columns:
                        context_sections.append("  Key Columns:")
                        context_sections.extend([f"    {col}" for col in primary_key_columns])
                    
                    if regular_data_columns:
                        context_sections.append("  Data Columns:")
                        context_sections.extend([f"    {col}" for col in regular_data_columns[:15]])  # Limit columns
        
        # Add relationship information if available
        if 'relationships' in database_schema_information:
            context_sections.append("\nTable Relationships:")
            for relationship in database_schema_information['relationships'][:10]:  # Limit relationships
                context_sections.append(f"- {relationship['from_table']}.{relationship['from_column']} -> {relationship['to_table']}.{relationship['to_column']}")
        
        # Add SQL Server specific patterns and examples
        context_sections.append("\nSQL Server Best Practices:")
        context_sections.append("- Use TOP n for limiting results in SQL Server")
        context_sections.append("- Use GETDATE() for current date/time")
        context_sections.append("- Use DATEPART() for date components")
        context_sections.append("- Use CAST() or CONVERT() for type conversions")
        
        return "\n".join(context_sections)
    
    def _generate_sql_with_intelligent_retry(self, natural_language_query: str, schema_context: str, 
                                query_analysis_result: Dict[str, Any], 
                                query_context: Optional[Dict[str, Any]] = None, 
                                max_retry_attempts: int = 2) -> Dict[str, Any]:
        """Generate SQL with intelligent retry mechanism for improved reliability."""
        
        for attempt_number in range(max_retry_attempts):
            try:
                # Build comprehensive prompt for OpenAI
                ai_prompt = self._build_comprehensive_sql_prompt(
                    natural_language_query, 
                    schema_context, 
                    query_analysis_result, 
                    query_context,
                    attempt_number
                )
                
                # Call OpenAI API
                openai_response = openai.ChatCompletion.create(
                    model=self.configuration.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": ai_prompt}
                    ],
                    max_tokens=self.configuration.OPENAI_MAX_TOKENS,
                    temperature=0.1,  # Lower temperature for more consistent SQL generation
                    top_p=0.9
                )
                
                ai_response_content = openai_response.choices[0].message.content.strip()
                
                # Extract SQL query from AI response
                extracted_sql = self._extract_sql_from_ai_response(ai_response_content)
                
                if extracted_sql:
                    return {
                        'success': True,
                        'sql_query': extracted_sql,
                        'explanation': self._extract_explanation_from_ai_response(ai_response_content),
                        'confidence': 0.9 - (attempt_number * 0.1),  # Decrease confidence with retries
                        'attempt_number': attempt_number + 1
                    }
                else:
                    if attempt_number == max_retry_attempts - 1:
                        return {
                            'success': False,
                            'error': 'Could not extract valid SQL from AI response',
                            'ai_response': ai_response_content
                        }
                    
            except Exception as exception:
                logger.error(f"Attempt {attempt_number + 1} failed: {str(exception)}")
                if attempt_number == max_retry_attempts - 1:
                    return {
                        'success': False,
                        'error': f'All retry attempts failed. Last error: {str(exception)}'
                    }
        
        return {
            'success': False,
            'error': 'Maximum retry attempts exceeded'
        }
    
    def _build_comprehensive_sql_prompt(self, natural_language_query: str, schema_context: str, 
                         query_analysis_result: Dict[str, Any], query_context: Optional[Dict[str, Any]],
                         attempt_number: int) -> str:
        """Build a comprehensive prompt for SQL generation."""
        
        prompt_sections = []
        
        prompt_sections.append("Convert the following natural language query to SQL:")
        prompt_sections.append(f"Query: \"{natural_language_query}\"")
        prompt_sections.append("\nDatabase Schema Context:")
        prompt_sections.append(schema_context)
        
        # Add query analysis insights
        if query_analysis_result.get('has_aggregation'):
            prompt_sections.append("\nNote: This query requires aggregation functions (SUM, COUNT, AVG, etc.)")
        
        if query_analysis_result.get('has_joins'):
            prompt_sections.append("Note: This query likely requires table joins")
        
        if query_analysis_result.get('has_date_filter'):
            prompt_sections.append("Note: This query involves date/time filtering")
        
        # Add context from previous attempts if this is a retry
        if attempt_number > 0:
            prompt_sections.append(f"\nThis is retry attempt #{attempt_number + 1}. Please ensure the SQL is valid and executable.")
        
        # Add specific formatting requirements
        prompt_sections.append("\nRequirements:")
        prompt_sections.append("1. Generate valid SQL Server syntax")
        prompt_sections.append("2. Use proper table and column names from the schema")
        prompt_sections.append("3. Include appropriate WHERE clauses for filters")
        prompt_sections.append("4. Use TOP instead of LIMIT for SQL Server")
        prompt_sections.append("5. Format the response as: SQL: [your query here]")
        prompt_sections.append("6. Provide a brief explanation after the SQL")
        
        return "\n".join(prompt_sections)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for OpenAI interactions."""
        return """You are an expert SQL developer specializing in Microsoft SQL Server. 
        Generate accurate, efficient SQL queries based on natural language requests. 
        Always use proper SQL Server syntax and best practices. 
        Ensure queries are safe and performant."""
    
    def _validate_and_optimize_generated_sql(self, generated_sql_query: str, database_schema_information: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and optimize the generated SQL query."""
        
        validation_warnings = []
        optimized_query = generated_sql_query.strip()
        
        # Basic SQL validation
        if not optimized_query.upper().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE')):
            validation_warnings.append("Query does not start with a valid SQL command")
        
        # Check for potentially dangerous operations
        dangerous_patterns = ['DROP ', 'TRUNCATE ', 'ALTER ']
        for pattern in dangerous_patterns:
            if pattern in optimized_query.upper():
                validation_warnings.append(f"Query contains potentially dangerous operation: {pattern.strip()}")
        
        # Validate table names against schema
        mentioned_tables = self._extract_table_names_from_sql(optimized_query)
        if database_schema_information.get('tables'):
            available_table_names = [table['TABLE_NAME'].lower() for table in database_schema_information['tables']]
            for table_name in mentioned_tables:
                if table_name.lower() not in available_table_names:
                    validation_warnings.append(f"Table '{table_name}' not found in database schema")
        
        return {
            'query': optimized_query,
            'warnings': validation_warnings,
            'is_valid': len(validation_warnings) == 0
        }
    
    def _extract_table_names_from_sql(self, sql_query: str) -> List[str]:
        """Extract table names from SQL query using regex patterns."""
        # Simple regex to find table names (this could be more sophisticated)
        table_pattern = r'(?:FROM|JOIN|INTO|UPDATE)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(table_pattern, sql_query, re.IGNORECASE)
        return list(set(matches))  # Remove duplicates
    
    def _identify_relevant_tables(self, database_tables: List[Dict[str, Any]], 
                            query_analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify tables most relevant to the query."""
        # For now, return all tables. In future, could implement scoring based on query content
        return database_tables
    
    def _is_table_contextually_relevant(self, table_name: str, query_analysis_result: Dict[str, Any]) -> bool:
        """Determine if a table is contextually relevant to the query."""
        # Simple heuristic - could be enhanced with ML or semantic analysis
        return True
    
    def _generate_intelligent_query_suggestions(self, natural_language_query: str, 
                                  database_schema_information: Dict[str, Any]) -> List[str]:
        """Generate intelligent suggestions for query improvements."""
        suggestions = []
        
        query_lowercase = natural_language_query.lower()
        
        # Suggest specific optimizations based on query content
        if 'all' in query_lowercase and 'customer' in query_lowercase:
            suggestions.append("Consider adding specific filters to limit results")
        
        if 'last' in query_lowercase or 'recent' in query_lowercase:
            suggestions.append("You might want to specify a time range (e.g., 'last 30 days')")
        
        if 'best' in query_lowercase or 'top' in query_lowercase:
            suggestions.append("Consider specifying how many results you want (e.g., 'top 10')")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _format_column_information(self, column_data: Dict[str, Any]) -> str:
        """Format column information for AI context."""
        column_name = column_data.get('COLUMN_NAME', 'unknown')
        data_type = column_data.get('DATA_TYPE', 'unknown')
        max_length = column_data.get('CHARACTER_MAXIMUM_LENGTH')
        
        if max_length:
            return f"{column_name} ({data_type}({max_length}))"
        else:
            return f"{column_name} ({data_type})"
    
    def _extract_sql_from_ai_response(self, ai_response: str) -> Optional[str]:
        """Extract SQL query from OpenAI response."""
        # Look for SQL: prefix
        sql_match = re.search(r'SQL:\s*(.+?)(?=\n\n|\nExplanation|\Z)', ai_response, re.DOTALL | re.IGNORECASE)
        if sql_match:
            return sql_match.group(1).strip()
        
        # Look for code blocks
        code_block_match = re.search(r'```(?:sql)?\s*(.+?)\s*```', ai_response, re.DOTALL | re.IGNORECASE)
        if code_block_match:
            return code_block_match.group(1).strip()
        
        return None
    
    def _extract_explanation_from_ai_response(self, ai_response: str) -> str:
        """Extract explanation from OpenAI response."""
        # Look for explanation after SQL
        explanation_match = re.search(r'(?:Explanation|Analysis):\s*(.+)', ai_response, re.DOTALL | re.IGNORECASE)
        if explanation_match:
            return explanation_match.group(1).strip()
        
        return "Query generated successfully"
    
    def explain_sql_query(self, sql_query: str) -> Dict[str, Any]:
        """Provide a detailed explanation of an SQL query."""
        try:
            if not self.configuration.OPENAI_API_KEY:
                return {
                    'success': False,
                    'error': 'OpenAI API key required for SQL explanation'
                }
            
            explanation_prompt = f"""
            Explain this SQL query in simple terms:
            
            {sql_query}
            
            Please provide:
            1. What the query does
            2. Which tables it accesses
            3. What conditions it applies
            4. What data it returns
            """
            
            openai_response = openai.ChatCompletion.create(
                model=self.configuration.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a SQL expert who explains queries clearly."},
                    {"role": "user", "content": explanation_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return {
                'success': True,
                'explanation': openai_response.choices[0].message.content.strip(),
                'sql_query': sql_query
            }
            
        except Exception as exception:
            return {
                'success': False,
                'error': f'Error explaining SQL query: {str(exception)}'
            }
    
    def suggest_query_optimizations(self, sql_query: str, 
                                 execution_statistics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Suggest optimizations for an SQL query."""
        optimization_suggestions = []
        
        query_uppercase = sql_query.upper()
        
        # Basic optimization suggestions
        if 'SELECT *' in query_uppercase:
            optimization_suggestions.append("Consider selecting only needed columns instead of using SELECT *")
        
        if 'ORDER BY' not in query_uppercase and 'TOP' in query_uppercase:
            optimization_suggestions.append("Consider adding ORDER BY clause when using TOP")
        
        if query_uppercase.count('JOIN') > 3:
            optimization_suggestions.append("Query has multiple joins - consider if all are necessary")
        
        # Execution-based suggestions
        if execution_statistics:
            execution_time = execution_statistics.get('execution_time', 0)
            if execution_time > 5:  # More than 5 seconds
                optimization_suggestions.append("Query execution time is high - consider adding indexes or optimizing joins")
        
        return {
            'success': True,
            'suggestions': optimization_suggestions,
            'sql_query': sql_query
        }