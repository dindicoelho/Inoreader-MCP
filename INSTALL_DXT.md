# Installing Inoreader MCP with .dxt File

## Easy Installation (Drag & Drop)

1. **Download the .dxt file**: `inoreader-mcp.dxt`

2. **Drag and drop** the file onto Claude Desktop

3. **Enter your credentials** when prompted:
   - Inoreader App ID
   - Inoreader App Key
   - Your Inoreader username (email)
   - Your Inoreader password

4. **Done!** The MCP server will be automatically configured and ready to use.

## Getting Inoreader API Credentials

1. Visit https://www.inoreader.com/developers/
2. Click "Create New Application"
3. Fill in the application details:
   - Name: Choose any name (e.g., "Claude Desktop Integration")
   - Type: Select "Web Application"
   - Description: Optional
4. Click "Create"
5. Copy the **App ID** and **App Key** from the application details

## Verifying Installation

After installation, try these commands in Claude Desktop:

- "List my feeds"
- "Show unread articles from today"
- "Search for articles about technology"

## Troubleshooting

If the installation fails:

1. Make sure you have Python 3.8+ installed
2. Verify your Inoreader credentials are correct
3. Check Claude Desktop logs for error messages

## Manual Installation

If drag-and-drop doesn't work, you can manually install by:

1. Extracting all files to a directory
2. Running: `pip install -r requirements.txt`
3. Adding the configuration to Claude Desktop's config file as shown in README.md