#!/usr/bin/env python3
"""
Local Visual Agent Server
Runs the visual agent as a local web server without Docker
"""

import json
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from visual_agent import VisualAgent
import threading
import webbrowser
import time


class VisualAgentHandler(BaseHTTPRequestHandler):
    """HTTP handler for visual agent requests"""

    def __init__(self, *args, **kwargs):
        self.agent = VisualAgent()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests - serve the demo page"""
        if self.path == '/' or self.path == '/index.html':
            self.serve_demo_page()
        elif self.path == '/health':
            self.send_health_response()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests - process visual generation"""
        if self.path == '/api/generate':
            self.handle_generate_request()
        else:
            self.send_error(404, "Not Found")

    def serve_demo_page(self):
        """Serve the interactive demo page"""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visual Agent - Local Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 300;
        }

        .header p {
            opacity: 0.9;
            font-size: 1.1rem;
        }

        .main-content {
            display: grid;
            grid-template-columns: 400px 1fr;
            gap: 0;
            min-height: 750px;
        }

        .input-panel {
            background: #f8f9fa;
            padding: 30px;
            border-right: 1px solid #e9ecef;
            overflow-y: auto;
            max-height: 750px;
        }

        .input-group {
            margin-bottom: 25px;
        }

        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2c3e50;
        }

        .input-group textarea {
            width: 100%;
            min-height: 220px;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-family: inherit;
            font-size: 14px;
            resize: vertical;
            transition: border-color 0.3s ease;
        }

        .input-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .visual-type-selector {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 20px;
        }

        .visual-type-btn {
            padding: 12px;
            border: 2px solid #e9ecef;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            font-weight: 500;
        }

        .visual-type-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .visual-type-btn:hover {
            border-color: #667eea;
        }

        .generate-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
        }

        .generate-btn:hover {
            transform: translateY(-2px);
        }

        .generate-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .visual-output {
            padding: 20px;
            background: white;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: auto;
        }

        .visual-container {
            width: 100%;
            height: 710px;
            border: 2px dashed #e9ecef;
            border-radius: 8px;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            background: #fafbfc;
            position: relative;
            overflow: auto;
            padding: 20px;
        }

        .placeholder {
            text-align: center;
            color: #6c757d;
            margin: auto;
        }

        .placeholder-icon {
            font-size: 4rem;
            margin-bottom: 15px;
        }

        .loading {
            display: none;
            text-align: center;
            color: #667eea;
        }

        .loading-icon {
            font-size: 3rem;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border: 1px solid #c3e6cb;
        }

        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border: 1px solid #f5c6cb;
        }

        .examples {
            margin-top: 20px;
        }

        .example-btn {
            display: block;
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            background: #e9ecef;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            cursor: pointer;
            text-align: left;
            font-size: 12px;
        }

        .example-btn:hover {
            background: #dee2e6;
        }

        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .input-panel {
                border-right: none;
                border-bottom: 1px solid #e9ecef;
                max-height: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Visual Agent - Local Demo</h1>
            <p>Transform text into interactive diagrams, flowcharts, and charts</p>
        </div>
        
        <div class="main-content">
            <div class="input-panel">
                <div class="input-group">
                    <label for="textInput">Enter your text:</label>
                    <textarea id="textInput" placeholder="Paste your text here..."></textarea>
                </div>
                
                <div class="visual-type-selector">
                    <button class="visual-type-btn active" data-type="auto">Auto Detect</button>
                    <button class="visual-type-btn" data-type="flowchart">Flowchart</button>
                    <button class="visual-type-btn" data-type="diagram">Diagram</button>
                    <button class="visual-type-btn" data-type="chart">Chart</button>
                </div>
                
                <button class="generate-btn" id="generateBtn">Generate Visual</button>
                
                <div class="examples">
                    <h4>Quick Examples:</h4>
                    <button class="example-btn" data-example="flowchart">Flowchart: User Login Process</button>
                    <button class="example-btn" data-example="diagram">Diagram: System Architecture</button>
                    <button class="example-btn" data-example="chart">Chart: Quarterly Sales Data</button>
                </div>
                
                <div id="messageContainer"></div>
            </div>
            
            <div class="visual-output">
                <div class="visual-container" id="visualContainer">
                    <div class="placeholder">
                        <div class="placeholder-icon">📊</div>
                        <h3>Your visual will appear here</h3>
                        <p>Enter text and click "Generate Visual" or try an example</p>
                    </div>
                </div>
                
                <div class="loading" id="loading">
                    <div class="loading-icon">⏳</div>
                    <p>Generating visual...</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        class LocalVisualAgent {
            constructor() {
                this.textInput = document.getElementById('textInput');
                this.generateBtn = document.getElementById('generateBtn');
                this.visualContainer = document.getElementById('visualContainer');
                this.loading = document.getElementById('loading');
                this.messageContainer = document.getElementById('messageContainer');
                this.selectedType = 'auto';
                
                this.initializeEventListeners();
                this.loadExamples();
            }

            initializeEventListeners() {
                this.generateBtn.addEventListener('click', () => this.generateVisual());
                
                document.querySelectorAll('.visual-type-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        document.querySelectorAll('.visual-type-btn').forEach(b => b.classList.remove('active'));
                        e.target.classList.add('active');
                        this.selectedType = e.target.dataset.type;
                    });
                });

                document.querySelectorAll('.example-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        this.loadExample(e.target.dataset.example);
                    });
                });

                this.textInput.addEventListener('keydown', (e) => {
                    if (e.ctrlKey && e.key === 'Enter') {
                        this.generateVisual();
                    }
                });
            }

            loadExamples() {
                this.examples = {
                    flowchart: `Start
User visits website
Check if user is logged in?
Yes: Show dashboard
No: Show login page
User enters credentials
Validate credentials?
Yes: Redirect to dashboard
No: Show error message
End`,
                    diagram: `Frontend Application connects to API Gateway
API Gateway routes to Authentication Service
API Gateway routes to Product Service
Authentication Service queries User Database
Product Service queries Product Database
API Gateway sends response to Frontend`,
                    chart: `Q1 2023: 45000
Q2 2023: 52000
Q3 2023: 48000
Q4 2023: 61000
Q1 2024: 58000
Q2 2024: 67000`
                };
            }

            loadExample(type) {
                if (this.examples[type]) {
                    this.textInput.value = this.examples[type];
                    // Auto-select the appropriate visual type
                    document.querySelectorAll('.visual-type-btn').forEach(btn => {
                        btn.classList.remove('active');
                        if (btn.dataset.type === type) {
                            btn.classList.add('active');
                            this.selectedType = type;
                        }
                    });
                }
            }

            showMessage(message, type = 'success') {
                this.messageContainer.innerHTML = `<div class="${type}-message">${message}</div>`;
                setTimeout(() => {
                    this.messageContainer.innerHTML = '';
                }, 5000);
            }

            showLoading() {
                this.visualContainer.style.display = 'none';
                this.loading.style.display = 'block';
                this.generateBtn.disabled = true;
            }

            hideLoading() {
                this.loading.style.display = 'none';
                this.visualContainer.style.display = 'flex';
                this.generateBtn.disabled = false;
            }

            async generateVisual() {
                const text = this.textInput.value.trim();
                if (!text) {
                    this.showMessage('Please enter some text to convert to a visual.', 'error');
                    return;
                }

                this.showLoading();

                try {
                    const response = await fetch('/api/generate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            text: text,
                            visual_type: this.selectedType
                        })
                    });

                    const result = await response.json();

                    if (result.html_output) {
                        // Extract just the visual content from the HTML
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(result.html_output, 'text/html');
                        const visualContent = doc.querySelector('.visual-container');
                        
                        if (visualContent) {
                            this.visualContainer.innerHTML = visualContent.innerHTML;
                        } else {
                            // Fallback: show the full HTML
                            this.visualContainer.innerHTML = result.html_output;
                        }
                        
                        this.showMessage(`Generated ${result.visual_type || this.selectedType} successfully!`, 'success');
                    } else {
                        this.showMessage('Error generating visual. Please check your input format.', 'error');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    this.showMessage('Error generating visual. Please try again.', 'error');
                } finally {
                    this.hideLoading();
                }
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            new LocalVisualAgent();
        });
    </script>
</body>
</html>
        """

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())

    def handle_generate_request(self):
        """Handle visual generation requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            text = data.get('text', '')
            visual_type = data.get('visual_type', 'auto')

            if not text:
                response = {
                    "error": "No text provided",
                    "html_output": ""
                }
            else:
                # Generate HTML visual
                html_output = self.agent.generate_html(text, visual_type)

                response = {
                    "html_output": html_output,
                    "visual_type": self.agent.detect_visual_type(text, visual_type).value,
                    "text_length": len(text)
                }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            error_response = {
                "error": str(e),
                "html_output": ""
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())

    def send_health_response(self):
        """Send health check response"""
        response = {"status": "healthy", "service": "visual-agent"}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass


def start_server(port=8080, open_browser=True):
    """Start the local server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, VisualAgentHandler)

    print(f"🚀 Visual Agent Server starting...")
    print(f"📡 Server running on http://localhost:{port}")
    print(f"🔗 API endpoint: http://localhost:{port}/api/generate")
    print(f"💻 Demo page: http://localhost:{port}/")
    print(f"❤️  Health check: http://localhost:{port}/health")
    print("\nPress Ctrl+C to stop the server")

    if open_browser:
        # Open browser after a short delay
        def open_browser_delayed():
            time.sleep(1)
            webbrowser.open(f'http://localhost:{port}')

        browser_thread = threading.Thread(target=open_browser_delayed)
        browser_thread.daemon = True
        browser_thread.start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Visual Agent Local Server')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port to run server on (default: 8080)')
    parser.add_argument('--no-browser', action='store_true',
                        help='Do not open browser automatically')

    args = parser.parse_args()

    start_server(port=args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
