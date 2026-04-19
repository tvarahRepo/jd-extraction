$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
& (Join-Path $Root ".venv\Scripts\python.exe") -m streamlit run dashboard.py --server.headless true --server.port 8501 --server.address 127.0.0.1

