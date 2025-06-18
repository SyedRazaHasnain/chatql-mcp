# ChatQL MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![SQL Server](https://img.shields.io/badge/SQL%20Server-2019+-red.svg)](https://www.microsoft.com/en-us/sql-server/)

A powerful **Model Context Protocol (MCP)** server that enables natural language querying of SQL Server databases. Transform your English questions into SQL queries automatically using OpenAI's GPT models, with intelligent schema awareness and query optimization.

**🚀 Perfect for developers using Cursor AI** - Integrate directly into your development workflow for instant database insights, schema exploration, and data analysis without leaving your code editor.

## 🗃️ Database Support

**Currently Supported:**
- ✅ **Microsoft SQL Server** (2017+)
- ✅ **SQL Server Express**
- ✅ **Azure SQL Database**

**Coming Soon:**
- 🔄 **PostgreSQL** (in development)
- 🔄 **MySQL/MariaDB** (planned)
- 🔄 **SQLite** (planned)
- 🔄 **Oracle Database** (planned)

> **Note:** This version is specifically designed for SQL Server. Support for additional database systems is actively being developed and will be available in future releases.

## 🌟 Features

### **Core Database Capabilities**
- 🗣️ **Natural Language to SQL**: Convert English questions to SQL queries automatically
- 🧠 **Schema-Aware**: Intelligent understanding of your database structure
- 🔍 **Multiple Query Methods**: Natural language, direct SQL, and schema exploration
- 📊 **Rich Results**: Formatted results with explanations and query analysis
- 🛡️ **Safety First**: Built-in query validation and result limiting

### **Developer Integration**
- 🔌 **MCP Protocol**: Native integration with Claude Desktop and Cursor AI
- 💻 **IDE Integration**: Perfect for development workflows in Cursor
- ⚡ **High Performance**: Connection pooling and query optimization
- 🎯 **Professional Logging**: Comprehensive logging and error handling

### **Perfect for Development Teams**
- 🚀 **Rapid Prototyping**: Get database insights without leaving your code editor
- 🔍 **Schema Exploration**: Understand database structure while coding
- 🐛 **Data Debugging**: Find data issues quickly during development
- 📊 **Quick Analytics**: Generate reports and insights on-demand
- 🏗️ **Database Design**: Understand relationships and optimize queries

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **SQL Server Express** (or any SQL Server edition)
- **ODBC Driver 17** for SQL Server
- **OpenAI API Key** (for natural language processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SyedRazaHasnain/chatql-mcp.git
   cd chatql-mcp
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

5. **Connect to your AI client**
   
   Choose your preferred AI client:
   - **🖥️ Claude Desktop** - General use and data analysis
   - **💻 Cursor AI** - Perfect for development workflows (Recommended for developers!)
   
   No need to start the server manually - your AI client will launch it automatically!

## 🛠️ Available Tools

When connected via MCP, the server provides these powerful tools:

### 1. `execute_natural_language_query`
Transform natural language into SQL and execute queries.

**Example:**
```
Query: "Show me the top 10 customers by total order value"
```

### 2. `execute_direct_sql_query`
Execute SQL queries directly with safety validation.

**Example:**
```sql
SELECT TOP 10 CustomerName, SUM(OrderValue) as Total
FROM Customers c JOIN Orders o ON c.ID = o.CustomerID
GROUP BY CustomerName ORDER BY Total DESC
```

### 3. `get_table_information`
Get detailed schema information for any table.

### 4. `list_database_tables`
Explore all available tables in your database.

### 5. `get_table_sample_data`
Preview sample data from any table.

## 📋 Example Queries

Here are some example natural language queries you can try:

### 💻 Development Workflows (Perfect for Cursor)
- *"Show me all database tables and their relationships"*
- *"What columns are in the users table?"*
- *"Give me sample data from the products table for testing"*
- *"Find users created in the last week for debugging"*
- *"Are there any foreign key constraints I should know about?"*
- *"Show me the schema for the orders table"*

### 📊 Business Intelligence
- *"What are our top 5 selling products this month?"*
- *"Show me customers who haven't ordered in the last 90 days"*
- *"What's the average order value by region?"*

### 🔍 Data Exploration
- *"How many records are in the customers table?"*
- *"What are the different product categories we have?"*
- *"Show me all orders placed yesterday"*

### 📈 Analytics
- *"What's our monthly revenue trend for this year?"*
- *"Which sales rep has the highest performance?"*
- *"Find duplicate customer records"*

### 🐛 Debugging & Troubleshooting
- *"Find orphaned records in the order_items table"*
- *"Show me users with missing email addresses"*
- *"What are the most common error codes in our logs table?"*
- *"Find products that have never been ordered"*

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
MCP_SERVER_NAME=chatql-mcp-server
MCP_SERVER_VERSION=1.0.0
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
MAX_QUERY_RESULTS=100            # Limit query results
QUERY_TIMEOUT=30                 # Query timeout in seconds
```

## 🔧 Connecting with AI Clients

### Supported MCP Clients

This server works with any MCP-compatible client:

- **✅ Claude Desktop** - Official Anthropic desktop application
- **✅ Cursor AI** - AI-powered code editor (Perfect for development!)
- **✅ Other MCP Clients** - Any application supporting the MCP protocol

### How MCP Connection Works

Your ChatQL server uses the **Model Context Protocol (MCP)** with `stdio` communication:

1. **Client reads your config** → Finds your server details
2. **Client launches your server** → Runs `python server.py` as a subprocess  
3. **Communicates via stdin/stdout** → JSON messages over standard streams
4. **Your server stays running** → Processes requests until client closes

### 1. **Find Claude Desktop Config File**

**For Windows Users (Step-by-Step):**

1. **Press `Windows Key + R`** (opens the Run dialog)
2. **Type:** `%APPDATA%` and press Enter
3. **Look for the "Claude" folder** and double-click it
4. **Find the file:** `claude_desktop_config.json`
   - If the file doesn't exist, create it by right-clicking → New → Text Document
   - Name it exactly: `claude_desktop_config.json` (not .txt!)

**For Mac Users:**
1. **Press `Cmd + Shift + G`** (opens Go to Folder)
2. **Type:** `~/Library/Application Support/Claude/`
3. **Find or create:** `claude_desktop_config.json`

### 2. **Edit the Config File**

**Open the file with Notepad (Windows) or TextEdit (Mac) and add this:**

```json
{
  "mcpServers": {
    "chatql-mcp": {
      "command": "python",
      "args": ["C:/Users/YourUsername/Desktop/mcp/server.py"],
      "env": {
        "DB_SERVER": "localhost\\SQLEXPRESS",
        "DB_DATABASE": "YourDatabase",
        "OPENAI_API_KEY": "your-openai-api-key"
      }
    }
  }
}
```

**🚨 CRITICAL: Replace these with YOUR actual values:**
- `C:/Users/YourUsername/Desktop/mcp/server.py` → **Your actual full path to server.py**
- `YourDatabase` → **Your actual database name**  
- `your-openai-api-key` → **Your actual OpenAI API key**

**💡 How to find your server.py path:**
1. **Navigate to your project folder** (where you saved ChatQL)
2. **Right-click on `server.py`**
3. **Click "Properties"** (Windows) or "Get Info" (Mac)
4. **Copy the full path** and paste it in the config

### 3. **Start Claude Desktop**

1. **Save your configuration file** (Ctrl+S)
2. **Close Claude Desktop completely** (right-click system tray icon → Exit)
3. **Reopen Claude Desktop** (it will read your new config)
4. **Look for MCP tools** in Claude's interface

### 4. **Test Your Connection**

Once Claude Desktop has restarted, try these test queries:

#### **Natural Language Queries:**
- *"What tables are available in my database?"*
- *"Show me sample data from the customers table"*
- *"How many records are in each table?"*

#### **Direct SQL:**
- *"Execute this SQL: SELECT TOP 5 * FROM YourTable"*
- *"Get the schema information for the orders table"*

### 5. **Success Indicators**

**When Claude connects successfully, you'll see:**
- 🔧 **MCP tools listed** in Claude's tool panel
- 📊 **Rich database responses** with formatted tables
- ⚡ **Fast query execution** from your database
- 🛡️ **Safety validations** blocking dangerous queries

**If connection fails, check:**
- ✅ **File path is correct** in your config
- ✅ **Python is in your PATH** 
- ✅ **All dependencies installed** (`pip install -r requirements.txt`)
- ✅ **Database connection works** (check your `.env` file)

## 🎯 Cursor AI Integration (Developers)

### Why Use ChatQL with Cursor?

**Transform your development workflow** by connecting your database directly to Cursor AI:

- 🔍 **Instant Schema Exploration** - "Show me all tables in this database"
- 📊 **Quick Data Analysis** - "What are the most common user types in our system?"
- 🐛 **Debug Data Issues** - "Find users who have orders but no email address"
- 🏗️ **Database Design Help** - "Show me the relationship between users and orders tables"
- ⚡ **Rapid Prototyping** - Get sample data for testing without writing SQL

### Setting Up with Cursor

#### **1. Configure Cursor for MCP**

Create or edit your Cursor settings file:

**Windows:** `%APPDATA%\Cursor\User\settings.json`
**Mac:** `~/Library/Application Support/Cursor/User/settings.json`
**Linux:** `~/.config/Cursor/User/settings.json`

Add the MCP configuration:

```json
{
  "mcp.servers": {
    "chatql-mcp": {
      "command": "python",
      "args": ["C:/path/to/your/project/server.py"],
      "env": {
        "DB_SERVER": "localhost\\SQLEXPRESS",
        "DB_DATABASE": "YourDatabase",
        "OPENAI_API_KEY": "your-openai-api-key"
      }
    }
  }
}
```

#### **2. Development Workflow Examples**

##### **🔍 Database Exploration During Development**
```
Developer: "What tables do I have available?"
ChatQL: Shows all database tables with schemas

Developer: "Show me the structure of the users table"
ChatQL: Displays columns, data types, constraints, relationships

Developer: "Give me sample data from the orders table"
ChatQL: Returns formatted sample records
```

##### **🐛 Debugging Data Issues**
```
Developer: "Find all users created in the last 7 days"
ChatQL: Converts to SQL and shows recent users

Developer: "Are there any orphaned records in order_items?"
ChatQL: Checks for referential integrity issues

Developer: "Show me users with duplicate email addresses"
ChatQL: Finds and displays duplicate data
```

##### **📊 Quick Analytics for Features**
```
Developer: "What's the distribution of user roles in our system?"
ChatQL: Groups and counts user roles

Developer: "Show me the average order value by month"
ChatQL: Generates time-based analytics

Developer: "Which products have never been ordered?"
ChatQL: Finds unused inventory
```

#### **3. Cursor-Specific Benefits**

- **🎯 Context-Aware**: Cursor can see your code and database structure simultaneously
- **⚡ Lightning Fast**: No switching between database tools and your editor
- **🧠 Intelligent Queries**: Cursor understands your codebase context for better questions
- **🔄 Iterative Development**: Ask follow-up questions based on query results
- **📝 Code Generation**: Generate database-related code based on schema insights

#### **4. Example Development Session**

```
# Working on a user dashboard feature
Developer: "Show me the user table structure"
ChatQL: Returns user schema with all fields

Developer: "What's the relationship between users and their orders?"
ChatQL: Shows JOIN relationships and foreign keys

Developer: "Give me sample data for testing the dashboard"
ChatQL: Returns realistic test data

Developer: "How many users registered each month this year?"
ChatQL: Generates registration analytics

# Cursor can now suggest code based on this database knowledge!
```

### Other MCP Clients

This server follows the standard MCP protocol and works with any MCP-compatible client.

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

### 🏷️ Version Management

This project uses a centralized versioning system with automated tools for contributors.

#### **Quick Version Commands**
```bash
# Check current version
python version_manager.py current

# Bump version for bug fixes (1.0.0 → 1.0.1)
python version_manager.py bump patch

# Bump version for new features (1.0.1 → 1.1.0)
python version_manager.py bump minor

# Bump version for breaking changes (1.1.0 → 2.0.0)
python version_manager.py bump major
```

#### **Semantic Versioning Guidelines**
- **PATCH** (`1.0.1`) - Bug fixes, security patches
- **MINOR** (`1.1.0`) - New features, database support additions
- **MAJOR** (`2.0.0`) - Breaking changes, API modifications

#### **Complete Release Workflow**
1. **Make your changes** and test thoroughly
2. **Update CHANGELOG.md** with your changes under `[Unreleased]`
3. **Bump version** using the appropriate type:
   ```bash
   python version_manager.py bump minor -m "Added PostgreSQL support"
   ```
4. **Push changes** including tags:
   ```bash
   git push origin master --tags
   ```

#### **Version System Details**
- ✅ **Single source of truth**: `__version__.py`
- ✅ **Automatic git tagging**: Creates annotated tags (v1.0.0, v1.1.0, etc.)
- ✅ **Auto-commit**: Commits version changes with proper messages
- ✅ **No manual updates**: All files automatically sync with central version

#### **Advanced Options**
```bash
# Set specific version
python version_manager.py set 1.2.3

# Skip git operations (for testing)
python version_manager.py bump patch --no-commit --no-tag

# Create tag with custom message
python version_manager.py tag -m "Hotfix release"
```

> **Note for Contributors**: Always use the version manager script instead of manually editing version numbers. This ensures consistency across all project files.

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

- 🐛 **Found a bug?** [Open an issue](https://github.com/SyedRazaHasnain/chatql-mcp/issues)
- 💡 **Have a feature request?** [Start a discussion](https://github.com/SyedRazaHasnain/chatql-mcp/discussions)
- 📧 **Need help?** Check our [troubleshooting guide](#-troubleshooting)

---

**Made with ❤️ by [Raza Hasnain](https://github.com/SyedRazaHasnain)** 