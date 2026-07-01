# Alternative Guide: Merging into the Portfolio (Monolithic Approach)

Welcome! This guide is for beginners who want to completely merge the Background Removal tool directly into the main Synora Portfolio codebase, rather than running it as a separate service on port 5050.

**WARNING:** This approach means your main Portfolio website will run the heavy Machine Learning code. If an image is huge, it could temporarily slow down your main website. 

If you are okay with that, here is the step-by-step guide to copying the entire app over!

---

## Step 1: Copy the Machine Learning Brain
Your Portfolio needs to know how to remove backgrounds. 

1. Open this folder: `synorastudio_bg_remove\core\core_main\`
2. Find the file named `bg.py`. 
3. Copy `bg.py` and paste it inside your main Portfolio's `backend` folder.
4. Open your main Portfolio's `requirements.txt` file and add the required AI libraries so your Portfolio can install them:
   ```text
   rembg
   numpy
   Pillow
   ```

## Step 2: Copy the Web Interface (UI)
The background remover has a beautiful web interface. We need to move those HTML, CSS, and Javascript files into your Portfolio so users can actually see it.

1. Open the `synorastudio_bg_remove\web\` folder.
2. Inside, you will see a `templates` folder and a `static` folder.
3. Copy the contents of the `templates` folder and paste them into your main Portfolio's `frontend/templates` folder.
4. Copy the contents of the `static` folder and paste them into your main Portfolio's `frontend/static` folder.

## Step 3: Create the Flask Routes in your Portfolio
Now we need to tell your Portfolio how to display the UI and how to process the images when a user clicks "Upload."

Open your main Portfolio's backend code (where your routes are defined) and add these two routes. Notice how we use your Portfolio's native `current_user.is_authenticated` to check if they are logged in!

```python
from flask_login import current_user
from flask import render_template, request, send_file
# Import the brain you copied in Step 1
from backend.bg import remove 

# 1. The UI Route
@app.route("/tools/bg-remove")
def bg_remove_page():
    # Show the webpage. If they are logged in, unlock advanced features!
    return render_template("index.html", is_logged_in=current_user.is_authenticated)

# 2. The API Route (Where the ML happens)
@app.route("/api/remove_bg", methods=["POST"])
def process_bg_remove():
    file = request.files["file"]
    input_data = file.read()
    
    kwargs = {}
    
    # Check if they are logged in using Flask-Login
    if current_user.is_authenticated:
        # User is logged in! Allow advanced AI features.
        if "model" in request.form: kwargs["model"] = request.form["model"]
        if request.form.get("a") in ["true", "True", "1"]: kwargs["alpha_matting"] = True
    else:
        # Guest user! Enforce safe defaults by passing no extra arguments.
        pass
        
    # Run the ML logic
    result_data = remove(input_data, **kwargs)
    
    # Save the file to your Portfolio's database here!
    
    return send_file(io.BytesIO(result_data), mimetype="image/png")
```

## Step 4: Observability (Swagger & OpenTelemetry)
You are done! 

Because you pasted this code directly into your main Portfolio, your Portfolio's existing Swagger API docs and OpenTelemetry traces will automatically pick up the `/api/remove_bg` route. You don't have to configure anything else.
