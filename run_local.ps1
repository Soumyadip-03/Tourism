# run_local.ps1
# ─────────────────────────────────────────────────────────────────────────────
# Windows PowerShell convenience launcher for the China Tourism Recommender.
# Run from the project root directory.
# ─────────────────────────────────────────────────────────────────────────────

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $Root "backend"
$VenvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Error "Virtual environment not found at: $VenvPython"
    Write-Host "Expected location: backend\.venv\Scripts\python.exe"
    exit 1
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  China Tourism Recommendation System         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting FastAPI backend..." -ForegroundColor Yellow
Write-Host "  → http://127.0.0.1:8000/health"
Write-Host "  → http://127.0.0.1:8000/docs"
Write-Host ""
Write-Host "Starting Streamlit UI..." -ForegroundColor Yellow
Write-Host "  → http://localhost:8501"
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop." -ForegroundColor Gray
Write-Host ""

# Start backend in a new terminal window
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$BackendDir'; & '$VenvPython' -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"
)

# Wait briefly for backend to initialise
Start-Sleep -Seconds 3

# Start Streamlit UI in a new terminal window
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$Root'; & '$VenvPython' -m streamlit run app.py"
)

Write-Host "Both servers launched in separate windows." -ForegroundColor Green
Write-Host "Close those windows (or press Ctrl+C inside them) to stop each server." -ForegroundColor Gray

