@echo off
REM CivicTrust AI - Windows CMD Run Script
REM Jalankan script ini di Command Prompt (CMD)

title CivicTrust AI Platform

echo.
echo ====== 🏛️ CivicTrust AI ======
echo Starting Application...
echo.

REM Pindah ke direktori script
cd /d "%~dp0"

REM Cek Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan. Install Python 3.11+ dulu.
    pause
    exit /b 1
)
echo [OK] Python terinstall

REM Install dependencies
echo.
echo [INFO] Menginstall dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Gagal install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies terinstall

REM Buat folder data
if not exist "data" mkdir data
if not exist "data\documents" mkdir data\documents
if not exist "data\vector_store" mkdir data\vector_store

REM Copy .env jika belum ada
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo [INFO] File .env dibuat. Edit dulu dengan API key Anda!
)

echo.
echo ====== 🚀 Memulai Server ======
echo.
echo    Backend API: http://localhost:8000
echo    API Docs:    http://localhost:8000/docs
echo    Frontend:    http://localhost:8501
echo.
echo Tekan Ctrl+C untuk menghentikan server
echo.

REM Jalankan backend di window terpisah
start "CivicTrust-Backend" cmd /c "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Tunggu 3 detik
timeout /t 3 /nobreak >nul

REM Jalankan frontend
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0

pause