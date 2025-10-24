# LangGraph API Usage Guide

## Server Status
✅ **LangGraph server is running correctly on http://127.0.0.1:2024**

## Correct API Endpoints

### 1. Non-streaming Request
```bash
POST http://127.0.0.1:2024/runs
Content-Type: application/json

{
  "assistant_id": "agent",
  "input": {
    "query": "your search query here",
    "max_results": 5
  }
}
```

### 2. Streaming Request (Recommended)
```bash
POST http://127.0.0.1:2024/runs/stream
Content-Type: application/json

{
  "assistant_id": "agent", 
  "input": {
    "query": "your search query here",
    "max_results": 5
  }
}
```

### 3. Available Endpoints
- `GET /docs` - API documentation
- `GET /openapi.json` - OpenAPI specification
- `POST /runs` - Execute graph (non-streaming)
- `POST /runs/stream` - Execute graph (streaming)
- `GET /info` - Server information
- `GET /ok` - Health check

## Current Issues

### ❌ Wrong Endpoint
- **Don't use**: `POST /api` (returns 404)
- **Use instead**: `POST /runs` or `POST /runs/stream`

### ⚠️ Blocking Operations
The server is working but has blocking operations that need to be fixed:

```
Google search failed: Blocking call to os.access

Heads up! LangGraph dev identified a synchronous blocking call in your code.
```

## Solutions

### 1. Quick Fix - Allow Blocking (Development Only)
```bash
langgraph dev --allow-blocking
```

### 2. Proper Fix - Convert to Async
The code needs to be updated to use async/await patterns instead of synchronous calls.

## Example Working Request

```python
import requests

response = requests.post(
    "http://127.0.0.1:2024/runs/stream",
    json={
        "assistant_id": "agent",
        "input": {
            "query": "search for AI news",
            "max_results": 3
        }
    },
    headers={"Content-Type": "application/json"},
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

## Next Steps

1. **Update your client code** to use the correct endpoint: `/runs` or `/runs/stream`
2. **Fix blocking operations** in the search nodes (optional for development)
3. **Use streaming** for better real-time feedback