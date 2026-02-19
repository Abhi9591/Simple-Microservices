# Simple Microservices System

A beginner-friendly microservice architecture with PostgreSQL, Redis, and FastAPI.

## Overview

This system consists of 3 services:
- **Database Service** - PostgreSQL with SQLAlchemy
- **Cache Service** - Redis with memory management
- **API Service** - FastAPI main entry point

## Architecture

```
API Service (Port 8000)
    ↓
    ├─→ Database Service (Port 8001) → PostgreSQL
    └─→ Cache Service (Port 8002) → Redis
```

All services run in Docker and communicate via internal network.

## Quick Start

1. **Build and start all services:**

```bash
docker-compose up --build
```

The system will start all 3 services + PostgreSQL + Redis.


## Features

### Create User Flow
1. API receives create request
2. Calls Database Service to store user


### Get User Flow (Cache-First)
1. API checks Cache Service first
2. If found in cache → return immediately
3. If not found → query Database Service
4. Store result in cache
5. Return response

### Automatic Cache Memory Management
- Before every cache SET operation:
  - Checks Redis memory usage
  - If used memory ≥ 75MB → Flush all cache
  - Then stores new value
- Redis max memory: 100MB
- Policy: noeviction

## Environment Variables

Edit `.env` file:

```
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=users_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

DATABASE_SERVICE_URL=http://database-service:8001
CACHE_SERVICE_URL=http://cache-service:8002
```

## Services

### Database Service (8001)

Endpoints:
- `POST /users` - Create user
- `GET /users/id/{id}` - Get user by ID
- `GET /users/name/{name}` - Get user by name

Database: PostgreSQL with automatic table creation

### Cache Service (8002)

Endpoints:
- `GET /cache/{key}` - Get cached value
- `POST /cache/{key}` - Set cached value (with memory check)
- `DELETE /cache/{key}` - Delete cache key
- `GET /cache/memory` - Get Redis memory stats

Features:
- Automatic memory monitoring
- Smart flush at 75MB threshold

### API Service (8000)

Public endpoints:
- `POST /users` - Create user (and invalidate cache)
- `GET /users/id/{id}` - Get user (cache-first)
- `GET /users/name/{name}` - Get user (cache-first)



## Stack

- **Python 3.12** - Runtime
- **FastAPI** - Web framework
- **PostgreSQL 15** - Database
- **Redis 7** - Cache
- **SQLAlchemy** - ORM
- **requests** - HTTP client
- **uvicorn** - ASGI server

## Start Services
```bash
docker-compose up -d
``` 

## Stop Services

```bash
docker-compose down
```

To also remove volumes:

```bash
docker-compose down -v
```

## Logs

View logs for all services:

```bash
docker-compose logs -f
```

View logs for specific service:

```bash
docker-compose logs -f api-service
```

## Notes

- Simple, synchronous code (no async)
- No complex patterns (no circuit breaker, retry logic, etc.)
- Clean beginner-friendly architecture
- Ready to extend with more features

## Microservices Architecture




