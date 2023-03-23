import telebot
import time
from telebot import types
import sqlite3

con = sqlite3.connect("server.db")
bot = telebot.TeleBot('5844570225:AAHVbCClhE53DdtM-RpZ1vKjrPPB4j_I538')
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()


def db_table_val(user_id: int, user_name: str, user_status: str, username: str):
    cursor.execute('INSERT INTO users (user_id, user_name, user_status, username) VALUES (?, ?, ?, ?)',
                   (user_id, user_name, user_status, username))
    conn.commit()


global conclusion
conclusion = []


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start":
        keyboard = types.InlineKeyboardMarkup()
        key_manager = types.InlineKeyboardButton(text='Менеджер', callback_data="manager")
        keyboard.add(key_manager)
        key_boss = types.InlineKeyboardButton(text='Управляющий', callback_data="boss")
        keyboard.add(key_boss)
        bot.send_message(message.from_user.id, 'Выберите вашу роль', reply_markup=keyboard)
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напишите /start")
    elif message.text == "Привет":
        bot.send_message(message.from_user.id, "Здравствуйте! Напишите /help")
    elif message.text.lower() == 'добавить тест' or message.text.lower() == '/addtest':
        send = bot.send_message(message.chat.id,
                                'Создайте пароль для доступа к вашему тесту, он может состоять только цифр')
        bot.register_next_step_handler(send, ask_key_word)
    else:
        bot.send_message(message.from_user.id, "Я вас не понимаю. Напишите /help.")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "manager" or "boss":
        if call.data == "manager":
            bot.send_message(call.from_user.id, "Вам предстоит выбрать тип продаж. ")
            b2b_msg = "B2B (Business to Business) – модель, когда клиенты компании – это другие фирмы или предприниматели."
            bot.send_message(call.from_user.id, b2b_msg)
            keyboard = types.InlineKeyboardMarkup()
            key_b2b = types.InlineKeyboardButton(text='B2B', callback_data="typeofclientb")
            keyboard.add(key_b2b)
            key_b2c = types.InlineKeyboardButton(text='B2C', callback_data="typeofclientc")
            keyboard.add(key_b2c)
            b2c_msg = "B2C(Business to Consumer) предполагает продажу товаров,услуг физическим лицам/конечным потребителям."
            bot.send_message(call.from_user.id, b2c_msg, reply_markup=keyboard)
        elif call.data == "boss":
            bot.send_message(call.message.chat.id, 'Вы можете создать свой тест')
        user_to = call.from_user.id
        info_user_to = cursor.execute("SELECT * FROM users WHERE user_id = " + str(user_to)).fetchall()
        if len(info_user_to) > 0:
            pass
        else:
            us_id = call.from_user.id
            us_name = call.from_user.first_name
            if call.data == "manager":
                status = "manager"
            else:
                status = "boss"
            username = call.from_user.username
            db_table_val(user_id=us_id, user_name=us_name, user_status=status, username=username)
    if call.data == "typeofclientb" or call.data == "typeofclientc":
        sms2 = 'Вы можете выбрать один из 4 вариантов: '
        if call.data == "typeofclientb":
            sms1 = 'Отлично! Вы выбрали продажи компании/магазину.Теперь нужно выбрать тип клиента'
            conclusion.append('b2b')
        else:
            sms1 = 'Отлично! Вы выбрали продажи частному лицу. Теперь нужно выбрать тип клиента'
            conclusion.append('b2c')
        keyboard = types.InlineKeyboardMarkup()
        key_loyal = types.InlineKeyboardButton(text='Лояльный', callback_data='loyal_client')
        key_new = types.InlineKeyboardButton(text='Новый', callback_data='new_client')
        key_negative = types.InlineKeyboardButton(text='Негативный', callback_data='negative_client')
        key_doubting = types.InlineKeyboardButton(text='Сомневающийся', callback_data='doubting_client')
        bot.send_message(call.message.chat.id, sms1)
        keyboard.add(key_loyal)
        keyboard.add(key_new)
        keyboard.add(key_negative)
        keyboard.add(key_doubting)
        bot.send_message(call.message.chat.id, sms2, reply_markup=keyboard)
    elif call.data == 'loyal_client' or call.data == 'new_client' or call.data == 'negative_client' or call.data == 'doubting_client':
        if call.data == 'loyal_client':
            conclusion.append('loyal')
        elif call.data == 'new_client':
            conclusion.append('new')
        elif call.data == 'negative_client':
            conclusion.append('negative')
        elif call.data == 'doubting_client':
            conclusion.append('doubting')
        sms3 = 'Давайте выберем форму коммуникации'
        keyboard = types.InlineKeyboardMarkup()
        key_phone = types.InlineKeyboardButton(text='Телефон', callback_data='phone_communication')
        key_meet = types.InlineKeyboardButton(text='Личная встреча', callback_data='meet_communication')
        key_message = types.InlineKeyboardButton(text='Переписка', callback_data='message_communication')
        keyboard.add(key_phone)
        keyboard.add(key_meet)
        keyboard.add(key_message)
        bot.send_message(call.message.chat.id, sms3, reply_markup=keyboard)
    elif call.data == 'phone_communication' or call.data == 'meet_communication' or call.data == 'message_communication':
        if call.data == 'phone_communication':
            conclusion.append('phone')
        elif call.data == 'meet_communication':
            conclusion.append('meet')
        elif call.data == 'message_communication':
            conclusion.append('message')
        sms4 = 'Осталось выбрать уровень'
        keyboard = types.InlineKeyboardMarkup()
        key_level1 = types.InlineKeyboardButton(text='Новичок', callback_data='level1')
        key_level2 = types.InlineKeyboardButton(text='Продвинутый', callback_data='level2')
        key_level3 = types.InlineKeyboardButton(text='Эксперт', callback_data='level3')
        keyboard.add(key_level1)
        keyboard.add(key_level2)
        keyboard.add(key_level3)
        bot.send_message(call.message.chat.id, sms4, reply_markup=keyboard)
    elif call.data == 'level1' or call.data == 'level2' or call.data == 'level3':
        sms5 = 'Поздравляю! Вы готовы проходить тест. Он будет сгенеривован нашей системой.'
        bot.send_message(call.message.chat.id, sms5)


global current_state
current_state = []
key_word = {}


@bot.message_handler()
def ask_key_word(message):
    msg = message.text
    msg = "'" + msg + "'"
    info_msg = cursor.execute("SELECT * FROM testbase WHERE test_id =" + str(msg)).fetchall()
    user_to = message.from_user.id
    key_word[user_to] = []
    key_word[user_to].append(msg)
    key_word[user_to].append(info_msg)
    while len(info_msg) > 0:
        current_state.append('receiving')
        send = bot.send_message(message.chat.id, 'Такой  пароль для доступа уже существует, придумайте новый')
        bot.register_next_step_handler(send, make_key_word)
        while (current_state[-1] != 'answering'):
            current_state_str = 'receiving'
            if current_state[-1] == 'answering':
                break
        info_msg = key_word[user_to][1]
    send = bot.send_message(message.chat.id, 'Ваш пароль успешно добавлен. Введите количество вопросов')
    bot.register_next_step_handler(send, numbers)


def make_key_word(message):
    msg = message.text
    user_to = message.from_user.id
    msg = "'" + msg + "'"
    info_msg = cursor.execute("SELECT * FROM testbase WHERE test_id = " + str(msg)).fetchall()
    if len(info_msg) == 0:
        key_word[user_to][0] = msg
    key_word[user_to].append(info_msg)
    current_state.append('answering')


@bot.message_handler()
def numbers(message):
    global i
    global j
    i = 0
    amount = message.text.split()[0]
    while (amount.isdigit() == False):
        current_state.append('receiving')
        send = bot.send_message(message.chat.id, 'Введите число, а не текст')
        bot.register_next_step_handler(send, read_number)
        while (current_state[-1] != 'answering'):
            current_state_str = 'receiving'
            if current_state[-1] == 'answering':
                break
        amount = current_state[-2]
    while (i != int(amount)):
        current_state.append('receiving')
        send = bot.send_message(message.chat.id, f'Введите {i + 1}-й вопрос')
        bot.register_next_step_handler(send, questions)
        while (current_state[-1] != 'answering'):
            current_state_str = 'receiving'
            if current_state[-1] == 'answering':
                break
        j = 0
        while (j != 4):
            current_state.append('receiving')
            send = bot.send_message(message.chat.id, f'Введите {j + 1}-й вариант ответа')
            bot.register_next_step_handler(send, answers)
            while (current_state[-1] != 'answering'):
                current_state_str = 'receiving'
                if current_state[-1] == 'answering':
                    break
            j += 1
        current_state.append('receiving')
        send = bot.send_message(message.chat.id, f'Введите номер правильного ответа')
        bot.register_next_step_handler(send, answers)
        while (current_state[-1] != 'answering'):
            current_state_str = 'receiving'
            if current_state[-1] == 'answering':
                break
        i += 1
    current_state.clear()


def read_number(message):
    amount = message.text
    if amount.isdigit() == True:
        current_state.append(amount)
    current_state.append('answering')


def questions(message):
    last = message.text
    user_to = message.from_user.id
    user_to = key_word[user_to][0]
    user_to = int(user_to[1:-1])
    add_question(i + 1, last, user_to)
    current_state.append('answering')


def answers(message):
    ans = message.text
    user_to = message.from_user.id
    user_to = key_word[user_to][0]
    user_to = int(user_to[1:-1])
    add_ans(ans, user_to, i + 1, j + 1)
    current_state.append('answering')


def add_test(question_number, question, ans_1, ans_2, ans_3, ans_4, right_ans, test_id):
    cursor.execute(
        'INSERT INTO testbase (question_number, question, ans_1 ,ans_2 ,ans_3,ans_4, right_ans, test_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (question_number, question, ans_1, ans_2, ans_3, ans_4, right_ans, test_id))
    conn.commit()


def add_question(question_number, question, test_id):
    cursor.execute(
        'INSERT INTO testbase (question_number,question, test_id) VALUES (?,?, ?)',
        (question_number, question, test_id))
    conn.commit()


def add_ans(ans, test_id, question_number, j_t):
    if (j_t != 5):
        answer = 'ans_'
        answer += str(j_t)
    else:
        answer = 'right_ans'
    string = 'UPDATE testbase SET ' + answer + '= ? WHERE test_id=? and question_number=?'
    cursor.execute(
        string,
        (ans, test_id, question_number))
    conn.commit()


bot.polling(none_stop=True, interval=0)
