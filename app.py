import os
import configparser
import logging
from flask import Flask, request, jsonify, render_template, send_file
import io
from PIL import Image
import base64
import json
from werkzeug.utils import secure_filename

from flasgger import Swagger
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Import UI and ML logics
from web.web_main.i18n import init_i18n
from core.core_main.bg import remove

# Import custom DB and Scheduler logic
from core.core_main.db import init_db, log_image, get_config
from core.core_main.scheduler import start_scheduler

# Create Unified Flask App
app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
init_i18n(app)
swagger = Swagger(app)

# -----------------------------------------
# Configuration & Telemetry Setup
# -----------------------------------------
config = get_config()
otlp_endpoint = config.get('Telemetry', 'otlp_endpoint', fallback='http://localhost:4317')

resource = Resource(attributes={"service.name": "synora-unified-api"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# -----------------------------------------
# UI Routes
# -----------------------------------------
@app.route("/")
def index():
    # Pass the dev flag to the UI to lock/unlock advanced features
    dev_is_logged_in = config.getboolean('Dev', 'simulate_logged_in_user', fallback=False)
    return render_template("index.html", is_logged_in=dev_is_logged_in)

# -----------------------------------------
# API Routes (ML Backend)
# -----------------------------------------
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
    responses:
      200:
        description: The image with the background removed.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
        
    try:
        input_data = file.read()
        
        # Check dev simulation flag to determine tier
        is_logged_in = config.getboolean('Dev', 'simulate_logged_in_user', fallback=False)
        
        kwargs = {}
        
        # If logged in, allow advanced settings
        if is_logged_in:
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
                try:
                    kwargs.update(json.loads(extras))
                except Exception:
                    pass
        else:
            # Guest tier: force default safe settings, ignore advanced params
            pass
            
        result_data = remove(input_data, **kwargs)
        
        # Match Portfolio standard: put uploads in a subfolder (e.g. 'bg_remover/guest' or 'bg_remover/user')
        base_upload_dir = config.get('UPLOADS', 'upload_path', fallback='storage/images')
        
        # Placeholder for real user ID integration later
        subfolder = "user" if is_logged_in else "guest"
        target_dir = os.path.join(base_upload_dir, "bg_remover", subfolder)
        os.makedirs(target_dir, exist_ok=True)
        
        safe_filename = secure_filename(f"nobg_{file.filename}")
        save_path = os.path.join(target_dir, safe_filename)
        
        with open(save_path, 'wb') as f:
            f.write(result_data)
            
        log_image(safe_filename, save_path, is_logged_in)
        
        return send_file(
            io.BytesIO(result_data),
            mimetype="image/png",
            as_attachment=True,
            download_name=safe_filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db(app)
    start_scheduler(app)
    port = config.getint('Network', 'port', fallback=5050)
    print(f"Starting Unified Synora Studio on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
