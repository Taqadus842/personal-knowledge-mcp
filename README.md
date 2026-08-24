# Personal Knowledge-Base MCP Server

A FastMCP server that exposes a personal knowledge-base stored in Qdrant vector database through Model Context Protocol (MCP) tools. This server can be integrated with Claude Desktop to enable semantic search over your documents.

## Features

- **search_notes**: Semantic search over your knowledge-base with configurable top-k results
- **get_document**: Retrieve full document content by document ID
- **list_sources**: List all available documents in the knowledge-base
- **Error Handling**: Comprehensive error handling for invalid queries, missing documents, and server errors
- **Claude Desktop Integration**: Full MCP configuration for seamless integration with Claude Desktop

## Project Structure

```
knowledge-base-mcp/
├── server/                 # FastMCP server implementation
│   ├── __init__.py
│   └── main.py            # Main MCP server with tools
├── retrieval/             # Retrieval system integration
│   ├── __init__.py
│   ├── qdrant_client.py   # Qdrant vector database client
│   ├── retrieval_adapter.py # Adapter for Taqadus's retrieval function
│   └── models.py          # Data models for search results
├── config/                # Configuration
│   ├── __init__.py
│   └── settings.py        # Settings and environment variables
├── tests/                 # Tests
│   └── test_tools.py      # Tool testing
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project metadata
└── README.md             # This file
```

## Installation

1. Clone the repository and navigate to the project directory
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Qdrant configuration
   ```

## Qdrant Setup

### Option 1: Docker (Recommended for development)

```bash
docker run -p 6333:6333 qdrant/qdrant:latest
```

### Option 2: Local Installation

Download and run Qdrant from [qdrant.io](https://qdrant.io/documentation/quick-start/)

The server expects Qdrant to be running on `localhost:6333` by default.

## Running the MCP Server

```bash
python -m server.main
```

The server will start and be ready to accept MCP connections.

## MCP Tools

### 1. search_notes(query: str, top_k: int = 5) -> List[SearchResult]

Search for notes in the knowledge-base using semantic search.

**Parameters:**
- `query` (str): Search query
- `top_k` (int): Number of top results to return (default: 5)

**Returns:**
- List of SearchResult objects containing:
  - `relevant_text`: The matching text snippet
  - `similarity_score`: Score between 0 and 1
  - `document_name`: Name of the source document
  - `page_number`: Page number in the document (if applicable)
  - `document_id`: Unique identifier for the document

**Errors:**
- `ValueError`: If query is empty
- `RuntimeError`: If no results found or server error

### 2. get_document(document_id: str) -> Document

Retrieve a complete document by its ID.

**Parameters:**
- `document_id` (str): The unique identifier of the document

**Returns:**
- Document object containing:
  - `id`: Document ID
  - `name`: Document name
  - `content`: Full document content
  - `metadata`: Document metadata

**Errors:**
- `ValueError`: If document_id is invalid
- `RuntimeError`: If document not found

### 3. list_sources() -> List[DocumentMetadata]

List all available documents in the knowledge-base.

**Returns:**
- List of DocumentMetadata objects containing:
  - `id`: Document ID
  - `name`: Document name
  - `size`: Size of the document
  - `created_at`: Creation timestamp
  - `metadata`: Additional document metadata

**Errors:**
- `RuntimeError`: If server error occurs

## Integrating with Taqadus's Retrieval Function

When Taqadus provides the retrieval implementation:

1. Place the retrieval code in `retrieval/` directory
2. Update `retrieval/retrieval_adapter.py` to import and wrap Taqadus's functions
3. Update the `search_notes()`, `get_document()`, and `list_sources()` tools to call your functions
4. The MCP layer will automatically use the new implementation

See `retrieval/retrieval_adapter.py` for the expected function signatures.

## Claude Desktop Integration

### Configuration

1. Locate Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the MCP server configuration:
   ```json
   {
     "mcpServers": {
       "knowledge-base-mcp": {
         "command": "python",
         "args": ["-m", "server.main"],
         "cwd": "/path/to/knowledge-base-mcp"
       }
     }
   }
   ```

3. Restart Claude Desktop

### Verifying Connection

In Claude Desktop, you should see the knowledge-base-mcp tools available. Test with a simple query like:
> "Search for information about [topic] in my knowledge base"

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

For specific tool testing:

```bash
pytest tests/test_tools.py::test_search_notes -v
```

## Troubleshooting

### Connection Issues

- Verify Qdrant is running: `curl http://localhost:6333/health`
- Check `.env` file has correct QDRANT_HOST and QDRANT_PORT
- Ensure virtual environment is activated

### No Tools Found in Claude

- Verify MCP server starts without errors: `python -m server.main`
- Check Claude Desktop configuration file for correct paths
- Restart Claude Desktop after configuration changes
- Check Claude debug logs for connection errors

### Search Returns No Results

- Verify documents are loaded in Qdrant
- Check query is not too specific or contains enough context
- Ensure `QDRANT_COLLECTION_NAME` matches your collection

## License

MIT
