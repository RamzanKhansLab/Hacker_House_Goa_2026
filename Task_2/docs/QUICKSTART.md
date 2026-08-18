# Quick start

From `Task_2`, create a virtual environment, install `.[dev]`, copy `.env.example` to `.env`, and run `python -m uvicorn app.main:app --reload`. Open `/docs` for OpenAPI and `GET /ready` to confirm the demo index loaded.

Run the React client with `cd frontend`, `npm install`, and `npm run dev`. The browser needs microphone permission only when using voice input.

Windows equivalent commands are `py -m venv .venv`, `.\.venv\Scripts\Activate.ps1`, `py -m pip install -e ".[dev]"`, and `npm.cmd run dev` if PowerShell blocks `npm.ps1`.
