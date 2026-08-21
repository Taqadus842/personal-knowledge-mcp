# Personal Knowledge-Base MCP Server

An MCP (Model Context Protocol) server that exposes semantic search over your
own PDF corpus — papers, notes, docs — as three callable tools any
MCP-compatible client (Claude Desktop, Claude Code, a custom client) can call
live.

## Problem

Keyword search misses content that's semantically related but doesn't share
exact words. This server lets an MCP client search a personal document
corpus **by meaning**, with cited results, exposed at the protocol level
rather than baked into a one-off chatbot UI.

## Architecture

```
 PDFs  --ingest.py-->  chunk_text()  --Gemini embed (RETRIEVAL_DOCUMENT)-->  Qdrant
                              |
                              +--> doc_registry (full text + metadata, local JSON)

 MCP client (Claude Desktop) <--stdio/JSON-RPC--> server.py (FastMCP)
                                                       |
                                          search_notes -> Gemini embed (RETRIEVAL_QUERY)
                                                        -> Qdrant similarity search
                                          get_document -> doc_registry (full text)
                                          list_sources -> doc_registry (metadata)
```

- **Chunking** (`chunking.py`): paragraph-aware, ~400-token windows with
  60-token overlap so context isn't lost at chunk boundaries. Oversized
  paragraphs are hard-split so one giant block never dodges chunking.
- **Embeddings** (`embeddings.py`): Gemini's embedding API, called with
  distinct `task_type`s — `RETRIEVAL_DOCUMENT` at ingest time,
  `RETRIEVAL_QUERY` at search time — which is what actually makes Gemini
  embeddings good at retrieval instead of generic similarity.
- **Vector store** (`qdrant_store.py`): one Qdrant collection, cosine
  distance, deterministic point IDs (`uuid5(doc_id:chunk_index)`) so
  re-ingesting a document overwrites cleanly instead of duplicating.
- **Doc registry** (`doc_registry.py`): flat local JSON + one `.txt` per
  document. Qdrant only needs to hold chunk text for search; full-document
  fetches and the source list are served from here without touching vectors.

## Tech stack

FastMCP (Python) · Qdrant Cloud · Gemini embeddings API · pypdf

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY
```

Get a Gemini API key at https://aistudio.google.com/apikey and a free Qdrant
Cloud cluster at https://cloud.qdrant.io.

## Ingest your corpus

```bash
python ingest.py /path/to/your/pdfs
```

Prints a `doc_id` per file — save these for the eval set below.

## Run the server

```bash
python server.py
```

### Connect from Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "personal-kb": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

Restart Claude Desktop, then ask it something your corpus can answer — it
will call `search_notes` and cite the source.

## Tools exposed

| Tool | Purpose |
|---|---|
| `search_notes(query, top_k=5)` | Ranked, cited chunks matching a query by meaning. Returns "no confident match" below the similarity threshold instead of forcing a weak answer. |
| `get_document(doc_id)` | Full original text of a source, for when a snippet needs more context. |
| `list_sources()` | Everything currently indexed. |

## Evaluation

```bash
python eval.py
```

Reads `data/eval_queries.json` (hand-labeled `{query, relevant_doc_ids}`
pairs against your own corpus) and reports mean precision@k. Write 15-25
realistic queries covering your actual documents — this is the one
measurable retrieval number this project is judged on, so don't softball it.

## Non-goals (this phase)

No autonomous agent/planning loops, no fine-tuning, no multi-user web
frontend — this is a single-user local MCP server. (Multi-user web UI is a
separate, later phase.)
