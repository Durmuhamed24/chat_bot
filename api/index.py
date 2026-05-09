"""
Vercel ASGI handler for Chainlit application
"""
import os
import sys

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chainlit.server import app as chainlit_app

# Export the ASGI app for Vercel
app = chainlit_app
