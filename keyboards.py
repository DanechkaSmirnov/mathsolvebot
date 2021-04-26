from telebot import types


def menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=3)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='Услуги'))
    keyboard_buttons.append(types.KeyboardButton(text='Аккаунт'))
    keyboard_buttons.append(types.KeyboardButton(text='Техподдержка'))
    keyboard_buttons.append(types.KeyboardButton(text='О нас'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def about_us_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='Как работает бот'))
    keyboard_buttons.append(types.KeyboardButton(text='Назад'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def how_it_words():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='Назад'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def services_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='Оставить заявку'))
    keyboard_buttons.append(types.KeyboardButton(text='Пополнить баланс'))
    keyboard_buttons.append(types.KeyboardButton(text='Назад'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def account_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='История заявок'))
    keyboard_buttons.append(types.KeyboardButton(text='Пополнить баланс'))
    keyboard_buttons.append(types.KeyboardButton(text='Назад'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def homework_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='Заполнить форму'))
    keyboard_buttons.append(types.KeyboardButton(text='Пополнить баланс'))
    keyboard_buttons.append(types.KeyboardButton(text='Назад'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def difficulty_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard_buttons = []
    keyboard_buttons.append(types.InlineKeyboardButton(text='Легкий', callback_data='easy'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Средний', callback_data='medium'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Сложный', callback_data='hard'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Олимпиадный', callback_data='olympiad'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def change_task_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(
        types.InlineKeyboardButton(text='Изменить количество заданий', callback_data='num_of_tasks'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Изменить тему ', callback_data='theme_of_task'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Изменить сложность', callback_data='difficult_of_task'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Изменить фото', callback_data='photo_of_task'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Изменить комментарий', callback_data='comment_of_task'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Отправить задание', callback_data='complete_task'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def set_of_tasks_keyboard(tasks):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    for task in tasks:
        text_button = ''
        if task[1] == 0:
            text_button = 'Задание {}: готовность - ❌'.format(1 + int(task[0][1 + str.find(task[0], '_'):]))
        if task[1] == 1:
            text_button = 'Задание {}: готовность - ✅'.format(1 + int(task[0][1 + str.find(task[0], '_'):]))
        if task[1] == 2:
            text_button = 'Задание {}: готовность - 💀'.format(1 + int(task[0][1 + str.find(task[0], '_'):]))
        keyboard_buttons.append(types.InlineKeyboardButton(text=text_button, callback_data=('task_' + str(task[0]))))
    keyboard.add(*keyboard_buttons)
    return keyboard


def open_task_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='Перейти в меню'))
    keyboard_buttons.append(types.KeyboardButton(text='Назад'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def solver_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='Статистика'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def solver_task_keyboard(task_id, solver_id):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard_buttons = []
    keyboard_buttons.append(
        types.InlineKeyboardButton(text='✅', callback_data='accept+' + str(task_id) + '+' + str(solver_id)))
    keyboard_buttons.append(
        types.InlineKeyboardButton(text='💀', callback_data='report+' + str(task_id) + '+' + str(solver_id)))
    keyboard_buttons.append(
        types.InlineKeyboardButton(text='❌', callback_data='deny+' + str(task_id) + '+' + str(solver_id)))
    keyboard.add(*keyboard_buttons)
    return keyboard


def solving_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.InlineKeyboardButton(text='Отправить решение', callback_data='send_solution'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Отменить решение', callback_data='deny_solution'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def report_task_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='Назад'))
    keyboard.add(*keyboard_buttons)
    return keyboard
