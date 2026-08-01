import re
from typing import Literal

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    RateLimitError,
)

from app.core.config import get_settings

SYSTEM_PROMPT = """Anda adalah MrKarirBot AI, asisten karier profesional Indonesia.
Jawab dalam Bahasa Indonesia dengan langkah yang konkret, ringkas, faktual, etis, dan aman.
Jangan mengarang lowongan, perusahaan, gaji, statistik, sumber, atau tautan. Nyatakan
keterbatasan dan sarankan verifikasi pada sumber resmi bila informasi tidak tersedia.
"""

TASK_PROMPTS = {
    "career": "Bantu pengguna merencanakan langkah karier yang realistis dan dapat dilakukan.",
    "ats": (
        "Tinjau teks CV untuk kompatibilitas ATS. Beri skor indikatif 1-100 beserta alasan, "
        "keyword gap, masalah format, dampak, dan checklist revisi. Jangan menjanjikan kelulusan."
    ),
    "interview": (
        "Buat latihan interview sesuai posisi: pertanyaan, kerangka jawaban STAR, indikator "
        "jawaban kuat, dan latihan lanjutan."
    ),
    "roadmap": (
        "Susun roadmap menuju peran target: gap skill, urutan belajar, proyek portofolio, "
        "milestone 30/60/90 hari, dan cara mengukur progres."
    ),
    "salary": (
        "Berikan panduan riset dan negosiasi gaji. Jangan membuat angka tanpa sumber; minta "
        "lokasi, mata uang, level, dan periode, serta jelaskan ketidakpastian."
    ),
    "company": (
        "Bantu pengguna meneliti perusahaan dengan checklist sumber resmi dan pertanyaan "
        "verifikasi. Jangan mengklaim fakta perusahaan yang tidak diberikan pengguna."
    ),
    "scam": (
        "Analisis indikator penipuan secara transparan sebagai risiko rendah/sedang/tinggi, "
        "jelaskan alasannya, dan beri langkah verifikasi. Jangan memvonis tanpa bukti."
    ),
}

TaskName = Literal["career", "ats", "interview", "roadmap", "salary", "company", "scam"]
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?62|0)[\s.-]?(?:\d[\s.-]?){8,13}(?!\d)")
NIK_PATTERN = re.compile(r"(?<!\d)\d{16}(?!\d)")


def redact_sensitive_text(value: str) -> str:
    """Remove identifiers that are unnecessary for career guidance."""

    value = EMAIL_PATTERN.sub("[EMAIL DIHAPUS]", value)
    value = PHONE_PATTERN.sub("[NOMOR TELEPON DIHAPUS]", value)
    return NIK_PATTERN.sub("[NIK DIHAPUS]", value)


class AIService:
    def __init__(self) -> None:
        settings = get_settings()
        self.enabled = bool(settings.openai_api_key)
        self.client = (
            AsyncOpenAI(
                api_key=settings.openai_api_key,
                timeout=settings.openai_timeout_seconds,
                max_retries=2,
            )
            if self.enabled
            else None
        )
        self.model = settings.openai_model

    async def career_chat(self, message: str) -> str:
        return await self._complete("career", message)

    async def ats_review(self, cv_text: str) -> str:
        return await self._complete("ats", cv_text)

    async def interview_coach(self, target_role: str) -> str:
        return await self._complete("interview", target_role)

    async def career_roadmap(self, target_role: str) -> str:
        return await self._complete("roadmap", target_role)

    async def salary_guidance(self, context: str) -> str:
        return await self._complete("salary", context)

    async def company_research(self, company: str) -> str:
        return await self._complete("company", company)

    async def scam_explanation(self, evidence: str) -> str:
        return await self._complete("scam", evidence)

    async def _complete(self, task: TaskName, message: str) -> str:
        if not self.enabled or self.client is None:
            return "AI belum dikonfigurasi. Tambahkan OPENAI_API_KEY untuk mengaktifkan fitur ini."
        safe_message = redact_sensitive_text(message.strip())[:8000]
        try:
            response = await self.client.responses.create(
                model=self.model,
                reasoning={"effort": "none"},
                text={"verbosity": "medium"},
                input=[
                    {"role": "system", "content": f"{SYSTEM_PROMPT}\n{TASK_PROMPTS[task]}"},
                    {"role": "user", "content": safe_message},
                ],
            )
        except RateLimitError:
            return "Layanan AI sedang mencapai batas penggunaan. Silakan coba lagi beberapa saat."
        except APITimeoutError:
            return "Layanan AI membutuhkan waktu terlalu lama. Silakan coba lagi."
        except APIConnectionError:
            return "Layanan AI sementara tidak dapat dihubungi. Silakan coba lagi."
        except APIStatusError:
            return "Layanan AI sementara mengalami gangguan. Silakan coba lagi."
        answer = response.output_text.strip()
        return answer or "AI belum menghasilkan jawaban. Silakan kirim pertanyaan yang lebih spesifik."
