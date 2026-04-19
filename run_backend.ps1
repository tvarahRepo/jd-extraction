$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $Root "JDParserAgent")
& (Join-Path $Root ".venv\Scripts\python.exe") -m uvicorn api:app --host 127.0.0.1 --port 8001

