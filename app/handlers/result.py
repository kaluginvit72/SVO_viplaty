"""Экран результата: переход к вопросу об этапе оформления."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.keyboards import questionnaire as kb
from app.states.questionnaire import Q
from app.texts import messages
from app.utils import safe_call_answer

router = Router()


@router.callback_query(StateFilter(Q.result), F.data == "res:apply")
async def result_to_stage(call: CallbackQuery, state: FSMContext) -> None:
    await safe_call_answer(call)
    if not call.message:
        return
    await state.set_state(Q.quiz_stage)
    await call.message.answer(messages.q_stage(), reply_markup=kb.quiz_stage_kb(), parse_mode="HTML")


@router.callback_query(StateFilter(Q.quiz_stage), F.data.startswith("stage:"))
async def step_stage(call: CallbackQuery, state: FSMContext) -> None:
    await safe_call_answer(call)
    stage = (call.data or "").split(":")[-1]
    await state.update_data(stage=stage)
    await state.set_state(Q.lead_name)
    if call.message:
        await call.message.answer(messages.ask_name(), parse_mode="HTML")
