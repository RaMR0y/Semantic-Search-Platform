#!/usr/bin/env python3
"""
Startup script for Semantic Search Q&A Platform
Handles database setup, data population, and server startup
"""

import os
import sys
import subprocess
import time
import asyncio
import asyncpg
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_docker():
    """Check if Docker is running"""
    try:
        subprocess.run(["docker", "info"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

async def wait_for_database():
    """Wait for database to be ready"""
    print("🔄 Waiting for database to be ready...")
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            conn = await asyncpg.connect(
                user="appuser",
                password="apppass",
                database="semsearch",
                host="localhost"
            )
            await conn.close()
            print("✅ Database is ready!")
            return True
        except Exception as e:
            attempt += 1
            print(f"⏳ Database not ready yet (attempt {attempt}/{max_attempts})...")
            time.sleep(2)
    
    print("❌ Database failed to start within expected time")
    return False

def main():
    """Main startup function"""
    print("🚀 Starting Semantic Search Q&A Platform...")
    print("=" * 50)
    
    # Check if Docker is available
    if not check_docker():
        print("❌ Docker is not running or not installed.")
        print("Please start Docker and try again.")
        sys.exit(1)
    
    # Step 1: Start database with Docker Compose
    if not run_command("docker-compose up -d", "Starting PostgreSQL database"):
        print("❌ Failed to start database. Please check Docker and try again.")
        sys.exit(1)
    
    # Step 2: Wait for database to be ready
    if not asyncio.run(wait_for_database()):
        print("❌ Database failed to start. Please check Docker logs:")
        run_command("docker-compose logs postgres", "Database logs")
        sys.exit(1)
    
    # Step 3: Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies.")
        sys.exit(1)
    
    # Step 4: Populate database with sample data
    if not run_command("python populate.py", "Populating database with sample data"):
        print("❌ Failed to populate database.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the API server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("2. Open the frontend: frontend/index.html")
    print("3. Access API docs: http://localhost:8000/docs")
    print("\n🔗 Quick links:")
    print("- API Documentation: http://localhost:8000/docs")
    print("- Health Check: http://localhost:8000/health")
    print("- Frontend: Open frontend/index.html in your browser")
    print("\n💡 Try searching for: 'What is machine learning?' or 'Python programming'")
    print("=" * 50)
    
    # Ask if user wants to start the server now
    response = input("\n🤔 Would you like to start the API server now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        print("\n🚀 Starting API server...")
        print("Press Ctrl+C to stop the server")
        run_command("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000", "Starting API server")

if __name__ == "__main__":
    main() 