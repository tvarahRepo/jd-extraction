# JD Extraction Studio

JD-only extraction app with:
- FastAPI backend in `JDParserAgent`
- Streamlit UI in `dashboard.py`
- OCR via Mistral
- Structured parsing and judge loop via OpenRouter

## Repository layout

- `JDParserAgent/`: backend code
- `dashboard.py`: Streamlit UI
- `requirements.txt`: Python dependencies
- `run_backend.sh`: Linux backend start script
- `run_ui.sh`: Linux UI start script
- `run_backend.ps1`: Windows backend start script
- `run_ui.ps1`: Windows UI start script
- `docs/DEPLOY_VM_UBUNTU.md`: step-by-step VM deployment guide
- `deploy/systemd/`: systemd service templates
- `deploy/nginx/`: Nginx reverse proxy config

## Local quick start

Linux:

```bash
git clone https://github.com/tvarahRepo/jd-extraction.git
cd jd-extraction
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
./run_backend.sh
```

In another terminal:

```bash
cd jd-extraction
source .venv/bin/activate
./run_ui.sh
```

Open:
- `http://127.0.0.1:8001/health`
- `http://127.0.0.1:8501`

## Windows quick start

```powershell
git clone https://github.com/tvarahRepo/jd-extraction.git
cd jd-extraction
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
powershell -ExecutionPolicy Bypass -File .\run_backend.ps1
```

In another terminal:

```powershell
cd jd-extraction
powershell -ExecutionPolicy Bypass -File .\run_ui.ps1
```

## Production deployment

Use the detailed guide here:

[docs/DEPLOY_VM_UBUNTU.md](docs/DEPLOY_VM_UBUNTU.md)
