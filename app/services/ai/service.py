from openai import AsyncOpenAI
from app.core.config import get_settings

SYSTEM_PROMPT = """Anda adalah MrKarirBot AI, asisten karier profesional Indonesia.
Berikan jawaban praktis, etis, aman, dan berorientasi aksi untuk pencari kerja.
"""


class AIService:
    def __init__(self) -> None:
        settings = get_settings()
        self.enabled = bool(settings.openai_api_key)
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if self.enabled else None

    async def career_chat(self, message: str) -> str:
        if not self.enabled or self.client is None:
            return "AI belum dikonfigurasi. Tambahkan OPENAI_API_KEY untuk mengaktifkan fitur ini."
        response = await self.client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
        )
        return response.output_text

    async def ats_review(self, cv_text: str) -> str:
        prompt = f"Review CV berikut untuk ATS, beri skor 1-100 dan rekomendasi konkret:\n{cv_text}"
        return await self.career_chat(prompt)
