import asyncio
import logging
from typing import Callable, Awaitable, TypeVar

from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError
from aiogram.types import CallbackQuery

from app.utils.money import format_money_ru
from app.utils.phone import normalize_phone

__all__ = ["format_money_ru", "normalize_phone", "send_with_retry", "safe_call_answer"]

_log = logging.getLogger(__name__)
T = TypeVar("T")


async def safe_call_answer(call: CallbackQuery, text: str = "") -> None:
    """Ответить на callback_query, игнорируя ошибку 'query is too old'."""
    try:
        await call.answer(text)
    except TelegramBadRequest:
        pass


async def send_with_retry(fn: Callable[[], Awaitable[T]], retries: int = 3, delay: float = 1.0) -> T:
    """Вызвать async-функцию с повторами при TelegramNetworkError."""
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            return await fn()
        except TelegramNetworkError as e:
            last_exc = e
            if attempt < retries - 1:
                _log.warning("TelegramNetworkError (attempt %d/%d): %s — retry in %.1fs", attempt + 1, retries, e, delay)
                await asyncio.sleep(delay)
    raise last_exc  # type: ignore[misc]
