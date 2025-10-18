from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.graph import create_unified_search_graph

graph = create_unified_search_graph()
app = FastAPI(title="Unified Search Agent")


class RunRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    max_results: Optional[int] = None
    geo: Optional[str] = None
    user_locale: Optional[str] = None


@app.post("/api/run")
async def run_unified_search(request: RunRequest) -> Dict[str, Any]:
    initial_state: Dict[str, Any] = {
        "query": request.query,
        "context": request.context or {},
        "geo": request.geo,
        "user_locale": request.user_locale,
        "max_results": request.max_results or 5,
        "raw_results": [],
    }

    try:
        result = await graph.ainvoke(initial_state)
        return {
            "results": result.get("final_results", []),
            "query_summary": result.get("query_summary"),
            "total_processed": result.get("total_processed"),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

