$ErrorActionPreference = 'Stop'

if (-not (Test-Path .venv)) {
  python -m venv .venv
}

$pythonExe = Join-Path (Get-Location) ".venv\Scripts\python.exe"

& $pythonExe -m pip install -r requirements.txt
& $pythonExe -m pip install -e ".[dev,ml]"
& $pythonExe -m main
