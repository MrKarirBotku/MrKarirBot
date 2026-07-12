from telegram import Update
from telegram.ext import ContextTypes
from app.services.ai.service import AIService
from app.bot.keyboards.main import back_menu, main_menu
from app.bot.messages import HELP, WELCOME
from app.bot.states import BotState

STATE_KEY = "mrkarirbot_state"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[STATE_KEY] = BotState.HOME
    target = update.message or update.callback_query.message
    await target.reply_text(WELCOME, parse_mode="Markdown", reply_markup=main_menu())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP, reply_markup=main_menu())


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
        prompt = f"Rekomendasikan strategi pencarian lowongan untuk kata kunci: {message}"
    elif state == BotState.ATS_REVIEW:
        prompt = f"Review CV berikut agar ATS friendly dan beri checklist perbaikan:\n{message}"
    elif state == BotState.INTERVIEW_COACH:
        prompt = f"Buat simulasi interview untuk posisi {message}: 5 pertanyaan dan contoh jawaban STAR."
    else:
        prompt = message
    reply = await ai.career_chat(prompt)
    await update.message.reply_text(reply[:3900], reply_markup=main_menu())
