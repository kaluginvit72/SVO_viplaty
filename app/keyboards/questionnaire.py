"""Inline-клавиатуры упрощённого флоу."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def _kb(rows: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t, callback_data=d) for t, d in row]
            for row in rows
        ]
    )


def start_kb() -> InlineKeyboardMarkup:
    return _kb([[("🧮 Узнать свою сумму", "start:quiz")]])


def quiz_status_kb() -> InlineKeyboardMarkup:
    return _kb([
        [("⚔️ Контрактник", "qs:contract")],
        [("🪖 Мобилизованный", "qs:mobilized")],
        [("🤝 Доброволец", "qs:volunteer")],
        [("❓ Другой / не знаю", "qs:other")],
    ])


def quiz_role_kb() -> InlineKeyboardMarkup:
    return _kb([
        [("💍 Супруга / муж", "qr:spouse")],
        [("👴 Родитель / усыновитель", "qr:parent")],
        [("🤝 Фактический воспитатель", "qr:foster_parent")],
        [("👶 Ребёнок (до 23 лет)", "qr:child")],
        [("🧑 Ребёнок 23+ / брат / сестра", "qr:other_kin")],
        [("👵 Дедушка / бабушка", "qr:grandparent")],
        [("👔 Отчим / мачеха", "qr:stepparent")],
        [("👤 Другое", "qr:other")],
    ])


def quiz_recipients_kb() -> InlineKeyboardMarkup:
    return _kb([
        [("👤 Только я", "qn:1"), ("👥 Нас 2", "qn:2")],
        [("👨‍👩‍👧 Нас 3", "qn:3"), ("👨‍👩‍👧‍👦 4 и более", "qn:4")],
    ])


def quiz_stage_kb() -> InlineKeyboardMarkup:
    return _kb([
        [("📝 Ещё не обращались", "stage:new")],
        [("⏳ Документы поданы, ждём", "stage:waiting")],
        [("💔 Выплатили меньше положенного", "stage:partial")],
        [("❌ Получили отказ", "stage:refused")],
    ])


def result_kb() -> InlineKeyboardMarkup:
    return _kb([
        [("✅ Хочу помощь с оформлением", "res:apply")],
        [("🔄 Начать заново", "res:restart")],
    ])


def restart_kb() -> InlineKeyboardMarkup:
    return _kb([[("🔄 Начать заново", "res:restart")]])
