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
    elif message.text.lower() == 'добавить тест':
            send = bot.send_message(message.chat.id, 'Введите количество вопросов')
            bot.register_next_step_handler(send, numbers)
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

def numbers(message):
    global i
    global j
    i = 0
    last = message.text.split()[0]
    last = int(last)
    while (i != last):
        send = bot.send_message(message.chat.id, f'Введите {i + 1}-й вопрос')
        bot.register_next_step_handler(send, questions)
        time.sleep(15)
        j = 0
        while (j != 4):
            send = bot.send_message(message.chat.id, f'Введите {j + 1}-й вариант ответа')
            bot.register_next_step_handler(send, answers)
            time.sleep(15)
            j += 1
        send = bot.send_message(message.chat.id, f'Введите номер правильного ответа')
        bot.register_next_step_handler(send, answers)
        time.sleep(15)
        i += 1

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


def add_ans1(ans_1, test_id, question_number):
    cursor.execute(
        'UPDATE testbase SET ans_1=? WHERE test_id=? and question_number=?',
        (ans_1, test_id, question_number))
    conn.commit()


def add_ans2(ans_2, test_id, question_number):
    cursor.execute(
        'UPDATE testbase SET ans_2=? WHERE test_id=? and question_number=?',
        (ans_2, test_id, question_number))
    conn.commit()


def add_ans3(ans_3, test_id, question_number):
    cursor.execute(
        'UPDATE testbase SET ans_3=? WHERE test_id=? and question_number=?',
        (ans_3, test_id, question_number))
    conn.commit()


def add_right_ans(right_ans, test_id, question_number):
    cursor.execute(
        'UPDATE testbase SET right_ans=? WHERE test_id=? and question_number=?',
        (right_ans, test_id, question_number))
    conn.commit()


def add_ans4(ans_4, test_id, question_number):
    cursor.execute(
        'UPDATE testbase SET ans_4=? WHERE test_id=? and question_number=?',
        (ans_4, test_id, question_number))
    conn.commit()

def questions(message):
    last = message.text
    user_to = message.from_user.id
    add_question(i + 1, last, user_to)


def answers(message):
    ans = message.text
    user_to = message.from_user.id
    if j == 0:
        add_ans1(ans, user_to, i + 1)
    elif j == 1:
        add_ans2(ans, user_to, i + 1)
    elif j == 2:
        add_ans3(ans, user_to, i + 1)
    elif j == 3:
        add_ans4(ans, user_to, i + 1)
    else:
        add_right_ans(ans, user_to, i + 1)

bot.polling(none_stop=True, interval=0)
