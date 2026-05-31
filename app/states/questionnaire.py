"""Состояния FSM — упрощённый продающий флоу."""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class Q(StatesGroup):
    quiz_status = State()       # статус погибшего
    quiz_role = State()         # кто обращается
    quiz_recipients = State()   # сколько получателей
    result = State()            # результат + CTA
    quiz_stage = State()        # этап оформления
    lead_name = State()         # имя
    lead_phone = State()        # телефон
    done = State()              # финал
