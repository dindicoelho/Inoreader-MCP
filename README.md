# Inoreader MCP Integration

An MCP (Model Context Protocol) server that integrates Inoreader with Claude Desktop, enabling intelligent RSS feed management and analysis.

## Features

### Feed and Article Management
- **List feeds**: View all your subscribed feeds
- **List articles**: Browse articles with filters (unread, by feed, by period)
- **Read content**: Access full content of specific articles
- **Mark as read**: Mark articles individually or in bulk

### Search and Analysis
- **Search articles**: Search for keywords across your feeds
- **Summarize articles**: Generate summaries of individual articles
- **Analyze multiple articles**: 
  - Consolidated summaries
  - Trend analysis
  - Sentiment analysis
  - Keyword extraction
- **Statistics**: View unread article counters

## Installation

### 🚀 Auto-Installer (Recommended)

**One command installs everything:**
```bash
python3 install_inoreader_mcp.py
```

The auto-installer will:
- ✅ Install all Python dependencies
- ✅ Prompt for your Inoreader credentials  
- ✅ Configure Claude Desktop automatically
- ✅ Leave everything ready to use!

**Windows users:** Double-click `install.bat`

### 📦 Drag & Drop Installation

**Try dragging `inoreader-mcp.dxt` onto Claude Desktop** (experimental - may not work on all versions)

### 🛠️ Manual Installation

1. Clone the repository
```bash
git clone <repository-url>
cd inoreader_mcp
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure credentials

Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```

Edit the `.env` file with your Inoreader credentials:
```
INOREADER_APP_ID=your_app_id
INOREADER_APP_KEY=your_app_key
INOREADER_USERNAME=your_email
INOREADER_PASSWORD=your_password
```

To obtain credentials:
1. Visit https://www.inoreader.com/developers/
2. Create a new application
3. Copy the App ID and App Key

### 4. Configure in Claude Desktop

Add to Claude Desktop's configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "inoreader": {
      "command": "python",
      "args": ["/full/path/to/inoreader_mcp/main.py"],
      "env": {
        "INOREADER_APP_ID": "your_app_id",
        "INOREADER_APP_KEY": "your_app_key",
        "INOREADER_USERNAME": "your_email",
        "INOREADER_PASSWORD": "your_password"
      }
    }
  }
}
```

## Usage

After configuration, restart Claude Desktop. Commands will be available in natural language:

### Example commands

**List feeds:**
- "List my feeds"
- "What feeds do I follow?"

**List articles:**
- "Show the last 20 unread articles"
- "What unread articles do I have from TechCrunch?"
- "Show articles from the last 3 days"

**Search:**
- "Search articles about artificial intelligence"
- "Find Python articles from the last 7 days"

**Read and mark:**
- "Read article [ID]"
- "Mark all articles from feed X as read"

**Analysis:**
- "Summarize the top 5 AI articles this week"
- "Analyze trends in my feeds today"
- "What's the overall sentiment of economy articles?"
- "Extract keywords from unread articles"

**Statistics:**
- "How many unread articles do I have?"
- "Show my feed statistics"

## Project Structure

```
inoreader_mcp/
├── main.py              # Main MCP server
├── inoreader_client.py  # Inoreader API client
├── tools.py             # MCP tools implementation
├── config.py            # Configuration and credentials
├── utils.py             # Helper functions
├── requirements.txt     # Python dependencies
├── .env.example         # Configuration example
└── README.md           # This file
```

## Development

### Testing locally
```bash
python main.py
```

### Logs
Logs are written to console. For debugging, check Claude Desktop's console.

### Limitations
- Maximum 50 articles per request
- 5-minute cache for feed list
- 10-second timeout for API requests

## Troubleshooting

**Authentication error:**
- Verify credentials are correct
- Confirm App has necessary permissions in Inoreader

**MCP doesn't appear in Claude:**
- Check the full path in configuration file
- Restart Claude Desktop
- Confirm Python is in system PATH

**Request timeouts:**
- Inoreader API may be slow
- Try reducing the number of requested articles

## Contributing

Contributions are welcome! Please:
1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.