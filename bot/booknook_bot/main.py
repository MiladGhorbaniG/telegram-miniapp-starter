from __future__ import annotations

import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from booknook_bot.handlers import handle_text, load_entries
from booknook_core.faq import MockFaqModel


def serve_health(port: int = 8081) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib name
            body = b'{"status":"ok","service":"booknook-bot"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *args) -> None:
            return

    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


async def poll(token: str, entries: list[dict]) -> None:
    from aiogram import Bot, Dispatcher, F
    from aiogram.filters import Command, CommandStart

    bot = Bot(token)
    dispatcher = Dispatcher()
    model = MockFaqModel()

    @dispatcher.message(CommandStart())
    async def start(message) -> None:
        await message.answer(handle_text("/start", entries, model))

    @dispatcher.message(Command("faq"))
    async def faq(message) -> None:
        await message.answer(handle_text(message.text or "", entries, model))

    @dispatcher.message(F.text)
    async def other(message) -> None:
        await message.answer(handle_text(message.text or "", entries, model))

    await dispatcher.start_polling(bot)


def main() -> None:
    port = int(os.environ.get("BOT_HEALTH_PORT", "8081"))
    threading.Thread(target=serve_health, args=(port,), daemon=True).start()
    faq_path = Path(os.environ.get("FAQ_PATH", "sample_data/faq.json"))
    entries = load_entries(faq_path) if faq_path.exists() else []
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print("BookNook bot is idle because TELEGRAM_BOT_TOKEN is empty.")
        threading.Event().wait()
        return
    asyncio.run(poll(token, entries))


if __name__ == "__main__":
    main()
