# Synora Studio Image Background Remover

Welcome to the **Synora Studio Image Background Remover**. This application is a powerful, ML-driven API and Web UI designed to seamlessly strip backgrounds from images. 

It is built to run as a **standalone local service** using SQLite, and is architected to **drop directly into a PostgreSQL-backed Portfolio App** when you are ready to merge.

## Core Features
- **Unified Architecture**: A single Flask application (`app.py`) serving both the interactive Glassmorphism UI and the headless REST API.
- **Tiered Access**: Supports a Guest mode (basic removal, short data retention) and a Logged-In mode (advanced parameters like Alpha Matting, long data retention).
- **Automated Data Retention**: A background scheduler automatically cleans up processed files from the server based on your configurable timeline.
- **Enterprise Telemetry & API Docs**: Built-in OpenTelemetry (OTLP) tracking and interactive Swagger API documentation.

## Quick Start (Standalone Dev)

1. Check the `config.ini` file in the root directory.
   - Change `simulate_logged_in_user` to `true` or `false` to instantly switch between access tiers during development.
2. Run the application:
   ```bash
   python app.py
   ```
3. Open `http://localhost:5050` in your browser to use the UI, or navigate to `http://localhost:5050/apidocs` to view the interactive API documentation.

## Documentation
- **Installation**: See `INSTALLATION.md` for complete environment setup instructions.
- **Integration**: See `integration_guide/portfolio_integration.py` for instructions on how to merge this into your existing PG18 Portfolio App.

## Packaging
To package this app into a single executable for distribution, run PyInstaller with the provided spec file:
```bash
pyinstaller synora-app.spec
```
