#!/usr/bin/env python3
"""
Test script to verify Semantic Search Q&A Platform setup
"""

import asyncio
import asyncpg
import requests
import json
from pathlib import Path

async def test_database():
    """Test database connection and basic operations"""
    print("🔍 Testing database connection...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            user="appuser",
            password="apppass",
            database="semsearch",
            host="localhost"
        )
        
        # Test basic queries
        doc_count = await conn.fetchval("SELECT COUNT(*) FROM documents")
        embedding_count = await conn.fetchval("SELECT COUNT(*) FROM embeddings")
        query_count = await conn.fetchval("SELECT COUNT(*) FROM queries")
        
        print(f"✅ Database connection successful")
        print(f"   - Documents: {doc_count}")
        print(f"   - Embeddings: {embedding_count}")
        print(f"   - Queries: {query_count}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_api():
    """Test API endpoints"""
    print("\n🔍 Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test health check
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check endpoint working")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test root endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working")
            print(f"   - API Version: {data.get('version', 'N/A')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        # Test documents endpoint
        response = requests.get(f"{base_url}/documents/", timeout=5)
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Documents endpoint working ({len(documents)} documents)")
        else:
            print(f"❌ Documents endpoint failed: {response.status_code}")
            return False
        
        # Test search endpoint
        search_data = {
            "query": "What is machine learning?",
            "top_k": 3
        }
        response = requests.post(
            f"{base_url}/search/query",
            json=search_data,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search endpoint working ({data['total_results']} results)")
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
            return False
        
        # Test stats endpoint
        response = requests.get(f"{base_url}/search/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("✅ Stats endpoint working")
            print(f"   - Total documents: {stats['total_documents']}")
            print(f"   - Total embeddings: {stats['total_embeddings']}")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running. Please start it with: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_frontend():
    """Test frontend file exists"""
    print("\n🔍 Testing frontend...")
    
    frontend_path = Path("frontend/index.html")
    if frontend_path.exists():
        print("✅ Frontend file exists")
        return True
    else:
        print("❌ Frontend file not found")
        return False

def test_sample_data():
    """Test if sample data is properly loaded"""
    print("\n🔍 Testing sample data...")
    
    try:
        response = requests.get("http://localhost:8000/documents/", timeout=5)
        if response.status_code == 200:
            documents = response.json()
            
            expected_files = [
                "machine_learning_basics.txt",
                "python_programming.txt", 
                "database_design.txt",
                "api_design.txt",
                "cloud_computing.txt"
            ]
            
            actual_files = [doc['filename'] for doc in documents]
            
            missing_files = set(expected_files) - set(actual_files)
            if missing_files:
                print(f"❌ Missing sample documents: {missing_files}")
                return False
            else:
                print("✅ All sample documents loaded")
                return True
        else:
            print("❌ Could not fetch documents")
            return False
            
    except Exception as e:
        print(f"❌ Sample data test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing Semantic Search Q&A Platform Setup")
    print("=" * 50)
    
    tests = [
        ("Database", test_database),
        ("API", test_api),
        ("Frontend", test_frontend),
        ("Sample Data", test_sample_data)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your platform is ready to use.")
        print("\n🔗 Quick access:")
        print("- API Docs: http://localhost:8000/docs")
        print("- Frontend: frontend/index.html")
        print("- Health Check: http://localhost:8000/health")
    else:
        print("\n⚠️  Some tests failed. Please check the setup.")
        print("\n💡 Common issues:")
        print("- Make sure Docker is running")
        print("- Start the API server: uvicorn app.main:app --reload")
        print("- Check database connection")

if __name__ == "__main__":
    asyncio.run(main()) 