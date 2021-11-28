import re

import pytz

import exceptions
from categories import Categories
from typing import NamedTuple, List, Optional
import db
import datetime


class Message(NamedTuple):
    """parse"""
    amount: int
    category_text: str


class Expense(NamedTuple):
    """BD"""
    id: Optional[int]
    amount: int
    category_name: str


def pars_messages(raw_message: str) -> Message:
    regex_result = re.match(r"([\d ]+) (.*)", raw_message)
    #print(regex_result.group(2))

    if not regex_result or not regex_result.group(0) \
            or not regex_result.group(1) or not regex_result.group(2):
        raise exceptions.NotCorrectMessage(
            'Некорректный ввод.\n'
            'Напишите сообщение в формате: 50 кофе '
        )
    amount = int(regex_result.group(1))
    category_text = regex_result.group(2).lower()
    return Message(amount=amount, category_text=category_text)


def add_expense(raw_message: str) -> Expense:
    """Принимает на вход текст сообщения, пришедшего в бот."""
    parsed_message = pars_messages(raw_message)
    amount = parsed_message.amount
    category = Categories().get_category(
        parsed_message.category_text)
    inserted_row_id = db.insert("expense", {
        "amount": amount,
        "created": _get_now_formatted(),
        "category_codename": category.codename,
        "raw_text": raw_message
    })
    return Expense(
        id=None,
        amount=parsed_message.amount,
        category_name=category.name
    )


def get_today_statistics() -> str:
    """Статистика расходов за сегодня"""
    cursor = db.get_cursor()
    cursor.execute("select sum(amount)"
                   "from expense where date(created)=date('now', 'localtime')")
    result = cursor.fetchone()
    if not result[0]:
        return "Сегодня ещё нет расходов"
    all_today_expenses = result[0]
    return (f"Расходы сегодня:\n"
            f"всего — {all_today_expenses} грн.\n"
            f"За текущий месяц: /month")


def get_month_statistics() -> str:
    """Возвращает строкой статистику расходов за текущий месяц"""
    now = _get_now_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    cursor = db.get_cursor()
    cursor.execute(f"select sum(amount) "
                   f"from expense where date(created) >= '{first_day_of_month}'")
    result = cursor.fetchone()
    if not result[0]:
        return "В этом месяце ещё нет расходов"
    all_month_expenses = result[0]
    cursor.execute(f"select sum(amount) "
                   f"from expense where date(created) >= '{first_day_of_month}' ")
    result = cursor.fetchone()
    base_today_expenses = result[0] if result[0] else 0
    return (f"Расходы в текущем месяце:\n"
            f"всего — {all_month_expenses} грн.\n")


def last() -> List[Expense]:
    """Возвращает последние несколько расходов"""
    cursor = db.get_cursor()
    cursor.execute(
        "select e.id, e.amount, c.name "
        "from expense e left join category c "
        "on c.codename=e.category_codename "
        "order by created desc limit 7")
    rows = cursor.fetchall()
    last_expenses = [Expense(id=row[0], amount=row[1], category_name=row[2]) for row in rows]
    return last_expenses


def delete_expense(row_id: int) -> None:
    """Удаляет сообщение по его идентификатору"""
    db.delete("expense", row_id)


def _get_now_formatted() -> str:
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    tz = pytz.timezone("Europe/Kiev")
    now = datetime.datetime.now(tz)
    return now
