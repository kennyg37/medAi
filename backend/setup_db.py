#!/usr/bin/env python3
"""
Database Setup Script for MedAI
Initializes PostgreSQL database and tables
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Setup PostgreSQL database and tables"""
    
    # Database configuration from environment variables
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("DB_NAME", "medai_chatbot")
    
    # Also check for DATABASE_URL
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        # Parse DATABASE_URL if provided
        try:
            # Simple parsing of DATABASE_URL
            if DATABASE_URL.startswith("postgresql://"):
                parts = DATABASE_URL.replace("postgresql://", "").split("@")
                if len(parts) == 2:
                    user_pass = parts[0].split(":")
                    host_port_db = parts[1].split("/")
                    if len(user_pass) == 2 and len(host_port_db) == 2:
                        DB_USER = user_pass[0]
                        DB_PASSWORD = user_pass[1]
                        host_port = host_port_db[0].split(":")
                        DB_HOST = host_port[0]
                        if len(host_port) == 2:
                            DB_PORT = host_port[1]
                        DB_NAME = host_port_db[1]
        except Exception as e:
            logger.warning(f"Could not parse DATABASE_URL: {e}")
    
    logger.info(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}")
    logger.info(f"Database: {DB_NAME}, User: {DB_USER}")
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"  # Connect to default database first
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            logger.info(f"Creating database '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            logger.info(f"Database '{DB_NAME}' created successfully!")
        else:
            logger.info(f"Database '{DB_NAME}' already exists.")
        
        cursor.close()
        conn.close()
        
        # Connect to the new database and create tables
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Create conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id VARCHAR PRIMARY KEY,
                title VARCHAR NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """)
        
        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                conversation_id VARCHAR NOT NULL,
                role VARCHAR NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL
            )
        """)
        
        # Create index for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
            ON messages(conversation_id)
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Database tables created successfully!")
        logger.info(f"Database URL: postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise

if __name__ == "__main__":
    setup_database() 