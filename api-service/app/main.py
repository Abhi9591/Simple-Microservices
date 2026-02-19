import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel

load_dotenv()

# Service URLs from environment
DATABASE_SERVICE_URL = os.getenv("DATABASE_SERVICE_URL")
CACHE_SERVICE_URL = os.getenv("CACHE_SERVICE_URL")

# FastAPI app
app = FastAPI()

# Pydantic models
class UserCreate(BaseModel):
    name: str

class UserResponse(BaseModel):
    id: int
    name: str

# user creation endpoint
@app.post("/users")
def create_user(user: UserCreate):
    """
    Create a new user:
    1. Call database service
    2. Store the new user in cache
    3. Cache flush only occurs automatically at 75MB
    """
    try:
        #  Create user in DB
        response = requests.post(
            f"{DATABASE_SERVICE_URL}/users",
            json={"name": user.name},
            timeout=5
        )
        response.raise_for_status()
        user_data = response.json()
        
        #  Update cache immediately
        try:
            # Check memory and flush automatically
            requests.post(
                f"{CACHE_SERVICE_URL}/cache/user:{user_data['id']}",
                json=user_data,
                timeout=5
            )
            requests.post(
                f"{CACHE_SERVICE_URL}/cache/name:{user_data['name']}",
                json=user_data,
                timeout=5
            )
        except:
            # If cache fails, ignore; DB data is safe
            pass
        
        return user_data

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Database service error: {str(e)}")

# Get user by ID endpoint
@app.get("/users/id/{user_id}")
def get_user_by_id(user_id: int):
    """
    Get user by ID (cache-first logic):
    1. Check cache
    2. If found, return
    3. If not found, call database and store in cache
    """
    cache_key = f"user:{user_id}"
    
    try:
        # Try to get from cache
        cache_response = requests.get(
            f"{CACHE_SERVICE_URL}/cache/{cache_key}",
            timeout=5
        )
        if cache_response.status_code == 200:
            return cache_response.json()
    except:
        pass
    
    try:
        # Get from database
        response = requests.get(
            f"{DATABASE_SERVICE_URL}/users/id/{user_id}",
            timeout=5
        )
        response.raise_for_status()
        user_data = response.json()
        
        # Store in cache
        try:
            requests.post(
                f"{CACHE_SERVICE_URL}/cache/{cache_key}",
                json=user_data,
                timeout=5
            )
        except:
            pass
        
        return user_data
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Database service error: {str(e)}")
# Get user by name endpoint
@app.get("/users/name/{name}")
def get_user_by_name(name: str):
    """
    Get user by name (cache-first logic):
    1. Check cache
    2. If found, return
    3. If not found, call database and store in cache
    """
    cache_key = f"name:{name}"
    
    try:
        # Try to get from cache
        cache_response = requests.get(
            f"{CACHE_SERVICE_URL}/cache/{cache_key}",
            timeout=5
        )
        if cache_response.status_code == 200:
            return cache_response.json()
    except:
        pass
    
    try:
        # Get from database
        response = requests.get(
            f"{DATABASE_SERVICE_URL}/users/name/{name}",
            timeout=5
        )
        response.raise_for_status()
        user_data = response.json()
        
        # Store in cache
        try:
            requests.post(
                f"{CACHE_SERVICE_URL}/cache/{cache_key}",
                json=user_data,
                timeout=5
            )
        except:
            pass
        
        return user_data
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Database service error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
