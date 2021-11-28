import logging
import os
import expenses
import exceptions
from aiogram import Bot, Dispatcher, executor, types
from categories import Categories
import buttons as nav
from access_for_bot import Access
from dotenv import load_dotenv
load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
ACCESS_ID = int(os.getenv("TELEGRAM_ACCESS_ID"))

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(Access(ACCESS_ID))


@dp.message_handler(commands=['start', 'help'])
async def welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer(
        "Привет! Я твой бот записи расходов)\n\n"
        "Добавить расход===> 750 АЗС\n",
        reply_markup=nav.mainMenu)


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
    """Удаляет одну запись о расходе по её идентификатору"""
    row_id = int(message.text[4:])
    expenses.delete_expense(row_id)
    answer_message = "Удалил"
    await message.answer(answer_message)


@dp.message_handler(commands=['Статистика_день'])
async def today_statistic(message: types.Message):
    """ Статистика за день """
    answer_message = expenses.get_today_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['Статистика_месяц'])
async def month_statistics(message: types.Message):
    answer_message = expenses.get_month_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['Категории'])
async def categories_list(message: types.Message):
    """Список категорий расходов"""
    categories = Categories().get_all_categories()
    answer_message = "Категории трат:\n\n* " + \
                    ("\n* ".join([c.name + ' (' + ", ".join(c.aliases) + ')' for c in categories]))
    await message.answer(answer_message)


@dp.message_handler(commands=['Посл_траты'])
async def list_expenses(message: types.Message):
    """Отправляет последние несколько записей о расходах"""
    last_expenses = expenses.last()
    if not last_expenses:
        await message.answer("Расходы ещё не заведены")
        return

    last_expenses_rows = [
        f"{expense.amount} грн. на {expense.category_name} — нажми "
        f"/del{expense.id} чтоб удалить"
        for expense in last_expenses]
    answer_message = "Последние сохранённые траты:\n\n* " + "\n\n* "\
            .join(last_expenses_rows)
    await message.answer(answer_message)


@dp.message_handler()
async def add_expense(message: types.Message):
    """ Add new expense"""
    try:
        expense = expenses.add_expense(message.text)
    except exceptions.NotCorrectMessage as error:
        await message.answer(str(error))
        return
    answer_message = (
        f"Добавлены траты :  {expense.amount} грн на {expense.category_name}.\n\n"
        f"{expenses.get_today_statistics()}")
    await message.answer(answer_message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

