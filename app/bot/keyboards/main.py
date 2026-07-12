from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🔍 Cari Lowongan", callback_data="jobs")],
        [InlineKeyboardButton("🤖 AI Karier", callback_data="ai")],
        [InlineKeyboardButton("📄 ATS CV Review", callback_data="ats")],
        [InlineKeyboardButton("🎤 Interview Coach", callback_data="interview")],
    ]
    return InlineKeyboardMarkup(rows)


def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="home")]])
