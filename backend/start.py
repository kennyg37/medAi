#!/usr/bin/env python3
"""
MedAI Backend Startup Script
Medical AI Chatbot powered by BioMedLM
"""

import uvicorn
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start the MedAI backend server"""
    try:
        logger.info("Starting MedAI Backend Server...")
        logger.info("Loading BioMedLM model (this may take a few minutes on first run)...")
        
        # Import main app after logging setup
        from main import app
        
        logger.info("Model loaded successfully!")
        logger.info("Server starting on http://localhost:8000")
        logger.info("API documentation available at http://localhost:8000/docs")
        logger.info("Auto-reload enabled - server will restart on code changes")
        
        # Start the server with auto-reload enabled
        uvicorn.run(
            "main:app",  # Use string reference for auto-reload
            host="0.0.0.0",
            port=8000,
            reload=True,  # Enable auto-reload
            reload_dirs=["."],  # Watch current directory for changes
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 