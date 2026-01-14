"""
Carousel Factory v6.0 - Vercel Minimal Edition
Step-by-step import isolation to find the crash source.
"""
from flask import Flask, jsonify
import os
import sys

app = Flask(__name__)

# Step 3: Test logger (was crash point)
sys.path.insert(0, os.path.dirname(__file__) + '/..')

# Test: logger
from logger import get_logger
logger = get_logger()
logger.info("Logger OK in Step 3")

# Step 4: Test gemini_integration
try:
    from gemini_integration import generate_carousel_content, get_temas_para_nicho, TEMAS_POR_NICHO
    GEMINI_OK = True
except Exception as e:
    GEMINI_OK = False
    logger.error(f"gemini_integration FAILED: {e}")

# Step 5: Test carousel_generator
try:
    from carousel_generator import generate_carousel
    CAROUSEL_OK = True
except Exception as e:
    CAROUSEL_OK = False
    logger.error(f"carousel_generator FAILED: {e}")

@app.route('/')
def index():
    return f"Step 5: Logger OK, Gemini={GEMINI_OK}, Carousel={CAROUSEL_OK}"

@app.route('/health')
def health():
    return jsonify({"status": "ok", "gemini": GEMINI_OK, "carousel": CAROUSEL_OK})
