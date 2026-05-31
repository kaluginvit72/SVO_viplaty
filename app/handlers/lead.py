"""Сбор имени и телефона + отправка лида в Telegram через Cloudflare Worker."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.config import Settings
from app.services import webhook_lead
from app.states.questionnaire import Q
from app.texts import messages
from app.utils import send_with_retry
from app.utils.phone import normalize_phone

log = logging.getLogger(__name__)
router = Router()


@router.message(StateFilter(Q.lead_name), F.text, F.chat.type == "private")
async def collect_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if not name or len(name) > 120:
        await send_with_retry(lambda: message.answer(messages.name_invalid(), parse_mode="HTML"))
        return
    await state.update_data(lead_name=name)
    await state.set_state(Q.lead_phone)
    await send_with_retry(lambda: message.answer(messages.ask_phone(), parse_mode="HTML"))


@router.message(StateFilter(Q.lead_phone), F.text, F.chat.type == "private")
async def collect_phone(message: Message, state: FSMContext, settings: Settings) -> None:
    raw = (message.text or "").strip()
    norm = normalize_phone(raw)
    if not norm:
        await send_with_retry(lambda: message.answer(messages.phone_invalid(), parse_mode="HTML"))
        return

    data = await state.get_data()
    await state.set_state(Q.done)

    lead_payload = {
        "name": data.get("lead_name"),
        "phone": norm,
        "phoneRaw": raw,
        "applicantRole": data.get("applicant_role"),
        "statusOfDeceased": data.get("status_of_deceased"),
        "recipientsCount": data.get("recipients_count"),
        "baseTotal": data.get("base_total"),
        "personalShare": data.get("personal_share"),
        "stage": data.get("stage"),
        "flowMode": "fresh",
        "source": "telegram_bot",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "telegram_user_id": data.get("telegram_user_id"),
        "telegram_username": data.get("telegram_username"),
    }

    if settings.lead_webhook_url:
        try:
            await webhook_lead.post_lead_completed(
                settings.lead_webhook_url,
                settings.lead_webhook_secret,
                lead_payload,
            )
        except Exception:
            log.exception("Ошибка отправки лида в webhook")

    await send_with_retry(lambda: message.answer(messages.done_screen(), parse_mode="HTML"))
    log.info(
        "Лид принят user=%s name=%s phone=%s",
        data.get("telegram_user_id"),
        data.get("lead_name"),
        norm,
    )
