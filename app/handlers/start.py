"""Команды /start, /help, /restart."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards import questionnaire as kb
from app.states.questionnaire import Q
from app.texts import messages

log = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart(), F.chat.type == "private")
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user:
        await state.update_data(
            telegram_user_id=message.from_user.id,
            telegram_username=message.from_user.username,
        )
    msg = await message.answer(messages.welcome(), reply_markup=kb.start_kb(), parse_mode="HTML")
    await state.update_data(ui_message_id=msg.message_id)
    await state.set_state(Q.quiz_status)
    log.info("start user=%s", message.from_user.id if message.from_user else "?")


@router.message(Command("restart"), F.chat.type == "private")
async def cmd_restart(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user:
        await state.update_data(
            telegram_user_id=message.from_user.id,
            telegram_username=message.from_user.username,
        )
    msg = await message.answer(messages.welcome(), reply_markup=kb.start_kb(), parse_mode="HTML")
    await state.update_data(ui_message_id=msg.message_id)
    await state.set_state(Q.quiz_status)


@router.message(Command("help"), F.chat.type == "private")
async def cmd_help(message: Message) -> None:
    await message.answer(messages.help_text(), parse_mode="HTML")
