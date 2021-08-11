START = 0  # Регистрация юзера, статус после /start
ENTER_NAME = 1  # При отсутствии регистрации или после /change_name
MAIN = 2  # После успешной регистрации или при выходе в главное меню
CHANGE_NAME = 3  # После команды /change_name
ABOUT_US = 4  # После нажатия на поле "О нас"
REVIEWS = 5  # Отзывы от пользователей, пока под вопросом
WRITE_REVIEW = 6  # Оставить отзыв, под вопросом
SUPPORT = 7  # Поле с информацией об обращении в support
MSG_TO_SUPPORT = 8  # Контакты для связи
REFUND_INFO = 9  # Условия, при которых совершается возврат денег
ACCOUNT = 10  # Личная страница пользователя, количество заданий/история задания/баланс
TASK_HISTORY = 11  # История всех заданий пользователя, даты, готовность
CHOSEN_TASK = 12  # Выбор определенного задания
REFERAL_CODE = 13  # Реферальный код юзера, как им воспользоваться
ENTER_REFERAL_CODE = 14  # Ввод реферального кода
SERVICES = 15  # Услуги, предоставляемые ботом
ADD_MONEY = 16  # Форма пополнения баланса, баланс пользователя
HOMEWORK = 17  # Создать заказ формата "Домашняя работа"
CLASSWORK = 18  # Создать заказ формата "Контрольная работа"
TUTOR = 19  # Создать заказ формата "Репетитор"
HOMEWORK_COMPLETE = 20  # Успешно созданный заказ формата "Домашняя работа", информация о готовности
HOMEWORK_WRONG = 21  # Неверно созданный заказ формата "Домашняя работа", причины
CLASSWORK_COMPLETE = 22  # Успешно созданный заказ формата "Контрольная работа", информация о готовности
CLASSWORK_WRONG = 23  # Неверно созданный заказ формата "Контрольная работа", причина
TUTOR_COMPLETE = 24  # Успешно созданный заказ формата "Репетитор", время ожидания ответа
TUTOR_WRONG = 25  # Неверно созданный заказ формата "Репетитор", причина

HOMEWORK_NUMBER = 26
HOMEWORK_THEME = 27
HOMEWORK_DIFFICULT = 28
HOMEWORK_TASK = 29
HOMEWORK_COMMENT = 30
HOMEWORK_COMPLETE = 31

CHANGE_NUMBER = 32
CHANGE_THEME = 33
CHANGE_DIFFICULT = 34
CHANGE_TASK = 35
CHANGE_COMMENT = 36

CHECKING_TASK = 37

LIST_OF_TASKS = 38
SELECTED_TASK = 39

SEND_MESSAGE_TO_SUPPORT = 40

SEND_AMOUNT = 41

ASK_QUESTION = 42

solver_START = 0
solver_REGISTRATION = 1
solver_MAIN = 2
solver_ENTER_NAME = 3
solver_CHANGE_STATUS = 4
solver_SOLVING = 5
solver_SENDING_SOLUTION = 6
solver_GET_REPORT_MESSAGE = 7
solver_ANSWER_QUESTION=8
