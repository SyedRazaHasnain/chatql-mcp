# Natural Language SQL MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![SQL Server](https://img.shields.io/badge/SQL%20Server-2019+-red.svg)](https://www.microsoft.com/en-us/sql-server/)

A powerful **Model Context Protocol (MCP)** server that enables natural language querying of SQL Server databases. Transform your English questions into SQL queries automatically using OpenAI's GPT models, with intelligent schema awareness and query optimization.

## 🌟 Features

- 🗣️ **Natural Language to SQL**: Convert English questions to SQL queries automatically
- 🧠 **Schema-Aware**: Intelligent understanding of your database structure
- 🔍 **Multiple Query Methods**: Natural language, direct SQL, and schema exploration
- 📊 **Rich Results**: Formatted results with explanations and query analysis
- 🛡️ **Safety First**: Built-in query validation and result limiting
- 🔌 **MCP Protocol**: Native integration with AI assistants supporting MCP
- ⚡ **High Performance**: Connection pooling and query optimization
- 🎯 **Professional Logging**: Comprehensive logging and error handling

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **SQL Server Express** (or any SQL Server edition)
- **ODBC Driver 17** for SQL Server
- **OpenAI API Key** (for natural language processing)

### Installation

1. **Clone the repository**
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

4. **Configure environment**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   # Database Configuration
   DB_SERVER=localhost\SQLEXPRESS
   DB_DATABASE=your_database_name
   DB_USERNAME=               # Leave empty for Windows Auth
   DB_PASSWORD=               # Leave empty for Windows Auth
   DB_DRIVER=ODBC Driver 17 for SQL Server

   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Start the server**
   ```bash
   python server.py
   ```

## 🛠️ Available Tools

When connected via MCP, the server provides these powerful tools:

### 1. `natural_language_query`
Transform natural language into SQL and execute queries.

**Example:**
```
Query: "Show me the top 10 customers by total order value"
```

### 2. `direct_sql_query`
Execute SQL queries directly with safety validation.

**Example:**
```sql
SELECT TOP 10 CustomerName, SUM(OrderValue) as Total
FROM Customers c JOIN Orders o ON c.ID = o.CustomerID
GROUP BY CustomerName ORDER BY Total DESC
```

### 3. `get_table_info`
Get detailed schema information for any table.

### 4. `list_tables`
Explore all available tables in your database.

### 5. `get_sample_data`
Preview sample data from any table.

## 📋 Example Queries

Here are some example natural language queries you can try:

### Business Intelligence
- *"What are our top 5 selling products this month?"*
- *"Show me customers who haven't ordered in the last 90 days"*
- *"What's the average order value by region?"*

### Data Exploration
- *"How many records are in the customers table?"*
- *"What are the different product categories we have?"*
- *"Show me all orders placed yesterday"*

### Analytics
- *"What's our monthly revenue trend for this year?"*
- *"Which sales rep has the highest performance?"*
- *"Find duplicate customer records"*

## ⚙️ Configuration Options

### Database Settings
```env
DB_SERVER=localhost\SQLEXPRESS    # SQL Server instance
DB_DATABASE=YourDatabase          # Target database
DB_USERNAME=                      # Username (optional for Windows Auth)
DB_PASSWORD=                      # Password (optional for Windows Auth)
DB_DRIVER=ODBC Driver 17 for SQL Server
```

### OpenAI Settings
```env
OPENAI_API_KEY=sk-...            # Your OpenAI API key
OPENAI_MODEL=gpt-4               # Model to use
OPENAI_MAX_TOKENS=2000           # Max tokens per request
```

### Server Settings
```env
MCP_SERVER_NAME=natural-language-sql-server
MCP_SERVER_VERSION=1.0.0
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
MAX_QUERY_RESULTS=100            # Limit query results
QUERY_TIMEOUT=30                 # Query timeout in seconds
```

## 🔧 MCP Integration

### Claude Desktop

Add to your Claude configuration:

```json
{
  "mcpServers": {
       "natural-language-sql": {
     "command": "python",
     "args": ["/path/to/your/server.py"],
     "env": {
        "DB_SERVER": "localhost\\SQLEXPRESS",
        "DB_DATABASE": "YourDatabase",
        "OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Other MCP Clients

This server follows the standard MCP protocol and should work with any compatible client.

## 🛡️ Security & Safety

### Built-in Protections
- **Query Validation**: Dangerous operations (DROP, TRUNCATE) are blocked
- **Result Limiting**: Automatic limits prevent memory exhaustion
- **Parameterized Queries**: Protection against SQL injection
- **Connection Pooling**: Secure and efficient database connections

### Best Practices
- Use read-only database accounts when possible
- Never expose the server to the internet
- Store credentials securely using environment variables
- Regularly rotate API keys and database passwords

## 🚨 Troubleshooting

### Database Connection Issues

**Error: "Data source name not found"**
```bash
# Install ODBC Driver 17 for SQL Server
# Download from Microsoft's official website
```

**Error: "Login failed"**
- Verify your credentials in `.env`
- For Windows Auth, leave username/password empty
- Ensure SQL Server allows your authentication method

**Error: "Named Pipes Provider error"**
- Verify SQL Server is running
- Check server name (usually `localhost\SQLEXPRESS`)
- Enable TCP/IP in SQL Server Configuration Manager

### OpenAI API Issues

**Error: "OpenAI API key not configured"**
- Set `OPENAI_API_KEY` in your `.env` file
- Get an API key from https://platform.openai.com/

**Error: Rate limiting**
- The server handles rate limits gracefully
- Consider upgrading your OpenAI plan for higher limits

## 🧪 Development

### Running Tests
```bash
# Tests coming soon!
python -m pytest
```

### Code Style
```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- Setting up development environment
- Code standards and best practices
- Pull request process

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Powered by [OpenAI GPT Models](https://openai.com/)
- Uses [SQLAlchemy](https://www.sqlalchemy.org/) for database connectivity

## 📞 Support

- 🐛 **Found a bug?** [Open an issue](https://github.com/your-username/natural-language-sql-mcp/issues)
- 💡 **Have a feature request?** [Start a discussion](https://github.com/your-username/natural-language-sql-mcp/discussions)
- 📧 **Need help?** Check our [troubleshooting guide](#-troubleshooting)

---

**Made with ❤️ by [Raza Hasnain](https://github.com/your-username)** 