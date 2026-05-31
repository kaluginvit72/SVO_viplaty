"""Запуск Telegram-бота: webhook (prod) или polling (dev)."""

from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode

from app.config import _env, get_settings
from app.db.base import init_db
from app.db.fsm_storage import SqliteFSMStorage
from app.handlers import register_handlers
from app.logging import setup_logging
from app.repositories.lead_repository import LeadRepository

log = logging.getLogger(__name__)


async def _run() -> None:
    settings = get_settings()
    if not settings.bot_token:
        print("Укажите BOT_TOKEN в .env", file=sys.stderr)
        raise SystemExit(1)

    setup_logging(settings.log_level)
    await init_db(settings.database_path)

    repo = LeadRepository(settings.database_path)
    storage = SqliteFSMStorage(settings.database_path)

    tg_server_url = _env("TELEGRAM_SERVER_URL")
    if tg_server_url:
        session = AiohttpSession(api=TelegramAPIServer.from_base(tg_server_url))
        log.info("Telegram Bot API proxied via %s", tg_server_url)
    else:
        session = AiohttpSession()
    # keepalive: close stale connections quickly to avoid "connection reset" on reuse
    session._connector_init.update({"keepalive_timeout": 10, "enable_cleanup_closed": True})

    bot = Bot(
        settings.bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)
    register_handlers(dp, repo, settings)

    if settings.admin_chat_id is None:
        log.warning("ADMIN_CHAT_ID не задан — уведомления о заявках отключены")
    if settings.lead_webhook_url:
        log.info("LEAD_WEBHOOK_URL задан — завершённые заявки дублируются POST JSON")

    webhook_url = _env("TELEGRAM_WEBHOOK_URL")
    if webhook_url:
        await _run_webhook(dp, bot, webhook_url)
    else:
        log.info("Бот запущен (polling)")
        await dp.start_polling(bot, polling_timeout=1)


async def _run_webhook(dp: Dispatcher, bot: Bot, webhook_url: str) -> None:
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    path = _env("TELEGRAM_WEBHOOK_PATH", "/tg")
    port = int(_env("TELEGRAM_WEBHOOK_PORT", "8080"))
    secret = _env("TELEGRAM_WEBHOOK_SECRET") or None

    await bot.set_webhook(webhook_url, secret_token=secret, drop_pending_updates=True)
    log.info("Webhook set: %s", webhook_url)

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=secret).register(app, path=path)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    log.info("Webhook server listening on port %d", port)
    await asyncio.Event().wait()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
