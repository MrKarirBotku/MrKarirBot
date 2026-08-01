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


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)


async def ats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _enter_state(update, context, BotState.ATS_REVIEW, "Kirim teks CV untuk review ATS awal.")


async def interview_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _enter_state(
        update,
        context,
        BotState.INTERVIEW_COACH,
        "Kirim posisi target untuk latihan interview dan jawaban STAR.",
    )


async def roadmap_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _enter_state(
        update,
        context,
        BotState.CAREER_ROADMAP,
        "Kirim posisi target dan pengalaman Anda saat ini untuk roadmap 30/60/90 hari.",
    )


async def salary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _enter_state(
        update,
        context,
        BotState.SALARY_GUIDANCE,
        "Kirim posisi, level, lokasi, mata uang, dan pengalaman untuk panduan riset gaji.",
    )


async def company_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _enter_state(
        update,
        context,
        BotState.COMPANY_RESEARCH,
        "Kirim nama perusahaan dan informasi yang ingin Anda verifikasi.",
    )


async def scam_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _enter_state(
        update,
        context,
        BotState.SCAM_CHECK,
        "Kirim ciri-ciri pesan atau proses rekrutmen. Hapus nama, nomor, dan data pribadi pihak lain.",
    )


async def privacy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Privasi: jangan kirim NIK, alamat lengkap, kata sandi, atau dokumen identitas. "
        "Email, nomor telepon, dan NIK dalam input AI akan disamarkan sebelum diproses. "
        "Lowongan hanya dibuka melalui tautan sumber aslinya.",
        reply_markup=main_menu(),
    )


async def _enter_state(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    state: BotState,
    prompt: str,
) -> None:
    context.user_data[STATE_KEY] = state
    await update.message.reply_text(prompt, reply_markup=back_menu())


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
    elif data == "roadmap":
        context.user_data[STATE_KEY] = BotState.CAREER_ROADMAP
        await query.edit_message_text(
            "🗺️ Kirim posisi target dan pengalaman Anda untuk roadmap 30/60/90 hari.",
            reply_markup=back_menu(),
        )
    elif data == "scam":
        context.user_data[STATE_KEY] = BotState.SCAM_CHECK
        await query.edit_message_text(
            "🛡️ Kirim ciri proses rekrutmen yang ingin diperiksa. Jangan kirim data pribadi.",
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
        reply = await ai.ats_review(message)
    elif state == BotState.INTERVIEW_COACH:
        reply = await ai.interview_coach(message)
    elif state == BotState.CAREER_ROADMAP:
        reply = await ai.career_roadmap(message)
    elif state == BotState.SALARY_GUIDANCE:
        reply = await ai.salary_guidance(message)
    elif state == BotState.COMPANY_RESEARCH:
        reply = await ai.company_research(message)
    elif state == BotState.SCAM_CHECK:
        reply = await ai.scam_explanation(message)
    else:
        reply = await ai.career_chat(message)
    await update.message.reply_text(reply[:3900], reply_markup=main_menu())


async def _send_job_results(
    update: Update,
    query: str = "",
    remote_only: bool = False,
) -> None:
    async with AsyncSessionLocal() as db:
        jobs, total = await JobService().search(
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

    await update.message.reply_text(f"Menampilkan {len(jobs)} dari {total} lowongan yang cocok:")
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
