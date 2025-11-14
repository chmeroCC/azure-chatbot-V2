from flask import Flask, request, jsonify, render_template
import os
import sys
import logging

# Configuration logging pour Azure
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = Flask(__name__)

# Log de démarrage
logging.info("=== AZURE CHATBOT V2 STARTING ===")
logging.info(f"Python version: {sys.version}")
logging.info(f"Current directory: {os.getcwd()}")
logging.info(f"Files in directory: {os.listdir('.')}")

@app.route('/')
def home():
    logging.info("Home page accessed")
    return render_template('chat.html')

@app.route('/health')
def health():
    logging.info("Health check")
    return jsonify({
        "status": "healthy", 
        "service": "azure-chatbot-v2",
        "python_version": sys.version
    })

@app.route('/debug')
def debug():
    """Page de debug pour Azure"""
    debug_info = {
        "python_version": sys.version,
        "current_directory": os.getcwd(),
        "files": os.listdir('.'),
        "templates_exists": os.path.exists('templates'),
        "chat_html_exists": os.path.exists('templates/chat.html'),
        "port": os.environ.get('PORT'),
        "azure_openai_key": "SET" if os.environ.get('AZURE_OPENAI_KEY') else "MISSING",
        "azure_openai_endpoint": "SET" if os.environ.get('AZURE_OPENAI_ENDPOINT') else "MISSING"
    }
    return jsonify(debug_info)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)