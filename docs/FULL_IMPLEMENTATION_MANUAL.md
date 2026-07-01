# Complete Implementation Guide: Background Removal Service

Welcome! This manual is written from scratch to guide you through deploying the `synorastudio_bg_remove` application and perfectly integrating it into your main Synora Portfolio platform. 

By the end of this guide, your Background Removal tool will run as an independent microservice, leveraging your existing Portfolio users (via Single Sign-On), while still allowing unauthenticated "guests" to use basic features.

---

## The Big Picture
- **The Main Portfolio** manages users, passwords, and sessions.
- **The Background Remover** does the heavy ML lifting. It has no login screen. It simply asks Nginx: *"Did the Portfolio say this person is logged in?"*
- **Nginx (The Web Server)** acts as the traffic cop connecting them together.

---

## Step 1: Preparing the Background Remover Service

First, we need to get the actual background removal app running on your server.

1. **Place the Folder:** Ensure this folder (`synorastudio_bg_remove`) is on your server.
2. **Install Dependencies:** Open your terminal inside this folder and run:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure the App (`config.ini`):** 
   Open `config.ini` and make sure it points to your main portfolio database (`synora_portfolio`). This allows the app to log the images it creates.
   - It will save guest images for **60 minutes**.
   - It will save logged-in user images for **1440 minutes** (24 hours).
4. **Start the Service:** Run the app:
   ```bash
   python app.py
   ```
   *The app is now running internally on port `5050`. It has OpenTelemetry tracing enabled (sending data to port 4317) and Swagger API docs ready.*

---

## Step 2: Creating the "Soft Gatekeeper" in your Portfolio

Because we want guests to be able to use the app, we cannot block people who aren't logged in. We need a "Soft Gatekeeper" in your main Portfolio backend.

1. Open your main Portfolio backend code (e.g., `backend/controllers/auth_controller.py`).
2. Add a new route called `/auth/verify_soft`:
   ```python
   @auth_bp.route('/verify_soft', methods=['GET', 'POST'])
   def verify_auth_soft():
       # Always return 200 OK so Nginx lets the request through
       response = make_response("OK", 200)
       
       # If the user is logged into the portfolio, inject their identity
       if 'user_id' in session:
           response.headers['X-Forwarded-User'] = session['user_email']
       
       return response
   ```
   *What this does:* If a user is logged in, their email is attached to the request invisibly. If they are a guest, they pass through freely but with no email attached.

---

## Step 3: Configuring Nginx (The Traffic Cop)

Now we need to tell your web server how to route traffic to `bgremove.synorastudio.in`.

1. Open your Nginx configuration files.
2. Create a new server block for the background removal tool:

```nginx
server {
    listen 443 ssl;
    server_name bgremove.synorastudio.in;

    # SSL Certificates go here...

    location / {
        # 1. Ask the Portfolio's soft gatekeeper who this is
        auth_request /auth/verify_soft;
        
        # 2. Extract the identity header from the gatekeeper
        auth_request_set $auth_user $upstream_http_x_forwarded_user;
        
        # 3. Pass that identity to the Background Remover app
        proxy_set_header X-Forwarded-User $auth_user;
        
        # 4. Route the traffic to port 5050
        proxy_pass http://127.0.0.1:5050;
    }
}
```
3. Restart Nginx: `sudo systemctl restart nginx`

---

## Step 4: Adding the "Card" to your Portfolio

Now that the system is fully connected, you just need to make it visible to your users!

1. Log into your main **Portfolio Superadmin Dashboard**.
2. Navigate to the **App Links** or **Tenant Settings** section.
3. Add a new App Card:
   - **Name:** Background Remover
   - **URL:** `https://bgremove.synorastudio.in`
   - **Description:** "Remove backgrounds instantly using AI."

## How it Works in Practice (Verification)

**Scenario A: A Guest visits `bgremove.synorastudio.in` directly.**
- Nginx checks with the Portfolio. They aren't logged in. 
- Nginx sends them to port 5050 with no headers. 
- The app sees no headers, treats them as a guest, limits their features, and deletes their image after 1 hour.

**Scenario B: A Logged-in User clicks the "Card" in the Portfolio.**
- Nginx checks with the Portfolio. They are logged in!
- Nginx sends them to port 5050 with the `X-Forwarded-User` header containing their email.
- The app sees the header, treats them as a premium user, unlocks all advanced ML parameters, and saves their images persistently.

---
### Viewing the API Docs & Traces
- **API Documentation:** You can view the Swagger UI at `https://bgremove.synorastudio.in/apidocs`.
- **OpenTelemetry Traces:** Your background removal performance metrics are exported to `localhost:4317` under the service name `synora-bg-remove`.
