#!/usr/bin/env python3
"""
Docker-compatible database initialization script for the Tube Capsule Model API.
This script creates the PostgreSQL database tables when running in Docker.
"""

import os
import sys
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add the project root to Python path
sys.path.append('/app')

def wait_for_postgres():
    """Wait for PostgreSQL to be ready"""
    print("Waiting for PostgreSQL to be ready...")
    
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Try to connect to PostgreSQL
            database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@tube-capsule-postgres:5432/tube_capsule_db")
            engine = create_engine(database_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL is ready!")
            return True
        except Exception as e:
            retry_count += 1
            print(f"PostgreSQL not ready yet (attempt {retry_count}/{max_retries}): {e}")
            time.sleep(2)
    
    print("❌ PostgreSQL failed to become ready within timeout")
    return False


def create_tables():
    """Create all tables defined in the models"""
    print("Creating database tables...")
    
    try:
        from app.database.config import DATABASE_URL, Base
        from app.database.models import EngagementEvent, SimulationRun
        
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Error creating tables: {e}")
        return False
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def main():
    """Main initialization function for Docker"""
    print("🚀 Docker: Initializing Tube Capsule Model Database")
    print("=" * 50)
    
    # Wait for PostgreSQL to be ready
    if not wait_for_postgres():
        sys.exit(1)
    
    # Create tables
    if not create_tables():
        sys.exit(1)
    
    print("\n🎉 Database initialization completed successfully!")


if __name__ == "__main__":
    main() 