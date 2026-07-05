# CivicTrust AI - PowerShell Run Script
# Jalankan script ini di PowerShell

Write-Host "🏛️ CivicTrust AI - Starting Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Pindah ke direktori project
Set-Location $PSScriptRoot

# Cek Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python tidak ditemukan. Install Python 3.11+ dulu." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Gagal install dependencies" -ForegroundColor Red
    exit 1
}

# Buat folder data jika belum ada
New-Item -ItemType Directory -Path "data" -Force | Out-Null
New-Item -ItemType Directory -Path "data\documents" -Force | Out-Null
New-Item -ItemType Directory -Path "data\vector_store" -Force | Out-Null

# Copy .env.example ke .env jika belum ada
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "📝 File .env dibuat. Edit dulu dengan API key Anda!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Memulai server..." -ForegroundColor Cyan
Write-Host ""
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Frontend:    http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "Tekan Ctrl+C untuk menghentikan server" -ForegroundColor Yellow
Write-Host ""

# Jalankan backend (background job) dan frontend
Write-Host "Starting Backend (FastAPI)..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

Start-Sleep -Seconds 3

Write-Host "Starting Frontend (Streamlit)..." -ForegroundColor Green
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0

# Cleanup saat exit
Stop-Job $backendJob
Remove-Job $backendJob