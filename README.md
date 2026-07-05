# 🏛️ CivicTrust AI

**Platform AI untuk membantu warga mengakses layanan publik yang terpercaya.**

CivicTrust AI adalah platform SaaS berbasis AI yang dirancang untuk membantu warga mencari informasi layanan publik, memeriksa fakta, dan mendapatkan panduan prosedur birokrasi dari sumber resmi pemerintah.

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 💬 **AI Assistant** | Chatbot multi-agen untuk informasi layanan publik |
| 🔍 **Cek Fakta** | Verifikasi otomatis dari sumber resmi |
| 📋 **Panduan Prosedur** | Langkah-langkah mengurus dokumen administrasi |
| 🌐 **Multi-Bahasa** | Dukungan ID, EN, FR, JA, AR |
| 🖼️ **Vision OCR** | Ekstrak teks dari gambar dokumen |
| 🎤 **Voice Module** | Speech-to-text dan text-to-speech |
| 📊 **AI Analytics** | Dashboard metrik performa AI |
| 🛡️ **Trust Score** | Skor kepercayaan berbasis kredibilitas sumber |

## 🏗️ Arsitektur

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit UI  │────▶│   FastAPI API   │────▶│   AI Layer      │
│   (Frontend)    │     │   (Backend)     │     │   (LLM + RAG)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                        │
                               ▼                        ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │   FAISS Vector  │
                        │   (Database)    │     │   Store (RAG)   │
                        └─────────────────┘     └─────────────────┘
```

### Multi-Agent Pipeline

```
User Query → Planner → Retriever (RAG) → FactChecker → Policy → Risk → Response
                                                                          │
                                                                    Explainability
                                                                    + Trust Score
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/civictrust-ai.git
cd civictrust-ai

# Buat virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env dengan API key Anda
```

### Menjalankan Aplikasi

**Backend (FastAPI):**
```bash
uvicorn app.main:app --reload --port 8000
```

**Frontend (Streamlit):**
```bash
streamlit run frontend/app.py --server.port 8501
```

Akses:
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Docker

```bash
docker build -t civictrust-ai .
docker run -p 8000:8000 -p 8501:8501 civictrust-ai
```

## 📁 Struktur Proyek

```
civictrust-ai/
├── app/                    # Backend (FastAPI)
│   ├── agents/            # Multi-agent system
│   │   ├── orchestrator.py
│   │   ├── planner.py
│   │   ├── retriever.py
│   │   ├── fact_checker.py
│   │   ├── policy.py
│   │   ├── risk.py
│   │   └── response.py
│   ├── modules/           # Modul pendukung
│   │   ├── memory.py
│   │   ├── translation.py
│   │   ├── vision.py
│   │   ├── voice.py
│   │   ├── explainability.py
│   │   ├── trust_score.py
│   │   └── analytics.py
│   ├── rag/               # RAG Pipeline
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   └── ingestion.py
│   ├── database/          # Database
│   │   └── connection.py
│   ├── utils/             # Utilities
│   │   └── llm.py
│   ├── config.py
│   ├── api.py
│   └── main.py
├── frontend/              # Frontend (Streamlit)
│   ├── app.py
│   ├── assets/
│   │   └── style.css
│   ├── pages/
│   └── components/
├── data/                  # Data storage
│   ├── documents/
│   └── vector_store/
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── .github/workflows/     # CI/CD
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🔧 Konfigurasi

### Environment Variables

| Variable | Default | Deskripsi |
|----------|---------|-----------|
| `LLM_PROVIDER` | `google` | Provider LLM (google/openai/deepseek/qwen) |
| `LLM_MODEL` | `gemini-2.0-flash` | Model LLM |
| `GOOGLE_API_KEY` | - | API Key Google Gemini |
| `OPENAI_API_KEY` | - | API Key OpenAI |
| `DATABASE_URL` | `sqlite:///./data/civictrust.db` | URL Database |

### LLM Providers

CivicTrust AI mendukung multiple LLM providers:

1. **Google Gemini** (default) - `google/gemini-2.0-flash`
2. **OpenAI** - `openai/gpt-4o-mini`
3. **DeepSeek** - `deepseek/deepseek-chat`
4. **Qwen** - `qwen/qwen-turbo`

Tanpa API key, sistem akan menggunakan **mock LLM** untuk development.

## 🧪 Testing

```bash
# Jalankan semua test
pytest tests/ -v

# Test spesifik
pytest tests/test_api.py -v

# Dengan coverage
pytest tests/ --cov=app --cov-report=html
```

## 🌐 Deployment

### Streamlit Community Cloud (Frontend)
1. Push repository ke GitHub
2. Hubungkan ke Streamlit Community Cloud
3. Set `frontend/app.py` sebagai entry point

### Render (Backend API)
1. Buat Web Service di Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Supabase (Database)
1. Buat project di Supabase
2. Update `DATABASE_URL` dengan connection string Supabase

## 📊 Metrik AI

| Metrik | Target | Deskripsi |
|--------|--------|-----------|
| Akurasi | >85% | Kebenaran jawaban |
| Presisi | >80% | Ketepatan informasi |
| Recall | >75% | Kelengkapan informasi |
| Hallucination Rate | <5% | Tingkat halusinasi AI |
| Citation Coverage | >90% | Jawaban dengan sumber |
| Latency | <3s | Waktu respons |
| Trust Score | >0.7 | Skor kepercayaan |

## 🤝 Responsible AI

CivicTrust AI menerapkan prinsip Responsible AI:

- **Bias Detection**: Memeriksa bias dalam konten
- **Privacy Protection**: Tidak menyimpan data pribadi
- **Hallucination Detection**: Mendeteksi informasi palsu
- **Human Review Mode**: Mode review manual untuk konten sensitif
- **Source Verification**: Verifikasi sumber secara sistematis (S4)
- **Transparency**: Menampilkan confidence score dan sumber

## 📚 Sumber Data Resmi

Informasi berasal dari domain resmi:
- Pemerintah Indonesia (.go.id)
- Kementerian (.kemenkes.go.id, .kemendikbud.go.id)
- WHO (who.int)
- United Nations (un.org)
- BPS (bps.go.id)
- Peraturan Perundang-undangan

## 📄 Lisensi

MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## 👥 Tim Pengembang

Dikembangkan untuk kompetisi LKS 2026 - Solusi AI untuk Layanan Publik.

---

*"Membangun kepercayaan publik melalui AI yang transparan dan bertanggung jawab."*