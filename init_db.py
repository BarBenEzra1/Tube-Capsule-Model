#!/usr/bin/env python3
"""
Database initialization script for the Tube Capsule Model API.
This script creates the PostgreSQL database tables and performs initial setup.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.config import DATABASE_URL, Base
from app.database.models import EngagementEvent, SimulationRun


def create_database():
    """Create the database if it doesn't exist"""
    # Extract database name from URL
    db_url_parts = DATABASE_URL.split('/')
    db_name = db_url_parts[-1]
    base_url = '/'.join(db_url_parts[:-1]) + '/postgres'
    
    print(f"Creating database '{db_name}' if it doesn't exist...")
    
    try:
        # Connect to postgres database to create our target database
        engine = create_engine(base_url)
        with engine.connect() as conn:
            # Set autocommit mode
            conn.execute(text("COMMIT"))
            
            # Check if database exists
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name}
            )
            
            if not result.fetchone():
                # Create database
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"✅ Database '{db_name}' created successfully!")
            else:
                print(f"ℹ️  Database '{db_name}' already exists.")
                
    except SQLAlchemyError as e:
        print(f"❌ Error creating database: {e}")
        return False
    
    return True


def create_tables():
    """Create all tables defined in the models"""
    print("Creating database tables...")
    
    try:
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # Print table information
        print("\n📊 Created tables:")
        print("  - simulation_runs: Stores simulation run metadata and summary statistics")
        print("  - engagement_events: Stores time series simulation events")
        print("\n🔍 Indexes created for optimal time series queries:")
        print("  - idx_simulation_time: (simulation_id, timestamp_s)")
        print("  - idx_system_time: (system_id, timestamp_s)")
        print("  - idx_event_time: (event, timestamp_s)")
        print("  - idx_coil_time: (coil_id, timestamp_s)")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Error creating tables: {e}")
        return False


def test_connection():
    """Test the database connection"""
    print("Testing database connection...")
    
    try:
        # Connect to the default postgres database to test connection
        db_url_parts = DATABASE_URL.split('/')
        base_url = '/'.join(db_url_parts[:-1]) + '/postgres'
        
        engine = create_engine(base_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
            
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Connection test failed: {e}")
        return False


def main():
    """Main initialization function"""
    print("🚀 Initializing Tube Capsule Model Database")
    print("=" * 50)
    
    # Check if PostgreSQL is running
    if not test_connection():
        print("\n❌ Cannot connect to PostgreSQL.")
        print("Please ensure PostgreSQL is running and the connection details are correct.")
        print(f"Database URL: {DATABASE_URL}")
        print("\nTo start PostgreSQL:")
        print("  macOS (Homebrew): brew services start postgresql")
        print("  Ubuntu/Debian: sudo systemctl start postgresql")
        print("  Docker: docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres")
        sys.exit(1)
    
    # Create database
    if not create_database():
        sys.exit(1)
    
    # Create tables
    if not create_tables():
        sys.exit(1)
    
    print("\n🎉 Database initialization completed successfully!")
    print("\n📝 Next steps:")
    print("1. Start your API server: python run_server.py")
    print("2. Run simulations - events will be stored in PostgreSQL")
    print("3. Query time series data using the database")
    
    print(f"\n🔗 Database connection string: {DATABASE_URL}")


if __name__ == "__main__":
    main() 