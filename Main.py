import telebot
from telebot import types

import STATES as st
import database_queries as dq
import keyboards as kb

token = '1630703867:AAFxhZoYqUFgCQqrXIxXRpENh73uOqBsUR8'

key_for_registration = 'rngofrhfrprvbfjegtfsdwlvuufracdp'

bot = telebot.TeleBot(token)

# Admin commands



# Solvers module


@bot.message_handler(func=lambda message: message.text == key_for_registration)
def registration(message):
    try:
        dq.add_info_log(message.chat.id, 'registration begin')
        if not dq.check_solver_in_db(message.chat.id):
            dq.add_solver_in_db(message.chat.id)
            dq.set_solver_state(message.chat.id, st.solver_REGISTRATION)
            bot.send_message(message.chat.id, 'Введите имя')
            if dq.check_user_in_db(message.chat.id):
                dq.delete_solver_from_user_db(message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Привет, ' + dq.get_solver_name(message.chat.id),
                             reply_markup=kb.solver_menu_keyboard())
            if dq.check_user_in_db(message.chat.id):
                dq.delete_solver_from_user_db(message.chat.id)
        dq.add_info_log(message.chat.id, 'registration end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим! ')
        dq.add_error_log(message.chat.id, 'registration_error', error)


def send_task_to_solvers(task_id):
    try:
        dq.add_info_log(task_id, 'send_task_to_solvers begin')
        text = dq.task_completed_message_for_solver(task_id)
        photo = dq.get_picture_of_task(task_id)
        solvers = dq.get_solvers_id()
        for solver in solvers:
            message_to_save = bot.send_photo(solver[0], photo, caption=text,
                                             reply_markup=kb.solver_task_keyboard(task_id, solver[0]))
            dq.save_sended_task(message_to_save.id, task_id, solver[0])
        dq.add_info_log(task_id, 'send_task_to_solvers end')
    except Exception as error:
        bot.send_message(task_id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим! ')
        dq.add_error_log(task_id, 'send_task_to_solvers_error', error)


# @bot.callback_query_handler(func=lambda call: dq.check_solver_in_db(
#     call.message.chat.id) == True and 'deny' in call.data and dq.get_solver_state(
#     call.message.chat.id) != st.solver_SOLVING)
# def deny_selected_task(call):
#     try:
#         dq.add_info_log(call.message.chat.id, 'deny_selected_task begin')
#         task_id = call.data.split('+')[1]
#         message_id = dq.get_message_id(task_id, call.message.chat.id)
#         dq.task_message_deleted(message_id)
#         bot.delete_message(call.message.chat.id, message_id)
#         dq.add_info_log(call.message.chat.id, 'deny_selected_task end')
#     except Exception as error:
#         bot.send_message(call.message.chat.id,
#                          'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
#                          'исправим! ')
#         dq.add_error_log(call.message.chat.id, 'deny_selected_task_error', error)


@bot.callback_query_handler(func=lambda call: dq.check_solver_in_db(
    call.message.chat.id) == True and 'accept' in call.data and dq.get_solver_state(
    call.message.chat.id) != st.solver_SOLVING)
def accept_selected_task(call):
    try:
        dq.add_info_log(call.message.chat.id, 'accept_selected_task begin')
        task_id = call.data.split('+')[1]
        photo_of_task = dq.get_picture_of_task(task_id)
        text = dq.task_completed_message_for_solver(task_id)
        solvers_raw = dq.get_solvers_id()
        solvers = []
        for i in solvers_raw:
            solvers.append(i[0])
        for solver in solvers:
            if dq.get_message_id(task_id, solver) is not None:
                message_id = dq.get_message_id(task_id, solver)
                dq.task_message_deleted(message_id)
                bot.delete_message(solver, message_id)
        # dq.set_solver_state(call.message.chat.id, st.solver_SOLVING)
        dq.set_current_task(call.message.chat.id, task_id)
        # bot.send_photo(call.message.chat.id, photo_of_task, caption=text, reply_markup=kb.solving_keyboard())
        bot.send_photo(call.message.chat.id, photo_of_task, caption='Выберите, за сколько вы готовы решить эту задачу',
                       reply_markup=kb.price_list_keyboard(task_id))
        dq.set_task_solver_id(task_id, call.message.chat.id)
        dq.add_info_log(call.message.chat.id, 'accept_selected_task end')
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим! ')
        dq.add_error_log(call.message.chat.id, 'accept_selected_task_error', error)


@bot.callback_query_handler(func=lambda call: dq.check_solver_in_db(
    call.message.chat.id) == True and 'price' in call.data)
def send_priced_task_to_user(call):
    task_id = call.data.split('+')[2]
    price = call.data.split('+')[1]
    num_of_task = task_id.split('_')[1]
    user_id = task_id.split('_')[0]
    dq.set_status_of_solution(task_id, 3)
    dq.set_price_of_task(task_id, price)
    bot.send_message(call.message.chat.id, 'Цена предложена клиенту. Ожидаем ответа', reply_markup=kb.solver_menu_keyboard())
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(user_id, 'Ваше задание №{} готовы решить за {} рублей'.format(str(int(num_of_task) + 1), price),
                     reply_markup=kb.decision_of_client_keyboard(task_id))


@bot.callback_query_handler(func=lambda call: 'pay' in call.data)
def pay_for_task(call):
    task_id = call.data.split('+')[1]
    if dq.check_task_id_db(task_id) == True:
        price_of_task = dq.get_price_of_task(task_id)
        user_id = task_id.split('_')[0]
        balance_of_user = dq.get_balance_of_user(user_id)
        if price_of_task <= balance_of_user:
            if dq.check_task_is_already_paid(task_id) == 3:
                new_balance = balance_of_user - price_of_task
                dq.set_balance_of_user(new_balance, user_id)
                dq.set_status_of_solution(task_id, 0)
                solver_id = dq.get_solver_of_task(task_id)
                bot.send_message(call.message.chat.id, 'Задание успешно оплачено. Менеджеры уже приступили к решению!')
                bot.send_message(solver_id, 'Задание {} было оплачено, можно приступать!'.format(task_id), reply_markup=kb.solver_menu_keyboard())
                bot.delete_message(call.message.chat.id, call.message.id)
        else:
            bot.send_message(call.message.chat.id, 'Недостаточно средств. Пополните баланс.')
    else:
        bot.send_message(call.message.chat.id, 'Задание было удалено')
        bot.delete_message(call.message.chat.id, call.message.id)


@bot.message_handler(func = lambda message: dq.check_solver_in_db(message.chat.id) and message.text == 'Список оплаченных задач')
def send_task_list_to_solver(message):
    if not dq.check_solver_in_db(message.chat.id):
        pass
    if dq.check_solver_in_db(message.chat.id):
        list_of_tasks = dq.get_list_of_paid_tasks(message.chat.id)
        bot.send_message(message.chat.id, 'Список заданий, к которым вы можете приступить',
                         reply_markup=kb.list_of_paid_tasks_keyboard(list_of_tasks))





@bot.callback_query_handler(func=lambda call: call.data == 'back_from_paid_tasks')
def back_from_list_of_paid_tasks(call):
    bot.delete_message(call.message.chat.id, call.message.id)
    solver_stats(call.message)




@bot.callback_query_handler(func=lambda call: 'paid_task' in call.data)
def solve_choosed_task(call):
    task_id = call.data.split('+')[1]
    dq.set_solver_state(call.message.chat.id, st.solver_SOLVING)
    dq.set_current_task(call.message.chat.id, task_id)
    text = dq.task_completed_message_for_solver(task_id)
    photo_of_task = dq.get_picture_of_task(task_id)
    bot.send_photo(call.message.chat.id, photo_of_task, caption=text, reply_markup=kb.solving_keyboard())
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=lambda call: 'delete_task' in call.data)
def delete_selected_task(call):
    task_id = call.data.split('+')[1]
    if dq.check_task_is_already_paid(task_id) in [2, 3]:
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





@bot.callback_query_handler(func=lambda call: dq.check_solver_in_db(
    call.message.chat.id) == True and 'report' in call.data and dq.get_solver_state(
    call.message.chat.id) != st.solver_SOLVING)
def report_selected_task(call):
    bot.send_message(call.message.chat.id, 'Напишите, по какой причине нужно отменить данную заявку',
                     reply_markup=kb.report_task_keyboard())
    dq.set_solver_state(call.message.chat.id, st.solver_GET_REPORT_MESSAGE)
    dq.set_reporting_task(call.message.chat.id, call.data.split('+')[1])


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == True and dq.get_solver_state(
    message.chat.id) == st.solver_GET_REPORT_MESSAGE and message.text == 'Назад')
def report_selected_task_back(message):
    dq.set_solver_state(message.chat.id, st.solver_MAIN)
    solver_stats(message)
    dq.set_reporting_task(message.chat.id, None)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == True and dq.get_solver_state(
    message.chat.id) == st.solver_GET_REPORT_MESSAGE and message.text != 'Назад')
def send_report_to_user(message):
    task_id = dq.get_reporting_task(message.chat.id)
    dq.report_task(task_id)
    dq.set_report_text(task_id, message.text)
    user_id = task_id.split('_')[0]
    solvers_raw = dq.get_solvers_id()
    solvers = []
    for i in solvers_raw:
        solvers.append(i[0])
    for solver in solvers:
        if dq.get_message_id(task_id, solver) is not None:
            message_id = dq.get_message_id(task_id, solver)
            dq.task_message_deleted(message_id)
            bot.delete_message(solver, message_id)
    bot.send_message(message.chat.id, 'Отмена произошла успешно, пользователь оповещен')
    bot.send_message(user_id, 'Ваше задание не было принято по следующей причине: ' + message.text,
                     reply_markup=kb.repeat_reported_task_keyboard(task_id))


@bot.callback_query_handler(func=lambda call: 'cancel_setting_cost' in call.data)
def stop_solving(call):
    try:
        dq.add_info_log(call.message.chat.id, 'stop_solving begin')
        task_id = call.data.split('+')[1]
        send_task_to_solvers(task_id)
        bot.delete_message(call.message.chat.id, call.message.id)
        dq.add_info_log(call.message.chat.id, 'stop_solving end')
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим! ')
        dq.add_error_log(call.message.chat.id, 'stop_solving_error', error)


@bot.callback_query_handler(func=lambda call: call.data == 'go_back_from_there')
def go_back_from_solving_task(call):
    bot.delete_message(call.message.chat.id, call.message.id)
    list_of_tasks = dq.get_list_of_paid_tasks(call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Список заданий, к которым вы можете приступить',
                     reply_markup=kb.list_of_paid_tasks_keyboard(list_of_tasks))
    dq.set_solver_state(call.message.chat.id, st.solver_MAIN)


@bot.callback_query_handler(func=lambda call: call.data == 'send_solution')
def get_photos_of_solution(call):
    try:
        dq.add_info_log(call.message.chat.id, 'get_photos_of_solution start')
        bot.send_message(call.message.chat.id, 'Отправляйте фотографии по одной, в конце нажмите на кнопку "Завершить"', reply_markup=kb.sending_photos_of_solution_keyboard())
        dq.set_solver_state(call.message.chat.id, st.solver_SENDING_SOLUTION)
        dq.add_info_log(call.message.chat.id, 'get_photos_of_solution end')
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все '
                         'исправим! ')
        dq.add_error_log(call.message.chat.id, 'get_photos_of_solution_error', error)


@bot.message_handler(func = lambda message: dq.check_solver_in_db(message.chat.id) and
                                            dq.get_solver_state(message.chat.id) == st.solver_SENDING_SOLUTION and
                                            message.text == 'Отмена')
def cancel_sending_photos_of_solution(message):
    task_id = dq.get_current_task(message.chat.id)
    dq.delete_all_photos_of_solution(task_id)
    dq.set_current_task(message.chat.id, None)
    dq.set_solver_state(message.chat.id, st.solver_MAIN)
    send_task_list_to_solver(message)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == True and dq.get_solver_state(
    message.chat.id) == st.solver_SENDING_SOLUTION and message.text != None and message.text.lower() == 'завершить')
def end_solution_sending(message):
    try:
        dq.add_info_log(message.chat.id, 'end_solution_sending begin')
        bot.send_message(message.chat.id, 'Решение успешно отправлено', reply_markup=kb.solver_menu_keyboard())
        task_id = dq.get_current_task(message.chat.id)
        dq.set_current_task(message.chat.id, None)
        dq.refresh_num_of_sended_photos(message.chat.id)
        dq.set_solver_state(message.chat.id, st.MAIN)
        user_id = task_id.split('_')[0]
        dq.set_status_of_solution(task_id, 1)
        dq.set_solution_time(task_id)
        dq.set_task_solver_id(task_id, message.chat.id)
        task_number = int(task_id.split('_')[1])+1
        bot.send_message(user_id, 'Задание №{} готово. Решение вы сможете найти во вкладке "Аккаунт"'.format(str(task_number)),
                         disable_notification=False)
        dq.add_info_log(message.chat.id, 'end_solution_sending end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'end_solution_sending_error', error)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == True and dq.get_solver_state(
    message.chat.id) == st.solver_REGISTRATION)
def enter_name(message):
    try:
        dq.add_info_log(message.chat.id, 'enter_name begin')
        dq.set_solver_name(message.chat.id, message.text)
        bot.send_message(message.chat.id, 'Привет, ' + dq.get_solver_name(message.chat.id),
                         reply_markup=kb.solver_menu_keyboard())
        dq.set_solver_state(message.chat.id, st.solver_MAIN)
        dq.add_info_log(message.chat.id, 'enter_name end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'enter_name_error', error)


@bot.message_handler(
    func=lambda message: dq.check_solver_in_db(message.chat.id) == True and message.text == 'Статистика')
def solver_stats(message):
    try:
        task_list = dq.get_today_solutions_of_solver(message.chat.id)
        num_of_tasks = len(task_list)
        today_amount = 0
        if not (task_list is None):
            for i in task_list:
                today_amount += i[0]
        bot.send_message(message.chat.id,
                         'Количество выполненных заданий: {} \nСегодняшняя зарплата: {}'.format(num_of_tasks,
                                                                                                today_amount), reply_markup=kb.solver_menu_keyboard())
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'enter_name_error', error)


# USER REGISGRATION

@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        dq.add_info_log(message.chat.id, 'welcome begin')
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
                bot.send_message(message.chat.id, 'Привет, ' + dq.get_solver_name(message.chat.id) + '✨',
                                 reply_markup=kb.solver_menu_keyboard())
                dq.set_solver_state(message.chat.id, st.solver_MAIN)
            else:
                dq.add_solver_in_db(message.chat.id)
                dq.set_solver_state(message.chat.id, st.solver_REGISTRATION)
                bot.send_message(message.chat.id, 'Введите имя')
        dq.add_info_log(message.chat.id, 'welcome end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'welcome_error', error)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.ENTER_NAME)
def enter_name(message):
    try:
        dq.add_info_log(message.chat.id, 'enter_name begin')
        dq.set_name(message.chat.id, message.text)
        bot.send_message(message.chat.id, 'Привет, ' + dq.get_name(message.chat.id), reply_markup=kb.menu_keyboard())
        dq.set_state(message.chat.id, st.MAIN)
        dq.add_info_log(message.chat.id, 'enter_name end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'enter_name_error', error)


# CHANGE USERNAME
@bot.message_handler(commands=['change_username'])
def query_to_change_username(message):
    try:
        dq.add_info_log(message.chat.id, 'query_to_change_username begin')
        dq.set_state(message.chat.id, st.CHANGE_NAME)
        bot.send_message(message.chat.id, 'Введите ваше имя')
        dq.add_info_log(message.chat.id, 'query_to_change_username end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'query_to_change_username_error', error)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.CHANGE_NAME)
def change_name(message):
    try:
        dq.add_info_log(message.chat.id, 'change_name begin')
        dq.set_name(message.chat.id, message.text)
        bot.send_message(message.chat.id, dq.get_name(message.chat.id) + ', имя успешно изменено!',
                         reply_markup=kb.menu_keyboard())
        dq.set_state(message.chat.id, st.MAIN)
        dq.add_info_log(message.chat.id, 'change_name end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'change_name_error', error)


# Support
@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.MAIN and message.text == '❓ Техподдержка')
def support_info(message):
    bot.send_message(message.chat.id,
                     'Если у вас возникли какие-либо вопросы - обращайтесь в техподдержку, нажав кнопку ниже\n\n'
                     'Задавайте вопросы по существу 👀', reply_markup=kb.support_keyboard())
    dq.set_state(message.chat.id, st.MSG_TO_SUPPORT)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.MSG_TO_SUPPORT and
                                          message.text == '🔙 Назад')
def support_info_back(message):
    dq.set_state(message.chat.id, st.MAIN)
    bot.send_message(message.chat.id, dq.print_account_info(message.chat.id), reply_markup=kb.menu_keyboard())


@bot.message_handler(
    func=lambda message: dq.check_solver_in_db(message.chat.id) == False and message.text == '💬 Отправить запрос')
def send_message_to_support(message):
    bot.send_message(message.chat.id, 'Напишите, с чем у вас возникла проблема', reply_markup=kb.how_it_words())
    dq.set_state(message.chat.id, st.SEND_MESSAGE_TO_SUPPORT)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and
                                          dq.get_state(message.chat.id) == st.SEND_MESSAGE_TO_SUPPORT and
                                          message.text == '🔙 Назад')
def send_message_to_support_back(message):
    bot.send_message(message.chat.id,
                     'При возникновении дополнительных вопросов обращайтесь в техподдержку, нажав кнопку ниже\n\n'
                     'Задавайте вопросы по существу 👀', reply_markup=kb.support_keyboard())
    dq.set_state(message.chat.id, st.MSG_TO_SUPPORT)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and
                                          dq.get_state(message.chat.id) == st.SEND_MESSAGE_TO_SUPPORT and
                                          message.text != '🔙 Назад')
def message_text_to_support(message):
    bot.send_message(message.chat.id, 'Ваш запрос принят! \nСовсем скоро вам ответят :)',
                     reply_markup=kb.menu_keyboard())
    bot.send_message(304987403, 'SUPPORT MESSAGE FROM USER {}\nMESSAGE_TEXT: {}'.format(message.chat.id, message.text))
    dq.add_message_to_support(message.chat.id, message.text)
    dq.set_state(message.chat.id, st.MAIN)


# About us
@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.MAIN and message.text == '👋 О нас')
def about_us_info(message):
    bot.send_message(message.chat.id, 'Привет, студент 🤓'
                                      'Дедлайны горят, а задание не готово? Надоели недобросовестные исполнители?\n\n'
                                      'Мы готовы решить любую математическую задачу - алгебра, дискретная математика '
                                      'или матанализ для нас не проблема 👨🏻‍🎓\n\n'
                                      'Достаточно оставить заявку в боте и Вы получите ответ в течение 10 минут!\n\n'
                                      'Главные преимущества MathHelper - децентрализация, скорость и удобство!\n\n'
                                      'Отправка задания, подтверждение, оплата - всё в одном месте. Найти подрядчика '
                                      'легче, чем заказать еду 🍕\n\n'
                                      'Обратная связь - @dannysmirnov', reply_markup=kb.about_us_keyboard())
    dq.set_state(message.chat.id, st.ABOUT_US)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.ABOUT_US and message.text == 'ℹ️ Как работает бот?')
def how_it_words(message):
    bot.send_message(message.chat.id, 'Работа с ботом происходит предельно просто:\n\n'
                                      '1) Вы оставляете заявку, указывая тему и прикрепляя фотографию задачи\n'
                                      '2) Мы обрабатываем заявку и присылаем Вам подтверждение с ценой, предложенной исполнителем\n'
                                      '3) Вы производите оплату и подтверждаете заявку\n'
                                      '4) Наш исполнитель начинает работу и отправляет вам решение в кратчайшие сроки\n\n'
                                      '⏱ Средняя скорость обработки одной заявки составляет 10 минут'
                     , reply_markup=kb.about_us_keyboard())


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.ABOUT_US and message.text == '🔙 Назад')
def how_it_words_back(message):
    bot.send_message(message.chat.id, dq.print_account_info(message.chat.id), reply_markup=kb.menu_keyboard())
    dq.set_state(message.chat.id, st.MAIN)


# Account
@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.MAIN and message.text == '📄 Аккаунт')
def account(message):
    try:
        dq.add_info_log(message.chat.id, 'account begin')
        bot.send_message(message.chat.id, 'Информация об аккаунте ', reply_markup=kb.account_keyboard())
        dq.set_state(message.chat.id, st.ACCOUNT)
        dq.add_info_log(message.chat.id, 'account end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'account_error', error)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.ACCOUNT and message.text == '🔙 Назад')
def account_back(message):
    try:
        dq.add_info_log(message.chat.id, 'account_back begin')
        bot.send_message(message.chat.id, dq.print_account_info(message.chat.id), reply_markup=kb.menu_keyboard())
        dq.set_state(message.chat.id, st.MAIN)
        dq.add_info_log(message.chat.id, 'account_back end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'account_back_error', error)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.ACCOUNT and message.text == '📍 История заявок')
def show_list_of_tasks(message):
    try:
        dq.add_info_log(message.chat.id, 'show_list_of_tasks begin')
        bot.send_message(message.chat.id, 'История заданий',
                         reply_markup=kb.set_of_tasks_keyboard(dq.select_set_of_task(message.chat.id)))
        dq.add_info_log(message.chat.id, 'show_list_of_tasks end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'show_list_of_tasks_error', error)


@bot.callback_query_handler(func=lambda call: 'task_' in call.data)
def open_selected_task(call):
    try:
        dq.add_info_log(call.message.chat.id, 'open_selected_task begin')
        task_id = call.data.replace('task_', '')
        if dq.check_task_id_db(task_id) == True:
            task = dq.select_task(task_id)
            if task[1] == 1:
                photos = dq.get_all_photos_of_solution(task_id)
                array_of_photos = []
                for i in range(len(photos)):
                    array_of_photos.append(types.InputMediaPhoto(media=photos[i][0]))
                bot.send_media_group(call.message.chat.id, array_of_photos)
            if task[1] == 0:
                bot.send_message(call.message.chat.id, 'Задание еще не выполнено')
            if task[1] == 2:
                text_of_report = dq.get_report_text(task_id)
                bot.send_message(call.message.chat.id,
                                 'Ваше задание не было принято по следующей причине: ' + text_of_report +'\nУдалите заявку и заполните заново, все получится :)',
                                 reply_markup=kb.repeat_reported_task_keyboard(task_id))
            if task[1] == 3:

                price = dq.get_price_of_task(task_id)
                num_of_task = task_id.split('_')[1]
                bot.send_message(call.message.chat.id,
                                    'Ваше задание №{} готовы решить за {} рублей'.format(str(int(num_of_task) + 1), price),
                                    reply_markup=kb.decision_of_client_keyboard(task_id))
        else:
            bot.send_message(call.message.chat.id, 'Задание было удалено')


        dq.add_info_log(call.message.chat.id, 'open_selected_task end')
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(call.message.chat.id, 'open_selected_task_error', error)





@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.SELECTED_TASK and message.text == '🔙 Назад')
def open_selected_task_back(message):
    try:
        dq.add_info_log(message.chat.id, 'open_selected_task_back begin')
        dq.set_state(message.chat.id, st.LIST_OF_TASKS)
        show_list_of_tasks(message)
        dq.add_info_log(message.chat.id, 'open_selected_task_back end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'open_selected_task_back_error', error)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.LIST_OF_TASKS and message.text == '🔙 Назад')
def back_from_selected_task(message):
    try:
        dq.add_info_log(message.chat.id, 'back_from_selected_task begin')
        dq.set_state(message.chat.id, st.MAIN)
        welcome(message)
        dq.add_info_log(message.chat.id, 'back_from_selected_task end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'back_from_selected_task_error', error)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.SELECTED_TASK and message.text == 'Перейти в меню')
def back_to_menu(message):
    try:
        dq.add_info_log(message.chat.id, 'back_to_menu begin')
        dq.set_state(message.chat.id, st.MAIN)
        welcome(message)
        dq.add_info_log(message.chat.id, 'back_to_menu end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'back_to_menu_error', error)


# Services
@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.MAIN and message.text == '📕 Услуги')
def services(message):
    try:
        dq.add_info_log(message.chat.id, 'services begin')
        dq.set_state(message.chat.id, st.SERVICES)
        bot.send_message(message.chat.id, 'Информация о заполнении формы', reply_markup=kb.services_keyboard())
        dq.add_info_log(message.chat.id, 'services end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'services_error', error)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.SERVICES and message.text == '🔙 Назад')
def services_back(message):
    try:
        dq.add_info_log(message.chat.id, 'services_back begin')
        bot.send_message(message.chat.id, dq.print_account_info(message.chat.id), reply_markup=kb.menu_keyboard())
        dq.set_state(message.chat.id, st.MAIN)
        dq.add_info_log(message.chat.id, 'services_back end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'services_back_error', error)


# Homework

# @bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
#     message.chat.id) == st.SERVICES and message.text == '📍 Оставить заявку')
# def create_task(message):
#     try:
#         dq.add_info_log(message.chat.id, 'create_task begin')
#         bot.send_message(message.chat.id, 'Введите количество заданий',
#                          reply_markup=telebot.types.ReplyKeyboardRemove())
#         dq.create_task_id(message.chat.id)
#         dq.set_state(message.chat.id, st.HOMEWORK_NUMBER)
#         dq.add_info_log(message.chat.id, 'create_task end')
#     except Exception as error:
#         bot.send_message(message.chat.id,
#                          'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
#         dq.add_error_log(message.chat.id, 'create_task_error', error)
#
#
# def check_isdigit(message):
#     if type(message) == str:
#         if str.isdigit(message) == True:
#             return True
#     return False


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.SERVICES and message.text == '📍 Оставить заявку')
def complete_num_of_task(message):
    try:
        dq.add_info_log(message.chat.id, 'complete_num_of_task begin')
        bot.send_message(message.chat.id, 'Введите тему задания', reply_markup=telebot.types.ReplyKeyboardRemove())
        dq.create_task_id(message.chat.id)
        dq.set_state(message.chat.id, st.HOMEWORK_THEME)
        dq.add_info_log(message.chat.id, 'complete_num_of_task end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'complete_num_of_task_error', error)


# @bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
#     message.chat.id) == st.HOMEWORK_NUMBER and not check_isdigit(message.text))
# def incomplete_num_of_task(message):
#     bot.send_message(message.chat.id, 'Неверный ввод, введите количество заданий')


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.HOMEWORK_THEME)
def complete_theme_of_task(message):
    try:
        dq.add_info_log(message.chat.id, 'complete_theme_of_task begin')
        bot.send_message(message.chat.id, 'Отправьте фотографию задания')
        dq.add_theme_of_problems(message.chat.id, message.text)
        dq.set_state(message.chat.id, st.HOMEWORK_TASK)
        dq.add_info_log(message.chat.id, 'complete_theme_of_task end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'complete_theme_of_task_error', error)


# @bot.callback_query_handler(func=lambda call: dq.check_solver_in_db(call.message.chat.id) == False and dq.get_state(
#     call.message.chat.id) == st.HOMEWORK_DIFFICULT)
# def complete_difficulty_of_task(call):
#     try:
#
#         dq.add_info_log(call.message.chat.id, 'complete_difficulty_of_task begin')
#         bot.send_message(call.message.chat.id, 'Выбрана сложность: ' + str(call.data) + ', отправьте фото задания')
#         dq.add_difficulty_of_problems(call.message.chat.id, call.data)
#         dq.set_state(call.message.chat.id, st.HOMEWORK_TASK)
#         dq.add_info_log(call.message.chat.id, 'complete_difficulty_of_task end')
#     except Exception as error:
#         bot.send_message(call.message.chat.id,
#                          'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
#         dq.add_error_log(call.message.chat.id, 'complete_difficulty_of_task_error', error)


@bot.message_handler(content_types=['photo'])
def complete_photo_of_task(message):
    try:
        dq.add_info_log(message.chat.id, 'complete_photo_of_task begin')
        if dq.check_solver_in_db(message.chat.id) == False:
            if dq.get_state(message.chat.id) == st.HOMEWORK_TASK:
                bot.send_message(message.chat.id, 'Оставьте комментарий к заявке')
                photo_id = bot.get_file(message.photo[-1].file_id).file_id
                dq.add_photo_of_problems(message.chat.id, photo_id)
                dq.set_state(message.chat.id, st.HOMEWORK_COMMENT)
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
        dq.add_info_log(message.chat.id, 'complete_photo_of_task end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'complete_photo_of_task_error', error)


def send_full_task(message):
    try:
        dq.add_info_log(message.chat.id, 'send_full_task begin')
        dq.set_state(message.chat.id, st.CHECKING_TASK)
        text_of_task = dq.task_completed_message(message.chat.id)
        bot.send_photo(message.chat.id, dq.get_photo_of_problems(message.chat.id), caption=text_of_task,
                       reply_markup=kb.change_task_keyboard())
        dq.add_info_log(message.chat.id, 'send_full_task end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'send_full_task_error', error)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.HOMEWORK_COMMENT)
def complete_comment_of_task(message):
    try:
        dq.add_info_log(message.chat.id, 'complete_comment_of_task begin')
        dq.add_comment_of_problems(message.chat.id, message.text)
        send_full_task(message)
        dq.add_info_log(message.chat.id, 'complete_comment_of_task end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'complete_comment_of_task_error', error)


@bot.callback_query_handler(func=lambda call: call.data == 'num_of_tasks')
def change_num_of_tasks(call):
    try:
        dq.add_info_log(call.message.chat.id, 'change_num_of_tasks begin')
        bot.send_message(call.message.chat.id, 'Введите количество заданий')
        dq.set_state(call.message.chat.id, st.CHANGE_NUMBER)
        dq.add_info_log(call.message.chat.id, 'change_num_of_tasks end')
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(call.message.chat.id, 'change_num_of_tasks_error', error)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.CHANGE_NUMBER and str.isdigit(message.text))
def set_changed_num_of_tasks(message):
    try:
        dq.add_info_log(message.chat.id, 'set_changed_num_of_tasks begin')
        dq.add_number_of_problems(message.chat.id, message.text)
        send_full_task(message)
        dq.add_info_log(message.chat.id, 'set_changed_num_of_tasks end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'set_changed_num_of_tasks_error', error)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.CHANGE_NUMBER and not str.isdigit(message.text))
def set_changed_num_of_tasks(message):
    bot.send_message(message.chat.id, 'Неверный ввод, введите количество заданий')


@bot.callback_query_handler(func=lambda call: call.data == 'theme_of_task')
def change_theme_of_tasks(call):
    try:
        dq.add_info_log(call.message.chat.id, 'change_theme_of_tasks begin')
        bot.send_message(call.message.chat.id, 'Введите тему задания')
        dq.set_state(call.message.chat.id, st.CHANGE_THEME)
        dq.add_info_log(call.message.chat.id, 'change_theme_of_tasks end')
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(call.message.chat.id, 'change_theme_of_tasks_error', error)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.CHANGE_THEME)
def set_changed_theme_of_tasks(message):
    try:
        dq.add_info_log(message.chat.id, 'set_changed_theme_of_tasks begin')
        dq.add_theme_of_problems(message.chat.id, message.text)
        send_full_task(message)
        dq.add_info_log(message.chat.id, 'set_changed_theme_of_tasks end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'set_changed_theme_of_tasks_error', error)


@bot.callback_query_handler(func=lambda call: call.data == 'difficult_of_task')
def change_difficult_of_tasks(call):
    try:
        dq.add_info_log(call.message.chat.id, 'change_difficult_of_tasks begin')
        bot.send_message(call.message.chat.id, 'Выберите сложность задания', reply_markup=kb.difficulty_keyboard())
        dq.set_state(call.message.chat.id, st.CHANGE_DIFFICULT)
        dq.add_info_log(call.message.chat.id, 'change_difficult_of_tasks end')
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(call.message.chat.id, 'change_difficult_of_tasks_error', error)


@bot.callback_query_handler(func=lambda call: dq.check_solver_in_db(call.message.chat.id) == False and dq.get_state(
    call.message.chat.id) == st.CHANGE_DIFFICULT)
def set_changed_difficult_of_tasks(call):
    try:
        dq.add_info_log(call.message.chat.id, 'set_changed_difficult_of_tasks begin')
        dq.add_difficulty_of_problems(call.message.chat.id, call.data)
        send_full_task(call.message)
        dq.add_info_log(call.message.chat.id, 'set_changed_difficult_of_tasks end')
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(call.message.chat.id, 'set_changed_difficult_of_tasks_error', error)


@bot.callback_query_handler(func=lambda call: call.data == 'photo_of_task')
def change_photo_of_tasks(call):
    try:
        dq.add_info_log(call.message.chat.id, 'change_photo_of_tasks begin')
        bot.send_message(call.message.chat.id, 'Отправьте фото задания')
        dq.set_state(call.message.chat.id, st.CHANGE_TASK)
        dq.add_info_log(call.message.chat.id, 'change_photo_of_tasks end')
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(call.message.chat.id, 'change_photo_of_tasks_error', error)


@bot.callback_query_handler(func=lambda call: call.data == 'comment_of_task')
def change_comment_of_tasks(call):
    try:
        dq.add_info_log(call.message.chat.id, 'change_comment_of_tasks begin')
        bot.send_message(call.message.chat.id, 'Оставьте комментарий к заявке')
        dq.set_state(call.message.chat.id, st.CHANGE_COMMENT)
        dq.add_info_log(call.message.chat.id, 'change_comment_of_tasks end')
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(call.message.chat.id, 'change_comment_of_tasks_error', error)


@bot.message_handler(func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(
    message.chat.id) == st.CHANGE_COMMENT)
def set_changed_comment_of_tasks(message):
    try:
        dq.add_info_log(message.chat.id, 'set_changed_comment_of_tasks begin')
        dq.add_comment_of_problems(message.chat.id, message.text)
        send_full_task(message)
        dq.add_info_log(message.chat.id, 'set_changed_comment_of_tasks end')
    except Exception as error:
        bot.send_message(message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(message.chat.id, 'set_changed_comment_of_tasks_error', error)


@bot.callback_query_handler(func=lambda call: call.data == 'complete_task')
def completed_task(call):
    try:
        dq.add_info_log(call.message.chat.id, 'completed_task begin')
        bot.send_message(call.message.chat.id, 'Ваша заявка принята, ожидайте ее подтверждения',
                         reply_markup=kb.menu_keyboard())
        task_id = dq.complete_task(call.message.chat.id)
        send_task_to_solvers(task_id)
        dq.set_state(call.message.chat.id, st.MAIN)
        dq.add_info_log(call.message.chat.id, 'completed_task end')
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as error:
        bot.send_message(call.message.chat.id,
                         'Произошла ошибка. \nВведите команду /start, чтобы вернуться в начало \nМы скоро все исправим! ')
        dq.add_error_log(call.message.chat.id, 'completed_task_error', error)


# Add money
@bot.message_handler(
    func=lambda message: dq.check_solver_in_db(message.chat.id) == False and dq.get_state(message.chat.id) in [
        st.SERVICES, st.ACCOUNT] and message.text == '💰 Пополнить баланс')
def add_money(message):
    bot.send_message(message.chat.id, 'Пополнение счета')



@bot.message_handler(func = lambda message: 'admin' in message.text and message.chat.id == 304987403)
def send_message_to_user_with_admin(message):
    user_id = message.text.split()[1]
    text = message.text.replace('admin {} '.format(user_id), '')
    bot.send_message(user_id, 'Ответ от администрации:\n'+text, disable_notification=True)



bot.infinity_polling(timeout=0, long_polling_timeout=0)
