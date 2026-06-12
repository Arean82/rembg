<div align="center">
  <h1>Rembg Core: ML Microservice Engine</h1>
  <p>The heavy-lifting Machine Learning backend for the Rembg Ecosystem.</p>

  <img src="https://img.shields.io/badge/Python-3.12%2B-blue.svg" alt="Python Version" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License" />
  <img src="https://img.shields.io/badge/Architecture-Hybrid%20Microservice-orange.svg" alt="Architecture" />

</div>

## Overview

`core` is the foundational ML engine of Rembg. It is entirely decoupled from the Web UI and the CLI. It uses **ONNX Runtime** and **U^2-Net** to perform state-of-the-art background removal.

Because of the **Hybrid Architecture**, you can use `core` in two completely different ways depending on your deployment needs:

---

## Method 1: Local Library (Monolithic Execution)

If you are building a simple Python script or running everything on a single machine, you can simply import the core engine directly into your code. The ML models will load directly into your local RAM/VRAM.

### Usage

```python
from core.bg import remove

# Read an image from disk
with open("input.png", "rb") as f:
    input_data = f.read()

# Remove the background
result_data = remove(input_data)

# Save the result
with open("output.png", "wb") as f:
    f.write(result_data)
```

---

## Method 2: Standalone API (Microservice Execution)

If you want to run the heavy Machine Learning models on a dedicated **GPU Server**, while keeping your web frontends lightweight, you can start `core` as a standalone HTTP API!

### 1. Start the API Server

On your heavy GPU machine, start the Core Server:

```bash
python -m core.server
```

*This will start an internal REST API on `http://0.0.0.0:5001`.*

### 2. Connect your Frontend

On your completely separate web server, you do **not** need to install `core`. Just point your Web UI to the GPU server's IP address:

**Windows (PowerShell):**

```powershell
$env:CORE_API_URL="http://your-gpu-server-ip:5001/api/remove"
python -m web.app
```

**Linux/macOS:**

```bash
export CORE_API_URL="http://your-gpu-server-ip:5001/api/remove"
python -m web.app
```

The Web UI will automatically detect the remote `core` server and proxy all heavy image processing over the network instantly!
