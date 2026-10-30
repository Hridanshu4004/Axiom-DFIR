# AXIOM DFIR - One-Click Launcher & Verification
# Nebius x NVIDIA Global AI Hackathon 2026

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AXIOM DFIR: Autonomous Evidence-Verified DFIR Platform" -ForegroundColor White
Write-Host "  Best Apps & Agents Track - Nebius x NVIDIA Hackathon 2026" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = ".;Axiom DFIR/src;src"

# Verify Python
Write-Host "[1/3] Checking Python 3.10 runtime..." -ForegroundColor Green
py -3.10 --version

# Check if frontend is built
if (-not (Test-Path "frontend/dist")) {
    Write-Host "[*] Building React Vite Frontend..." -ForegroundColor Yellow
    Set-Location -Path "frontend"
    npm run build
    Set-Location -Path ".."
} else {
    Write-Host "[2/3] Frontend build verified (frontend/dist ready)." -ForegroundColor Green
}

Write-Host "[3/3] Launching AXIOM DFIR Production Server on http://127.0.0.1:8000..." -ForegroundColor Cyan
Write-Host "Opening web browser at http://127.0.0.1:8000..." -ForegroundColor Gray
Start-Process "http://127.0.0.1:8000"

py -3.10 run_web.py --port 8000 --host 127.0.0.1

