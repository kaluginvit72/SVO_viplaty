"""3 вопроса квиза + кнопка рестарта."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards import questionnaire as kb
from app.services import calculator as calc
from app.states.questionnaire import Q
from app.texts import messages
from app.utils import safe_call_answer

log = logging.getLogger(__name__)
router = Router()


async def _edit(call: CallbackQuery, state: FSMContext, text: str, markup) -> None:
    data = await state.get_data()
    mid = data.get("ui_message_id")
    if mid and call.message:
        from aiogram.exceptions import TelegramBadRequest
        try:
            await call.message.bot.edit_message_text(
                text,
                chat_id=call.message.chat.id,
                message_id=mid,
                reply_markup=markup,
                parse_mode="HTML",
            )
            return
        except TelegramBadRequest:
            pass
    if call.message:
        msg = await call.message.answer(text, reply_markup=markup, parse_mode="HTML")
        await state.update_data(ui_message_id=msg.message_id)


# ── Кнопка «Узнать свою сумму» на стартовом экране ─────────────────────────

@router.callback_query(StateFilter(Q.quiz_status), F.data == "start:quiz")
async def start_quiz(call: CallbackQuery, state: FSMContext) -> None:
    await safe_call_answer(call)
    await _edit(call, state, messages.q_status(), kb.quiz_status_kb())


# ── Вопрос 1: статус погибшего ───────────────────────────────────────────────

@router.callback_query(StateFilter(Q.quiz_status), F.data.startswith("qs:"))
async def step_status(call: CallbackQuery, state: FSMContext) -> None:
    await safe_call_answer(call)
    key = (call.data or "").split(":")[-1]
    await state.update_data(status_of_deceased=key)
    await state.set_state(Q.quiz_role)
    await _edit(call, state, messages.q_role(), kb.quiz_role_kb())


# ── Вопрос 2: роль заявителя ────────────────────────────────────────────────

@router.callback_query(StateFilter(Q.quiz_role), F.data.startswith("qr:"))
async def step_role(call: CallbackQuery, state: FSMContext) -> None:
    await safe_call_answer(call)
    key = (call.data or "").split(":")[-1]
    await state.update_data(applicant_role=key)
    await state.set_state(Q.quiz_recipients)
    await _edit(call, state, messages.q_recipients(), kb.quiz_recipients_kb())


# ── Вопрос 3: количество получателей ────────────────────────────────────────

@router.callback_query(StateFilter(Q.quiz_recipients), F.data.startswith("qn:"))
async def step_recipients(call: CallbackQuery, state: FSMContext) -> None:
    await safe_call_answer(call)
    raw = (call.data or "").split(":")[-1]
    n = int(raw) if raw in ("1", "2", "3", "4") else 1
    data = await state.get_data()
    role = data.get("applicant_role", "other")
    result = calc.calculate_share(role, n)
    await state.update_data(
        recipients_count=n,
        base_total=result["base_total"],
        personal_share=result["personal_total"],
    )
    await state.set_state(Q.result)
    await _edit(call, state, messages.result_screen(result, role), kb.result_kb())


# ── Рестарт из любого места ─────────────────────────────────────────────────

@router.callback_query(F.data == "res:restart")
async def do_restart(call: CallbackQuery, state: FSMContext) -> None:
    await safe_call_answer(call)
    await state.clear()
    if call.from_user:
        await state.update_data(
            telegram_user_id=call.from_user.id,
            telegram_username=call.from_user.username,
        )
    await state.set_state(Q.quiz_status)
    await _edit(call, state, messages.welcome(), kb.start_kb())


# ── Заглушка для текстовых сообщений вне ожидаемого ввода ───────────────────

@router.message(StateFilter(Q.quiz_status, Q.quiz_role, Q.quiz_recipients, Q.result), F.chat.type == "private")
async def quiz_unexpected_text(message: Message) -> None:
    await message.answer("Пожалуйста, выберите вариант кнопками выше или нажмите /start.", parse_mode="HTML")
