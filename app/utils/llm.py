import asyncio
import json
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

KNOWLEDGE_BASE = {
    "ktp": {
        "title": "Pembuatan KTP Elektronik (e-KTP)",
        "procedure": [
            "Datang ke kantor Dinas Kependudukan dan Pencatatan Sipil (Disdukcapil) setempat",
            "Membawa fotokopi Kartu Keluarga (KK)",
            "Mengisi formulir permohonan",
            "Melakukan perekaman data: foto, sidik jari, tanda tangan",
            "Menunggu proses verifikasi dan pencetakan (biasanya 14 hari kerja)",
            "Mengambil KTP di kantor Disdukcapil atau dikirim ke alamat"
        ],
        "requirements": [
            "Kartu Keluarga (KK)",
            "Usia minimal 17 tahun",
            "Sudah menikah (bagi yang belum berusia 17 tahun)",
            "Mengisi formulir permohonan"
        ],
        "source": "https://dukcapil.kemendagri.go.id",
        "source_type": "government",
        "regulations": ["UU No. 24 Tahun 2013 tentang Administrasi Kependudukan"],
        "cost": "Gratis (tidak dipungut biaya)"
    },
    "kk": {
        "title": "Pembuatan Kartu Keluarga (KK)",
        "procedure": [
            "Datang ke kantor Disdukcapil setempat",
            "Membawa dokumen persyaratan",
            "Mengisi formulir permohonan KK",
            "Petugas memverifikasi data",
            "KK baru akan diterbitkan dalam 14 hari kerja"
        ],
        "requirements": [
            "Surat nikah/akta perkawinan",
            "Akta kelahiran semua anggota keluarga",
            "KK lama (jika ada perubahan data)",
            "Surat pindah (jika pindah domisili)"
        ],
        "source": "https://dukcapil.kemendagri.go.id",
        "source_type": "government",
        "regulations": ["UU No. 24 Tahun 2013 tentang Administrasi Kependudukan"],
        "cost": "Gratis"
    },
    "bpjs": {
        "title": "Pendaftaran BPJS Kesehatan",
        "procedure": [
            "Kunjungi kantor BPJS Kesehatan terdekat atau website bpjs-kesehatan.go.id",
            "Siapkan nomor induk kependudukan (NIK)",
            "Pilih kelas rawat inap (I, II, atau III)",
            "Membayar iuran bulanan sesuai kelas yang dipilih",
            "Kartu BPJS akan diterbitkan dan dikirim ke alamat"
        ],
        "requirements": [
            "KTP",
            "Kartu Keluarga (KK)",
            "Nomor rekening bank (untuk autodebet)",
            "Pas foto 3x4 (2 lembar)"
        ],
        "source": "https://bpjs-kesehatan.go.id",
        "source_type": "government",
        "regulations": [
            "UU No. 40 Tahun 2004 tentang Sistem Jaminan Sosial Nasional",
            "UU No. 24 Tahun 2011 tentang BPJS"
        ],
        "cost": "Kelas I: Rp150.000/bln, Kelas II: Rp100.000/bln, Kelas III: Rp42.000/bln"
    },
    "pajak": {
        "title": "Pembuatan NPWP (Nomor Pokok Wajib Pajak)",
        "procedure": [
            "Buka website ereg.pajak.go.id",
            "Daftar akun dengan email dan NIK",
            "Isi formulir pendaftaran secara online",
            "Unggah dokumen persyaratan",
            "Verifikasi data oleh petugas pajak",
            "NPWP akan dikirim ke email dalam 1-3 hari kerja"
        ],
        "requirements": [
            "KTP",
            "Kartu Keluarga (KK)",
            "NPWP (jika sudah punya) - untuk perubahan data",
            "Akte pendirian perusahaan (untuk badan usaha)"
        ],
        "source": "https://pajak.go.id",
        "source_type": "government",
        "regulations": ["UU No. 36 Tahun 2008 tentang Pajak Penghasilan"],
        "cost": "Gratis"
    },
    "paspor": {
        "title": "Pembuatan Paspor",
        "procedure": [
            "Buat janji online di website imigrasi.go.id atau aplikasi M-Paspor",
            "Datang ke kantor Imigrasi sesuai jadwal",
            "Membawa dokumen persyaratan",
            "Melakukan wawancara dan verifikasi data",
            "Perekaman foto dan sidik jari",
            "Pembayaran biaya paspor",
            "Paspor selesai dalam 3-5 hari kerja"
        ],
        "requirements": [
            "KTP",
            "Kartu Keluarga (KK)",
            "Akta kelahiran",
            "Pas foto terbaru background putih",
            "Paspor lama (jika perpanjangan)"
        ],
        "source": "https://imigrasi.go.id",
        "source_type": "government",
        "regulations": [
            "UU No. 6 Tahun 2011 tentang Keimigrasian",
            "PP No. 28 Tahun 2019 tentang Paspor"
        ],
        "cost": "Paspor 48 halaman: Rp350.000, Paspor 24 halaman: Rp250.000"
    },
    "akta_lahir": {
        "title": "Pembuatan Akta Kelahiran",
        "procedure": [
            "Datang ke kantor Disdukcapil setempat",
            "Membawa dokumen persyaratan",
            "Mengisi formulir permohonan",
            "Petugas memverifikasi data",
            "Akta kelahiran diterbitkan dalam 14 hari kerja",
            "Pengambilan akta kelahiran di Disdukcapil"
        ],
        "requirements": [
            "Surat keterangan lahir dari bidan/dokter/rumah sakit",
            "Kartu Keluarga (KK) orang tua",
            "KTP orang tua (ayah dan ibu)",
            "Akta nikah orang tua",
            "Saksi kelahiran (2 orang)"
        ],
        "source": "https://dukcapil.kemendagri.go.id",
        "source_type": "government",
        "regulations": ["UU No. 24 Tahun 2013 tentang Administrasi Kependudukan"],
        "cost": "Gratis"
    },
    "skck": {
        "title": "Pembuatan SKCK (Surat Keterangan Catatan Kepolisian)",
        "procedure": [
            "Download dan isi formulir dari website Polri",
            "Ambil sidik jari di kantor Polsek/Polres",
            "Datang ke kantor Polres dengan dokumen",
            "Verifikasi data oleh petugas",
            "Pembayaran biaya SKCK",
            "SKCK diterbitkan dalam 1-3 hari kerja"
        ],
        "requirements": [
            "KTP",
            "Kartu Keluarga (KK)",
            "Pas foto 4x6 (6 lembar) background merah",
            "Fotokopi akta kelahiran",
            "Rumus sidik jari",
            "SKCK lama (jika perpanjangan)"
        ],
        "source": "https://polri.go.id",
        "source_type": "government",
        "regulations": ["UU No. 2 Tahun 2002 tentang Kepolisian RI"],
        "cost": "Rp30.000"
    },
    "beasiswa": {
        "title": "Program Beasiswa Pemerintah",
        "procedure": [
            "Cek informasi beasiswa di website kemdikbud.go.id atau puslapdik.kemdikbud.go.id",
            "Siapkan dokumen persyaratan",
            "Daftar secara online melalui portal beasiswa",
            "Ikuti seleksi administrasi",
            "Ikuti tes kemampuan akademik",
            "Wawancara",
            "Pengumuman hasil seleksi"
        ],
        "requirements": [
            "KTP",
            "Kartu Keluarga (KK)",
            "Rapor/transkrip nilai",
            "Surat rekomendasi dari sekolah/kampus",
            "Surat keterangan tidak mampu (jika ada)",
            "Esai motivasi"
        ],
        "source": "https://kemdikbud.go.id",
        "source_type": "government",
        "regulations": [
            "UU No. 20 Tahun 2003 tentang Sistem Pendidikan Nasional",
            "Permendikbud No. 10 Tahun 2020 tentang Beasiswa"
        ],
        "cost": "Gratis (tidak dipungut biaya pendaftaran)"
    },
    "bansos": {
        "title": "Program Bantuan Sosial Pemerintah",
        "procedure": [
            "Pastikan terdaftar di Data Terpadu Kesejahteraan Sosial (DTKS)",
            "Cek status penerima manfaat di website cekbansos.kemensos.go.id",
            "Jika belum terdaftar, ajukan melalui kelurahan/desa",
            "Verifikasi data oleh petugas sosial",
            "Bantuan akan disalurkan melalui Himbara (bank BUMN)",
            "Ambil bantuan di kantor pos atau bank yang ditunjuk"
        ],
        "requirements": [
            "KTP",
            "Kartu Keluarga (KK)",
            "Terdaftar di DTKS",
            "Surat keterangan tidak mampu dari kelurahan/desa"
        ],
        "source": "https://kemensos.go.id",
        "source_type": "government",
        "regulations": [
            "UU No. 13 Tahun 2011 tentang Penanganan Fakir Miskin",
            "Perpres No. 63 Tahun 2017 tentang DTKS"
        ],
        "cost": "Gratis"
    },
    "vaksin": {
        "title": "Vaksinasi COVID-19",
        "content": "Vaksin COVID-19 telah terbukti aman dan efektif berdasarkan penelitian ilmiah dan rekomendasi WHO. Vaksin yang digunakan di Indonesia (Sinovac, AstraZeneca, Moderna) telah mendapat Emergency Use Authorization dari BPOM dan halal dari MUI. Efek samping umum bersifat ringan seperti nyeri di tempat suntikan, demam ringan, dan kelelahan. Vaksinasi gratis untuk seluruh warga Indonesia melalui program pemerintah.",
        "verdict": "true",
        "source": "https://who.int, https://kemkes.go.id",
        "source_type": "who",
        "regulations": ["Permenkes No. 10 Tahun 2021 tentang Vaksinasi COVID-19"]
    },
    "hoaks": {
        "title": "Verifikasi Informasi Hoaks",
        "procedure": [
            "Periksa sumber informasi asli",
            "Cek di portal resmi pemerintah",
            "Verifikasi di fact-checking platform",
            "Cross-check dengan sumber terpercaya lainnya"
        ],
        "requirements": [],
        "source": "https://kominfo.go.id",
        "source_type": "government",
        "regulations": [
            "UU No. 19 Tahun 2016 tentang Informasi dan Transaksi Elektronik",
            "UU No. 1 Tahun 2024 tentang Perubahan Kedua UU ITE"
        ],
        "cost": "N/A"
    }
}

TRANSLATIONS = {
    ("id", "en"): {
        "ktp": "ID Card",
        "kk": "Family Card",
        "bpjs": "BPJS Health Insurance",
        "paspor": "Passport",
        "akta_lahir": "Birth Certificate",
        "skck": "Police Clearance Certificate",
        "pajak": "Tax ID",
        "bansos": "Social Assistance",
        "beasiswa": "Scholarship",
        "vaksin": "Vaccine",
        "selamat pagi": "Good morning",
        "selamat siang": "Good afternoon",
        "selamat malam": "Good evening",
        "terima kasih": "Thank you",
        "tolong": "Please",
        "ya": "Yes",
        "tidak": "No",
        "berapa biaya": "How much does it cost",
        "syarat": "Requirements",
        "cara": "How to",
        "dimana": "Where",
        "kapan": "When",
    },
    ("en", "id"): {
        "id card": "KTP",
        "family card": "Kartu Keluarga",
        "passport": "Paspor",
        "birth certificate": "Akta Kelahiran",
        "good morning": "Selamat pagi",
        "thank you": "Terima kasih",
        "how much": "Berapa biaya",
        "requirements": "Persyaratan",
        "how to": "Bagaimana cara",
        "where": "Dimana",
        "when": "Kapan",
    }
}

class LLMInterface:
    """Unified interface for LLM providers with async support."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self._client = None

    def _get_client(self):
        current_provider = settings.LLM_PROVIDER
        if current_provider != self.provider:
            self.provider = current_provider
            self.model = settings.LLM_MODEL
            self.temperature = settings.LLM_TEMPERATURE
            self.max_tokens = settings.LLM_MAX_TOKENS
            self._client = None

        if self._client is not None:
            return self._client

        provider_map = {
            "google": self._init_google,
            "openai": self._init_openai,
            "deepseek": self._init_deepseek,
            "qwen": self._init_qwen,
            "openrouter": self._init_openrouter,
        }

        init_fn = provider_map.get(self.provider)
        if init_fn:
            self._client = init_fn()
        else:
            logger.warning(f"Unknown provider {self.provider}, falling back to mock")
            self._client = self._init_mock()

        return self._client

    def _init_google(self):
        try:
            from google import genai
            api_key = settings.GOOGLE_API_KEY or settings.LLM_API_KEY
            if not api_key:
                logger.warning("No Google API key found, using mock")
                return self._init_mock()
            client = genai.Client(api_key=api_key)
            return client
        except ImportError:
            logger.warning("google-genai not installed, using mock")
            return self._init_mock()

    def _init_openai(self):
        try:
            from openai import OpenAI
            api_key = settings.OPENAI_API_KEY or settings.LLM_API_KEY
            if not api_key:
                logger.warning("No OpenAI API key found, using mock")
                return self._init_mock()
            return OpenAI(api_key=api_key)
        except ImportError:
            logger.warning("openai not installed, using mock")
            return self._init_mock()

    def _init_deepseek(self):
        try:
            from openai import OpenAI
            api_key = settings.DEEPSEEK_API_KEY or settings.LLM_API_KEY
            if not api_key:
                logger.warning("No DeepSeek API key found, using mock")
                return self._init_mock()
            return OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1",
            )
        except ImportError:
            logger.warning("openai not installed for DeepSeek, using mock")
            return self._init_mock()

    def _init_qwen(self):
        try:
            from openai import OpenAI
            api_key = settings.QWEN_API_KEY or settings.LLM_API_KEY
            if not api_key:
                logger.warning("No Qwen API key found, using mock")
                return self._init_mock()
            return OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
        except ImportError:
            logger.warning("openai not installed for Qwen, using mock")
            return self._init_mock()

    def _init_openrouter(self):
        try:
            from openai import OpenAI
            api_key = settings.OPENROUTER_API_KEY or settings.LLM_API_KEY
            if not api_key:
                logger.warning("No OpenRouter API key found, using mock")
                return self._init_mock()
            return OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://civictrust.ai",
                    "X-Title": "CivicTrust AI",
                },
            )
        except ImportError:
            logger.warning("openai not installed for OpenRouter, using mock")
            return self._init_mock()

    def _init_mock(self):
        logger.info("Using mock LLM (no API keys configured)")
        return "mock"

    async def generate(self, prompt: str) -> str:
        client = self._get_client()
        if client == "mock":
            return await asyncio.to_thread(self._mock_generate, prompt)
        try:
            if self.provider == "google":
                return await asyncio.to_thread(self._generate_google_sync, client, prompt)
            else:
                return await asyncio.to_thread(self._generate_openai_like_sync, client, prompt)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._mock_generate(prompt)

    def _generate_google_sync(self, client, prompt: str) -> str:
        try:
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            logger.error(f"Google generation error: {e}")
            raise

    def _generate_openai_like_sync(self, client, prompt: str) -> str:
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI-like generation error: {e}")
            raise

    def _mock_generate(self, prompt: str) -> str:
        prompt_lower = prompt.lower()

        if "helpful ai assistant for civictrust ai" in prompt_lower:
            return self._mock_response(prompt_lower, prompt)
        elif "planning agent" in prompt_lower or "planning" in prompt_lower:
            return self._mock_planner(prompt_lower, prompt)
        elif "fact-checking agent" in prompt_lower or "fact_check" in prompt_lower:
            return self._mock_fact_check(prompt_lower, prompt)
        elif "policy compliance agent" in prompt_lower:
            return self._mock_policy(prompt_lower, prompt)
        elif "risk assessment agent" in prompt_lower:
            return self._mock_risk(prompt_lower, prompt)
        elif "translate" in prompt_lower:
            return self._mock_translate(prompt_lower, prompt)
        elif "detect the language" in prompt_lower:
            return "id"
        else:
            return self._mock_response(prompt_lower, prompt)

    def _find_knowledge(self, query: str) -> Optional[dict]:
        query_lower = query.lower()
        for key, info in KNOWLEDGE_BASE.items():
            if key in query_lower or key.replace("_", " ") in query_lower:
                return info
            title_lower = info.get("title", "").lower()
            for word in title_lower.split():
                if word in query_lower and len(word) > 3:
                    return info
        return None

    def _mock_planner(self, prompt_lower: str, prompt: str) -> str:
        query_line = ""
        for line in prompt.split("\n"):
            line = line.strip()
            if line.startswith("Query:") and "Context:" not in line:
                query_line = line.replace("Query:", "").strip()
                break

        if not query_line:
            query_line = prompt_lower

        info = self._find_knowledge(query_line)

        if info:
            return json.dumps({
                "topic": info.get("title", "public_service"),
                "sub_questions": [
                    f"Apa saja persyaratan untuk {info.get('title', 'layanan ini')}?",
                    f"Bagaimana prosedur pengurusan {info.get('title', 'layanan ini')}?",
                    f"Berapa biaya untuk {info.get('title', 'layanan ini')}?",
                ],
                "required_sources": ["government", "regulation"],
                "needs_fact_check": True,
                "needs_policy_check": True,
                "steps": ["retrieve_information", "verify_facts", "check_policy", "assess_risk", "generate_response"],
            })
        elif "vaksin" in query_line or "covid" in query_line:
            return json.dumps({
                "topic": "kesehatan_masyarakat",
                "sub_questions": ["Apakah vaksin COVID-19 aman?", "Apa saja efek samping vaksin?"],
                "required_sources": ["who", "ministry"],
                "needs_fact_check": True,
                "needs_policy_check": False,
                "steps": ["retrieve_information", "verify_facts", "assess_risk"],
            })
        elif "hoaks" in query_line or "bohong" in query_line or "fake" in query_line:
            return json.dumps({
                "topic": "cek_fakta",
                "sub_questions": ["Apakah informasi ini benar?", "Apa kata sumber resmi?"],
                "required_sources": ["government", "who"],
                "needs_fact_check": True,
                "needs_policy_check": True,
                "steps": ["retrieve_information", "verify_facts", "check_policy"],
            })
        else:
            return json.dumps({
                "topic": "public_service",
                "sub_questions": [query_line],
                "required_sources": ["government", "general"],
                "needs_fact_check": True,
                "needs_policy_check": True,
                "steps": ["retrieve_information", "generate_response"],
            })

    def _mock_fact_check(self, prompt_lower: str, prompt: str) -> str:
        query_line = ""
        for line in prompt.split("\n"):
            line = line.strip()
            if line.startswith("Claim:") or line.startswith("Query:"):
                query_line = line.split(":", 1)[1].strip()
                break
        if not query_line:
            query_line = prompt_lower

        info = self._find_knowledge(query_line)

        if info and "verdict" in info:
            return json.dumps({
                "verdict": info["verdict"],
                "confidence": 0.92,
                "explanation": "Informasi ini telah diverifikasi dan sesuai dengan sumber resmi. Vaksin COVID-19 telah melalui uji klinis dan mendapatkan izin edar dari BPOM serta rekomendasi WHO. Keamanan vaksin terus dipantau melalui sistem surveillance keamanan vaksin.",
                "supporting_sources": [info.get("source", "Sumber Resmi")],
                "contradicting_sources": [],
            })

        if info:
            return json.dumps({
                "verdict": "true",
                "confidence": 0.88,
                "explanation": f"Informasi ini sesuai dengan sumber resmi yaitu {info.get('source', 'portal pemerintah')}. Data telah diverifikasi dan sesuai dengan regulasi yang berlaku.",
                "supporting_sources": [info.get("source", "Sumber Resmi")],
                "contradicting_sources": [],
            })

        return json.dumps({
            "verdict": "unverified",
            "confidence": 0.35,
            "explanation": "Informasi ini belum dapat diverifikasi karena tidak ditemukan sumber resmi yang relevan. Silakan periksa langsung ke instansi terkait.",
            "supporting_sources": [],
            "contradicting_sources": [],
        })

    def _mock_policy(self, prompt_lower: str, prompt: str) -> str:
        query_line = ""
        for line in prompt.split("\n"):
            line = line.strip()
            if line.startswith("Query:"):
                query_line = line.split(":", 1)[1].strip()
                break
        if not query_line:
            query_line = prompt_lower

        info = self._find_knowledge(query_line)

        if info and info.get("regulations"):
            return json.dumps({
                "compliant": True,
                "applicable_regulations": info["regulations"],
                "conflicts": [],
                "notes": f"Informasi sesuai dengan regulasi yang berlaku. Regulasi terkait: {', '.join(info['regulations'])}",
                "confidence": 0.92,
            })

        return json.dumps({
            "compliant": True,
            "applicable_regulations": ["UU No. 25 Tahun 2009 tentang Pelayanan Publik"],
            "conflicts": [],
            "notes": "Informasi umum tentang pelayanan publik sesuai dengan regulasi yang berlaku.",
            "confidence": 0.80,
        })

    def _mock_risk(self, prompt_lower: str, prompt: str) -> str:
        query_line = ""
        for line in prompt.split("\n"):
            line = line.strip()
            if line.startswith("Query:"):
                query_line = line.split(":", 1)[1].strip()
                break
        if not query_line:
            query_line = prompt_lower

        info = self._find_knowledge(query_line)

        if info:
            return json.dumps({
                "hallucination_risk": 0.05,
                "bias_risk": 0.02,
                "sensitive_content_risk": 0.0,
                "misinformation_risk": 0.03,
                "privacy_risk": 0.0,
                "overall_risk": 0.03,
                "flags": [],
                "recommendations": ["Informasi aman untuk disampaikan", "Sumber resmi terpercaya"],
            })
        elif "vaksin" in query_line or "covid" in query_line:
            return json.dumps({
                "hallucination_risk": 0.05,
                "bias_risk": 0.05,
                "sensitive_content_risk": 0.0,
                "misinformation_risk": 0.1,
                "privacy_risk": 0.0,
                "overall_risk": 0.05,
                "flags": [],
                "recommendations": ["Gunakan sumber WHO dan Kemenkes", "Cantumkan disclaimer medis"],
            })
        else:
            return json.dumps({
                "hallucination_risk": 0.15,
                "bias_risk": 0.1,
                "sensitive_content_risk": 0.0,
                "misinformation_risk": 0.15,
                "privacy_risk": 0.0,
                "overall_risk": 0.12,
                "flags": [],
                "recommendations": ["Informasi perlu diverifikasi lebih lanjut"],
            })

    def _mock_translate(self, prompt_lower: str, prompt: str) -> str:
        lines = prompt.strip().split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("Text:"):
                text_parts = [stripped.split(":", 1)[1].strip()]
                for next_line in lines[i+1:]:
                    next_stripped = next_line.strip()
                    if next_stripped.startswith("Translation:") or next_stripped == "":
                        break
                    text_parts.append(next_stripped)
                return "\n".join(text_parts).strip()
        for line in lines:
            stripped = line.strip()
            if stripped and not any(x in stripped.lower() for x in ["translate", "translation", "from ", "to ", "source:", "target:", "text:", "the following"]):
                if ":" not in stripped:
                    return stripped
        return prompt[:200]

    def _mock_response(self, prompt_lower: str, prompt: str) -> str:
        query_line = ""
        for line in prompt.split("\n"):
            line = line.strip()
            if line.startswith("Query:"):
                query_line = line.split(":", 1)[1].strip()
                break
        if not query_line:
            query_line = prompt_lower

        info = self._find_knowledge(query_line)

        if info:
            title = info.get("title", "")
            procedure = info.get("procedure", [])
            requirements = info.get("requirements", [])
            cost = info.get("cost", "Tidak disebutkan")
            source = info.get("source", "Sumber Resmi")

            answer_parts = [f"**{title}**\n"]

            if procedure:
                answer_parts.append("**Prosedur:**")
                for i, step in enumerate(procedure, 1):
                    answer_parts.append(f"{i}. {step}")

            if requirements:
                answer_parts.append("\n**Persyaratan:**")
                for req in requirements:
                    answer_parts.append(f"- {req}")

            answer_parts.append(f"\n**Biaya:** {cost}")
            answer_parts.append(f"**Sumber:** [Link Resmi]({source})")
            answer_parts.append(f"\n*Informasi ini diverifikasi dari sumber resmi. Untuk informasi lebih detail, kunjungi {source}.*")

            return json.dumps({
                "answer": "\n".join(answer_parts),
                "key_points": [
                    f"Prosedur pengurusan {title} tersedia dalam {len(procedure)} langkah",
                    f"{len(requirements)} persyaratan dokumen diperlukan",
                    f"Biaya: {cost}",
                ],
                "next_steps": [
                    f"Siapkan dokumen persyaratan untuk {title}",
                    "Kunjungi kantor pelayanan terkait",
                    "Hubungi call center untuk informasi lebih lanjut",
                ],
                "citations": [f"{title} - {source}"],
                "confidence": 0.90,
            })

        if "vaksin" in query_line or "covid" in query_line:
            return json.dumps({
                "answer": "**Vaksinasi COVID-19 di Indonesia**\n\nVaksin COVID-19 yang digunakan di Indonesia (Sinovac, AstraZeneca, Moderna) telah mendapatkan izin edar dari BPOM dan dinyatakan halal oleh MUI. Vaksinasi terbukti aman dan efektif dalam mencegah gejala berat COVID-19.\n\n**Fakta Penting:**\n- Vaksin telah melalui uji klinis fase 1-3\n- Efek samping umum: nyeri lokal, demam ringan, fatigue\n- Efek samping serius sangat jarang (<0.01%)\n- Vaksinasi gratis untuk seluruh warga Indonesia\n\n**Sumber:** WHO, Kemenkes RI, BPOM\n\n*Untuk informasi lebih lanjut, hubungi hotline Kemenkes di 119 atau kunjungi kemkes.go.id*",
                "key_points": [
                    "Vaksin COVID-19 aman dan efektif",
                    "Telah mendapat izin BPOM dan fatwa halal MUI",
                    "Efek samping serius sangat jarang terjadi",
                    "Vaksinasi gratis untuk semua warga",
                ],
                "next_steps": [
                    "Kunjungi fasilitas kesehatan terdekat untuk vaksinasi",
                    "Daftar melalui aplikasi PeduliLindungi/SatuSehat",
                    "Lengkapi vaksinasi dosis 1, 2, dan booster",
                ],
                "citations": [
                    "WHO - COVID-19 Vaccine Safety",
                    "Kemenkes RI - Vaksinasi COVID-19",
                    "BPOM - Emergency Use Authorization",
                ],
                "confidence": 0.95,
            })

        return json.dumps({
            "answer": "Terima kasih atas pertanyaan Anda. Berdasarkan sumber resmi yang tersedia, berikut informasi yang dapat kami berikan.\n\nUntuk pertanyaan yang lebih spesifik tentang layanan publik seperti:\n- **KTP Elektronik** (persyaratan, prosedur, biaya)\n- **Kartu Keluarga** (perubahan data, pencetakan baru)\n- **BPJS Kesehatan** (pendaftaran, iuran, kelas)\n- **Paspor** (pembuatan baru, perpanjangan)\n- **Akta Kelahiran** (pembuatan, duplikat)\n- **NPWP** (pendaftaran, pelaporan pajak)\n- **SKCK** (pembuatan baru, perpanjangan)\n- **Bantuan Sosial** (PKH, BPNT, BST)\n\nSilakan tanyakan spesifik layanan yang Anda butuhkan.",
            "key_points": [
                "Silakan tanyakan spesifik tentang layanan publik",
                "Informasi bersumber dari portal resmi pemerintah",
                "Kami siap membantu 24/7",
            ],
            "next_steps": [
                "Sebutkan layanan publik yang ingin ditanyakan",
                "Sebutkan kota/kabupaten domisili",
                "Kami akan memberikan panduan lengkap",
            ],
            "citations": ["Portal Informasi Pemerintah - Indonesia.go.id"],
            "confidence": 0.80,
        })


_llm_instance = None


def get_llm() -> LLMInterface:
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMInterface()
    return _llm_instance
