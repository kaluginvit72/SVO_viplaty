"""Тексты бота — продающий флоу."""

from __future__ import annotations

from app.utils.money import format_money_ru

BASE_TOTAL = 14_208_154.28

CONTACT_PHONE = "8(993)502-10-61"
CONTACT_NAME = "Виталий"
CONTACT_EMAIL = "iTrader7.5@yandex.ru"

STATUS_LABELS: dict[str, str] = {
    "contract": "Военнослужащий по контракту",
    "mobilized": "Мобилизованный",
    "volunteer": "Доброволец",
    "other": "Другой статус",
}

ROLE_LABELS: dict[str, str] = {
    "spouse": "Супруга / муж",
    "parent": "Родитель / усыновитель",
    "foster_parent": "Фактический воспитатель",
    "child": "Ребёнок (до 23 лет)",
    "other_kin": "Ребёнок 23+ / брат / сестра",
    "grandparent": "Дедушка / бабушка",
    "stepparent": "Отчим / мачеха",
    "other": "Другое",
}

STAGE_LABELS: dict[str, str] = {
    "new": "Ещё не обращались",
    "waiting": "Документы поданы, ждём",
    "partial": "Выплатили меньше положенного",
    "refused": "Получили отказ",
}


def welcome() -> str:
    total = format_money_ru(BASE_TOTAL)
    return (
        f"💰 <b>Семьи погибших бойцов СВО получают выплаты\n"
        f"до {total} ₽</b>\n"
        "\n"
        "Президентская, страховая, по 306-ФЗ — всё вместе.\n"
        "\n"
        "Узнайте вашу сумму за 2 минуты — ответьте на 3 вопроса."
    )


def q_status() -> str:
    return "⚔️ <b>Вопрос 1 из 3</b>\n\nКакой статус был у погибшего?"


def q_role() -> str:
    return "👤 <b>Вопрос 2 из 3</b>\n\nКто вы по отношению к погибшему?"


def q_recipients() -> str:
    return "👨‍👩‍👧 <b>Вопрос 3 из 3</b>\n\nСколько человек будут получать выплаты?"


def q_stage() -> str:
    return (
        "📋 <b>Последний вопрос</b>\n"
        "\n"
        "На каком этапе оформления вы сейчас?"
    )


def result_screen(calc_result: dict, role: str) -> str:
    role_label = ROLE_LABELS.get(role, "Заявитель")
    n = calc_result["recipients"]
    share_note = f" · {n} получателей" if n > 1 else ""

    if calc_result.get("is_insurance_only"):
        i = format_money_ru(calc_result["insurance_52"])
        total = format_money_ru(calc_result["personal_total"])
        return (
            f"📊 <b>Предварительный расчёт</b>\n"
            f"\n"
            f"<b>{role_label}</b>{share_note}\n"
            f"\n"
            f"• Указ Президента № 98:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>не применимо</i>\n"
            f"• Единовр. пособие (306-ФЗ):&nbsp;<i>не применимо</i>\n"
            f"• Страховая выплата (52-ФЗ):&nbsp;<b>{i} ₽</b>\n"
            f"\n"
            f"💰 <b>Итого ваша доля: {total} ₽</b>\n"
            f"\n"
            f"<i>При наличии подтверждающих документов или решения суда.</i>\n"
            f"\n"
            f"Точный расчёт — бесплатно.\n"
            f"\n"
            f"Хотите, чтобы {CONTACT_NAME} помог с оформлением?"
        )

    if calc_result.get("is_limited"):
        p = format_money_ru(calc_result["presidential"])
        total = format_money_ru(calc_result["personal_total"])
        return (
            f"📊 <b>Предварительный расчёт</b>\n"
            f"\n"
            f"<b>{role_label}</b>{share_note}\n"
            f"\n"
            f"• Указ Президента № 98:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>{p} ₽</b>\n"
            f"• Единовр. пособие (306-ФЗ):&nbsp;<i>уточняется</i>\n"
            f"• Страховая выплата (52-ФЗ):&nbsp;<i>уточняется</i>\n"
            f"\n"
            f"💰 <b>Ориентировочно: {total} ₽</b>\n"
            f"\n"
            f"<i>Право на Указ № 98 — при отсутствии супруги, детей и родителей.</i>\n"
            f"\n"
            f"Точный расчёт — бесплатно.\n"
            f"\n"
            f"Хотите, чтобы {CONTACT_NAME} помог с оформлением?"
        )

    # Полный круг: spouse, parent, foster_parent, child, other
    p = format_money_ru(calc_result["presidential"])
    b = format_money_ru(calc_result["benefit_306"])
    i = format_money_ru(calc_result["insurance_52"])
    total = format_money_ru(calc_result["personal_total"])
    return (
        f"📊 <b>Предварительный расчёт</b>\n"
        f"\n"
        f"<b>{role_label}</b>{share_note}\n"
        f"\n"
        f"• Указ Президента № 98:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>{p} ₽</b>\n"
        f"• Единовр. пособие (306-ФЗ):&nbsp;<b>{b} ₽</b>\n"
        f"• Страховая выплата (52-ФЗ):&nbsp;<b>{i} ₽</b>\n"
        f"\n"
        f"💰 <b>Итого ваша доля: {total} ₽</b>\n"
        f"\n"
        f"Плюс: погребение до 51 552 ₽, памятник до 49 511 ₽,\n"
        f"пенсии и региональные выплаты — считаются отдельно.\n"
        f"\n"
        f"Точный расчёт — бесплатно.\n"
        f"\n"
        f"Хотите, чтобы {CONTACT_NAME} помог с оформлением?"
    )


def ask_name() -> str:
    return "✏️ Напишите ваше <b>имя</b>:"


def ask_phone() -> str:
    return "📞 Напишите ваш <b>номер телефона</b>:"


def name_invalid() -> str:
    return "⚠️ Пожалуйста, введите имя (не более 120 символов)."


def phone_invalid() -> str:
    return "⚠️ Не распознаю номер. Введите в формате +7 999 123 45 67 или 8-999-123-45-67."


def done_screen() -> str:
    return (
        "✅ <b>Заявка принята!</b>\n"
        "\n"
        f"{CONTACT_NAME} свяжется с вами в ближайшее время.\n"
        "\n"
        f"📞 <b>{CONTACT_PHONE}</b>\n"
        f"📧 {CONTACT_EMAIL}\n"
        "\n"
        "<i>Если возникнут вопросы — пишите напрямую.</i>"
    )


def fallback_hint() -> str:
    return "Пожалуйста, напишите текстом или выберите вариант кнопками."


def help_text() -> str:
    return (
        "ℹ️ <b>Помощь</b>\n"
        "\n"
        "Этот бот помогает узнать ориентировочную сумму выплат семьям погибших бойцов СВО "
        "и связаться со специалистом для оформления.\n"
        "\n"
        "/start — начать заново\n"
        "\n"
        f"Вопросы: {CONTACT_PHONE}, {CONTACT_NAME}"
    )
