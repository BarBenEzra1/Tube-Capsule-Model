#!/usr/bin/env python3
"""
Script to run the Tube Capsule Model API server with Swagger UI
"""
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Tube Capsule Model API server...")
    print("📚 Swagger UI will be available at: http://localhost:8000/docs")
    print("📖 ReDoc will be available at: http://localhost:8000/redoc")
    print("🌐 API root: http://localhost:8000")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    ) 