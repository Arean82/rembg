"""
================================================================================
SYNORA STUDIO BG REMOVE - PORTFOLIO INTEGRATION GUIDE
================================================================================

This module provides a drop-in reference for integrating the unified background
removal logic directly into your Portfolio App, completely bypassing the local 
SQLite tracking and the `config.ini` dev flag, and instead utilizing your 
existing PG18 database and Flask-Login setup.

Prerequisites:
- Your Portfolio App is a Flask application.
- You are using Flask-Login (`current_user.is_authenticated`).
- You have copied the `core/core_main/bg.py` into your Portfolio App.

"""

from flask import current_app
from flask_login import current_user
import io
import os

# Assume you placed bg.py inside your Portfolio app's backend/ folder
# from backend.core_main.bg import remove

def process_image_for_portfolio(file_bytes, request_form):
    """
    Called from your Portfolio App's route when an image is uploaded.
    This dynamically determines access tier via Flask-Login.
    """
    
    # 1. Determine Access Tier automatically from SSO
    is_logged_in = current_user.is_authenticated
    
    kwargs = {}
    
    # 2. Apply Tier Logic
    if is_logged_in:
        # User is logged in! Allow them to use all advanced ML parameters.
        if "model" in request_form: kwargs["model"] = request_form["model"]
        if request_form.get("a") in ["true", "True", "1"]: kwargs["alpha_matting"] = True
        if "af" in request_form: kwargs["alpha_matting_foreground_threshold"] = int(request_form["af"])
        if "ab" in request.form: kwargs["alpha_matting_background_threshold"] = int(request_form["ab"])
        # ... parse other advanced parameters ...
    else:
        # Guest user! Enforce plain background removal by ignoring advanced params.
        # kwargs remains empty, ensuring safe defaults.
        pass

    # 3. Process the image directly (no HTTP API call needed if merged)
    # result_bytes = remove(file_bytes, **kwargs)
    result_bytes = b"" # Placeholder for the line above
    
    # 4. Save to your Portfolio App's native storage
    # Instead of SQLite and `config.ini` local folders, save directly to your 
    # Cloud Bucket or PG18 Database.
    
    if is_logged_in:
        # Save permanently linked to current_user.id in PG18
        # e.g., db.session.add(PortfolioImage(user_id=current_user.id, data=result_bytes))
        pass
    else:
        # Save to temporary session or temp folder for 1-hour cleanup logic 
        # handled by your Portfolio app's existing systems.
        pass
        
    return result_bytes

"""
NOTES ON OPENTELEMETRY & SWAGGER:
---------------------------------
Because your Portfolio App already initializes OpenTelemetry (`FlaskInstrumentor().instrument_app(app)`)
and Swagger (`flasgger`), you do NOT need to bring over the initialization code 
from this repository's `app.py`. 

The `remove()` function calls and the API routes will automatically be picked up 
and traced by your Portfolio App's existing instrumentation.
"""
