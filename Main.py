import telebot
from telebot import types
import logging
import time
import STATES as st
import database_queries as dq
import keyboards as kb
from api_token import API_TOKEN, yoomoney_token
import flask
import random
import string
from datetime import datetime
import inspect

bot = telebot.TeleBot(API_TOKEN, threaded=False)


# WEBHOOK_HOST = '194.67.105.41'
# WEBHOOK_PORT = 443  # 443, 80, 88 or 8443 (port need to be 'open')
# WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
#
# WEBHOOK_SSL_CERT = '/etc/ssl/danny/server.crt'  # Path to the ssl certificate
# WEBHOOK_SSL_PRIV = '/etc/ssl/danny/server.pass.key'  # Path to the ssl private key
#
# WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
# WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)
#
# logger = telebot.logger
# telebot.logger.setLevel(logging.INFO)
#
# app = flask.Flask(__name__)
#
#
# # Empty webserver index, return nothing, just http 200
# @app.route('/', methods=['GET', 'HEAD'])
# def index():
#     return ''
#
#
# # Process webhook calls
# @app.route(WEBHOOK_URL_PATH, methods=['POST'])
# def webhook():
#     if flask.request.headers.get('content-type') == 'application/json':
#         json_string = flask.request.get_data().decode('utf-8')
#         update = telebot.types.Update.de_json(json_string)
#         bot.process_new_updates([update])
#         return ''
#     else:
#         flask.abort(403)


# Если пользователь находится в черном списке - pass
@bot.message_handler(func=lambda message: dq.check_user_in_ban_list(message.chat.id))
def banned(message):
    pass


# При отправлении типов контента, не предусмотренных работой бота - pass
@bot.message_handler(content_types=['sticker', 'video', 'voice', 'document', 'video_note', 'location', 'contact',
                                    'left_chat_member', 'new_chat_title', 'new_chat_photo', 'delete_chat_photo',
                                    'group_chat_created', 'supergroup_chat_created', 'channel_chat_created',
                                    'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message'])
def wrong_type(message):
    pass


# Функция обрабатывает все фотографии. Сначала идет проверка, к какой группе принадлежит
# пользователь.
@bot.message_handler(content_types=['photo'])
def complete_photo_of_task(message):
    try:
        if dq.check_user_in_db(message.chat.id) == True:  # Если пользователь - заказчик
            if dq.get_state(message.chat.id) == st.HOMEWORK_TASK:  # Добавление фотографии во время составления заказа
                bot.send_message(message.chat.id, 'Оставьте комментарий к заявке')
                photo_id = bot.get_file(message.photo[-1].file_id).file_id
                dq.add_photo_of_problems(message.chat.id, photo_id)
                dq.set_state(message.chat.id, st.HOMEWORK_COMMENT)
            if dq.get_state(message.chat.id) == st.CHANGE_TASK:  # Замена фотографии составленного заказа
                photo_id = bot.get_file(message.photo[-1].file_id).file_id
                dq.add_photo_of_problems(message.chat.id, photo_id)
                send_full_task(message)
        if dq.check_solver_in_db(message.chat.id) == True:  # Если пользователь - менеджер
            if dq.get_solver_state(message.chat.id) == st.solver_SENDING_SOLUTION:
                photo = bot.get_file(message.photo[-1].file_id).file_id
                dq.add_photo_of_solution(message.chat.id, photo)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


# В случае, если пользователь не является ни клиентом, ни исполнителем - срабатывает команда /start
@bot.message_handler(func=lambda message: dq.check_user_in_db(message.chat.id) == False and dq.check_solver_in_db(
    message.chat.id) == False)
def add_unadded_user_in_db(message):
    try:
        welcome(message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


# При отправлении "ключа" регистрации менеджеров, пользователь удаляется из таблицы клиентов и
# добавляется в таблицу менеджеров, после чего генерируется новый "ключ"
# Если пользователь уже находился в таблице менеджеров - только генерируется новый код
@bot.message_handler(func=lambda message: message.text == dq.get_key_for_registration())
def solver_registration(message):
    try:
        # Регистрация
        if not dq.check_solver_in_db(message.chat.id):
            dq.add_solver_in_db(message.chat.id)
            bot.send_message(message.chat.id, 'Введите имя')
            if dq.check_user_in_db(message.chat.id):
                dq.delete_solver_from_user_db(message.chat.id)
            bot.register_next_step_handler(message, enter_solver_name)
        else:
            bot.send_message(message.chat.id, 'Привет, ' + dq.get_solver_name(message.chat.id),
                             reply_markup=kb.solver_menu_keyboard())
            if dq.check_user_in_db(message.chat.id):
                dq.delete_solver_from_user_db(message.chat.id)

        # Генерация ключа
        letters = string.ascii_lowercase
        random.seed(int(time.time()))
        key = ''.join(random.choice(letters) for i in range(20))
        dq.set_key_for_registration(key)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


# Функция добавляет имя менеджера в базу данных
def enter_solver_name(message):
    try:
        dq.set_solver_name(message.chat.id, message.text)
        bot.send_message(message.chat.id, 'Привет, ' + dq.get_solver_name(message.chat.id),
                         reply_markup=kb.solver_menu_keyboard())
        dq.set_solver_state(message.chat.id, st.solver_MAIN)
    except Exception as error:
        bot.send_message(message.chat.id, 'Имя введено неверно, повторите')
        bot.register_next_step_handler(message, enter_solver_name)


# Выбирается группа менеджеров, которым будет отправлено задание, после отправление
# номер группы, которая должна получить задание, инкрементируется. Информация об отправленных
# сообщениях заносится в БД для последующего удаления сообщения у всех менеджеров, кроме того,
# который принял задание
def send_task_to_solvers(task_id, from_client=True):
    try:
        text = dq.task_completed_message_for_solver(task_id)
        photo = dq.get_picture_of_task(task_id)
        group = dq.get_group_of_task(task_id)
        solvers = dq.get_solvers_from_selected_group(group)
        for solver in solvers:
            message_to_save = bot.send_photo(solver[0], photo, caption=text,
                                             reply_markup=kb.solver_task_keyboard(task_id, solver[0]))
            dq.save_sended_task(message_to_save.id, task_id, solver[0], group)
        if from_client == True:
            dq.increment_current_group()
    except Exception as error:
        dq.add_error_to_error_list(task_id.split('_')[0], str(inspect.stack()[0][3]), str(error))


# Функция активируется, когда менеджер принимает задание от клиента.
@bot.callback_query_handler(func=lambda call: 'accept' in call.data)
def accept_selected_task(call):
    try:
        task_id = call.data.split('+')[1]
        if dq.get_status_of_solution(task_id) == 0:
            dq.set_status_of_solution(task_id, 4)  # Статус задания - Ожидает подтверждения
            photo_of_task = dq.get_picture_of_task(task_id)
            solvers = dq.get_solvers_id()  # Список всех менеджеров
            for solver in solvers:
                # Если существует сообщение с данным заданием у данного менеджера, выполняется условие
                if dq.get_message_id(task_id, solver[0]) is not None:
                    message_id = dq.get_message_id(task_id, solver[0])
                    dq.task_message_deleted(message_id)
                    bot.delete_message(solver[0], message_id)
            # В бд у менеджера появляется
            dq.set_current_task(call.message.chat.id, task_id)
            bot.send_photo(call.message.chat.id, photo_of_task, caption='Выберите сложность данной задачи',
                           reply_markup=kb.price_list_keyboard(task_id))
            dq.set_task_solver_id(task_id, call.message.chat.id)
        elif dq.get_status_of_solution(task_id) == 4:
            bot.send_message(call.message.chat.id, 'Задание уже было взято')
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


# Для всех работников "Назад", для всех клиентов "🔙 Назад"
@bot.message_handler(func=lambda message: message.text == '🔙 Назад')
def client_back_steps(message):
    try:
        if dq.check_solver_in_db(message.chat.id) == False:
            if dq.get_state(message.chat.id) == st.MSG_TO_SUPPORT:
                dq.set_state(message.chat.id, st.MAIN)
                bot.send_message(message.chat.id, dq.print_account_info(message.chat.id),
                                 reply_markup=kb.menu_keyboard())

            elif dq.get_state(message.chat.id) == st.HOMEWORK_THEME:
                services(message)

            elif dq.get_state(message.chat.id) == st.SEND_MESSAGE_TO_SUPPORT:
                dq.set_state(message.chat.id, st.MAIN)
                bot.send_message(message.chat.id, dq.print_account_info(message.chat.id),
                                 reply_markup=kb.menu_keyboard())

            elif dq.get_state(message.chat.id) == st.ABOUT_US:
                bot.send_message(message.chat.id, dq.print_account_info(message.chat.id),
                                 reply_markup=kb.menu_keyboard())
                dq.set_state(message.chat.id, st.MAIN)

            elif dq.get_state(message.chat.id) == st.ACCOUNT:
                bot.send_message(message.chat.id, dq.print_account_info(message.chat.id),
                                 reply_markup=kb.menu_keyboard())
                dq.set_state(message.chat.id, st.MAIN)

            elif dq.get_state(message.chat.id) == st.SELECTED_TASK:
                dq.set_state(message.chat.id, st.LIST_OF_TASKS)
                show_list_of_tasks(message)

            elif dq.get_state(message.chat.id) == st.LIST_OF_TASKS:
                dq.set_state(message.chat.id, st.MAIN)
                welcome(message)

            elif dq.get_state(message.chat.id) == st.SERVICES:
                bot.send_message(message.chat.id, dq.print_account_info(message.chat.id),
                                 reply_markup=kb.menu_keyboard())
                dq.set_state(message.chat.id, st.MAIN)

            elif dq.get_state(message.chat.id) == st.SEND_AMOUNT:
                dq.set_state(message.chat.id, st.ACCOUNT)
                account(message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: 'price' in call.data)
def send_priced_task_to_user(call):
    try:
        task_id = call.data.split('+')[2]
        if dq.get_status_of_solution(task_id) == 4:
            price = call.data.split('+')[1]
            num_of_task = task_id.split('_')[1]
            user_id = task_id.split('_')[0]
            dq.set_status_of_solution(task_id, 3)
            dq.set_price_of_task(task_id, price)
            bot.send_message(call.message.chat.id, 'Цена предложена клиенту. Ожидаем ответа',
                             reply_markup=kb.solver_menu_keyboard())
            bot.delete_message(call.message.chat.id, call.message.id)
            photo = dq.get_picture_of_task(task_id)
            bot.send_photo(user_id, photo,
                           caption='Ваше задание №{} готовы решить за {} рублей'.format(str(int(num_of_task) + 1),
                                                                                        price),
                           reply_markup=kb.decision_of_client_keyboard(task_id))
        elif dq.get_status_of_solution(task_id) == 3:
            bot.send_message(call.message.chat.id, 'К сожалению, данное задание было выбрано одновременно двумя людьми')
            bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: 'pay' in call.data)
def pay_for_task(call):
    try:
        task_id = call.data.split('+')[1]
        if dq.check_task_id_db(task_id) == True:
            price_of_task = dq.get_price_of_task(task_id)
            user_id = task_id.split('_')[0]
            balance_of_user = dq.get_balance_of_user(user_id)
            if price_of_task <= balance_of_user:
                if dq.get_status_of_solution(task_id) == 3:
                    new_balance = balance_of_user - price_of_task
                    dq.set_balance_of_user(new_balance, user_id)
                    dq.set_status_of_solution(task_id, 5)
                    solver_id = dq.get_solver_of_task(task_id)
                    bot.send_message(call.message.chat.id,
                                     'Задание успешно оплачено. Менеджеры уже приступили к решению!')
                    bot.send_message(solver_id, 'Задание {} было оплачено, можно приступать!'.format(task_id),
                                     reply_markup=kb.solver_menu_keyboard())
                    bot.delete_message(call.message.chat.id, call.message.id)
                    dq.set_time_of_accept(task_id)
            else:
                bot.send_message(call.message.chat.id, 'Недостаточно средств. Пополните баланс.')
        else:
            bot.send_message(call.message.chat.id, 'Задание было удалено')
            bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text == 'Список оплаченных задач')
def send_task_list_to_solver(message):
    try:
        if dq.check_solver_in_db(message.chat.id):
            list_of_tasks = dq.get_list_of_paid_tasks(message.chat.id)
            now = datetime.now()
            bot.send_message(message.chat.id, 'Список заданий, к которым вы можете приступить',
                             reply_markup=kb.list_of_paid_tasks_keyboard(list_of_tasks, now))
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text == 'Список неоплаченных задач')
def send_task_of_unpaid_list_to_solver(message):
    try:
        if dq.check_solver_in_db(message.chat.id):
            list_of_tasks = dq.get_list_of_unpaid_tasks(message.chat.id)
            bot.send_message(message.chat.id, 'Список принятых, но неоплаченных задач за последние сутки',
                             reply_markup=kb.list_of_unpaid_tasks_keyboard(list_of_tasks))
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data == 'back_from_paid_tasks')
def back_from_list_of_paid_tasks(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.id)
        solver_stats(call.message)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data == 'back_from_free_tasks')
def back_from_list_of_paid_tasks(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.id)
        solver_stats(call.message)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: 'paid_task' in call.data)
def solve_choosed_task(call):
    try:
        task_id = call.data.split('+')[1]
        dq.set_solver_state(call.message.chat.id, st.solver_SOLVING)
        dq.set_current_task(call.message.chat.id, task_id)
        text = dq.task_completed_message_for_solver(task_id)
        photo_of_task = dq.get_picture_of_task(task_id)
        bot.send_photo(call.message.chat.id, photo_of_task, caption=text, reply_markup=kb.solving_keyboard())
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: 'free_task+' in call.data)
def choose_unpaid_task(call):
    try:
        task_id = call.data.split('+')[1]
        dq.set_solver_state(call.message.chat.id, st.solver_SOLVING)
        dq.set_current_task(call.message.chat.id, task_id)
        text = dq.task_completed_message_for_solver(task_id)
        photo_of_task = dq.get_picture_of_task(task_id)
        bot.send_photo(call.message.chat.id, photo_of_task, caption=text, reply_markup=kb.watch_unpaid_task_keyboard())
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: 'delete_task' in call.data)
def delete_selected_task(call):
    try:
        task_id = call.data.split('+')[1]
        if not dq.check_task_in_task_list(task_id):
            bot.send_message(call.message.chat.id, 'Заявка уже была удалена')
            bot.delete_message(call.message.chat.id, call.message.id)
        elif dq.get_status_of_solution(task_id) in [2, 3]:
            bot.send_message(call.message.chat.id, 'Заявка успешно удалена')
            task_id = call.data.split('+')[1]
            dq.delete_selected_task(task_id)
            bot.delete_message(call.message.chat.id, call.message.id)
        elif dq.get_status_of_solution(task_id) == 0:
            bot.send_message(call.message.chat.id, 'Задание невозможно удалить, так как оно уже было оплачено')
            bot.delete_message(call.message.chat.id, call.message.id)
        elif dq.get_status_of_solution(task_id) == 1:
            bot.send_message(call.message.chat.id, 'Задание невозможно удалить, так как оно уже готов')
            bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: 'report' in call.data and dq.get_solver_state(
    call.message.chat.id) != st.solver_SOLVING)
def report_selected_task(call):
    try:
        task_id = call.data.split('+')[1]
        bot.send_message(call.message.chat.id, 'Напишите, по какой причине нужно отменить данную заявку',
                         reply_markup=kb.report_task_keyboard())
        solvers_raw = dq.get_solvers_id()
        solvers = []
        for i in solvers_raw:
            solvers.append(i[0])
        for solver in solvers:
            if dq.get_message_id(task_id, solver) is not None:
                message_id = dq.get_message_id(task_id, solver)
                dq.task_message_deleted(message_id)
                bot.delete_message(solver, message_id)
        dq.set_solver_state(call.message.chat.id, st.solver_GET_REPORT_MESSAGE)
        dq.set_reporting_task(call.message.chat.id, call.data.split('+')[1])
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: 'rotate' in call.data)
def rotate_task_to_next_group(call):
    try:
        task_id = call.data.split('+')[1]
        bot.send_message(call.message.chat.id, 'Если вы уверены, что в вашей группе никто не сможет решить данную '
                                               'задачу - нажмите на кнопку "Отправить следующей группе"',
                         reply_markup=kb.rotation_keyboard())
        solvers_raw = dq.get_solvers_id()
        solvers = []
        for i in solvers_raw:
            solvers.append(i[0])
        for solver in solvers:
            if dq.get_message_id(task_id, solver) is not None:
                message_id = dq.get_message_id(task_id, solver)
                dq.task_message_deleted(message_id)
                bot.delete_message(solver, message_id)
        dq.set_solver_state(call.message.chat.id, st.solver_ROTATION)
        dq.set_rotating_task_id(call.message.chat.id, task_id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text == 'Отправить следующей группе' and dq.check_solver_in_db(
    message.chat.id) == True and dq.get_solver_state(
    message.chat.id) == st.solver_ROTATION)
def send_task_to_next_group(message):
    try:
        dq.set_solver_state(message.chat.id, st.MAIN)
        next_group = dq.get_num_of_next_group(dq.get_rotating_task_id(message.chat.id))
        dq.set_group_of_task(dq.get_rotating_task_id(message.chat.id), next_group)
        send_task_to_solvers(dq.get_rotating_task_id(message.chat.id), from_client=False)
        dq.set_rotating_task_id(message.chat.id, None)
        bot.send_message(message.chat.id, 'Задание успешно отправлено следующей группе',
                         reply_markup=kb.solver_menu_keyboard())
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text == 'Назад' and dq.check_solver_in_db(
    message.chat.id) == True and dq.get_solver_state(
    message.chat.id) == st.solver_ROTATION)
def rotate_selected_task_back(message):
    try:
        dq.set_solver_state(message.chat.id, st.solver_MAIN)
        solver_stats(message)
        send_task_to_solvers(dq.get_rotating_task_id(message.chat.id), from_client=False)
        dq.set_rotating_task_id(message.chat.id, None)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text == 'Назад' and dq.check_solver_in_db(
    message.chat.id) == True and dq.get_solver_state(
    message.chat.id) == st.solver_GET_REPORT_MESSAGE)
def report_selected_task_back(message):
    try:
        dq.set_solver_state(message.chat.id, st.solver_MAIN)
        solver_stats(message)
        send_task_to_solvers(dq.get_reporting_task(message.chat.id), from_client=False)
        dq.set_reporting_task(message.chat.id, None)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == True and dq.get_solver_state(
    message.chat.id) == st.solver_GET_REPORT_MESSAGE and message.text != 'Назад')
def send_report_to_user(message):
    try:
        task_id = dq.get_reporting_task(message.chat.id)
        if dq.get_status_of_solution(task_id) != 2:
            dq.report_task(task_id)
            dq.set_report_text(task_id, message.text)
            user_id = task_id.split('_')[0]
            bot.send_message(message.chat.id, 'Отмена произошла успешно, пользователь оповещен',
                             reply_markup=kb.solver_menu_keyboard())
            dq.set_solver_state(message.chat.id, st.solver_MAIN)
            dq.set_reporting_task(message.chat.id, None)
            number_of_task = int(task_id.split('_')[1])
            bot.send_message(user_id, 'Ваше задание №{} не было принято по следующей причине: '.format(
                str(number_of_task + 1)) + message.text,
                             reply_markup=kb.repeat_reported_task_keyboard(task_id))
        else:
            bot.send_message(message.chat.id, 'Задание уже было отменено')
            dq.set_solver_state(message.chat.id, st.solver_MAIN)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: 'cancel_setting_cost' in call.data)
def stop_solving(call):
    try:
        task_id = call.data.split('+')[1]
        send_task_to_solvers(task_id, from_client=False)
        dq.set_status_of_solution(task_id, 0)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data == 'back_from_solving')
def go_back_from_solving_task(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.id)
        list_of_tasks = dq.get_list_of_paid_tasks(call.message.chat.id)
        now = datetime.now()
        bot.send_message(call.message.chat.id, 'Список заданий, к которым вы можете приступить',
                         reply_markup=kb.list_of_paid_tasks_keyboard(list_of_tasks, now))
        dq.set_solver_state(call.message.chat.id, st.solver_MAIN)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data == 'back_from_watching_free_task')
def go_back_from_watching_unpaid_task(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.id)
        list_of_tasks = dq.get_list_of_unpaid_tasks(call.message.chat.id)
        bot.send_message(call.message.chat.id, 'Список принятых, но неоплаченных задач за последние сутки',
                         reply_markup=kb.list_of_unpaid_tasks_keyboard(list_of_tasks))
        dq.set_solver_state(call.message.chat.id, st.solver_MAIN)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data == 'send_solution')
def get_photos_of_solution(call):
    try:
        bot.send_message(call.message.chat.id, 'Отправляйте фотографии по одной, в конце нажмите на кнопку "Завершить"',
                         reply_markup=kb.sending_photos_of_solution_keyboard())
        dq.set_solver_state(call.message.chat.id, st.solver_SENDING_SOLUTION)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text == 'Отмена' and dq.check_solver_in_db(message.chat.id) and
                                          dq.get_solver_state(message.chat.id) == st.solver_SENDING_SOLUTION)
def cancel_sending_photos_of_solution(message):
    try:
        task_id = dq.get_current_task(message.chat.id)
        dq.delete_all_photos_of_solution(task_id)
        dq.set_current_task(message.chat.id, None)
        dq.set_solver_state(message.chat.id, st.solver_MAIN)
        send_task_list_to_solver(message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text.lower() == 'завершить' and dq.check_solver_in_db(
    message.chat.id) == True and dq.get_solver_state(
    message.chat.id) == st.solver_SENDING_SOLUTION and message.text != None)
def end_solution_sending(message):
    try:
        task_id = dq.get_current_task(message.chat.id)
        num_of_photos = dq.get_num_of_sended_photos(task_id)
        if num_of_photos != 0:
            bot.send_message(message.chat.id, 'Решение успешно отправлено', reply_markup=kb.solver_menu_keyboard())
            dq.set_current_task(message.chat.id, None)
            dq.refresh_num_of_sended_photos(message.chat.id)
            dq.set_solver_state(message.chat.id, st.MAIN)
            user_id = task_id.split('_')[0]
            dq.set_status_of_solution(task_id, 1)
            dq.set_solution_time(task_id)
            dq.set_task_solver_id(task_id, message.chat.id)
            task_number = int(task_id.split('_')[1]) + 1
            bot.send_message(user_id,
                             'Задание №{} готово. Решение вы сможете найти во вкладке "Аккаунт"'.format(
                                 str(task_number)),
                             disable_notification=False)
            dq.add_solver_profit_made(message.chat.id, int(dq.get_price_of_task(task_id)) // 2)
        else:
            bot.send_message(message.chat.id,
                             'Не было отправлено ни одной фотографии. Отправьте решение и после этого нажмите "Завершить"')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(
    func=lambda message: message.text == 'Статистика' and dq.check_solver_in_db(message.chat.id) == True)
def solver_stats(message):
    try:
        task_list = dq.get_today_solutions_of_solver(message.chat.id)
        num_of_tasks = len(task_list)
        today_amount = 0
        if not (task_list is None):
            for i in task_list:
                today_amount += i[0] / 2
        bot.send_message(message.chat.id,
                         'Количество выполненных заданий: {} \nСегодняшняя зарплата: {}'.format(num_of_tasks,
                                                                                                today_amount),
                         reply_markup=kb.solver_menu_keyboard())
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


# USER REGISGRATION

@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        if dq.check_solver_in_db(message.chat.id) == False:
            if dq.check_user_in_db(message.chat.id) == False:
                bot.send_message(message.chat.id, 'Привет, как тебя зовут? 👨🏻‍💻')
                dq.add_client(message.chat.id)
                dq.set_state(message.chat.id, st.ENTER_NAME)
            else:
                if type(dq.get_name(message.chat.id)) == str:
                    bot.send_message(message.chat.id, 'Привет, ' + dq.get_name(message.chat.id),
                                     reply_markup=kb.menu_keyboard())
                    dq.set_state(message.chat.id, st.MAIN)
                else:
                    bot.send_message(message.chat.id, 'Привет, как тебя зовут? 👨🏻‍💻')
                    dq.set_state(message.chat.id, st.ENTER_NAME)
        if dq.check_solver_in_db(message.chat.id) == True:
            if dq.check_solver_in_db(message.chat.id):
                bot.send_message(message.chat.id, 'Привет, ' + dq.get_solver_name(message.chat.id),
                                 reply_markup=kb.solver_menu_keyboard())
                dq.set_solver_state(message.chat.id, st.solver_MAIN)
            else:
                dq.add_solver_in_db(message.chat.id)
                dq.set_solver_state(message.chat.id, st.solver_REGISTRATION)
                bot.send_message(message.chat.id, 'Введите имя')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: dq.check_user_in_db(message.chat.id) and dq.get_state(
    message.chat.id) == st.ENTER_NAME)
def enter_name(message):
    try:
        dq.set_name(message.chat.id, message.text)
        bot.send_message(message.chat.id, 'Привет, ' + dq.get_name(message.chat.id), reply_markup=kb.menu_keyboard())
        dq.set_state(message.chat.id, st.MAIN)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: dq.check_user_in_db(message.chat.id) and dq.get_state(
    message.chat.id) == st.CHANGE_NAME)
def change_name(message):
    try:
        dq.set_name(message.chat.id, message.text)
        bot.send_message(message.chat.id, dq.get_name(message.chat.id) + ', имя успешно изменено!',
                         reply_markup=kb.menu_keyboard())
        dq.set_state(message.chat.id, st.MAIN)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


# Support
@bot.message_handler(func=lambda message: message.text == '❓ Техподдержка' and dq.check_user_in_db(
    message.chat.id) and dq.get_state(
    message.chat.id) == st.MAIN)
def support_info(message):
    try:
        bot.send_message(message.chat.id,
                         'Если у вас возникли вопросы, связанные с выполненным заказом или работой с ботом - '
                         'смело пишите их прямо сюда.\n\nМы ответим вам как можно скорее!'
                         , reply_markup=kb.how_it_words())
        dq.set_state(message.chat.id, st.SEND_MESSAGE_TO_SUPPORT)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: dq.check_user_in_db(message.chat.id) and
                                          dq.get_state(message.chat.id) == st.SEND_MESSAGE_TO_SUPPORT)
def message_text_to_support(message):
    try:
        if message.text != '🔙 Назад':
            bot.send_message(message.chat.id, 'Ваш запрос принят! \nСовсем скоро вам ответят :)',
                             reply_markup=kb.menu_keyboard())
            bot.send_message(304987403,
                             'SUPPORT MESSAGE FROM USER {}\nMESSAGE_TEXT:\n{}'.format(message.chat.id, message.text))
            dq.add_message_to_support(message.chat.id, message.text)
            dq.set_state(message.chat.id, st.MAIN)
        else:
            account(message)

    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


# About us
@bot.message_handler(func=lambda message: message.text == '👋 О нас' and dq.check_user_in_db(
    message.chat.id) == True and dq.get_state(
    message.chat.id) == st.MAIN)
def about_us_info(message):
    try:
        bot.send_message(message.chat.id, 'Привет, студент 🤓\n\n'
                                          'Дедлайны горят, а задание не готово? Надоели недобросовестные исполнители?\n\n'
                                          'Мы готовы решить для тебя любую математическую задачу - алгебра, дискретная математика '
                                          'или матанализ для нас не проблема 👨🏻‍🎓\n\n'
                                          'Достаточно оставить заявку и Вы получите ответ в течение 10 минут!\n\n'
                                          'Главные преимущества MathHelper - децентрализация, скорость и удобство!\n\n'
                                          'Отправка задания, подтверждение, оплата - всё в одном месте. Получить готовое решение '
                                          'легче, чем заказать еду 🍕\n\n'
                                          'Обратная связь - @dannysmirnov', reply_markup=kb.about_us_keyboard())
        dq.set_state(message.chat.id, st.ABOUT_US)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text == 'ℹ️ Как работает бот?' and dq.check_user_in_db(
    message.chat.id) == True and dq.get_state(
    message.chat.id) == st.ABOUT_US)
def how_it_words(message):
    try:
        bot.send_message(message.chat.id, 'Работа с ботом происходит предельно просто:\n\n'
                                          '1) Вы оставляете заявку, указывая тему и прикрепляя фотографию задачи\n'
                                          '2) Мы обрабатываем заявку и присылаем Вам подтверждение с ценой, предложенной исполнителем\n'
                                          '3) Вы производите оплату и подтверждаете заявку\n'
                                          '4) Наш исполнитель начинает работу и отправляет вам решение в кратчайшие сроки\n\n'
                                          '⏱ Средняя скорость обработки одной заявки составляет 10 минут'
                         , reply_markup=kb.about_us_keyboard())
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


# Account
@bot.message_handler(
    func=lambda message: message.text == '📄 Аккаунт' and dq.check_user_in_db(message.chat.id) == True and dq.get_state(
        message.chat.id) == st.MAIN)
def account(message):
    try:
        bot.send_message(message.chat.id, 'Здесь вы можете проверить историю своих заявок и пополнить баланс',
                         reply_markup=kb.account_keyboard())
        dq.set_state(message.chat.id, st.ACCOUNT)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: 'page_' in call.data)
def select_page(call):
    page = int(call.data.replace('page_', ''))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                  reply_markup=kb.set_of_tasks_keyboard(dq.select_set_of_task(call.message.chat.id),
                                                                        page))


@bot.message_handler(func=lambda message: message.text == '📍 История заявок' and dq.check_user_in_db(
    message.chat.id) == True and dq.get_state(
    message.chat.id) == st.ACCOUNT)
def show_list_of_tasks(message):
    try:
        bot.send_message(message.chat.id, '📄 История заданий',
                         reply_markup=kb.set_of_tasks_keyboard(dq.select_set_of_task(message.chat.id)))
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: 'task_' in call.data)
def open_selected_task(call):
    try:
        task_id = call.data.replace('task_', '')
        if dq.check_task_id_db(task_id):
            photo_of_task = dq.get_picture_of_task(task_id)
            task = dq.select_task(task_id)
            if task[1] == 1:
                photos = dq.get_all_photos_of_solution(task_id)
                array_of_photos = []
                for i in range(len(photos) - 1):
                    array_of_photos.append(types.InputMediaPhoto(media=photos[i][0]))
                array_of_photos.append(types.InputMediaPhoto(media=photos[len(photos) - 1][0], caption='Решение'))
                solver_id = dq.get_solver_of_task(task_id)
                bot.send_photo(call.message.chat.id, photo_of_task, caption='Задание')
                if len(array_of_photos) <= 10:
                    bot.send_media_group(call.message.chat.id, array_of_photos)
                else:
                    while len(array_of_photos) > 10:
                        send_ten_photos = array_of_photos[:10]
                        array_of_photos = array_of_photos[10:]
                        bot.send_media_group(call.message.chat.id, send_ten_photos)
                    bot.send_media_group(call.message.chat.id, array_of_photos)

                bot.send_message(call.message.chat.id,
                                 'Если у вас остались вопросы по решению, вы можете задать их исполнителю'
                                 , reply_markup=kb.send_message_to_solver(task_id))

            if task[1] == 0:
                bot.send_photo(call.message.chat.id, photo_of_task, caption='Заявку скоро проверят')
            if task[1] == 2:
                text_of_report = dq.get_report_text(task_id)
                number_of_task = int(task_id.split('_')[1])
                bot.send_photo(call.message.chat.id, photo_of_task, caption=
                'Ваше задание №{} не было принято по следующей причине: '.format(str(
                    number_of_task + 1)) + text_of_report + '\n\nУдалите задание и заполните заново',
                               reply_markup=kb.repeat_reported_task_keyboard(task_id))
            if task[1] == 3:
                price = dq.get_price_of_task(task_id)
                num_of_task = task_id.split('_')[1]
                bot.send_photo(call.message.chat.id, photo_of_task, caption=
                'Ваше задание №{} готовы решить за {} рублей'.format(str(int(num_of_task) + 1), price),
                               reply_markup=kb.decision_of_client_keyboard(task_id))
            if task[1] == 5:
                photo = dq.get_picture_of_task(task_id)
                bot.send_photo(call.message.chat.id, photo, caption='Задание скоро будет выполнено')
        else:
            bot.send_message(call.message.chat.id, 'Задание было удалено')

    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: 'ask_solver' in call.data)
def send_question_to_solver(call):
    try:
        bot.send_message(call.message.chat.id,
                         'Напишите одним сообщением, какие именно вопросы у вас остались по заданию.\n\n'
                         'Ответ от исполнителя появится в этом же чате в ближайшее время',
                         reply_markup=kb.how_it_words())
        task_id = call.data.replace('ask_solver+', '')
        dq.set_question_task_id(call.message.chat.id, task_id)
        bot.register_next_step_handler(call.message, enter_question_to_solver)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


def enter_question_to_solver(message):
    try:
        if message.text == '🔙 Назад':
            account(message)
        else:
            task_id = dq.get_question_task_id(message.chat.id)
            solver_id = dq.get_solver_of_task(task_id)
            photo_of_task = dq.get_picture_of_task(task_id)
            photos_of_solution = dq.get_all_photos_of_solution(task_id)
            array_of_photos = []
            array_of_photos.append(types.InputMediaPhoto(media=photo_of_task))
            for i in range(len(photos_of_solution) - 1):
                array_of_photos.append(types.InputMediaPhoto(media=photos_of_solution[i][0]))
            array_of_photos.append(
                types.InputMediaPhoto(media=photos_of_solution[len(photos_of_solution) - 1][0], caption=message.text))
            if len(array_of_photos) <= 10:
                bot.send_media_group(solver_id, array_of_photos)
            else:
                while len(array_of_photos) > 10:
                    send_ten_photos = array_of_photos[:10]
                    array_of_photos = array_of_photos[10:]
                    bot.send_media_group(solver_id, send_ten_photos)
                bot.send_media_group(solver_id, array_of_photos)
            bot.send_message(solver_id, 'ВНИМАНИЕ, ВОПРОС\n\nОтветьте на него так, чтобы клиенту все было понятно',
                             reply_markup=kb.answer_clients_question(task_id))
            bot.send_message(message.chat.id, 'Вопрос успешно доставлен. Скоро вам ответят',
                             reply_markup=kb.account_keyboard())
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: 'send_answer' in call.data)
def send_answer_to_user(call):
    try:
        bot.send_message(call.message.chat.id, 'Напишите ответ одним сообщением, ответьте на все поставленные вопросы',
                         reply_markup=kb.report_task_keyboard())
        task_id = call.data.replace('send_answer+', '')
        dq.set_answer_task_id(call.message.chat.id, task_id)
        bot.register_next_step_handler(call.message, enter_answer_to_user)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


def enter_answer_to_user(message):
    try:
        if message.text == 'Назад':
            solver_stats(message)
            dq.set_solver_state(message.chat.id, st.solver_MAIN)
        else:
            task_id = dq.get_answer_task_id(message.chat.id)
            user_id = task_id.split('_')[0]
            photos_of_solution = dq.get_all_photos_of_solution(task_id)
            array_of_photos = []
            for i in range(len(photos_of_solution) - 1):
                array_of_photos.append(types.InputMediaPhoto(media=photos_of_solution[i][0]))
            array_of_photos.append(
                types.InputMediaPhoto(media=photos_of_solution[len(photos_of_solution) - 1][0],
                                      caption='Ответ на ваш вопрос:\n\n' + message.text))
            if len(array_of_photos) <= 10:
                bot.send_media_group(user_id, array_of_photos)
            else:
                while len(array_of_photos) > 10:
                    send_ten_photos = array_of_photos[:10]
                    array_of_photos = array_of_photos[10:]
                    bot.send_media_group(user_id, send_ten_photos)
                bot.send_media_group(user_id, array_of_photos)
            bot.send_message(message.chat.id, 'Ответ успешно отправлен', reply_markup=kb.solver_menu_keyboard())
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text == 'Перейти в меню' and dq.check_solver_in_db(
    message.chat.id) == False and dq.get_state(
    message.chat.id) == st.SELECTED_TASK)
def back_to_menu(message):
    try:
        dq.set_state(message.chat.id, st.MAIN)
        welcome(message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


# Services
@bot.message_handler(func=lambda message: message.text == '📕 Услуги' and dq.check_solver_in_db(
    message.chat.id) == False and dq.get_state(
    message.chat.id) == st.MAIN)
def services(message):
    try:
        dq.set_state(message.chat.id, st.SERVICES)
        bot.send_message(message.chat.id, 'Чтобы отправить нам вашу задачу, нажмите на кнопку "Оставить заявку"\n'
                                          'Заполните форму по инструкции и ждите ответа в ближайшее время!\n\n'
                                          'В настоящий момент можно отправлять задания только по одному, '
                                          'в ином случае заявка будет отклонена',
                         reply_markup=kb.services_keyboard())
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


# Homework

# @bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
#     message.chat.id) == st.SERVICES and message.text == '📍 Оставить заявку')
# def create_task(message):
#     try:
#         bot.send_message(message.chat.id, 'Введите количество заданий',
#                          reply_markup=telebot.types.ReplyKeyboardRemove())
#         dq.create_task_id(message.chat.id)
#         dq.set_state(message.chat.id, st.HOMEWORK_NUMBER)
#     except Exception as error:
#         bot.send_message(message.chat.id,
#                          'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!'+str(inspect.stack()[0][3]))
#
#
# def check_isdigit(message):
#     if type(message) == str:
#         if str.isdigit(message) == True:
#             return True
#     return False


@bot.message_handler(func=lambda message: message.text == '📍 Оставить заявку' and dq.check_solver_in_db(
    message.chat.id) == False and dq.get_state(
    message.chat.id) == st.SERVICES)
def complete_num_of_task(message):
    try:
        bot.send_message(message.chat.id, 'Введите тему задания',
                         reply_markup=kb.how_it_words())
        dq.create_task_id(message.chat.id)
        dq.set_state(message.chat.id, st.HOMEWORK_THEME)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


# @bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
#     message.chat.id) == st.HOMEWORK_NUMBER and not check_isdigit(message.text))
# def incomplete_num_of_task(message):
#     bot.send_message(message.chat.id, 'Неверный ввод, введите количество заданий')

@bot.message_handler(func=lambda message: dq.check_user_in_db(message.chat.id) == True and dq.get_state(
    message.chat.id) == st.HOMEWORK_THEME)
def complete_theme_of_task(message):
    try:
        if message.text != '🔙 Назад':
            if message.text != None:
                bot.send_message(message.chat.id, 'Отправьте фотографию задания',
                                 reply_markup=types.ReplyKeyboardRemove())
                dq.add_theme_of_problems(message.chat.id, message.text)
                dq.set_state(message.chat.id, st.HOMEWORK_TASK)
            else:
                bot.send_message(message.chat.id, 'Произошла ошибка. Введите тему задания еще раз')
        else:
            services(message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


# @bot.callback_query_handler(func=lambda call: dq.check_solver_in_db(call.message.chat.id) == False and dq.get_state(
#     call.message.chat.id) == st.HOMEWORK_DIFFICULT)
# def complete_difficulty_of_task(call):
#     try:
#
#         bot.send_message(call.message.chat.id, 'Выбрана сложность: ' + str(call.data) + ', отправьте фото задания')
#         dq.add_difficulty_of_problems(call.message.chat.id, call.data)
#         dq.set_state(call.message.chat.id, st.HOMEWORK_TASK)
#     except Exception as error:
#         bot.send_message(call.message.chat.id,
#                          'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!'+str(inspect.stack()[0][3]))


def send_full_task(message):
    try:
        dq.set_state(message.chat.id, st.CHECKING_TASK)
        task_id = dq.get_current_task_id(message.chat.id)
        text_of_task = dq.task_completed_message(message.chat.id)
        bot.send_photo(message.chat.id, dq.get_photo_of_problems(message.chat.id), caption=text_of_task,
                       reply_markup=kb.change_task_keyboard(task_id))
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: dq.check_user_in_db(message.chat.id) == True and dq.get_state(
    message.chat.id) == st.HOMEWORK_COMMENT)
def complete_comment_of_task(message):
    try:
        dq.add_comment_of_problems(message.chat.id, message.text)
        send_full_task(message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data == 'num_of_tasks')
def change_num_of_tasks(call):
    try:
        bot.send_message(call.message.chat.id, 'Введите количество заданий')
        dq.set_state(call.message.chat.id, st.CHANGE_NUMBER)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.CHANGE_NUMBER and str.isdigit(message.text))
def set_changed_num_of_tasks(message):
    try:
        dq.add_number_of_problems(message.chat.id, message.text)
        send_full_task(message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.CHANGE_NUMBER and not str.isdigit(message.text))
def set_changed_num_of_tasks(message):
    try:
        bot.send_message(message.chat.id, 'Неверный ввод, введите количество заданий')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data.split('+')[0] == 'theme_of_task')
def change_theme_of_tasks(call):
    try:
        bot.send_message(call.message.chat.id, 'Введите тему задания')
        dq.set_state(call.message.chat.id, st.CHANGE_THEME)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.CHANGE_THEME)
def set_changed_theme_of_tasks(message):
    try:
        dq.add_theme_of_problems(message.chat.id, message.text)
        send_full_task(message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data == 'difficult_of_task')
def change_difficult_of_tasks(call):
    try:
        bot.send_message(call.message.chat.id, 'Выберите сложность задания', reply_markup=kb.difficulty_keyboard())
        dq.set_state(call.message.chat.id, st.CHANGE_DIFFICULT)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: dq.check_solver_in_db(call.message.chat.id) == False and dq.get_state(
    call.message.chat.id) == st.CHANGE_DIFFICULT)
def set_changed_difficult_of_tasks(call):
    try:
        dq.add_difficulty_of_problems(call.message.chat.id, call.data)
        send_full_task(call.message)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data.split('+')[0] == 'photo_of_task')
def change_photo_of_tasks(call):
    try:
        bot.send_message(call.message.chat.id, 'Отправьте фото задания')
        dq.set_state(call.message.chat.id, st.CHANGE_TASK)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data.split('+')[0] == 'comment_of_task')
def change_comment_of_tasks(call):
    try:
        bot.send_message(call.message.chat.id, 'Оставьте комментарий к заявке')
        dq.set_state(call.message.chat.id, st.CHANGE_COMMENT)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.CHANGE_COMMENT)
def set_changed_comment_of_tasks(message):
    try:
        dq.add_comment_of_problems(message.chat.id, message.text)
        send_full_task(message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data.split('+')[0] == 'complete_task')
def completed_task(call):
    try:
        bot.send_message(call.message.chat.id, 'Ваша заявка принята, ожидайте ее подтверждения',
                         reply_markup=kb.menu_keyboard())
        task_id = dq.complete_task(call.message.chat.id)
        num_of_group = dq.get_current_group()
        dq.set_group_of_task(task_id, num_of_group)
        send_task_to_solvers(task_id)
        dq.set_state(call.message.chat.id, st.MAIN)
        bot.delete_message(call.message.chat.id, call.message.id)

    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка при отправке заявки. Введите команду /start и заполните заявку заново')
        bot.delete_message(call.message.chat.id, call.message.id)
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data.split('+')[0] == 'deny_task')
def cancel_the_task(call):
    try:
        dq.set_state(call.message.chat.id, st.SERVICES)
        bot.delete_message(call.message.chat.id, call.message.id)
        services(call.message)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка при отправке заявки. Введите команду /start и заполните заявку заново')
        bot.delete_message(call.message.chat.id, call.message.id)
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


# Add money

@bot.callback_query_handler(
    func=lambda call: dq.check_solver_in_db(call.message.chat.id) == False and call.data == 'add_money')
def callback_add_money(call):
    try:
        add_money(call.message)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(
    func=lambda message: message.text == '💰 Пополнить баланс' and dq.check_solver_in_db(
        message.chat.id) == False and dq.get_state(message.chat.id) in [
                             st.SERVICES, st.ACCOUNT])
def add_money(message):
    try:
        bot.send_message(message.chat.id, 'Минимальный платеж составляет 100 рублей\n\n'
                                          'На какую сумму вы хотите пополнить ваш баланс?',
                         reply_markup=kb.how_it_words())
        dq.set_state(message.chat.id, st.SEND_AMOUNT)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


def check_isdigit(message):
    if type(message) == str:
        if str.isdigit(message) == True:
            return True
    return False


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.SEND_AMOUNT)
def send_recipies(message):
    try:
        if check_isdigit(message.text):
            amount = int(message.text) * 100
            labeled_price = types.LabeledPrice('Руб', amount)
            if amount < 10000:
                bot.send_message(message.chat.id, 'Минимальная сумма платежа - 100 рублей')
            elif amount > 1000000:
                bot.send_message(message.chat.id, 'Максимальная сумма платежа - 10000')
            elif 10000 <= amount <= 1000000:
                bot.send_invoice(chat_id=message.chat.id,
                                 title='Пополнение счета',
                                 description='Пополнение счета в боте MathHelpersBot',
                                 invoice_payload='true',
                                 provider_token=yoomoney_token,
                                 currency='RUB',
                                 prices=[types.LabeledPrice(label='Rub', amount=amount)],
                                 start_parameter='add_money',
                                 is_flexible=False)
        else:
            bot.send_message(message.chat.id, 'Неверная сумма платежа')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    try:
        bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                      error_message="Ошибка при проведении оплаты")
    except Exception as error:
        dq.add_error_to_error_list('checkout', str(inspect.stack()[0][3]), str(error))


@bot.message_handler(content_types=['successful_payment'])
def add_amount_to_user(message):
    try:
        bot.send_message(message.chat.id,
                         'Оплата на {} рублей прошла успешно'.format(message.successful_payment.total_amount / 100),
                         reply_markup=kb.menu_keyboard())
        dq.add_money_to_user(message.chat.id, int(int(message.successful_payment.total_amount) / 100))
        dq.set_state(message.chat.id, st.MAIN)
        dq.add_payment_in_database(message.chat.id, int(int(message.successful_payment.total_amount) / 100))
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: 'admin' in message.text and message.chat.id == 304987403)
def send_message_to_user_with_admin(message):
    try:
        user_id = message.text.split()[1]
        text = message.text.replace('admin {} '.format(user_id), '')
        bot.send_message(user_id, 'Ответ от администрации:\n' + text, disable_notification=True)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text.lower() == 'last5' and message.chat.id == 304987403)
def get_last_five_users(message):
    try:
        list = dq.get_last_five_users()
        text = ''
        for i in list:
            text += str(i) + '\n'
        bot.send_message(message.chat.id, text)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(
    func=lambda message: message.text.split()[0].lower() == 'addmoney' and message.chat.id == 304987403)
def admin_add_money(message):
    try:
        user_id = message.text.split()[1]
        amount = message.text.split()[2]
        if dq.check_user_in_db(user_id):
            dq.add_money_to_user(user_id, int(amount))
        else:
            bot.send_message(message.chat.id, 'User not in db')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text.lower() == 'key' and message.chat.id == 304987403)
def get_registration_key(message):
    try:
        bot.send_message(message.chat.id, dq.get_key_for_registration())
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text.lower() == 'solvers' and message.chat.id == 304987403)
def get_list_of_solvers(message):
    try:
        list = dq.get_list_of_solvers()
        text = ''
        for i in list:
            text += str(i) + '\n'
        bot.send_message(message.chat.id, text)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text.lower() == 'stats' and message.chat.id == 304987403)
def get_stats_of_solvers(message):
    try:
        list = dq.get_list_of_solvers()
        text = ''
        for i in list:
            today = dq.get_today_solutions_of_solver(i[1])
            yesterday = dq.get_yesterday_solutions_of_solver(i[1])
            today_amount = 0
            yesterday_amount = 0
            if not (today is None):
                for j in today:
                    today_amount += j[0]
            if not (yesterday is None):
                for j in yesterday:
                    yesterday_amount += j[0]
            text += str(i[0]) + ': сегодня - ' + str(today_amount) + ', вчера - ' + str(yesterday_amount) + '\n'
        bot.send_message(message.chat.id, text)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text.split()[0].lower() == 'ban' and message.chat.id == 304987403)
def ban_user(message):
    try:
        dq.add_user_to_ban_list(message.text.split()[1])
        bot.send_message(message.chat.id, 'User has been banned')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text.split()[0].lower() == 'unban' and message.chat.id == 304987403)
def ban_user(message):
    try:
        dq.remove_user_to_ban_list(message.text.split()[1])
        bot.send_message(message.chat.id, 'User has been unbanned')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text.lower() == 'new users today' and message.chat.id == 304987403)
def users_came_today(message):
    try:
        bot.send_message(message.chat.id, str(dq.count_today_users()))
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text.lower() == 'on balance' and message.chat.id == 304987403)
def reserved_money(message):
    try:
        bot.send_message(message.chat.id, str(dq.money_on_user_balances()))
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text.lower() == 'today payments' and message.chat.id == 304987403)
def today_payments(message):
    try:
        bot.send_message(message.chat.id, str(dq.today_payments()))
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: 'set group' in message.text.lower() and message.chat.id == 304987403)
def set_num_of_group(message):
    try:
        solver_id = message.text.split()[2]
        num_of_group = message.text.split()[3]
        dq.set_solver_group(solver_id, num_of_group)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: 'show' in message.text.lower() and message.chat.id == 304987403)
def show_task_id(message):
    try:
        task_id = message.text.lower().replace('show ', '')
        open_solution_of_selected_task(task_id, message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


def open_solution_of_selected_task(task_id, message):
    try:
        if dq.check_task_id_db(task_id):
            photo_of_task = dq.get_picture_of_task(task_id)
            task = dq.select_task(task_id)
            if task[1] == 1:
                photos = dq.get_all_photos_of_solution(task_id)
                array_of_photos = []
                for i in range(len(photos) - 1):
                    array_of_photos.append(types.InputMediaPhoto(media=photos[i][0]))
                array_of_photos.append(types.InputMediaPhoto(media=photos[len(photos) - 1][0], caption='Решение'))
                solver_id = dq.get_solver_of_task(task_id)
                name = dq.get_solver_name(solver_id)
                price = dq.get_price_of_task(task_id)
                bot.send_photo(message.chat.id, photo_of_task, caption=f'{name} решил задание за {price} рублей')
                if len(array_of_photos) <= 10:
                    bot.send_media_group(message.chat.id, array_of_photos)
                else:
                    while len(array_of_photos) > 10:
                        send_ten_photos = array_of_photos[:10]
                        array_of_photos = array_of_photos[10:]
                        bot.send_media_group(message.chat.id, send_ten_photos)
                    bot.send_media_group(message.chat.id, array_of_photos)
            if task[1] == 0:
                bot.send_photo(message.chat.id, photo_of_task, caption='Заявка еще не была принята')
            if task[1] == 2:
                text_of_report = dq.get_report_text(task_id)
                bot.send_photo(message.chat.id, photo_of_task,
                               caption='Заявка была удалена по причине:\n\n' + text_of_report)
            if task[1] == 3:
                price = dq.get_price_of_task(task_id)
                solver_id = dq.get_solver_of_task(task_id)
                name = dq.get_solver_name(solver_id)
                bot.send_photo(message.chat.id, photo_of_task, caption=
                f'{name} принял это задание за {price} рублей')
            if task[1] == 5:
                photo = dq.get_picture_of_task(task_id)
                solver_id = dq.get_solver_of_task(task_id)
                name = dq.get_solver_name(solver_id)
                bot.send_photo(message.chat.id, photo, caption=f'{name} выполняет заказ')
        else:
            bot.send_message(message.chat.id, 'Задание было удалено')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text.split()[0] == 'solved' and message.chat.id == 304987403)
def watch_solver_account(message):
    try:
        solver_id = message.text.split()[2]
        tasks = dq.get_list_of_solved_task(solver_id)
        bot.send_message(message.chat.id, 'Решенные задания', reply_markup=kb.list_of_completed_tasks_keyboard(tasks))
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data == 'completed_close')
def close_completed_tasks(call):
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=lambda call: 'completed+' in call.data)
def open_completed_task(call):
    try:
        task_id = call.data.split('+')[1]
        open_solution_of_selected_task(task_id, call.message)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.message_handler(func=lambda message: message.text.split()[0] == 'unsolved' and message.chat.id == 304987403)
def check_unsolved_tasks_of_solver(message):
    try:
        solver_id = message.text.split()[2]
        tasks = dq.get_list_of_paid_tasks(solver_id)
        time = datetime.now()
        bot.send_message(message.chat.id, 'Нерешенные задания',
                         reply_markup=kb.list_of_solvers_paid_tasks_keyboard(tasks, time))
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data.split('+')[0] == 'unsolved')
def open_unsolved_task(call):
    try:
        task_id = call.data.split('+')[1]
        open_solution_of_selected_task(task_id, call.message)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(call.message.chat.id, str(inspect.stack()[0][3]), str(error))


@bot.callback_query_handler(func=lambda call: call.data == 'back_from_unsolved_tasks')
def back_from_unsolved_tasks(call):
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.message_handler(func=lambda message: message.text.lower() == 'help' and message.chat.id == 304987403)
def admin_help(message):
    try:
        bot.send_message(message.chat.id, 'Commands\n\n'
                                          '1) admin [user_id] [text] - Ответ от поддержки\n'
                                          '2) last5 - пять последних зарегистрированных пользователей\n'
                                          '3) ban [user_id] / unban [user_id] \n'
                                          '4) addmoney [user_id] [amount] - добавить деньги пользователю\n'
                                          '5) key - ключ для регистрации работника\n'
                                          '6) solvers - список всех работников\n'
                                          '7) stats - статистика за последние два дня\n'
                                          '8) new users today - количество новых клиентов сегодня \n'
                                          '9) on balance - сумма денег на балансах пользователей\n'
                                          '10) today payments - сумма сегодняшних транзакций'
                                          '11) set group [solver_id] [group] - назначить группу менеджеру'
                                          '12) show [task_id] - показать информацию о задании'
                                          '13) solved task [solver_id] - решенные задачи за последний день'
                                          '14) unsolved task [solver_id] - нерешенные задачи')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
        dq.add_error_to_error_list(message.chat.id, str(inspect.stack()[0][3]), str(error))


# bot.remove_webhook()
#
# time.sleep(0.1)
#
# # Set webhook
# bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
#                 certificate=open(WEBHOOK_SSL_CERT, 'r'))

bot.infinity_polling()
