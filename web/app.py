import os
import io
import requests
import base64
from flask import Flask, request, jsonify, send_file, render_template

app = Flask(__name__)

# Extensible Provider Configuration
# AI_PROVIDER can be 'core', 'ollama', or 'custom'
AI_PROVIDER = os.environ.get("AI_PROVIDER", "core").lower()

# URLs for remote execution
CORE_API_URL = os.environ.get("CORE_API_URL", "")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")

def execute_local_core(input_data):
    """Fallback to direct python execution on the same machine."""
    from core.bg import remove
    return remove(input_data)

def execute_remote_core(input_data):
    """Proxy the request over the network to the dedicated core/ server."""
    files = {'file': ('image.png', input_data, 'image/png')}
    response = requests.post(CORE_API_URL, files=files)
    response.raise_for_status()
    return response.content

def execute_ollama(input_data):
    """Example adapter for routing an image to a local Ollama Vision Model."""
    # Note: Ollama requires images to be base64 encoded strings
    base64_image = base64.b64encode(input_data).decode('utf-8')
    payload = {
        "model": "llava", # Example vision model
        "prompt": "Remove the background from this image. Output only the PNG raw bytes.",
        "images": [base64_image],
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    
    # In reality, Ollama outputs text. If using a specialized model that outputs base64 images, 
    # you would decode it here. This is an extensible stub!
    result_text = response.json().get("response", "")
    return result_text.encode('utf-8') # Just a stub!

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/remove", methods=["POST"])
def remove_background():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    try:
        input_data = file.read()
        
        # Route to the appropriate provider based on Extensible Architecture
        if AI_PROVIDER == "ollama":
            result_data = execute_ollama(input_data)
        elif AI_PROVIDER == "core" and CORE_API_URL:
            result_data = execute_remote_core(input_data)
        else:
            result_data = execute_local_core(input_data)
            
        return send_file(
            io.BytesIO(result_data),
            mimetype="image/png",
            as_attachment=True,
            download_name=f"nobg_{file.filename}"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"Starting Rembg Web UI on port {port}...")
    print(f"Provider: {AI_PROVIDER}")
    if AI_PROVIDER == "core" and CORE_API_URL:
        print(f"Routing to Remote Core: {CORE_API_URL}")
    elif AI_PROVIDER == "ollama":
        print(f"Routing to Ollama: {OLLAMA_URL}")
    else:
        print("Routing to Local Engine")
        
    app.run(host="0.0.0.0", port=port, debug=True)
