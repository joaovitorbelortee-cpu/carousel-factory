"""
Carousel Factory v6.0 - Vercel Minimal Edition
Step-by-step import isolation to find the crash source.
"""
from flask import Flask, jsonify
import os

app = Flask(__name__)

# --- IMPORT TEST: Each step will add one more import ---
# Step 1: Basic imports (DONE - works)
# Step 2: local imports
import sys
sys.path.insert(0, os.path.dirname(__file__) + '/..')

# Test: logger
from logger import get_logger
logger = get_logger()

@app.route('/')
def index():
    return "Step 2: Logger loaded OK"

@app.route('/health')
def health():
    return jsonify({"status": "ok", "step": 2})
