# ==================================================================
# File: core/core_main/server.py
# Description: 
# ==================================================================

from flask import Flask, request, jsonify, send_file
import io
import logging

from flasgger import Swagger
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Ensure this script runs independently using its own package scope
from .bg import remove

app = Flask(__name__)

# Initialize Swagger
swagger = Swagger(app)

# Initialize OpenTelemetry for Jaeger (OTLP)
resource = Resource(attributes={"service.name": "synora-core-api"})
provider = TracerProvider(resource=resource)
# Jaeger's default OTLP gRPC port is 4317
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

FlaskInstrumentor().instrument_app(app)

# Reduce Flask logging spam
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route("/api/remove", methods=["POST"])
def remove_background():
    """
    Remove background from an image.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: The image file to process.
      - in: formData
        name: model
        type: string
        required: false
        description: The ML model to use (e.g., u2net).
      - in: formData
        name: a
        type: boolean
        required: false
        description: Apply alpha matting.
    responses:
      200:
        description: The image with the background removed.
        content:
          image/png:
            schema:
              type: string
              format: binary
      400:
        description: Invalid request.
      500:
        description: Internal server error.
    """
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
