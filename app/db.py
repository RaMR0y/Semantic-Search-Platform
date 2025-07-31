import os
import asyncpg
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://appuser:apppass@localhost:5432/semsearch")

async def connect_db(app: FastAPI):
    """Create database connection pool on app startup"""
    app.state.db = await asyncpg.create_pool(DATABASE_URL)
    print(f"Connected to database: {DATABASE_URL}")

async def close_db(app: FastAPI):
    """Close database connection pool on app shutdown"""
    await app.state.db.close()
    print("Database connection closed")

async def get_db_pool():
    """Dependency to get database pool"""
    return asyncpg.create_pool(DATABASE_URL) 