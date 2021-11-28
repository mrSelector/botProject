from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

btnToday = KeyboardButton('/Статистика_день', )
btnMonth = KeyboardButton('/Статистика_месяц')
btnCategory = KeyboardButton('/Категории')
btnLastExp = KeyboardButton('/Посл_траты')

mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnToday, btnMonth, btnLastExp, btnCategory)
