from telebot import types


def menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='📕 Услуги'))
    keyboard_buttons.append(types.KeyboardButton(text='📄 Аккаунт'))
    keyboard_buttons.append(types.KeyboardButton(text='❓ Техподдержка'))
    keyboard_buttons.append(types.KeyboardButton(text='👋 О нас'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def about_us_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='ℹ️ Как работает бот?'))
    keyboard_buttons.append(types.KeyboardButton(text='🔙 Назад'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def support_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='💬 Отправить запрос'))
    keyboard_buttons.append(types.KeyboardButton(text='🔙 Назад'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def how_it_words():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='🔙 Назад'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def services_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='📍 Оставить заявку'))
    keyboard_buttons.append(types.KeyboardButton(text='💰 Пополнить баланс'))
    keyboard_buttons.append(types.KeyboardButton(text='🔙 Назад'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def account_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='📍 История заявок'))
    keyboard_buttons.append(types.KeyboardButton(text='💰 Пополнить баланс'))
    keyboard_buttons.append(types.KeyboardButton(text='🔙 Назад'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def homework_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='📥 Заполнить форму'))
    keyboard_buttons.append(types.KeyboardButton(text='💰 Пополнить баланс'))
    keyboard_buttons.append(types.KeyboardButton(text='🔙 Назад'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def difficulty_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard_buttons = []
    keyboard_buttons.append(types.InlineKeyboardButton(text='Легкий', callback_data='easy'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Средний', callback_data='medium'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Сложный', callback_data='hard'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def change_task_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    # keyboard_buttons.append(
        # types.InlineKeyboardButton(text='Изменить количество заданий', callback_data='num_of_tasks'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='📖 Изменить тему ', callback_data='theme_of_task'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='📷 Изменить фото', callback_data='photo_of_task'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='📋 Изменить комментарий', callback_data='comment_of_task'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='✅ Отправить задание', callback_data='complete_task'))
    keyboard.add(*keyboard_buttons)
    return keyboard


# Статусы задания: 0 - решается, 1 - решено, 2 - отменено, 3 - ожидает оплаты
def set_of_tasks_keyboard(tasks):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    for task in tasks:
        text_button = ''
        if task[1] in [0, 4]:
            text_button = 'Задание {}: Ожидает подтверждения'.format(1 + int(task[0][1 + str.find(task[0], '_'):]))
        if task[1] == 1:
            text_button = 'Задание {}: Решено'.format(1 + int(task[0][1 + str.find(task[0], '_'):]))
        if task[1] == 2:
            text_button = 'Задание {}: Отменено'.format(1 + int(task[0][1 + str.find(task[0], '_'):]))
        if task[1] == 3:
            text_button = 'Задание {}: Ожидает оплаты'.format(1 + int(task[0][1 + str.find(task[0], '_'):]))
        if task[1] == 5:
            text_button = 'Задание {}: Готовится'.format(1 + int(task[0][1 + str.find(task[0], '_'):]))

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
    keyboard_buttons.append(types.KeyboardButton(text='Список оплаченных задач'))
    keyboard_buttons.append(types.KeyboardButton(text='Список неоплаченных задач'))

    # if status == True:
    #     keyboard_buttons.append(types.KeyboardButton(text='Online✅'))
    # elif status == False:
    #     keyboard_buttons.append(types.KeyboardButton(text='Offline❌ '))
    keyboard.add(*keyboard_buttons)
    return keyboard

def sending_photos_of_solution_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='Завершить'))
    keyboard_buttons.append(types.KeyboardButton(text='Отмена'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def solver_task_keyboard(task_id, solver_id):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard_buttons = []
    keyboard_buttons.append(
        types.InlineKeyboardButton(text='✅', callback_data='accept+' + str(task_id) + '+' + str(solver_id)))
    keyboard_buttons.append(
        types.InlineKeyboardButton(text='💀', callback_data='report+' + str(task_id) + '+' + str(solver_id)))
    keyboard.add(*keyboard_buttons)
    return keyboard


def solving_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.InlineKeyboardButton(text='Отправить решение', callback_data='send_solution'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Назад', callback_data='back_from_solving'))
    keyboard.add(*keyboard_buttons)
    return keyboard

def watch_unpaid_task_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.InlineKeyboardButton(text='Назад', callback_data='back_from_watching_free_task'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def report_task_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    keyboard_buttons = []
    keyboard_buttons.append(types.KeyboardButton(text='Назад'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def repeat_reported_task_keyboard(task_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.InlineKeyboardButton(text='Удалить задание', callback_data='delete_task+' + str(task_id)))
    keyboard.add(*keyboard_buttons)
    return keyboard


def price_list_keyboard(task_id):
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard_buttons = []
    keyboard_buttons.append(types.InlineKeyboardButton(text='I', callback_data='price+150+' + str(task_id)))
    keyboard_buttons.append(types.InlineKeyboardButton(text='II', callback_data='price+250+' + str(task_id)))
    keyboard_buttons.append(types.InlineKeyboardButton(text='III', callback_data='price+350+' + str(task_id)))
    keyboard_buttons.append(types.InlineKeyboardButton(text='IV', callback_data='price+500+' + str(task_id)))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Назад', callback_data='cancel_setting_cost+'+str(task_id)))
    keyboard.add(*keyboard_buttons)
    return keyboard

def list_of_paid_tasks_keyboard(tasks):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    for task in tasks:
        text_of_button = str(task[0])+': {} рублей'.format(str(task[1]))
        keyboard_buttons.append(types.InlineKeyboardButton(text=text_of_button, callback_data='paid_task+'+str(task[0])))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Назад', callback_data=('back_from_paid_tasks')))
    keyboard.add(*keyboard_buttons)
    return keyboard

def list_of_unpaid_tasks_keyboard(tasks):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    for task in tasks:
        text_of_button = str(task[0])+': {} рублей'.format(str(task[1]))
        keyboard_buttons.append(types.InlineKeyboardButton(text=text_of_button, callback_data='free_task+'+str(task[0])))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Назад', callback_data=('back_from_free_tasks')))
    keyboard.add(*keyboard_buttons)
    return keyboard

def send_message_to_solver(task_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(types.InlineKeyboardButton(text='Связаться с исполнителем', callback_data='ask_solver+' + str(task_id)))
    keyboard.add(*keyboard_buttons)
    return keyboard

def answer_clients_question(task_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard_buttons = []
    keyboard_buttons.append(
        types.InlineKeyboardButton(text='Ответить на вопрос', callback_data=f'send_answer+{str(task_id)}'))
    keyboard.add(*keyboard_buttons)
    return keyboard


def decision_of_client_keyboard(task_id):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard_buttons = []
    keyboard_buttons.append(types.InlineKeyboardButton(text='Оплатить', callback_data='pay+' + str(task_id)))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Пополнить баланс', callback_data='add_money'))
    keyboard_buttons.append(types.InlineKeyboardButton(text='Удалить задание', callback_data='delete_task+'+str(task_id)))
    keyboard.add(*keyboard_buttons)
    return keyboard