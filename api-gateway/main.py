# api-gateway/main.py
from fastapi import FastAPI, Request, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
import httpx, os, time

app = FastAPI(title="AI Platform API Gateway")
Instrumentator().instrument(app).expose(app)  # Integration 9: Prometheus

VLLM_URL = os.environ.get("VLLM_URL", "")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4")

@app.post("/api/v1/chat")
async def chat(request: Request):
    body = await request.json()
    query = body.get("query")
    if not query:
        raise HTTPException(status_code=422, detail="query is required")

    embedding = body.get("embedding", [0.0] * 384)
    if len(embedding) != 384:
        raise HTTPException(status_code=422, detail="embedding must be 384 dimensions")

    if not VLLM_URL:
        raise HTTPException(status_code=503, detail="VLLM_URL not configured")

    start = time.time()

    # 1. Vector search
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            search_resp = await client.post(
                f"{QDRANT_URL}/collections/documents/points/search",
                json={"vector": embedding, "limit": 3}
            )
            context = search_resp.json().get("result", [])
    except Exception:
        context = []

    # 2. LLM inference
    prompt = f"Context: {context}\n\nQuery: {query}"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            llm_resp = await client.post(f"{VLLM_URL}/v1/chat/completions", json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}]
            })
            llm_resp.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="LLM timeout")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {str(e)}")

    latency = (time.time() - start) * 1000
    result = llm_resp.json()

    return {
        "answer": result["choices"][0]["message"]["content"],
        "latency_ms": round(latency, 2),
        "model": result.get("model", MODEL_NAME)
    }

@app.get("/health")
def health():
    return {"status": "ok"}
