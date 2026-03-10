from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core import config
from app.core.dependencies import get_embedder, get_storage
import uvicorn
import time

app = FastAPI(title="LSV Engine", version="2.0")

# --- Telemetry Middleware ---
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    
    # X-Crystal-Latency: Total time in ms
    response.headers["X-Crystal-Latency"] = f"{process_time * 1000:.2f}ms"
    return response

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting LSV Engine...")
    # Initialize Core Modules
    embedder = get_embedder()
    storage = get_storage()
    
    # OPTIONAL: Load vocab.txt into LanceDB on startup if empty
    if storage.total_items == 0:
        print("Empty DB detected. You might want to ingest vocab.txt.")
        
    print("✅ System Ready.")

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
