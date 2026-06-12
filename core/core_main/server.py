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
        
        kwargs = {}
        if "model" in request.form: kwargs["model"] = request.form["model"]
        if request.form.get("a") in ["true", "True", "1"]: kwargs["alpha_matting"] = True
        if "af" in request.form: kwargs["alpha_matting_foreground_threshold"] = int(request.form["af"])
        if "ab" in request.form: kwargs["alpha_matting_background_threshold"] = int(request.form["ab"])
        if "ae" in request.form: kwargs["alpha_matting_erode_size"] = int(request.form["ae"])
        if request.form.get("om") in ["true", "True", "1"]: kwargs["only_mask"] = True
        if request.form.get("ppm") in ["true", "True", "1"]: kwargs["post_process_mask"] = True
        if "bgc" in request.form and request.form["bgc"]:
            kwargs["bgcolor"] = tuple(map(int, request.form["bgc"].split(",")))
            
        extras = request.form.get("extras")
        if extras:
            import json
            try:
                kwargs.update(json.loads(extras))
            except Exception:
                pass
            
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
    import os
    port = int(os.environ.get("PORT", 5051))
    print(f"Starting Rembg Core API Server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
