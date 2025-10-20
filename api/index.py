#!/usr/bin/env python3
"""
Vercel-compatible Visual Agent API
Serves the web interface and handles visual generation
"""

from visual_agent import VisualAgent
import json
import os
import sys
from flask import Flask, request, jsonify, send_file
from urllib.parse import urlparse, parse_qs

# Add the parent directory to the path so we can import visual_agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


app = Flask(__name__)
agent = VisualAgent()


@app.route('/')
def index():
    """Serve the main demo page"""
    try:
        # Read the index.html file
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error loading page: {str(e)}", 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Visual Agent API'
    })


@app.route('/generate', methods=['POST'])
def generate():
    """Generate visual from text"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        text = data.get('text', '')
        visual_type = data.get('type', 'auto')

        if not text.strip():
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400

        # Generate visual
        html_content = agent.generate_html(text, visual_type)

        return jsonify({
            'success': True,
            'html': html_content,
            'type': visual_type
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate', methods=['POST'])
def api_generate():
    """Alternative API endpoint for generate"""
    return generate()


# Vercel handler
def handler(request):
    """Vercel handler function"""
    return app(request.environ, lambda *args: None)


if __name__ == '__main__':
    app.run(debug=True)
