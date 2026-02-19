import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import redis

load_dotenv()

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# FastAPI app
app = FastAPI()

def check_memory_and_flush():
    """Check Redis memory and flush if >= 75MB"""
    info = r.info("memory")
    used_memory = info.get("used_memory", 0)
    used_memory_mb = used_memory / (1024 * 1024)
    
    if used_memory_mb >= 75:
        r.flushall()
# Cache endpoints
@app.get("/cache/{key}")
def get_cache(key: str):
    """Get value from cache"""
    value = r.get(key)
    if not value:
        raise HTTPException(status_code=404, detail="Key not found")
    try:
        return json.loads(value)
    except:
        return value
    
# Set and delete cache endpoints with memory check
@app.post("/cache/{key}")
def set_cache(key: str, data: dict):
    """Set value in cache with memory check"""
    check_memory_and_flush()
    r.set(key, json.dumps(data))
    return {"status": "stored", "key": key}

@app.delete("/cache/{key}")
def delete_cache(key: str):
    """Delete key from cache"""
    result = r.delete(key)
    if result == 0:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"status": "deleted", "key": key}

@app.get("/cache/memory")
def get_memory():
    """Get Redis memory info"""
    info = r.info("memory")
    return {
        "used_memory_mb": info.get("used_memory", 0) / (1024 * 1024),
        "max_memory": info.get("maxmemory", 0),
        "max_memory_policy": info.get("maxmemory_policy", "")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
