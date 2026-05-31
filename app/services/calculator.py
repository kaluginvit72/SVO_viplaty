"""Расчёт предварительных сумм (не юридическая консультация)."""

from __future__ import annotations

PRESIDENTIAL_PAYMENT = 5_000_000.0       # Указ № 98
BENEFIT_306_FZ = 5_524_892.57            # Единовременное пособие
INSURANCE_PAYMENT = 3_683_261.71         # Страховая сумма по 52-ФЗ
CHILD_MONTHLY_PAYMENT = 3_311.15

# Роли: только Указ № 98 (при отсутствии приоритетных получателей)
_LIMITED_ROLES = {"other_kin"}

# Роли: только страховая выплата по 52-ФЗ (при условии подтверждения)
_INSURANCE_ONLY_ROLES = {"grandparent", "stepparent"}


def calculate_share(applicant_role: str, recipients_count: int) -> dict:
    """Рассчитать долю заявителя с учётом роли и числа получателей.

    Три уровня:
    - full: все 3 выплаты (супруга, родитель, ребёнок до 23, воспитатель, другое)
    - limited: только Указ № 98 (ребёнок 23+, брат/сестра — при отсутствии приоритетных)
    - insurance_only: только 52-ФЗ (дедушка/бабушка, отчим/мачеха — при подтверждении)
    """
    n = max(1, int(recipients_count))
    limited = applicant_role in _LIMITED_ROLES
    insurance_only = applicant_role in _INSURANCE_ONLY_ROLES

    if insurance_only:
        presidential = None
        benefit_306 = None
        insurance_52 = INSURANCE_PAYMENT / n
        personal_total = insurance_52
        base_total = INSURANCE_PAYMENT
    elif limited:
        presidential = PRESIDENTIAL_PAYMENT / n
        benefit_306 = None
        insurance_52 = None
        personal_total = presidential
        base_total = PRESIDENTIAL_PAYMENT
    else:
        presidential = PRESIDENTIAL_PAYMENT / n
        benefit_306 = BENEFIT_306_FZ / n
        insurance_52 = INSURANCE_PAYMENT / n
        personal_total = presidential + benefit_306 + insurance_52
        base_total = PRESIDENTIAL_PAYMENT + BENEFIT_306_FZ + INSURANCE_PAYMENT

    return {
        "presidential": presidential,
        "benefit_306": benefit_306,
        "insurance_52": insurance_52,
        "personal_total": personal_total,
        "base_total": base_total,
        "is_limited": limited,
        "is_insurance_only": insurance_only,
        "recipients": n,
    }


def get_base_total() -> float:
    return PRESIDENTIAL_PAYMENT + BENEFIT_306_FZ + INSURANCE_PAYMENT


def get_personal_share(recipients_count: int) -> float:
    n = max(1, int(recipients_count))
    return get_base_total() / n


def has_child_monthly_payment(applicant_role: str | None) -> bool:
    return applicant_role in ("child", "child_u18", "child_student")


def calculate_lost_income(amount: float, months_waiting: int, monthly_rate: float = 0.012) -> float:
    m = max(0, int(months_waiting))
    return float(amount) * float(monthly_rate) * m


def months_from_waiting_key(key: str | None) -> int | None:
    mp = {"w1": 1, "w2": 2, "w4": 4, "w6": 6}
    return mp.get(key or "")
