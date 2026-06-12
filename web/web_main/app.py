import os
import io
import requests
import base64
from flask import Flask, request, jsonify, send_file, render_template
from web.web_main.i18n import init_i18n
from PIL import Image

app = Flask(__name__)
init_i18n(app)

# Extensible Provider Configuration
# AI_PROVIDER can be 'core', 'ollama', or 'custom'
AI_PROVIDER = os.environ.get("AI_PROVIDER", "core").lower()

# URLs for remote execution
CORE_API_URL = os.environ.get("CORE_API_URL", "")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")

def execute_local_core(input_data, **kwargs):
    """Fallback to direct python execution on the same machine."""
    from core.core_main.bg import remove
    return remove(input_data, **kwargs)

def execute_remote_core(input_data, **kwargs):
    """Proxy the request over the network to the dedicated core/ server."""
    files = {'file': ('image.png', input_data, 'image/png')}
    response = requests.post(CORE_API_URL, files=files, data=kwargs)
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
        
        # Parse exact parameters for backward-compatibility with s_command API
        kwargs = {}
        if "model" in request.form: kwargs["model"] = request.form["model"]
        if request.form.get("a") == "true": kwargs["alpha_matting"] = True
        if "af" in request.form: kwargs["alpha_matting_foreground_threshold"] = int(request.form["af"])
        if "ab" in request.form: kwargs["alpha_matting_background_threshold"] = int(request.form["ab"])
        if "ae" in request.form: kwargs["alpha_matting_erode_size"] = int(request.form["ae"])
        if request.form.get("om") == "true": kwargs["only_mask"] = True
        if request.form.get("ppm") == "true": kwargs["post_process_mask"] = True
        if "bgc" in request.form and request.form["bgc"]:
            kwargs["bgcolor"] = tuple(map(int, request.form["bgc"].split(",")))
        
        extras = request.form.get("extras")
        if extras:
            import json
            try:
                kwargs.update(json.loads(extras))
            except Exception:
                pass

        # Route to the appropriate provider based on Extensible Architecture
        if AI_PROVIDER == "ollama":
            result_bytes = execute_ollama(input_data)
        elif AI_PROVIDER == "core" and CORE_API_URL:
            result_bytes = execute_remote_core(input_data, **kwargs)
        else:
            result_bytes = execute_local_core(input_data, **kwargs)

        # Apply Grayscale if requested
        if request.form.get("grayscale") == "true":
            try:
                img = Image.open(io.BytesIO(result_bytes)).convert("RGBA")
                r, g, b, a = img.split()
                gray = Image.merge("RGB", (r, g, b)).convert("L")
                out = Image.merge("RGBA", (gray, gray, gray, a))
                out_io = io.BytesIO()
                out.save(out_io, format="PNG")
                result_bytes = out_io.getvalue()
            except Exception as e:
                print("Grayscale conversion error:", e)

        return send_file(
            io.BytesIO(result_bytes),
            mimetype='image/png'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"Starting Synora Studio Web UI on port {port}...")
    print(f"Provider: {AI_PROVIDER}")
    if AI_PROVIDER == "core" and CORE_API_URL:
        print(f"Routing to Remote Core: {CORE_API_URL}")
    elif AI_PROVIDER == "ollama":
        print(f"Routing to Ollama: {OLLAMA_URL}")
    else:
        print("Routing to Local Engine")
        
    app.run(host="0.0.0.0", port=port, debug=False)
