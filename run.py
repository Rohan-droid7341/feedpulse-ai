#!/usr/bin/env python3
"""
FeedPulse AI - Entry Point
Launches the FastAPI backend and interactive Customer Feedback Intelligence dashboard.
"""
import sys
import os
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

import uvicorn
from feedpulse.config import settings

if __name__ == "__main__":
    print("=" * 70)
    print("  FEEDPULSE AI — CUSTOMER FEEDBACK INTELLIGENCE & EVAL HARNESS")
    print(f"  Listening on http://{settings.HOST}:{settings.PORT}")
    print("=" * 70)
    uvicorn.run(
        "feedpulse.api.routes:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )
