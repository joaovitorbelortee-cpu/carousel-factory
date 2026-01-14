from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Carousel Factory - Health Check OK"

# Vercel handler
