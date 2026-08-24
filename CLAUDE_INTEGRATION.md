# Claude Desktop Integration Guide

This guide walks you through connecting the Knowledge-Base MCP Server to Claude Desktop.

## Prerequisites

1. ✅ Knowledge-Base MCP Server installed and working
2. ✅ Qdrant running (either Docker or local)
3. ✅ Claude Desktop installed
4. ✅ Python 3.11+ available in your PATH

## Step-by-Step Integration

### Step 1: Prepare the Server

Ensure the MCP server can start without errors:

```bash
# Navigate to project directory
cd /path/to/knowledge-base-mcp

# Activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Test the Server Independently

Before connecting to Claude, verify the server works:

```bash
# Test retrieval functions directly
python scripts/test_tools.py

# Start the MCP server (it will wait for MCP client)
python -m server.main
```

You should see:
```
INFO:server.main:Initialized knowledge-base-mcp v1.0.0
INFO:server.main:Registered tool: search_notes
INFO:server.main:Registered tool: get_document
INFO:server.main:Registered tool: list_sources
INFO:server.main:All tools registered successfully
INFO:server.main:knowledge-base-mcp server is running
```

If the server starts successfully, it's ready for Claude Desktop. **Keep the server running for the next steps.**

### Step 3: Locate Claude Desktop Configuration

Find the Claude Desktop configuration file based on your OS:

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

### Step 4: Add MCP Server Configuration

Edit the configuration file and add the MCP server. If the file doesn't exist, create it.

**Example configuration:**

```json
{
  "mcpServers": {
    "knowledge-base-mcp": {
      "command": "python",
      "args": ["-m", "server.main"],
      "cwd": "/absolute/path/to/knowledge-base-mcp",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "QDRANT_HOST": "localhost",
        "QDRANT_PORT": "6333",
        "QDRANT_COLLECTION_NAME": "knowledge_base"
      }
    }
  }
}
```

**IMPORTANT:**
- Replace `/absolute/path/to/knowledge-base-mcp` with the actual full path to your project
- On Windows, use forward slashes or double backslashes: `C:/Users/YourName/Documents/knowledge-base-mcp`
- Ensure the Python path matches where Python is installed (usually just `python` if in PATH)

### Step 5: Restart Claude Desktop

Close Claude Desktop completely and reopen it. This forces Claude to reload the MCP server configuration.

### Step 6: Verify Tool Discovery

In Claude Desktop:

1. Look for an indicator showing MCP servers are connected (usually a small icon)
2. Start a conversation and ask Claude to use the knowledge base

Try this test prompt:
```
Can you search my knowledge base for "Python"?
```

If the connection is working, Claude will call your `search_notes` tool.

### Step 7: Check Connection Status

If tools don't appear:

1. **Check Claude Debug Logs:**
   - macOS: `~/Library/Logs/Claude/debug.log`
   - Windows: `%APPDATA%\Claude\logs\debug.log`

2. **Verify Server is Running:**
   - Open a new terminal and test: `python -m server.main`
   - Should show the server registration messages

3. **Check Configuration Syntax:**
   - Ensure JSON is valid (no trailing commas, proper quotes)
   - Paths should be absolute, not relative

4. **Verify Python Path:**
   - Run `which python` (macOS/Linux) or `where python` (Windows)
   - Make sure this path exists and points to Python 3.11+

## Testing the Integration

### Test 1: Simple Search

**Prompt:** "Search my knowledge base for machine learning"

**Expected:** Claude calls `search_notes` with query="machine learning"

### Test 2: Retrieve Document

**Prompt:** "Get document ID 1 from my knowledge base"

**Expected:** Claude calls `get_document` with document_id="1"

### Test 3: List Sources

**Prompt:** "What documents do I have in my knowledge base?"

**Expected:** Claude calls `list_sources`

### Test 4: Multi-step Task

**Prompt:** "Search my knowledge base for 'AI', then get the first document and summarize it"

**Expected:** Claude chains multiple tool calls and provides a summary

## Troubleshooting

### Issue: Tools Don't Appear in Claude

**Solution:**
1. Close Claude Desktop completely
2. Verify MCP server configuration JSON syntax
3. Restart Claude Desktop
4. Check debug logs for connection errors

### Issue: Server Connection Timeout

**Solution:**
1. Verify `python -m server.main` runs without errors
2. Check firewall isn't blocking connections
3. Ensure Qdrant is running: `curl http://localhost:6333/health`

### Issue: "Document not found" Error

**Solution:**
1. Run `python scripts/init_qdrant.py` to populate with sample data
2. Use `list_sources` to see available documents
3. Verify document IDs are correct when using `get_document`

### Issue: Empty Search Results

**Solution:**
1. Verify Qdrant collection has documents: `python scripts/test_tools.py`
2. Try broader search queries
3. Check that QDRANT_COLLECTION_NAME environment variable matches actual collection

### Issue: Import Errors

**Solution:**
1. Ensure virtual environment is activated
2. Run `pip install -r requirements.txt` again
3. Check Python version: `python --version` (should be 3.11+)

## Advanced Configuration

### Custom Qdrant Host

If Qdrant is running on a different machine:

```json
{
  "mcpServers": {
    "knowledge-base-mcp": {
      "command": "python",
      "args": ["-m", "server.main"],
      "cwd": "/path/to/knowledge-base-mcp",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "QDRANT_HOST": "192.168.1.100",
        "QDRANT_PORT": "6333"
      }
    }
  }
}
```

### Debug Mode

Enable debug logging by adding to configuration:

```json
{
  "mcpServers": {
    "knowledge-base-mcp": {
      "command": "python",
      "args": ["-m", "server.main"],
      "cwd": "/path/to/knowledge-base-mcp",
      "env": {
        "PYTHONUNBUFFERED": "1",
        "MCP_DEBUG": "true"
      }
    }
  }
}
```

## Next Steps

1. ✅ Integrate Taqadus's retrieval function
2. ✅ Load your actual documents into Qdrant
3. ✅ Test search against real data
4. ✅ Verify source citations are preserved
5. ✅ Create demo recording for team presentation

## Support

For issues with:
- **MCP Server**: Check server logs and test with `python scripts/test_tools.py`
- **Qdrant**: Verify with `curl http://localhost:6333/health`
- **Claude Desktop Configuration**: Review JSON syntax and path variables
- **Integration with Taqadus retrieval**: See retrieval_adapter.py for integration points
