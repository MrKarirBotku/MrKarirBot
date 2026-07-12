import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


def main() -> int:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL")
    if not token or not webhook_url:
        print("TELEGRAM_BOT_TOKEN and TELEGRAM_WEBHOOK_URL are required", file=sys.stderr)
        return 2

    api_url = urljoin(f"https://api.telegram.org/bot{token}/", "setWebhook")
    payload = json.dumps({"url": webhook_url, "drop_pending_updates": True}).encode("utf-8")
    request = Request(api_url, data=payload, headers={"Content-Type": "application/json"}, method="POST")

    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        print(f"Telegram setWebhook failed with HTTP {exc.code}", file=sys.stderr)
        return 1
    except URLError as exc:
        print(f"Telegram setWebhook network error: {exc.reason}", file=sys.stderr)
        return 1

    if not data.get("ok"):
        print(f"Telegram setWebhook rejected request: {data.get('description', 'unknown error')}", file=sys.stderr)
        return 1
    print("Telegram webhook configured successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
