from html import escape

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.bot.keyboards.main import back_menu, main_menu
from app.bot.messages import HELP, WELCOME
from app.bot.states import BotState
from app.database.session import AsyncSessionLocal
from app.services.ai.service import AIService
from app.services.jobs.service import JobService

STATE_KEY = "mrkarirbot_state"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[STATE_KEY] = BotState.HOME
    target = update.message or update.callback_query.message
    await target.reply_text(WELCOME, parse_mode="Markdown", reply_markup=main_menu())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP, reply_markup=main_menu())


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args).strip()
    if not query:
        context.user_data[STATE_KEY] = BotState.JOB_SEARCH
        await update.message.reply_text(
            "Kirim kata kunci setelah /cari. Contoh: /cari customer support",
            reply_markup=back_menu(),
        )
        return
    await _send_job_results(update, query=query)


async def remote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args).strip()
    await _send_job_results(update, query=query, remote_only=True)


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "home":
        context.user_data[STATE_KEY] = BotState.HOME
        await query.edit_message_text(WELCOME, parse_mode="Markdown", reply_markup=main_menu())
    elif data == "jobs":
        context.user_data[STATE_KEY] = BotState.JOB_SEARCH
        await query.edit_message_text(
            "🔍 Kirim kata kunci lowongan, contoh: `Data Analyst Jakarta`.",
            parse_mode="Markdown",
            reply_markup=back_menu(),
        )
    elif data == "ai":
        context.user_data[STATE_KEY] = BotState.AI_CHAT
        await query.edit_message_text(
            "🤖 Kirim pertanyaan karier Anda. Contoh: `Bagaimana negosiasi gaji fresh graduate?`",
            parse_mode="Markdown",
            reply_markup=back_menu(),
        )
    elif data == "ats":
        context.user_data[STATE_KEY] = BotState.ATS_REVIEW
        await query.edit_message_text(
            "📄 Kirim teks CV Anda untuk review ATS awal.", reply_markup=back_menu()
        )
    elif data == "interview":
        context.user_data[STATE_KEY] = BotState.INTERVIEW_COACH
        await query.edit_message_text(
            "🎤 Kirim posisi target Anda, lalu MrKarirBot akan memberi simulasi pertanyaan interview.",
            reply_markup=back_menu(),
        )


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text.strip()
    state = context.user_data.get(STATE_KEY, BotState.AI_CHAT)
    ai = AIService()
    if state == BotState.JOB_SEARCH:
        await _send_job_results(update, query=message)
        return
    elif state == BotState.ATS_REVIEW:
        prompt = f"Review CV berikut agar ATS friendly dan beri checklist perbaikan:\n{message}"
    elif state == BotState.INTERVIEW_COACH:
        prompt = (
            f"Buat simulasi interview untuk posisi {message}: 5 pertanyaan dan contoh jawaban STAR."
        )
    else:
        prompt = message
    reply = await ai.career_chat(prompt)
    await update.message.reply_text(reply[:3900], reply_markup=main_menu())


async def _send_job_results(
    update: Update,
    query: str = "",
    remote_only: bool = False,
) -> None:
    async with AsyncSessionLocal() as db:
        jobs = await JobService().search(
            db,
            query=query,
            limit=5,
            remote_only=remote_only,
        )

    if not jobs:
        await update.message.reply_text(
            "Belum ada lowongan yang cocok. Coba kata kunci lain atau tunggu sinkronisasi berikutnya.",
            reply_markup=main_menu(),
        )
        return

    await update.message.reply_text(f"Ditemukan {len(jobs)} lowongan terbaru:")
    for job in jobs:
        remote_label = "🌍 Remote\n" if job.is_remote else ""
        text = (
            f"<b>{escape(job.title)}</b>\n"
            f"🏢 {escape(job.company)}\n"
            f"📍 {escape(job.location or 'Lokasi tidak disebutkan')}\n"
            f"{remote_label}"
            f"🔎 Sumber: {escape(job.source_name)}"
        )
        keyboard = None
        if job.source_url:
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Lihat & Lamar", url=job.source_url)]]
            )
        await update.message.reply_text(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=keyboard,
        )
