from flask import Flask, request, jsonify, send_file
import io
import logging

# Ensure this script runs independently using its own package scope
from .bg import remove

app = Flask(__name__)

# Reduce Flask logging spam
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route("/api/remove", methods=["POST"])
def remove_background():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    try:
        input_data = file.read()
        
        # We can extract optional parameters (like model name) from the request form
        kwargs = {}
        if "model" in request.form:
            kwargs["model"] = request.form["model"]
            
        result_data = remove(input_data, **kwargs)
        
        return send_file(
            io.BytesIO(result_data),
            mimetype="image/png",
            as_attachment=True,
            download_name=f"nobg_{file.filename}"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Rembg Core API Server on port 5001...")
    app.run(host="0.0.0.0", port=5001, debug=True)
