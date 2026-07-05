"""
CivicTrust AI - Streamlit Frontend
Multi-page dashboard for public service AI assistant.
"""
import os
import uuid
from typing import Optional, Dict

import requests
import streamlit as st

st.set_page_config(
    page_title="CivicTrust AI",
    page_icon="\U0001f3db\ufe0f",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")
API_HEALTH_URL = os.environ.get("API_HEALTH_URL", "http://localhost:8000/health")

_DEFAULT_STATE = {
    "session_id": str(uuid.uuid4()),
    "messages": [],
    "language": "id",
    "theme": "light",
    "api_key": os.environ.get("STREAMLIT_API_KEY", ""),
    "backend_connected": None,
}
for key, val in _DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = val


def get_headers() -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if st.session_state.api_key:
        headers["X-API-Key"] = st.session_state.api_key
    return headers


def check_backend():
    if st.session_state.backend_connected is None:
        try:
            resp = requests.get(API_HEALTH_URL, timeout=5)
            st.session_state.backend_connected = resp.status_code == 200
        except requests.ConnectionError:
            st.session_state.backend_connected = False
    return st.session_state.backend_connected


def api_post(endpoint: str, json_body: dict, timeout: int = 30) -> Optional[Dict]:
    try:
        resp = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=json_body,
            headers=get_headers(),
            timeout=timeout,
        )
        if resp.status_code == 401:
            st.error("\U0001f512 API Key tidak valid. Set API Key di sidebar.")
            return None
        if resp.status_code == 429:
            st.warning("\u23f3 Terlalu banyak permintaan. Tunggu 60 detik.")
            return None
        if resp.status_code != 200:
            detail = resp.json().get("detail", resp.text)
            st.error(f"Error {resp.status_code}: {detail}")
            return None
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("\u274c Tidak dapat terhubung ke server backend.")
        return None
    except Exception as e:
        st.error(f"\u274c Error: {str(e)}")
        return None


def api_get(endpoint: str, timeout: int = 10) -> Optional[Dict]:
    try:
        resp = requests.get(
            f"{API_BASE_URL}{endpoint}",
            headers=get_headers(),
            timeout=timeout,
        )
        if resp.status_code == 401:
            st.error("\U0001f512 API Key tidak valid.")
            return None
        if resp.status_code == 200:
            return resp.json()
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp { font-family: 'Inter', sans-serif; }
        </style>
        """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h1>\U0001f3db\ufe0f CivicTrust AI</h1>
            <p class="sidebar-subtitle">Platform Layanan Publik Terpercaya</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        backend_ok = check_backend()
        if backend_ok:
            st.success("\u2705 Backend Terhubung")
        else:
            st.error("\u274c Backend Offline")
            st.page_link("http://localhost:8000/docs", label="Buka Swagger UI")

        st.divider()
        st.markdown("### \U0001f4c2 Navigasi")
        page = st.radio(
            "Menu",
            [
                "\U0001f3e0 Beranda",
                "\U0001f4ac Layanan Publik",
                "\U0001f50d Cek Fakta",
                "\U0001f310 Terjemahan",
                "\U0001f4c4 Upload Dokumen",
                "\U0001f4ca Statistik",
            ],
            label_visibility="collapsed",
            key="nav",
        )

        st.divider()
        st.markdown("### \u2699\ufe0f Pengaturan")
        lang = st.selectbox(
            "Bahasa",
            options=["id", "en", "fr", "ja", "ar"],
            format_func=lambda x: {
                "id": "\U0001f1ee\U0001f1e9 Indonesia",
                "en": "\U0001f1ec\U0001f1e7 English",
                "fr": "\U0001f1eb\U0001f1f7 Français",
                "ja": "\U0001f1ef\U0001f1f5 日本語",
                "ar": "\U0001f1f8\U0001f1e6 العربية",
            }.get(x, x),
            index=0,
        )
        st.session_state.language = lang

        theme = st.toggle("\U0001f319 Mode Gelap", value=(st.session_state.theme == "dark"))
        st.session_state.theme = "dark" if theme else "light"

        api_key = st.text_input(
            "\U0001f512 API Key",
            value=st.session_state.api_key,
            placeholder="opsional",
            type="password",
        )
        st.session_state.api_key = api_key

        st.divider()
        if st.button("\U0001f504 Sesi Baru", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.markdown(f"""
        <div class="sidebar-footer">
            <small>Sesi: {st.session_state.session_id[:8]}...</small><br>
            <small>CivicTrust AI v1.0.0</small>
        </div>
        """, unsafe_allow_html=True)

    return page


def render_home():
    st.markdown("""
    <div class="page-header">
        <h1>\U0001f3e0 CivicTrust AI</h1>
        <p>Platform AI untuk membantu warga mengakses layanan publik yang terpercaya.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("### \U0001f4ac Tanya Layanan")
            st.write("Tanyakan prosedur KTP, KK, BPJS, paspor, dan layanan publik lainnya.")
    with col2:
        with st.container(border=True):
            st.markdown("### \U0001f50d Cek Fakta")
            st.write("Verifikasi kebenaran informasi dengan sumber resmi pemerintah.")
    with col3:
        with st.container(border=True):
            st.markdown("### \U0001f310 Terjemahan")
            st.write("Terjemahkan dokumen ke 5 bahasa: Indonesia, Inggris, Prancis, Jepang, Arab.")

    st.divider()
    st.markdown("### \U0001f4dd Layanan Publik yang Didukung")
    cols = st.columns(4)
    services = [
        ("\U0001f9fe", "KTP Elektronik"),
        ("\U0001f46a", "Kartu Keluarga"),
        ("\U0001f3e5", "BPJS Kesehatan"),
        ("\U0001f30d", "Paspor"),
        ("\U0001f4b0", "NPWP"),
        ("\U0001f6a8", "SKCK"),
        ("\U0001f476", "Akta Kelahiran"),
        ("\U0001f4da", "Beasiswa"),
    ]
    for i, (icon, name) in enumerate(services):
        with cols[i % 4]:
            st.button(f"{icon} {name}", use_container_width=True, disabled=True)

    st.divider()
    with st.expander("\u2139\ufe0f Tentang CivicTrust AI"):
        st.markdown("""
        **CivicTrust AI** dikembangkan untuk kompetisi LKS 2026 - Solusi AI untuk Layanan Publik.

        **Fitur:**
        - Multi-agent AI pipeline (Planner, Retriever, FactChecker, Policy, Risk, Response)
        - RAG (Retrieval-Augmented Generation) dengan FAISS vector store
        - Trust Score & Explainability
        - Multi-bahasa (ID, EN, FR, JA, AR)
        - Vision OCR & Voice recognition
        - Dashboard analitik real-time

        **Prinsip Responsible AI:**
        - Verifikasi sumber secara sistematis
        - Transparansi confidence score
        - Deteksi bias dan hallucination
        """)


def render_chat():
    st.markdown("""
    <div class="page-header">
        <h1>\U0001f4ac Layanan Publik</h1>
        <p>Tanyakan tentang prosedur, persyaratan, dan informasi layanan publik.</p>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "details" in msg:
                with st.expander("\U0001f4cb Detail"):
                    for k, v in msg["details"].items():
                        st.markdown(f"**{k}:** {v}")

    if prompt := st.chat_input("Tanyakan sesuatu tentang layanan publik..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.status("Memproses...", expanded=True) as status:
                st.write("\U0001f50d Menganalisis pertanyaan...")
                data = api_post("/chat", {
                    "message": prompt,
                    "session_id": st.session_state.session_id,
                    "language": st.session_state.language,
                })

            if data:
                answer = data.get("answer", "Tidak ada jawaban.")
                trust_score = data.get("trust_score", 0.0)
                confidence = data.get("confidence", 0.0)
                latency = data.get("latency", 0.0)
                sources = data.get("sources", [])
                reasoning = data.get("reasoning_path", [])

                status.update(label="Selesai!", state="complete", expanded=False)
                st.markdown(answer)

                details = {}
                if reasoning:
                    with st.expander("\U0001f9e0 Proses Penalaran"):
                        for step in reasoning:
                            st.markdown(f"- {step}")
                    details["Penalaran"] = f"{len(reasoning)} langkah"

                if sources:
                    with st.expander(f"\U0001f4da Sumber ({len(sources)})"):
                        for src in sources:
                            title = src.get("title", "Sumber")
                            rel = src.get("relevance", "N/A")
                            st.markdown(f"**{title}** (relevansi: {rel})")
                            if src.get("content_preview"):
                                st.caption(src["content_preview"][:200] + "...")
                            st.divider()
                    details["Sumber"] = f"{len(sources)} dokumen"

                score_color = "\U0001f7e2" if trust_score >= 0.7 else ("\U0001f7e1" if trust_score >= 0.4 else "\U0001f534")
                st.caption(f"{score_color} Trust: {trust_score:.0%} | Confidence: {confidence:.0%} | Latensi: {latency:.1f}s")
                details["Trust Score"] = f"{trust_score:.0%}"
                details["Confidence"] = f"{confidence:.0%}"
                details["Latensi"] = f"{latency:.1f}s"

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "details": details,
                })

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("\U0001f9fe Cara buat KTP", use_container_width=True):
            _quick_chat("Bagaimana cara membuat KTP elektronik? Jelaskan langkah-langkahnya.")
    with col2:
        if st.button("\U0001f3e5 Daftar BPJS", use_container_width=True):
            _quick_chat("Bagaimana cara mendaftar BPJS Kesehatan?")
    with col3:
        if st.button("\U0001f30d Urus Paspor", use_container_width=True):
            _quick_chat("Apa saja syarat dan cara mengurus paspor?")


def _quick_chat(message: str):
    st.session_state.messages.append({"role": "user", "content": message})
    st.rerun()


def render_fact_check():
    st.markdown("""
    <div class="page-header">
        <h1>\U0001f50d Cek Fakta</h1>
        <p>Verifikasi kebenaran informasi atau klaim dengan sumber resmi pemerintah dan internasional.</p>
    </div>
    """, unsafe_allow_html=True)

    statement = st.text_area(
        "Masukkan pernyataan atau klaim:",
        placeholder="Contoh: Vaksin COVID-19 menyebabkan autisme...",
        height=120,
    )

    if st.button("\U0001f50d Verifikasi", type="primary", use_container_width=True):
        if not statement:
            st.warning("Silakan masukkan pernyataan.")
            return

        with st.spinner("Memverifikasi..."):
            data = api_post("/fact-check", {
                "statement": statement,
                "language": st.session_state.language,
            })

        if data:
            verdict = data.get("verdict", "unverified")
            confidence = data.get("confidence", 0.0)
            explanation = data.get("explanation", "")
            sources = data.get("sources", [])

            colors = {
                "true": "#d4edda", "false": "#f8d7da",
                "misleading": "#fff3cd", "unverified": "#e2e3e5",
            }
            icons = {
                "true": "\u2705", "false": "\u274c",
                "misleading": "\u26a0\ufe0f", "unverified": "\u2753",
            }
            labels = {
                "true": "TERVERIFIKASI - Informasi ini benar",
                "false": "TERBUKTI SALAH - Informasi ini tidak benar",
                "misleading": "MENYESATKAN - Informasi ini menyesatkan",
                "unverified": "BELUM TERVERIFIKASI - Tidak cukup data",
            }

            st.markdown(f"""
            <div style="padding:20px;border-radius:10px;background:{colors.get(verdict,'#e2e3e5')};">
                <h2 style="margin:0;">{icons.get(verdict,'\u2753')} {labels.get(verdict,'BELUM TERVERIFIKASI')}</h2>
                <p style="margin:10px 0 0 0;"><strong>Tingkat Keyakinan:</strong> {confidence:.0%}</p>
            </div>
            """, unsafe_allow_html=True)

            if explanation:
                st.markdown("### \U0001f4dd Penjelasan")
                st.write(explanation)

            if sources:
                with st.expander(f"\U0001f4da Sumber ({len(sources)})"):
                    for src in sources:
                        title = src.get("title", src) if isinstance(src, dict) else src
                        st.markdown(f"- {title}")


def render_translation():
    st.markdown("""
    <div class="page-header">
        <h1>\U0001f310 Terjemahan</h1>
        <p>Terjemahkan teks antar bahasa yang didukung.</p>
    </div>
    """, unsafe_allow_html=True)

    LANG_NAMES = {
        "id": "Indonesia", "en": "English",
        "fr": "Français", "ja": "日本語", "ar": "العربية",
    }

    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox(
            "Bahasa asal",
            options=list(LANG_NAMES.keys()),
            format_func=lambda x: f"\U0001f310 {LANG_NAMES.get(x, x)}",
            index=0,
        )
    with col2:
        target_lang = st.selectbox(
            "Bahasa tujuan",
            options=list(LANG_NAMES.keys()),
            format_func=lambda x: f"\U0001f310 {LANG_NAMES.get(x, x)}",
            index=1,
        )

    text = st.text_area(
        "Masukkan teks:",
        placeholder="Tulis teks yang ingin diterjemahkan...",
        height=150,
    )

    if st.button("\U0001f504 Terjemahkan", type="primary", use_container_width=True):
        if not text:
            st.warning("Silakan masukkan teks.")
            return

        with st.spinner("Menerjemahkan..."):
            data = api_post("/translate", {
                "text": text,
                "source_language": source_lang,
                "target_language": target_lang,
            })

        if data:
            st.markdown("### \U0001f4cd Hasil Terjemahan")
            st.markdown(f"""
            <div style="padding:20px;border-radius:10px;background:#f0fdf4;border:1px solid #bbf7d0;">
                <p style="font-size:1.1rem;margin:0;">{data.get('translated_text', '')}</p>
            </div>
            """, unsafe_allow_html=True)

            st.caption(f"{LANG_NAMES.get(source_lang, source_lang)} \u2192 {LANG_NAMES.get(target_lang, target_lang)}")


def render_upload():
    st.markdown("""
    <div class="page-header">
        <h1>\U0001f4c4 Upload Dokumen</h1>
        <p>Unggah dokumen ke basis pengetahuan untuk referensi AI.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        doc_id = st.text_input("ID Dokumen", placeholder="contoh: peraturan-menteri-001")
        source = st.text_input("Sumber", placeholder="contoh: Kementerian Kesehatan RI")
        source_type = st.selectbox(
            "Tipe Sumber",
            options=["law", "regulation", "ministry", "who", "un", "government", "news", "general"],
            format_func=lambda x: {
                "law": "\u2696\ufe0f Undang-Undang",
                "regulation": "\U0001f4c4 Peraturan",
                "ministry": "\U0001f3e6 Kementerian",
                "who": "\U0001f30d WHO",
                "un": "\U0001f30d PBB",
                "government": "\U0001f3db\ufe0f Pemerintah",
                "news": "\U0001f4f0 Berita",
                "general": "\U0001f4c1 Umum",
            }.get(x, x)
        )
        content = st.text_area(
            "Konten Dokumen",
            placeholder="Tempel konten dokumen di sini...",
            height=200,
        )

        if st.button("\U0001f4e4 Upload", type="primary", use_container_width=True):
            if not doc_id or not source or not content:
                st.warning("Lengkapi semua field.")
                return

            with st.spinner("Mengupload..."):
                data = api_post("/documents/ingest", {
                    "document_id": doc_id,
                    "content": content,
                    "source": source,
                    "source_type": source_type,
                    "language": st.session_state.language,
                })

            if data:
                st.success(f"\u2705 Dokumen '{doc_id}' berhasil diupload!")


def render_analytics():
    st.markdown("""
    <div class="page-header">
        <h1>\U0001f4ca Dashboard Analitik</h1>
        <p>Metrik performa dan evaluasi sistem CivicTrust AI.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Memuat data..."):
        data = api_get("/analytics")

    if data:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Pertanyaan", data.get("total_queries", 0))
        with col2:
            st.metric("Akurasi", f"{data.get('accuracy', 0):.0%}")
        with col3:
            st.metric("Trust Score Rata-rata", f"{data.get('trust_score_avg', 0):.0%}")
        with col4:
            st.metric("Latensi Rata-rata", f"{data.get('avg_latency', 0):.2f}s")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### \U0001f4ca Kualitas Jawaban")
            for metric, value in {
                "Presisi": data.get("precision", 0),
                "Recall": data.get("recall", 0),
                "Cakupan Sitasi": data.get("citation_coverage", 0),
            }.items():
                st.metric(metric, f"{value:.0%}")
        with col2:
            st.markdown("### \U0001f6e1\ufe0f Keamanan & Kepercayaan")
            for metric, value in {
                "Hallucination Rate": data.get("hallucination_rate", 0),
                "Rata-rata Trust Score": data.get("trust_score_avg", 0),
            }.items():
                st.metric(metric, f"{value:.0%}")

        st.info("\U0001f4c8 Grafik tren akan tersedia setelah sistem memiliki data yang cukup.")
    else:
        st.info("\u2139\ufe0f Data analitik belum tersedia. Gunakan fitur chat dan fact-check untuk mengumpulkan data.")


def main():
    load_css()

    if st.session_state.theme == "dark":
        st.markdown("""
        <style>
        .stApp { background-color: #0f172a; color: #e0e0e0; }
        .stChatMessage { background-color: #1e293b; }
        </style>
        """, unsafe_allow_html=True)

    page = render_sidebar()

    if not check_backend():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align:center;padding:4rem 1rem;">
                <div style="font-size:4rem;margin-bottom:1rem;">\U0001f6ab</div>
                <h2>Backend Tidak Terhubung</h2>
                <p style="color:#64748b;">
                    Jalankan backend terlebih dahulu:<br>
                    <code>uvicorn app.main:app --reload --port 8000</code>
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("\U0001f504 Coba Lagi", use_container_width=True, type="primary"):
                st.session_state.backend_connected = None
                st.rerun()
        return

    pages = {
        "\U0001f3e0 Beranda": render_home,
        "\U0001f4ac Layanan Publik": render_chat,
        "\U0001f50d Cek Fakta": render_fact_check,
        "\U0001f310 Terjemahan": render_translation,
        "\U0001f4c4 Upload Dokumen": render_upload,
        "\U0001f4ca Statistik": render_analytics,
    }
    pages.get(page, render_home)()


if __name__ == "__main__":
    main()
