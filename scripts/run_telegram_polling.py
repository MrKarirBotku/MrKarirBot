from app.bot.application import build_application


def main() -> None:
    application = build_application()
    application.run_polling(allowed_updates=None)


if __name__ == "__main__":
    main()
