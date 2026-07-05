#!/bin/bash
# =============================================================================
# CivicTrust AI - Quick Start Script
# =============================================================================
# Usage:
#   chmod +x scripts/run.sh
#   ./scripts/run.sh          # Start both backend and frontend
#   ./scripts/run.sh backend  # Start only backend
#   ./scripts/run.sh frontend # Start only frontend
#   ./scripts/run.sh seed     # Seed database with sample documents
#   ./scripts/run.sh test     # Run tests
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════╗"
echo "║         CivicTrust AI - Quick Start          ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

check_python() {
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        echo -e "${RED}Error: Python tidak ditemukan. Install Python 3.11+.${NC}"
        exit 1
    fi
    PYTHON=$(command -v python3 || command -v python)
    echo -e "${GREEN}✓ Python: $($PYTHON --version)${NC}"
}

check_env() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠ .env belum ada. Menyalin dari .env.example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✓ .env dibuat. Edit sesuai kebutuhan.${NC}"
    else
        echo -e "${GREEN}✓ .env ditemukan${NC}"
    fi
}

install_deps() {
    echo -e "${YELLOW}Memeriksa dependensi...${NC}"
    pip install -r requirements.txt -q 2>/dev/null || pip3 install -r requirements.txt -q
    echo -e "${GREEN}✓ Dependensi terinstall${NC}"
}

seed_data() {
    echo -e "${YELLOW}Menseed database dengan dokumen contoh...${NC}"
    $PYTHON scripts/seed_data.py
    echo -e "${GREEN}✓ Database siap${NC}"
}

start_backend() {
    echo -e "${GREEN}Menjalankan backend di http://localhost:8000${NC}"
    echo -e "${GREEN}API Docs: http://localhost:8000/docs${NC}"
    $PYTHON -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

start_frontend() {
    echo -e "${GREEN}Menjalankan frontend di http://localhost:8501${NC}"
    $PYTHON -m streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
}

run_tests() {
    echo -e "${YELLOW}Menjalankan tests...${NC}"
    $PYTHON -m pytest tests/ -v --asyncio-mode=auto --tb=short
}

case "${1:-all}" in
    backend)
        check_python
        check_env
        install_deps
        start_backend
        ;;
    frontend)
        check_python
        check_env
        install_deps
        start_frontend
        ;;
    seed)
        check_python
        check_env
        install_deps
        seed_data
        ;;
    test)
        check_python
        check_env
        install_deps
        run_tests
        ;;
    all)
        check_python
        check_env
        install_deps
        seed_data
        echo -e "${GREEN}"
        echo "Mulai backend dan frontend..."
        echo -e "${NC}"
        # Start backend in background
        $PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        sleep 2
        # Start frontend
        $PYTHON -m streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
        # Cleanup on exit
        kill $BACKEND_PID 2>/dev/null
        ;;
    *)
        echo "Usage: $0 {backend|frontend|seed|test|all}"
        exit 1
        ;;
esac
