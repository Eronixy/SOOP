from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime, timezone
from lexical_analyzer import LexicalAnalyzer
from syntax_analyzer import SyntaxAnalyzer
from typing import Dict

# Initialize Flask application
app = Flask(__name__)
CORS(app)

# Configuration
class Config:
    # Paths
    FRONTEND_FOLDER = os.path.join(os.getcwd(), "..", "frontend")
    DIST_FOLDER = os.path.join(FRONTEND_FOLDER, "dist")
    
    # Server settings
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Analysis settings
    MAX_CODE_LENGTH = 1000000  # Maximum code length in characters
    
    # Logging
    LOG_FOLDER = "logs"
    LOG_FILE = f"soop_analyzer_{datetime.now().strftime('%Y%m%d')}.log"

app.config.from_object(Config)

# Ensure log directory exists
if not os.path.exists(Config.LOG_FOLDER):
    os.makedirs(Config.LOG_FOLDER)

def log_analysis(code: str, result: Dict, user: str):
    """Log analysis requests and results"""
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    log_entry = f"""
--- Analysis Log Entry ---
Timestamp: {timestamp}
User: {user}
Code Length: {len(code)} characters
Tokens Found: {len(result.get('tokens', []))}
Errors Found: {len(result.get('errors', []))}
------------------------
"""
    log_path = os.path.join(Config.LOG_FOLDER, Config.LOG_FILE)
    with open(log_path, 'a') as log_file:
        log_file.write(log_entry)

def connect_analyzers(code: str) -> Dict:
    """
    Connect lexical and syntax analyzers and process the code
    Returns a dictionary containing tokens and errors
    """
    try:
        lexical_analyzer = LexicalAnalyzer(code)
        tokens, lexical_errors = lexical_analyzer.tokenize()
        
        if lexical_errors:
            return {
                "tokens": tokens,
                "errors": [{
                    "type": "Lexical Error",
                    "line": error["line"],
                    "message": error["message"]
                } for error in lexical_errors],
                "status": "error"
            }
        
        syntax_analyzer = SyntaxAnalyzer(tokens)
        syntax_errors = syntax_analyzer.analyze()
        
        return {
            "tokens": tokens,
            "errors": syntax_errors,
            "status": "success" if not syntax_errors else "error"
        }
        
    except Exception as e:
        return {
            "tokens": [],
            "errors": [{
                "type": "System Error",
                "line": 0,
                "message": f"Analysis failed: {str(e)}"
            }],
            "status": "error"
        }

# Routes
@app.route("/", defaults={"filename": ""})
@app.route("/<path:filename>")
def serve_frontend(filename):
    """Serve frontend files"""
    if not filename:
        filename = "index.html"
    try:
        return send_from_directory(Config.DIST_FOLDER, filename)
    except Exception as e:
        return jsonify({
            "error": "File not found",
            "message": str(e)
        }), 404

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze SOOP code
    Expects JSON with 'code' field containing the code to analyze
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({
                "error": "No code provided",
                "message": "Request must include 'code' field"
            }), 400
            
        code = data['code']
        
        # Validate code length
        if len(code) > Config.MAX_CODE_LENGTH:
            return jsonify({
                "error": "Code too long",
                "message": f"Code exceeds maximum length of {Config.MAX_CODE_LENGTH} characters"
            }), 400
            
        # Process the code
        result = connect_analyzers(code)
        
        # Log the analysis
        user = request.headers.get('X-User', 'anonymous')
        log_analysis(code, result, user)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": "Analysis failed",
            "message": str(e),
            "tokens": [],
            "errors": [{
                "type": "System Error",
                "line": 0,
                "message": f"Server error: {str(e)}"
            }]
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        "version": "1.0.0"
    })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "error": "Not Found",
        "message": "The requested resource was not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }), 500

# Main entry point
if __name__ == '__main__':
    print(f"""
SOOP Language Analyzer Server
----------------------------
Version: 1.0.0
Started at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
Debug Mode: {Config.DEBUG}
Frontend Path: {Config.DIST_FOLDER}
Logs Path: {os.path.join(Config.LOG_FOLDER, Config.LOG_FILE)}
----------------------------
    """)
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )