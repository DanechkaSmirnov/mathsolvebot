import telebot
from telebot import types
import logging
import time
import STATES as st
import database_queries as dq
import keyboards as kb
import flask
import random
import string


# API_TOKEN = '1746641292:AAE0c9i1cXYPeFglByfTzO6DyHI3FH7TRlk' #MathHelpersBot
API_TOKEN = '1630703867:AAGfz8jxBQoViIIvwcT21A3kn42WbnUHvgk'  # MathHelpersTestBot
bot = telebot.TeleBot(API_TOKEN, threaded=False)
key_for_registration = 'rngofrhfrprvbfjegtfsdwlvuufracdp'


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


# Solvers module


@bot.message_handler(func=lambda message: dq.check_user_in_ban_list(message.chat.id))
def banned(message):
    pass


@bot.message_handler(content_types=['sticker', 'video', 'voice', 'document', 'video_note', 'location', 'contact',
                                    'left_chat_member', 'new_chat_title', 'new_chat_photo', 'delete_chat_photo',
                                    'group_chat_created', 'supergroup_chat_created', 'channel_chat_created',
                                    'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message'])
def wrong_type(message):
    pass

@bot.message_handler(content_types=['photo'])
def complete_photo_of_task(message):
    try:
        if dq.check_user_in_db(message.chat.id) == True:
            if dq.get_state(message.chat.id) == st.HOMEWORK_TASK:
                bot.send_message(message.chat.id, 'Оставьте комментарий к заявке')
                photo_id = bot.get_file(message.photo[-1].file_id).file_id
                dq.add_photo_of_problems(message.chat.id, photo_id)
                bot.register_next_step_handler(message, complete_comment_of_task)
            if dq.get_state(message.chat.id) == st.CHANGE_TASK:
                photo_id = bot.get_file(message.photo[-1].file_id).file_id
                dq.add_photo_of_problems(message.chat.id, photo_id)
                send_full_task(message)
        if dq.check_solver_in_db(message.chat.id) == True:
            if dq.get_solver_state(message.chat.id) != st.solver_SENDING_SOLUTION:
                pass
            if dq.get_solver_state(message.chat.id) == st.solver_SENDING_SOLUTION:
                photo = bot.get_file(message.photo[-1].file_id).file_id
                dq.add_photo_of_solution(message.chat.id, photo)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')



@bot.message_handler(func=lambda message: message.text == dq.get_key_for_registration())
def solver_registration(message):
    try:
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
        letters = string.ascii_lowercase
        random.seed(int(time.time()))
        key = ''.join(random.choice(letters) for i in range(20))
        dq.set_key_for_registration(key)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


def enter_solver_name(message):
    try:
        dq.set_solver_name(message.chat.id, message.text)
        bot.send_message(message.chat.id, 'Привет, ' + dq.get_solver_name(message.chat.id),
                         reply_markup=kb.solver_menu_keyboard())
        dq.set_solver_state(message.chat.id, st.solver_MAIN)
    except Exception as error:
        bot.send_message(message.chat.id, 'Имя введено неверно, повторите')
        bot.register_next_step_handler(message, enter_solver_name)


def send_task_to_solvers(task_id):
    try:
        text = dq.task_completed_message_for_solver(task_id)
        photo = dq.get_picture_of_task(task_id)
        solvers = dq.get_solvers_id()
        for solver in solvers:
            message_to_save = bot.send_photo(solver[0], photo, caption=text,
                                             reply_markup=kb.solver_task_keyboard(task_id, solver[0]))
            dq.save_sended_task(message_to_save.id, task_id, solver[0])
    except Exception as error:
        bot.send_message(task_id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


@bot.callback_query_handler(func=lambda call: 'accept' in call.data)
def accept_selected_task(call):
    try:
        task_id = call.data.split('+')[1]
        if dq.check_task_is_already_paid(task_id) == 0:
            photo_of_task = dq.get_picture_of_task(task_id)
            solvers = dq.get_solvers_id()
            for solver in solvers:
                if dq.get_message_id(task_id, solver[0]) is not None:
                    message_id = dq.get_message_id(task_id, solver[0])
                    dq.task_message_deleted(message_id)
                    bot.delete_message(solver[0], message_id)
            dq.set_current_task(call.message.chat.id, task_id)
            bot.send_photo(call.message.chat.id, photo_of_task, caption='Выберите сложность данной задачи',
                           reply_markup=kb.price_list_keyboard(task_id))
            dq.set_task_solver_id(task_id, call.message.chat.id)
            dq.set_status_of_solution(task_id, 4)
        elif dq.check_task_is_already_paid(task_id) == 4:
            bot.send_message(call.message.chat.id, 'Задание уже было взято')
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


# Для всех работников "Назад", для всех клиентов "🔙 Назад"
@bot.message_handler(func=lambda message: message.text == '🔙 Назад')
def client_back_steps(message):
    try:
        if dq.check_solver_in_db(message.chat.id) == False:
            if dq.get_state(message.chat.id) == st.MSG_TO_SUPPORT:
                dq.set_state(message.chat.id, st.MAIN)
                bot.send_message(message.chat.id, dq.print_account_info(message.chat.id),
                                 reply_markup=kb.menu_keyboard())

            elif dq.get_state(message.chat.id) == st.SEND_MESSAGE_TO_SUPPORT:
                bot.send_message(message.chat.id,
                                 'При возникновении дополнительных вопросов обращайтесь в техподдержку, нажав кнопку ниже\n\n'
                                 'Задавайте вопросы по существу 👀', reply_markup=kb.support_keyboard())
                dq.set_state(message.chat.id, st.MSG_TO_SUPPORT)

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
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


@bot.callback_query_handler(func=lambda call: 'price' in call.data)
def send_priced_task_to_user(call):
    try:
        task_id = call.data.split('+')[2]
        if dq.check_task_is_already_paid(task_id) == 4:
            price = call.data.split('+')[1]
            num_of_task = task_id.split('_')[1]
            user_id = task_id.split('_')[0]
            dq.set_status_of_solution(task_id, 3)
            dq.set_price_of_task(task_id, price)
            bot.send_message(call.message.chat.id, 'Цена предложена клиенту. Ожидаем ответа',
                             reply_markup=kb.solver_menu_keyboard())
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(user_id,
                             'Ваше задание №{} готовы решить за {} рублей'.format(str(int(num_of_task) + 1), price),
                             reply_markup=kb.decision_of_client_keyboard(task_id))
        elif dq.check_task_is_already_paid(task_id) == 3:
            bot.send_message(call.message.chat.id, 'К сожалению, данное задание было выбрано одновременно двумя людьми')
            bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


@bot.callback_query_handler(func=lambda call: 'pay' in call.data)
def pay_for_task(call):
    try:
        task_id = call.data.split('+')[1]
        if dq.check_task_id_db(task_id) == True:
            price_of_task = dq.get_price_of_task(task_id)
            user_id = task_id.split('_')[0]
            balance_of_user = dq.get_balance_of_user(user_id)
            if price_of_task <= balance_of_user:
                if dq.check_task_is_already_paid(task_id) == 3:
                    new_balance = balance_of_user - price_of_task
                    dq.set_balance_of_user(new_balance, user_id)
                    dq.set_status_of_solution(task_id, 5)
                    solver_id = dq.get_solver_of_task(task_id)
                    bot.send_message(call.message.chat.id,
                                     'Задание успешно оплачено. Менеджеры уже приступили к решению!')
                    bot.send_message(solver_id, 'Задание {} было оплачено, можно приступать!'.format(task_id),
                                     reply_markup=kb.solver_menu_keyboard())
                    bot.delete_message(call.message.chat.id, call.message.id)
            else:
                bot.send_message(call.message.chat.id, 'Недостаточно средств. Пополните баланс.')
        else:
            bot.send_message(call.message.chat.id, 'Задание было удалено')
            bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


@bot.message_handler(func=lambda message: message.text == 'Список оплаченных задач')
def send_task_list_to_solver(message):
    try:
        if dq.check_solver_in_db(message.chat.id):
            list_of_tasks = dq.get_list_of_paid_tasks(message.chat.id)
            bot.send_message(message.chat.id, 'Список заданий, к которым вы можете приступить',
                                 reply_markup=kb.list_of_paid_tasks_keyboard(list_of_tasks))
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')
        
        
@bot.message_handler(func=lambda message: message.text == 'Список неоплаченных задач')
def send_task_list_to_solver(message):
    try:
        if dq.check_solver_in_db(message.chat.id):
            list_of_tasks = dq.get_list_of_unpaid_tasks(message.chat.id)
            bot.send_message(message.chat.id, 'Список принятых, но неоплаченных задач за последние сутки',
                                 reply_markup=kb.list_of_unpaid_tasks_keyboard(list_of_tasks))
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


@bot.callback_query_handler(func=lambda call: call.data == 'back_from_paid_tasks')
def back_from_list_of_paid_tasks(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.id)
        solver_stats(call.message)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')

@bot.callback_query_handler(func=lambda call: call.data == 'back_from_free_tasks')
def back_from_list_of_paid_tasks(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.id)
        solver_stats(call.message)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


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
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')



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
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')

@bot.callback_query_handler(func=lambda call: 'delete_task' in call.data)
def delete_selected_task(call):
    try:
        task_id = call.data.split('+')[1]
        if not dq.check_task_in_task_list(task_id):
            bot.send_message(call.message.chat.id, 'Заявка уже была удалена')
            bot.delete_message(call.message.chat.id, call.message.id)
        elif dq.check_task_is_already_paid(task_id) in [2, 3]:
            bot.send_message(call.message.chat.id, 'Заявка успешно удалена')
            task_id = call.data.split('+')[1]
            dq.delete_selected_task(task_id)
            bot.delete_message(call.message.chat.id, call.message.id)
        elif dq.check_task_is_already_paid(task_id) == 0:
            bot.send_message(call.message.chat.id, 'Задание невозможно удалить, так как оно уже было оплачено')
            bot.delete_message(call.message.chat.id, call.message.id)
        elif dq.check_task_is_already_paid(task_id) == 1:
            bot.send_message(call.message.chat.id, 'Задание невозможно удалить, так как оно уже готов')
            bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


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
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


@bot.message_handler(func=lambda message: message.text == 'Назад' and dq.check_solver_in_db(
    message.chat.id) == True and dq.get_solver_state(
    message.chat.id) == st.solver_GET_REPORT_MESSAGE)
def report_selected_task_back(message):
    try:
        dq.set_solver_state(message.chat.id, st.solver_MAIN)
        solver_stats(message)
        send_task_to_solvers(dq.get_reporting_task(message.chat.id))
        dq.set_reporting_task(message.chat.id, None)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == True and dq.get_solver_state(
    message.chat.id) == st.solver_GET_REPORT_MESSAGE and message.text != 'Назад')
def send_report_to_user(message):
    try:
        task_id = dq.get_reporting_task(message.chat.id)
        if dq.check_task_is_already_paid(task_id) != 2:
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
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


@bot.callback_query_handler(func=lambda call: 'cancel_setting_cost' in call.data)
def stop_solving(call):
    try:
        task_id = call.data.split('+')[1]
        send_task_to_solvers(task_id)
        dq.set_status_of_solution(task_id, 0)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


@bot.callback_query_handler(func=lambda call: call.data == 'back_from_solving')
def go_back_from_solving_task(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.id)
        list_of_tasks = dq.get_list_of_paid_tasks(call.message.chat.id)
        bot.send_message(call.message.chat.id, 'Список заданий, к которым вы можете приступить',
                         reply_markup=kb.list_of_paid_tasks_keyboard(list_of_tasks))
        dq.set_solver_state(call.message.chat.id, st.solver_MAIN)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')

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
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


@bot.callback_query_handler(func=lambda call: call.data == 'send_solution')
def get_photos_of_solution(call):
    try:
        bot.send_message(call.message.chat.id, 'Отправляйте фотографии по одной, в конце нажмите на кнопку "Завершить"',
                         reply_markup=kb.sending_photos_of_solution_keyboard())
        dq.set_solver_state(call.message.chat.id, st.solver_SENDING_SOLUTION)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


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
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим!')


@bot.message_handler(func=lambda message: message.text.lower() == 'завершить' and dq.check_solver_in_db(
    message.chat.id) == True and dq.get_solver_state(
    message.chat.id) == st.solver_SENDING_SOLUTION and message.text != None)
def end_solution_sending(message):
    try:
        bot.send_message(message.chat.id, 'Решение успешно отправлено', reply_markup=kb.solver_menu_keyboard())
        task_id = dq.get_current_task(message.chat.id)
        dq.set_current_task(message.chat.id, None)
        dq.refresh_num_of_sended_photos(message.chat.id)
        dq.set_solver_state(message.chat.id, st.MAIN)
        user_id = task_id.split('_')[0]
        dq.set_status_of_solution(task_id, 1)
        dq.set_solution_time(task_id)
        dq.set_task_solver_id(task_id, message.chat.id)
        task_number = int(task_id.split('_')[1]) + 1
        bot.send_message(user_id,
                         'Задание №{} готово. Решение вы сможете найти во вкладке "Аккаунт"'.format(str(task_number)),
                         disable_notification=False)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


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


# Support
@bot.message_handler(func=lambda message: message.text == '❓ Техподдержка' and dq.check_user_in_db(
    message.chat.id) and dq.get_state(
    message.chat.id) == st.MAIN)
def support_info(message):
    try:
        bot.send_message(message.chat.id,
                         'Если у вас возникли какие-либо вопросы - обращайтесь в техподдержку, нажав кнопку ниже\n\n'
                         'Задавайте вопросы по существу 👀', reply_markup=kb.support_keyboard())
        dq.set_state(message.chat.id, st.MSG_TO_SUPPORT)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


@bot.message_handler(
    func=lambda message: message.text == '💬 Отправить запрос' and dq.check_user_in_db(message.chat.id))
def send_message_to_support(message):
    try:
        bot.send_message(message.chat.id, 'Напишите, с чем у вас возникла проблема\n\n'
                                          'Для удобства и скорости ответа воспользуйтесь формой:\n\n'
                                          'Проблема: ...\n'
                                          'Описание проблемы: ...\n'
                                          'Идеи по ее решению: ...', reply_markup=kb.how_it_words())
        dq.set_state(message.chat.id, st.SEND_MESSAGE_TO_SUPPORT)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


@bot.message_handler(func=lambda message: dq.check_user_in_db(message.chat.id) and
                                          dq.get_state(message.chat.id) == st.SEND_MESSAGE_TO_SUPPORT and
                                          message.text != '🔙 Назад')
def message_text_to_support(message):
    try:
        bot.send_message(message.chat.id, 'Ваш запрос принят! \nСовсем скоро вам ответят :)',
                         reply_markup=kb.menu_keyboard())
        bot.send_message(304987403,
                         'SUPPORT MESSAGE FROM USER {}\nMESSAGE_TEXT:\n {}'.format(message.chat.id, message.text))
        dq.add_message_to_support(message.chat.id, message.text)
        dq.set_state(message.chat.id, st.MAIN)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


# About us
@bot.message_handler(func=lambda message: message.text == '👋 О нас' and dq.check_user_in_db(
    message.chat.id) == True and dq.get_state(
    message.chat.id) == st.MAIN)
def about_us_info(message):
    try:
        bot.send_message(message.chat.id, 'Привет, студент 🤓\n\n'
                                          'Дедлайны горят, а задание не готово? Надоели недобросовестные исполнители?\n\n'
                                          'Мы готовы решить для тебя любую математическую задачу - алгебра, дискретная математика '
                                          'и матанализ для нас не проблема 👨🏻‍🎓\n\n'
                                          'Достаточно оставить заявку в боте и Вы получите ответ в течение 10 минут!\n\n'
                                          'Главные преимущества MathHelper - децентрализация, скорость и удобство!\n\n'
                                          'Отправка задания, подтверждение, оплата - всё в одном месте. Получить готовое решение '
                                          'легче, чем заказать еду 🍕\n\n'
                                          'Обратная связь - @dannysmirnov', reply_markup=kb.about_us_keyboard())
        dq.set_state(message.chat.id, st.ABOUT_US)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


@bot.message_handler(func=lambda message: message.text == 'ℹ️ Как работает бот?' and dq.check_user_in_db(
    message.chat.id) == True and dq.get_state(
    message.chat.id) == st.ABOUT_US)
def how_it_words(message):
    bot.send_message(message.chat.id, 'Работа с ботом происходит предельно просто:\n\n'
                                      '1) Вы оставляете заявку, указывая тему и прикрепляя фотографию задачи\n'
                                      '2) Мы обрабатываем заявку и присылаем Вам подтверждение с ценой, предложенной исполнителем\n'
                                      '3) Вы производите оплату и подтверждаете заявку\n'
                                      '4) Наш исполнитель начинает работу и отправляет вам решение в кратчайшие сроки\n\n'
                                      '⏱ Средняя скорость обработки одной заявки составляет 10 минут'
                     , reply_markup=kb.about_us_keyboard())


# Account
@bot.message_handler(func=lambda message: message.text == '📄 Аккаунт' and dq.check_user_in_db(message.chat.id) == True and dq.get_state(
    message.chat.id) == st.MAIN)
def account(message):
    try:
        bot.send_message(message.chat.id, 'Здесь вы можете проверить историю своих заявок и пополнить баланс',
                         reply_markup=kb.account_keyboard())
        dq.set_state(message.chat.id, st.ACCOUNT)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


@bot.message_handler(func=lambda message: message.text == '📍 История заявок' and dq.check_user_in_db(message.chat.id) == True and dq.get_state(
    message.chat.id) == st.ACCOUNT)
def show_list_of_tasks(message):
    try:
        bot.send_message(message.chat.id, '📄 История заданий',
                         reply_markup=kb.set_of_tasks_keyboard(dq.select_set_of_task(message.chat.id)))
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


@bot.callback_query_handler(func=lambda call: 'task_' in call.data)
def open_selected_task(call):
    try:
        task_id = call.data.replace('task_', '')
        if dq.check_task_id_db(task_id) == True:
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


@bot.callback_query_handler(func=lambda call: 'ask_solver' in call.data)
def send_question_to_solver(call):
    bot.send_message(call.message.chat.id,
                     'Напишите одним сообщением, какие именно вопросы у вас остались по заданию.\n\n'
                     'Ответ от исполнителя появится в этом же чате в ближайшее время', reply_markup=kb.how_it_words())
    task_id = call.data.replace('ask_solver+', '')
    dq.set_question_task_id(call.message.chat.id, task_id)
    bot.register_next_step_handler(call.message, enter_question_to_solver)


def enter_question_to_solver(message):
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
        bot.send_media_group(solver_id, array_of_photos)
        bot.send_message(solver_id, 'ВНИМАНИЕ, ВОПРОС\n\nОтветьте на него так, чтобы клиенту все было понятно',
                         reply_markup=kb.answer_clients_question(task_id))
        bot.send_message(message.chat.id, 'Вопрос успешно доставлен. Скоро вам ответят',
                         reply_markup=kb.account_keyboard())


@bot.callback_query_handler(func=lambda call: 'send_answer' in call.data)
def send_answer_to_user(call):
    bot.send_message(call.message.chat.id, 'Напишите ответ одним сообщением, ответьте на все поставленные вопросы',
                     reply_markup=kb.report_task_keyboard())
    task_id = call.data.replace('send_answer+', '')
    dq.set_answer_task_id(call.message.chat.id, task_id)
    bot.register_next_step_handler(call.message, enter_answer_to_user)


def enter_answer_to_user(message):
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
                                  caption='Ответ на ваш вопрос\n\n' + message.text))
        bot.send_media_group(user_id, array_of_photos)
        bot.send_message(message.chat.id, 'Ответ успешно отправлен', reply_markup=kb.solver_menu_keyboard())


@bot.message_handler(func=lambda message: message.text == 'Перейти в меню' and dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.SELECTED_TASK)
def back_to_menu(message):
    try:
        dq.set_state(message.chat.id, st.MAIN)
        welcome(message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


# Services
@bot.message_handler(func=lambda message: message.text == '📕 Услуги' and dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
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
#                          'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')
#
#
# def check_isdigit(message):
#     if type(message) == str:
#         if str.isdigit(message) == True:
#             return True
#     return False


@bot.message_handler(func=lambda message: message.text == '📍 Оставить заявку' and dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.SERVICES)
def complete_num_of_task(message):
    try:
        bot.send_message(message.chat.id, 'Введите тему задания (матанализ, алгебра и т.д)', reply_markup=telebot.types.ReplyKeyboardRemove())
        dq.create_task_id(message.chat.id)
        bot.register_next_step_handler(message, complete_theme_of_task)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


# @bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
#     message.chat.id) == st.HOMEWORK_NUMBER and not check_isdigit(message.text))
# def incomplete_num_of_task(message):
#     bot.send_message(message.chat.id, 'Неверный ввод, введите количество заданий')



def complete_theme_of_task(message):
    try:
        bot.send_message(message.chat.id, 'Отправьте фотографию задания')
        dq.add_theme_of_problems(message.chat.id, message.text)
        dq.set_state(message.chat.id, st.HOMEWORK_TASK)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


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
#                          'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')



def send_full_task(message):
    try:
        dq.set_state(message.chat.id, st.CHECKING_TASK)
        text_of_task = dq.task_completed_message(message.chat.id)
        bot.send_photo(message.chat.id, dq.get_photo_of_problems(message.chat.id), caption=text_of_task,
                       reply_markup=kb.change_task_keyboard())
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.HOMEWORK_COMMENT)
def complete_comment_of_task(message):
    try:
        dq.add_comment_of_problems(message.chat.id, message.text)
        send_full_task(message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


@bot.callback_query_handler(func=lambda call: call.data == 'num_of_tasks')
def change_num_of_tasks(call):
    try:
        bot.send_message(call.message.chat.id, 'Введите количество заданий')
        dq.set_state(call.message.chat.id, st.CHANGE_NUMBER)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.CHANGE_NUMBER and str.isdigit(message.text))
def set_changed_num_of_tasks(message):
    try:
        dq.add_number_of_problems(message.chat.id, message.text)
        send_full_task(message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.CHANGE_NUMBER and not str.isdigit(message.text))
def set_changed_num_of_tasks(message):
    bot.send_message(message.chat.id, 'Неверный ввод, введите количество заданий')


@bot.callback_query_handler(func=lambda call: call.data == 'theme_of_task')
def change_theme_of_tasks(call):
    try:
        bot.send_message(call.message.chat.id, 'Введите тему задания')
        dq.set_state(call.message.chat.id, st.CHANGE_THEME)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.CHANGE_THEME)
def set_changed_theme_of_tasks(message):
    try:
        dq.add_theme_of_problems(message.chat.id, message.text)
        send_full_task(message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


@bot.callback_query_handler(func=lambda call: call.data == 'difficult_of_task')
def change_difficult_of_tasks(call):
    try:
        bot.send_message(call.message.chat.id, 'Выберите сложность задания', reply_markup=kb.difficulty_keyboard())
        dq.set_state(call.message.chat.id, st.CHANGE_DIFFICULT)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


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


@bot.callback_query_handler(func=lambda call: call.data == 'photo_of_task')
def change_photo_of_tasks(call):
    try:
        bot.send_message(call.message.chat.id, 'Отправьте фото задания')
        dq.set_state(call.message.chat.id, st.CHANGE_TASK)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


@bot.callback_query_handler(func=lambda call: call.data == 'comment_of_task')
def change_comment_of_tasks(call):
    try:
        bot.send_message(call.message.chat.id, 'Оставьте комментарий к заявке')
        dq.set_state(call.message.chat.id, st.CHANGE_COMMENT)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.CHANGE_COMMENT)
def set_changed_comment_of_tasks(message):
    try:
        dq.add_comment_of_problems(message.chat.id, message.text)
        send_full_task(message)
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


@bot.callback_query_handler(func=lambda call: call.data == 'complete_task')
def completed_task(call):
    try:
        bot.send_message(call.message.chat.id, 'Ваша заявка принята, ожидайте ее подтверждения',
                         reply_markup=kb.menu_keyboard())
        task_id = dq.complete_task(call.message.chat.id)
        send_task_to_solvers(task_id)
        dq.set_state(call.message.chat.id, st.MAIN)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим!')


# Add money

@bot.callback_query_handler(
    func=lambda call: dq.check_solver_in_db(call.message.chat.id) == False and call.data == 'add_money')
def callback_add_money(call):
    add_money(call.message)


@bot.message_handler(
    func=lambda message: message.text == '💰 Пополнить баланс' and dq.check_solver_in_db(message.chat.id) == False and dq.get_state(message.chat.id) in [
        st.SERVICES, st.ACCOUNT])
def add_money(message):
    bot.send_message(message.chat.id, 'Минимальный платеж составляет 100 рублей\n\n'
                                      'На какую сумму вы хотите пополнить ваш баланс?', reply_markup=kb.how_it_words())
    dq.set_state(message.chat.id, st.SEND_AMOUNT)


def check_isdigit(message):
    if type(message) == str:
        if str.isdigit(message) == True:
            return True
    return False


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.SEND_AMOUNT)
def send_recipies(message):
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
                             provider_token='390540012:LIVE:16909',
                             currency='RUB',
                             prices=[types.LabeledPrice(label='Rub', amount=amount)],
                             start_parameter='add_money',
                             is_flexible=False)
    else:
        bot.send_message(message.chat.id, 'Неверная сумма платежа')


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Ошибка при проведении оплаты")


@bot.message_handler(content_types=['successful_payment'])
def add_amount_to_user(message):
    bot.send_message(message.chat.id,
                     'Оплата на {} рублей прошла успешно'.format(message.successful_payment.total_amount / 100),
                     reply_markup=kb.menu_keyboard())
    dq.add_money_to_user(message.chat.id, int(int(message.successful_payment.total_amount) / 100))
    dq.set_state(message.chat.id, st.MAIN)
    dq.add_payment_in_database(message.chat.id, int(int(message.successful_payment.total_amount) / 100))


@bot.message_handler(func=lambda message: 'admin' in message.text and message.chat.id == 304987403)
def send_message_to_user_with_admin(message):
    try:
        user_id = message.text.split()[1]
        text = message.text.replace('admin {} '.format(user_id), '')
        bot.send_message(user_id, 'Ответ от администрации:\n' + text, disable_notification=True)
    except Exception as error:
        bot.send_message(message.chat.id, str(error))


@bot.message_handler(func=lambda message: message.text.lower() == 'last5' and message.chat.id == 304987403)
def get_last_five_users(message):
    try:
        list = dq.get_last_five_users()
        text = ''
        for i in list:
            text += str(i) + '\n'
        bot.send_message(message.chat.id, text)
    except Exception as error:
        bot.send_message(message.chat.id, str(error))


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
        bot.send_message(message.chat.id, str(error))


@bot.message_handler(func=lambda message: message.text.lower() == 'key' and message.chat.id == 304987403)
def get_registration_key(message):
    try:
        bot.send_message(message.chat.id, dq.get_key_for_registration())
    except Exception as error:
        bot.send_message(message.chat.id, error)


@bot.message_handler(func=lambda message: message.text.lower() == 'solvers' and message.chat.id == 304987403)
def get_list_of_solvers(message):
    try:
        list = dq.get_list_of_solvers()
        text = ''
        for i in list:
            text += str(i) + '\n'
        bot.send_message(message.chat.id, text)
    except Exception as error:
        bot.send_message(message.chat.id, str(error))


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
        bot.send_message(message.chat.id, str(error))


@bot.message_handler(func=lambda message: message.text.split()[0] == 'ban' and message.chat.id == 304987403)
def ban_user(message):
    try:
        dq.add_user_to_ban_list(message.text.split()[1])
        bot.send_message(message.chat.id, 'User has been banned')
    except Exception as error:
        bot.send_message(message.chat.id, str(error))


@bot.message_handler(func=lambda message: message.text.split()[0] == 'unban' and message.chat.id == 304987403)
def ban_user(message):
    try:
        dq.remove_user_to_ban_list(message.text.split()[1])
        bot.send_message(message.chat.id, 'User has been unbanned')
    except Exception as error:
        bot.send_message(message.chat.id, str(error))


@bot.message_handler(func=lambda message: message.text == 'new users today' and message.chat.id == 304987403)
def users_came_today(message):
    try:
        bot.send_message(message.chat.id, str(dq.count_today_users()))
    except Exception as error:
        bot.send_message(message.chat.id, str(error))


@bot.message_handler(func=lambda message: message.text == 'on balance' and message.chat.id == 304987403)
def reserved_money(message):
    try:
        bot.send_message(message.chat.id, str(dq.money_on_user_balances()))
    except Exception as error:
        bot.send_message(message.chat.id, str(error))


@bot.message_handler(func=lambda message: message.text == 'today payments' and message.chat.id == 304987403)
def today_payments(message):
    try:
        bot.send_message(message.chat.id, str(dq.today_payments()))
    except Exception as error:
        bot.send_message(message.chat.id, str(error))

# @bot.message_handler(func=lambda message: 'solver account' in message.text and message.chat.id == 304987403)
# def watch_solver_account(message):
#


@bot.message_handler(func=lambda message: message.text == 'help' and message.chat.id == 304987403)
def admin_help(message):
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
                                      '10) today payments - сумма сегодняшних транзакций')


# bot.remove_webhook()
#
# time.sleep(0.1)
#
# # Set webhook
# bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
#                 certificate=open(WEBHOOK_SSL_CERT, 'r'))

bot.infinity_polling()
