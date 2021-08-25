import sqlite3
from datetime import datetime


def check_user_in_db(user_id):  # Проверка наличия пользователя в базе данных
    con = sqlite3.connect('bot_database.db')  # Возвращает True, если пользователь есть в бд, иначе False
    cursor = con.cursor()
    a = cursor.execute("SELECT * FROM client WHERE user_id = (?)", (user_id,))
    if a.fetchall() == []:
        con.close()
        return False
    con.close()
    return True


def get_state(user_id):  # Получает состояние пользователя на данный момент
    con = sqlite3.connect('bot_database.db')  # Возвращается число, которое связано с каким-либо состоянием
    cursor = con.cursor()
    a = cursor.execute("SELECT state FROM client WHERE user_id = (?)", (user_id,)).fetchone()
    con.close()
    return a[0]


def set_state(user_id, state):  # Записывает новое состояние пользователя в базу данных
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE client SET state = (?) WHERE user_id = (?)", (state, user_id))
        con.commit()
        con.close()
    except:
        con.close()
        print('state_error')


def get_name(user_id):  # Получить имя пользователя по заданному user_id
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT name FROM client WHERE user_id = (?)", (user_id,)).fetchone()
    con.close()
    return a[0]


def add_client(user_id):  # Регистрация пользователя, добавление его user_id в бд
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("INSERT INTO client(user_id, referal_code) VALUES (?, ?)", (user_id, user_id))
        con.commit()
        con.close()
    except:
        con.close()
        print('add_client_error')


def set_name(user_id, user_name):  # Регистрация пользователя, добавление его имени и user_id в бд
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE client SET name = (?) WHERE user_id = (?)", (user_name, user_id))
        con.commit()
        con.close()
    except:
        con.close()
        print('add_name_error')


def print_account_info(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT name, balance, number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()
    con.close()
    return 'Имя: ' + str(a[0]) + '\nБаланс: ' + str(a[1]) + '\nКоличество заказов: ' + str(a[2])


def increment_num_of_tasks(user_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        num_of_tasks = cursor.execute('SELECT number_of_tasks FROM client WHERE user_id = (?)', (user_id,)).fetchone()[
            0]
        num_of_tasks += 1
        cursor.execute("UPDATE client SET number_of_tasks = (?) WHERE user_id = (?)", (num_of_tasks, user_id))
        con.commit()
        con.close()
    except Exception as e:
        print(e)
        con.close()
        print('increment_num_of_tasks_error')


def decrement_num_of_tasks(user_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        num_of_tasks = cursor.execute('SELECT number_of_tasks FROM client WHERE user_id = (?)', (user_id,)).fetchone()[
            0]
        num_of_tasks += -1
        cursor.execute("UPDATE client SET number_of_tasks = (?) WHERE user_id = (?)", (num_of_tasks, user_id))
        con.commit()
        con.close()
    except Exception as e:
        print(e)
        con.close()
        print('decrement_num_of_tasks_error')


def check_task_in_db(user_id):
    con = sqlite3.connect('bot_database.db')  # Возвращает True, если пользователь есть в бд, иначе False
    cursor = con.cursor()
    num_of_tasks = cursor.execute('SELECT number_of_tasks FROM client WHERE user_id = (?)', (user_id,)).fetchone()[0]
    task_id = str(user_id) + '_' + str(num_of_tasks)
    a = cursor.execute("SELECT * FROM tasks WHERE task_id = (?)", (task_id,))
    if a.fetchall() == []:
        con.close()
        return False
    con.close()
    return True


def create_task_id(user_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        num_of_tasks = cursor.execute("SELECT number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()[
            0]
        task_id = str(user_id) + '_' + str(num_of_tasks)
        if check_task_in_db(user_id) == False:
            cursor.execute("INSERT INTO tasks(task_id, user_id) VALUES (?, ?)", (task_id, user_id))
        con.commit()
        con.close()
    except:
        con.close()
        print('create_task_id_error')


def add_number_of_problems(user_id, num_of_problems):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        num_of_tasks = cursor.execute("SELECT number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()[
            0]
        task_id = str(user_id) + '_' + str(num_of_tasks)
        cursor.execute("UPDATE tasks SET num_of_problems = (?) WHERE task_id = (?)", (num_of_problems, task_id))
        con.commit()
        con.close()
    except:
        con.close()
        print('add_number_of_problems_error')


def get_number_of_problems(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    num_of_tasks = cursor.execute("SELECT number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()[0]
    task_id = str(user_id) + '_' + str(num_of_tasks)
    a = cursor.execute("SELECT num_of_problems FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]


def add_theme_of_problems(user_id, theme_of_task):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        num_of_tasks = cursor.execute("SELECT number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()[
            0]
        task_id = str(user_id) + '_' + str(num_of_tasks)
        cursor.execute("UPDATE tasks SET theme_of_task = (?) WHERE task_id = (?)", (theme_of_task, task_id))
        con.commit()
        con.close()
    except:
        con.close()
        print('add_theme_of_problems_error')


def get_theme_of_problems(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    num_of_tasks = cursor.execute("SELECT number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()[0]
    task_id = str(user_id) + '_' + str(num_of_tasks)
    a = cursor.execute("SELECT theme_of_task FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]


def add_difficulty_of_problems(user_id, difficulty_of_task):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        num_of_tasks = cursor.execute("SELECT number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()[
            0]
        task_id = str(user_id) + '_' + str(num_of_tasks)
        cursor.execute("UPDATE tasks SET difficulty_of_task = (?) WHERE task_id = (?)", (difficulty_of_task, task_id))
        con.commit()
        con.close()
    except Exception as e:
        print(e)
        con.close()
        print('add_difficulty_of_problems_error')


def get_difficulty_of_problems(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    num_of_tasks = cursor.execute("SELECT number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()[0]
    task_id = str(user_id) + '_' + str(num_of_tasks)
    a = cursor.execute("SELECT difficulty_of_task FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]


def add_photo_of_problems(user_id, photo_url):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        num_of_tasks = cursor.execute("SELECT number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()[
            0]
        task_id = str(user_id) + '_' + str(num_of_tasks)
        cursor.execute("UPDATE tasks SET picture_of_task = (?) WHERE task_id = (?)", (photo_url, task_id))
        con.commit()
        con.close()
    except:
        con.close()
        print('add_photo_of_problems_error')


def get_photo_of_problems(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    num_of_tasks = cursor.execute("SELECT number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()[0]
    task_id = str(user_id) + '_' + str(num_of_tasks)
    a = cursor.execute("SELECT picture_of_task FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]


def add_comment_of_problems(user_id, comment):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        num_of_tasks = cursor.execute("SELECT number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()[
            0]
        task_id = str(user_id) + '_' + str(num_of_tasks)
        cursor.execute("UPDATE tasks SET comment = (?) WHERE task_id = (?)", (comment, task_id))
        con.commit()
        con.close()
    except:
        con.close()
        print('add_comment_of_problems_error')


def get_comment_of_problems(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    num_of_tasks = cursor.execute("SELECT number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()[0]
    task_id = str(user_id) + '_' + str(num_of_tasks)
    a = cursor.execute("SELECT comment FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]


def complete_task(user_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        num_of_tasks = cursor.execute("SELECT number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()[
            0]
        task_id = str(user_id) + '_' + str(num_of_tasks)
        cursor.execute("UPDATE tasks SET success_of_request = (?) WHERE task_id = (?)", (True, task_id))
        num_of_tasks = cursor.execute('SELECT number_of_tasks FROM client WHERE user_id = (?)', (user_id,)).fetchone()[
            0]
        num_of_tasks += 1
        cursor.execute("UPDATE client SET number_of_tasks = (?) WHERE user_id = (?)", (num_of_tasks, user_id))
        con.commit()
        con.close()
        return task_id
    except:
        con.close()
        print('complete_task_error')

def get_current_task_id(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    num_of_tasks = cursor.execute("SELECT number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()[
        0]
    task_id = str(user_id) + '_' + str(num_of_tasks)
    con.commit()
    con.close()
    return task_id

def task_completed_message(user_id):
    text_of_task = ''
    # text_of_task += 'Количество заданий: ' + str(get_number_of_problems(user_id)) + '\n'
    text_of_task += 'Тема заданий: ' + str(get_theme_of_problems(user_id)) + '\n'
    text_of_task += 'Комментарий: ' + str(get_comment_of_problems(user_id)) + '\n'
    return text_of_task


def select_set_of_task(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    tasks = cursor.execute("SELECT task_id, status_of_solution, date_of_creating FROM (SELECT * FROM tasks ORDER BY date_of_creating DESC)"
                           "WHERE user_id = (?)",
                           (user_id,)).fetchall()
    con.commit()
    con.close()
    return tasks




def select_task(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    task = cursor.execute(
        "SELECT num_of_problems, status_of_solution, date_of_solution, task_id FROM tasks WHERE task_id = (?)",
        (task_id,)).fetchone()
    con.commit()
    con.close()
    return task


def add_solver_in_db(user_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("INSERT INTO solver(user_id) VALUES (?)", (user_id,))
        con.commit()
        con.close()
    except:
        con.close()
        print('registration_error')


def check_solver_in_db(user_id):
    con = sqlite3.connect('bot_database.db')  # Возвращает True, если пользователь есть в бд, иначе False
    cursor = con.cursor()
    a = cursor.execute("SELECT * FROM solver WHERE user_id = (?)", (user_id,))
    if a.fetchall() == []:
        con.close()
        return False
    con.close()
    return True

def check_photo_of_task(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    num_of_tasks = cursor.execute("SELECT number_of_tasks FROM client WHERE user_id = (?)", (user_id,)).fetchone()[
        0]
    task_id = str(user_id) + '_' + str(num_of_tasks)
    a = cursor.execute("SELECT picture_of_task FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    if a[0] == None:
        con.close()
        return False
    con.close()
    return True

def check_name_of_user(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT name FROM client WHERE user_id = (?)", (user_id,)).fetchone()
    if a[0] == None:
        con.close()
        return False
    con.close()
    return True


def set_solver_state(user_id, state):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE solver SET state = (?) WHERE user_id = (?)", (state, user_id))
        con.commit()
        con.close()
    except:
        con.close()
        print('state_error')


def get_solver_state(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT state FROM solver WHERE user_id = (?)", (user_id,)).fetchone()
    con.close()
    return a[0]


def set_solver_name(user_id, user_name):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE solver SET name = (?) WHERE user_id = (?)", (user_name, user_id))
        con.commit()
        con.close()
    except:
        con.close()
        print('add_name_error')


def get_solver_name(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT name FROM solver WHERE user_id = (?)", (user_id,)).fetchone()
    con.close()
    return a[0]


def get_solvers_id():
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT user_id FROM solver").fetchall()
    con.close()
    return a

def get_solvers_from_selected_group(group):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT user_id FROM solver WHERE num_of_group = (?)", (group,)).fetchall()
    con.close()
    return a

def add_error_to_error_list(user_id, name_of_function, error_text):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("INSERT INTO error_list(user_id, name_of_function, error_text) VALUES (?, ?, ?)", (user_id, name_of_function, error_text))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(str(error))

def add_solver_profit_made(solver_id, price):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE solver SET profit_made = profit_made + (?) WHERE user_id = (?)", (price, solver_id))
        con.commit()
        con.close()
    except:
        con.close()
        print('add_name_error')


def get_num_of_next_group(task_id):
    num_of_groups = int(get_num_of_groups())
    current_group = int(get_group_of_task(task_id))
    current_group = (current_group + 1) % num_of_groups
    return current_group


def save_sended_task(message_id, task_id, solver_id, group):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("INSERT INTO messages_of_task(message_id, task_id, solver_id, num_of_group) VALUES(?, ?, ?, ?)",
                       (message_id, task_id, solver_id, group))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print('save_sended_task_error', error)


def get_message_id(task_id, solver_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute(
        "SELECT message_id FROM (SELECT * FROM messages_of_task ORDER BY time_of_message DESC) WHERE task_id = (?) and solver_id = (?)",
        (task_id, solver_id)).fetchone()
    con.close()
    if a != None:
        return a[0]
    else:
        return None


def get_num_of_task(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT num_of_problems FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]


def get_theme_of_task(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT theme_of_task FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]


def get_difficulty_of_task(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT difficulty_of_task FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]

def get_current_group():
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT current_group FROM groups").fetchone()
    con.close()
    return a[0]

def get_num_of_groups():
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT num_of_groups FROM groups").fetchone()
    con.close()
    return a[0]

def set_number_of_groups(number):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE groups SET num_of_groups = (?)", (number,))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print('increment'+str(error))

def increment_current_group():
    try:
        num_of_groups = int(get_num_of_groups())
        current_group = int(get_current_group())
        current_group = (current_group+1)%num_of_groups
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE groups SET current_group = (?)", (current_group,))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print('increment'+str(error))


def get_picture_of_task(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT picture_of_task FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]


def get_comment_of_task(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT comment FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]


def task_message_deleted(message_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("DELETE FROM messages_of_task WHERE message_id = (?)", (message_id,))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def set_current_task(solver_id, task_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE solver SET current_task_id = (?) WHERE user_id = (?)", (task_id, solver_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def get_current_task(solver_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT current_task_id FROM solver WHERE user_id = (?)", (solver_id,)).fetchone()
    con.close()
    return a[0]


def task_completed_message_for_solver(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    text = ''
    text += 'Номер задания: ' + str(task_id) + '\n'
    # text += 'Количество заданий: ' + str(get_num_of_task(task_id)) + '\n'
    text += 'Тема задания: ' + str(get_theme_of_task(task_id)) + '\n'
    text += 'Комментарий: ' + str(get_comment_of_task(task_id)) + '\n'
    con.close()
    return text


def get_num_of_sended_photos(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT COUNT (*) FROM photos_of_solutions WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]

def get_num_of_solution_photos(solver_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT current_photo_sended FROM solver WHERE user_id = (?)", (solver_id,)).fetchone()
    con.close()
    return a[0]


def refresh_num_of_sended_photos(solver_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE solver SET current_photo_sended = 0 WHERE user_id = (?)", (solver_id,))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def increment_num_of_sended_photos(solver_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE solver SET current_photo_sended = current_photo_sended + 1 WHERE user_id = (?)",
                       (solver_id,))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def add_photo_of_solution(solver_id, photo):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        task_id = get_current_task(solver_id)
        photo_id = str(task_id) + '_' + str(get_num_of_solution_photos(solver_id))
        increment_num_of_sended_photos(solver_id)
        cursor.execute("INSERT INTO photos_of_solutions(photo_id, task_id, photo) VALUES (?, ?, ?)",
                       (photo_id, task_id, photo))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def get_all_photos_of_solution(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT photo FROM photos_of_solutions WHERE task_id = (?)", (task_id,)).fetchall()
    con.close()
    return a


def set_status_of_solution(task_id, status):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE tasks SET status_of_solution = (?) WHERE task_id = (?)", (status, task_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def delete_solver_from_user_db(user_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("DELETE FROM client WHERE user_id = (?)", (user_id,))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def add_info_log(user_id, text):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("INSERT INTO logs(user_id, text_of_log, type_of_log) VALUES (?, ?, ?)", (user_id, text, 'info'))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def add_error_log(user_id, text, error):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        error_name = str(error)
        cursor.execute("INSERT INTO logs(user_id, text_of_log, type_of_log, error_name) VALUES (?, ?, ?, ?)",
                       (user_id, text, 'error', error_name))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def set_solution_time(task_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE tasks SET date_of_solution = (?) WHERE task_id = (?)", (date_time, task_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def get_solution_time(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT date_of_solution FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]


def set_task_solver_id(task_id, solver_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE tasks SET solver_id = (?) WHERE task_id = (?)", (solver_id, task_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def get_today_solutions_of_solver(solver_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT price_of_task FROM tasks WHERE date(date_of_solution) = date('now') and solver_id = (?)",
                       (solver_id,)).fetchall()
    con.close()
    return a

def get_yesterday_solutions_of_solver(solver_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT price_of_task FROM tasks WHERE date(date_of_solution) = date('now','-1 day') and solver_id = (?)",
                       (solver_id,)).fetchall()
    con.close()
    return a


def set_reporting_task(solver_id, task_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE solver SET reporting_task_id = (?) WHERE user_id = (?)", (task_id, solver_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def get_reporting_task(solver_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT reporting_task_id FROM solver WHERE user_id = (?)", (solver_id,)).fetchone()
    con.close()
    return a[0]


def set_report_text(task_id, text):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE tasks SET task_report_text = (?) WHERE task_id = (?)", (text, task_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def get_report_text(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT task_report_text FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]


def report_task(task_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE tasks SET status_of_solution = (?) WHERE task_id = (?)", (2, task_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def set_price_of_task(task_id, price):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE tasks SET price_of_task = (?) WHERE task_id = (?)", (price, task_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def get_price_of_task(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT price_of_task FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]


def get_balance_of_user(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT balance FROM client WHERE user_id = (?)", (user_id,)).fetchone()
    con.close()
    return a[0]


def set_balance_of_user(balance, user_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE client SET balance = (?) WHERE user_id = (?)", (balance, user_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def get_solver_of_task(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT solver_id FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]


def add_message_to_support(user_id, text):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("INSERT INTO messages_to_support(user_id, text_of_message) VALUES (?, ?)", (user_id, text))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)

def set_time_of_accept(task_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE tasks SET time_of_accept = (?) WHERE task_id = (?)", (date_time, task_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def get_list_of_paid_tasks(solver_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT task_id, price_of_task, time_of_accept FROM tasks WHERE solver_id = (?) and status_of_solution = 5", (solver_id,)).fetchall()
    con.close()
    return a



def get_list_of_unpaid_tasks(solver_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT task_id, price_of_task FROM tasks WHERE solver_id = (?) and status_of_solution = 3 and "
                       "date(date_of_creating) > date('now', '-1 days') and date(date_of_creating) <= date('now')", (solver_id,)).fetchall()
    con.close()
    return a

def get_list_of_solved_task(solver_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT task_id, price_of_task FROM tasks WHERE solver_id = (?) and status_of_solution = 1 and "
                       "date(date_of_creating) > date('now', '-1 days') and date(date_of_creating) <= date('now')",
                       (solver_id,)).fetchall()
    con.close()
    return a

def delete_selected_task(task_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("DELETE FROM tasks WHERE task_id = (?)", (task_id,))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)

def delete_all_photos_of_solution(task_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("DELETE FROM photos_of_solutions WHERE task_id = (?)", (task_id,))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def get_status_of_solution(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT status_of_solution FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]

def check_task_id_db(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT * FROM tasks WHERE task_id = (?)", (task_id,))
    if a.fetchall() == []:
        con.close()
        return False
    con.close()
    return True

def get_last_five_users():
    con = sqlite3.connect('bot_database.db')  # Возвращает True, если пользователь есть в бд, иначе False
    cursor = con.cursor()
    a = cursor.execute('SELECT name, user_id, balance FROM (SELECT * FROM client ORDER BY date_of_registration DESC LIMIT 5)').fetchall()
    con.close()
    return a

def add_money_to_user(user_id, money):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE client SET balance = balance + (?) WHERE user_id = (?)", (money, user_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)

def set_rotating_task_id(solver_id, task_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE solver SET rotating_task_id = (?) WHERE user_id = (?)", (task_id, solver_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)

def get_rotating_task_id(solver_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT rotating_task_id FROM solver WHERE user_id = (?)", (solver_id,)).fetchone()
    con.close()
    return a[0]

def set_group_of_task(task_id, group):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE tasks SET num_of_group = (?) WHERE task_id = (?)", (group, task_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)

def get_group_of_task(task_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT num_of_group FROM tasks WHERE task_id = (?)", (task_id,)).fetchone()
    con.close()
    return a[0]


def set_question_task_id(user_id, task_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE client SET question_task_id = (?) WHERE user_id = (?)", (task_id, user_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)

def get_question_task_id(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT question_task_id FROM client WHERE user_id = (?)", (user_id,)).fetchone()
    con.close()
    return a[0]


def set_answer_task_id(user_id, task_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE solver SET answer_task_id = (?) WHERE user_id = (?)", (task_id, user_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)

def get_answer_task_id(user_id):
    con = sqlite3.connect('bot_database.db')
    cursor = con.cursor()
    a = cursor.execute("SELECT answer_task_id FROM solver WHERE user_id = (?)", (user_id,)).fetchone()
    con.close()
    return a[0]

def set_solver_group(user_id, group):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE solver SET num_of_group = (?) WHERE user_id = (?)", (group, user_id))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def get_list_of_solvers():
    con = sqlite3.connect('bot_database.db')  # Возвращает True, если пользователь есть в бд, иначе False
    cursor = con.cursor()
    a = cursor.execute(
        'SELECT name, user_id, num_of_group FROM solver').fetchall()
    con.close()
    return a

def ban_list():
    con = sqlite3.connect('bot_database.db')  # Возвращает True, если пользователь есть в бд, иначе False
    cursor = con.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS ban_list (user_id BIGINT PRIMARY KEY);')
    con.close()

def payment_list():
    con = sqlite3.connect('bot_database.db')  # Возвращает True, если пользователь есть в бд, иначе False
    cursor = con.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS payments (user_id BIGINT, amount BIGINT, time_of_message '
                   'TIME DEFAULT (CURRENT_TIMESTAMP));')
    con.close()

def add_user_to_ban_list(user_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("INSERT INTO ban_list(user_id) VALUES (?)", (user_id,))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)

def remove_user_to_ban_list(user_id):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("DELETE FROM ban_list WHERE user_id = (?)", (user_id,))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def check_user_in_ban_list(user_id):  # Проверка наличия пользователя в базе данных
    try:
        con = sqlite3.connect('bot_database.db')  # Возвращает True, если пользователь есть в бд, иначе False
        cursor = con.cursor()
        a = cursor.execute("SELECT * FROM ban_list WHERE user_id = (?)", (user_id,))
        if a.fetchall() == []:
            con.close()
            return False
        con.close()
        return True
    except Exception as error:
        con.close()
        print(error)


def check_task_in_task_list(task_id):
    try:
        con = sqlite3.connect('bot_database.db')  # Возвращает True, если пользователь есть в бд, иначе False
        cursor = con.cursor()
        a = cursor.execute("SELECT * FROM tasks WHERE task_id = (?)", (task_id,))
        if a.fetchall() == []:
            con.close()
            return False
        con.close()
        return True
    except Exception as error:
        con.close()
        print(error)


def add_payment_in_database(user_id, amount):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("INSERT INTO payments(user_id, amount) VALUES (?, ?)", (user_id, amount))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def create_key_for_registration_table():
    con = sqlite3.connect('bot_database.db')  # Возвращает True, если пользователь есть в бд, иначе False
    cursor = con.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS key (key_for_registration STRING);')
    con.close()


def set_key_for_registration(key):
    try:
        con = sqlite3.connect('bot_database.db')
        cursor = con.cursor()
        cursor.execute("UPDATE key SET key_for_registration = (?)", (key,))
        con.commit()
        con.close()
    except Exception as error:
        con.close()
        print(error)


def get_key_for_registration():
    con = sqlite3.connect('bot_database.db')  # Возвращает True, если пользователь есть в бд, иначе False
    cursor = con.cursor()
    a = cursor.execute('SELECT key_for_registration FROM key').fetchone()
    con.close()
    return a[0]

def count_today_users():
    con = sqlite3.connect('bot_database.db')  # Возвращает True, если пользователь есть в бд, иначе False
    cursor = con.cursor()
    a = cursor.execute("SELECT COUNT(*) FROM client WHERE date(date_of_registration) = date('now')").fetchone()
    con.close()
    return a[0]

def money_on_user_balances():
    con = sqlite3.connect('bot_database.db')  # Возвращает True, если пользователь есть в бд, иначе False
    cursor = con.cursor()
    a = cursor.execute("SELECT SUM(balance) FROM client").fetchone()
    con.close()
    return a[0]

def today_payments():
    con = sqlite3.connect('bot_database.db')  # Возвращает True, если пользователь есть в бд, иначе False
    cursor = con.cursor()
    a = cursor.execute("SELECT SUM(amount) FROM payments WHERE date(time_of_message) = date('now')").fetchone()
    con.close()
    return a[0]

# def change_solver_status():
#     try:
#         con = sqlite3.connect('bot_database.db')
#         cursor = con.cursor()
#         cursor.execute("UPDATE solver SET CASE WHEN status = True ")
#         con.commit()
#         con.close()
#     except Exception as error:
#         con.close()
#         print(error)