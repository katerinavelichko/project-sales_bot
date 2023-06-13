from importt import *
from sendmail import ask_boss

mutex = threading.Lock()
lock = Lock()
bot = telebot.TeleBot('5844570225:AAHVbCClhE53DdtM-RpZ1vKjrPPB4j_I538', 'markdown')
db_server = sqlite3.connect("server.db", check_same_thread=False)
cur = db_server.cursor()
db_users = sqlite3.connect('users.db', check_same_thread=False)
cursor = db_users.cursor()


def set_main_menu():
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Запуск бота'),
        BotCommand(command='/send_statistics_to_mail',
                   description='Отправить статистику подчиненных на почту'),
        BotCommand(command='/help',
                   description='Помощь'),
        BotCommand(command='/addtest',
                   description='Добавить тест'),
        BotCommand(command='/choosetestb2b',
                   description='Выбрать тест b2b'),
        BotCommand(command='/choosetestb2c',
                   description='Выбрать тест b2c'),
        BotCommand(command='/show_statistic',
                   description='Просмотр статистики')
    ]

    bot.set_my_commands(main_menu_commands)


# создание строки в базе данных с пользователями
def insert_into_users_table(user_id: int, user_name: str, user_status: str, username: str):
    cursor.execute('INSERT INTO users (user_id, user_name, user_status, username) VALUES (?, ?, ?, ?)',
                   (user_id, user_name, user_status, username))
    db_users.commit()


# создание строки в базе данных для отслеживания взаимосвязи босса и менеджера
def insert_into_boss_to_users(user_id: int, user_status: str, user_boss: str):
    cursor.execute('INSERT INTO boss_to_users (user_id, user_status, user_boss) VALUES (?, ?, ?)',
                   (user_id, user_status, user_boss))
    db_users.commit()


# создание строки в базе данных для статистики
def insert_into_statistics_table(user_id: int, user_name: str, first_name: str, second_name: str, user_status: str, test_password: int,
                  correct_answers: int, boss_id: int):
    cur.execute(
        'INSERT INTO statistics(user_id, user_name, first_name, second_name, user_status, test_password, correct_answers, boss_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (user_id, user_name, first_name, second_name, user_status, test_password, correct_answers, boss_id))
    db_server.commit()


from crop import crop_background

user_id_to_tests_options = defaultdict(list)


# обработка команд бота
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start":
        user_id = message.from_user.id
        user_id_to_tests_options[user_id].append(
            {'test_id': 2, 'b2b_or_b2c': 'b2c', 'test': 0, 'question_number': 1, 'correct_option': -1, 'result': 0,
             'level': 0})
        keyboard = types.InlineKeyboardMarkup()
        key_manager = types.InlineKeyboardButton(text='Менеджер', callback_data="manager")
        keyboard.add(key_manager)
        key_boss = types.InlineKeyboardButton(text='Управляющий', callback_data="boss")
        keyboard.add(key_boss)
        bot.send_message(message.from_user.id, 'Выберите вашу роль', reply_markup=keyboard)

    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напишите /start")

    elif message.text == "/show_statistic":
        user_id = message.from_user.id
        requests.post('http://127.0.0.1:8080/update', json={"user_id": user_id})
        for value in cursor.execute('SELECT * FROM users WHERE user_id=?', (message.from_user.id,)):
            if value[2] == 'boss':
                murkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                webAppTest = types.WebAppInfo('https://anyashishkina.github.io/test_repository/')
                murkup.add(types.InlineKeyboardButton('Заполните форму', web_app=webAppTest))
                bot.send_message(message.from_user.id, 'Выберите тип клиента', reply_markup=murkup)
            else:
                requests.post('http://127.0.0.1:8080/update', json={"user_id": message.from_user.id})
                hti = Html2Image()
                hti.screenshot(url=f'http://127.0.0.1:8080/?user_id={message.from_user.id}', save_as='statistic.png')
                crop_background('statistic.png')
                bot.send_photo(message.chat.id, photo=open('statistic.png', 'rb'),
                               caption='Статистика')  # бот показывает картинку

    elif message.text == "/send_statistics_to_mail":
        send = bot.send_message(message.chat.id, 'Введите Ваш email')
        bot.register_next_step_handler(send, ask_boss)
    elif message.text.lower() in ['добавить тест', '/addtest']:
        send = bot.send_message(message.chat.id,
                                'Создайте пароль для доступа к вашему тесту, он может состоять только цифр')
        bot.register_next_step_handler(send, ask_key_word)
    elif message.text == '/choosetestb2b':
        if str(user_id_to_tests_options[message.chat.id][0]['test'])[0] == "2":
            bot.send_message(message.chat.id,
                             'Вы проходили входной тест для B2C, поэтому можете выбрать тест только из этой категории. Нажмите "Выбрать тест b2c"')
        else:
            user_id_to_tests_options[message.chat.id][0]['test'] = 1000
            user_id_to_tests_options[message.chat.id][0]['test'] += user_id_to_tests_options[message.chat.id][0][
                'level']
            user_id_to_tests_options[message.chat.id][0]['question_number'] = 1
            keyboard = types.InlineKeyboardMarkup()
            key_loyal = types.InlineKeyboardButton(text='Лояльный', callback_data='loyal_client')
            key_new = types.InlineKeyboardButton(text='Новый', callback_data='new_client')
            key_negative = types.InlineKeyboardButton(text='Негативный', callback_data='negative_client')
            key_doubting = types.InlineKeyboardButton(text='Сомневающийся', callback_data='doubting_client')
            keyboard.add(key_loyal)
            keyboard.add(key_new)
            keyboard.add(key_negative)
            keyboard.add(key_doubting)
            bot.send_message(message.from_user.id, 'Выберите тип клиента', reply_markup=keyboard)
    elif message.text == '/choosetestb2c':
        if str(user_id_to_tests_options[message.chat.id][0]['test'])[0] == "1":
            bot.send_message(message.chat.id,
                             'Вы проходили входной тест для B2B, поэтому можете выбрать тест только из этой категории. Нажмите "Выбрать тест b2b"')
        else:
            user_id_to_tests_options[message.chat.id][0]['test'] = 2000
            user_id_to_tests_options[message.chat.id][0]['test'] += user_id_to_tests_options[message.chat.id][0][
                'level']
            user_id_to_tests_options[message.chat.id][0]['question_number'] = 1
            keyboard = types.InlineKeyboardMarkup()
            key_loyal = types.InlineKeyboardButton(text='Лояльный', callback_data='loyal_client')
            key_new = types.InlineKeyboardButton(text='Новый', callback_data='new_client')
            key_negative = types.InlineKeyboardButton(text='Негативный', callback_data='negative_client')
            key_doubting = types.InlineKeyboardButton(text='Сомневающийся', callback_data='doubting_client')
            keyboard.add(key_loyal)
            keyboard.add(key_new)
            keyboard.add(key_negative)
            keyboard.add(key_doubting)
            bot.send_message(message.from_user.id, 'Выберите тип клиента', reply_markup=keyboard)
    elif message.text == "Следующий вопрос":
        user_id = message.from_user.id
        if user_id_to_tests_options[message.chat.id][0]['b2b_or_b2c'] == 'b2b':
            for value in cur.execute("SELECT * FROM entrance_test_b2b WHERE id=?",
                                     (user_id_to_tests_options[user_id][0]['test_id'],)):
                answers = [value[2], value[3], value[4]]
                user_id_to_tests_options[message.chat.id][0]['correct_option'] = value[5]
                bot.send_poll(chat_id=message.chat.id, question=value[1], options=answers, type='quiz',
                              correct_option_id=value[5], open_period=30, is_anonymous=False)
                user_id_to_tests_options[message.chat.id][0]['test_id'] += 1
                # if test_id == 4:
                if user_id_to_tests_options[message.chat.id][0]['test_id'] == 29:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    button_next_question = types.KeyboardButton('Выбрать тест')
                    markup.row(button_next_question)
                    bot.send_message(message.from_user.id, 'Нажмите кнопку "Выбрать тест", когда будете готовы.',
                                     reply_markup=markup)

        elif user_id_to_tests_options[message.chat.id][0]['b2b_or_b2c'] == 'b2c':
            for value in cur.execute("SELECT * FROM entrance_test_b2c WHERE id=?",
                                     (user_id_to_tests_options[message.chat.id][0]['test_id'],)):
                answers = [value[2], value[3], value[4]]
                user_id_to_tests_options[message.chat.id][0]['correct_option'] = value[5]
                bot.send_poll(chat_id=message.chat.id, question=value[1], options=answers, type='quiz',
                              correct_option_id=value[5], open_period=30, is_anonymous=False)
                user_id_to_tests_options[message.chat.id][0]['test_id'] += 1
                # if user_id_to_tests_options[message.chat.id][0]['test_id'] == 4:
                if user_id_to_tests_options[message.chat.id][0]['test_id'] == 25:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    button_next_question = types.KeyboardButton('Выбрать тест')
                    markup.row(button_next_question)
                    bot.send_message(message.from_user.id, 'Нажмите кнопку "Выбрать тест", когда будете готовы.',
                                     reply_markup=markup)

        elif user_id_to_tests_options[message.chat.id][0]['b2b_or_b2c'] == 'boss_test':
            for value in cursor.execute("SELECT * FROM testbase WHERE question_number=? and test_id=?",
                                        (user_id_to_tests_options[message.chat.id][0]['question_number'],
                                         user_id_to_test_boss_key[message.chat.id][0])):
                answers = [value[2], value[3], value[4], value[5]]
                user_id_to_tests_options[message.chat.id][0]['correct_option'] = value[6] - 1
                bot.send_poll(chat_id=message.chat.id, question=value[1], options=answers, type='quiz',
                              correct_option_id=value[6] - 1, open_period=30, is_anonymous=False)
                user_id_to_tests_options[message.chat.id][0]['question_number'] += 1

        else:
            for value in cur.execute("SELECT * FROM main_tests WHERE test_password=? AND question_number=?",
                                     (user_id_to_tests_options[message.chat.id][0]['test'],
                                      user_id_to_tests_options[message.chat.id][0]['question_number'],)):
                answers = [value[3], value[4], value[5]]
                user_id_to_tests_options[message.chat.id][0]['correct_option'] = value[6]
                bot.send_poll(chat_id=message.chat.id, question=value[2], options=answers, type='quiz',
                              correct_option_id=value[6], open_period=30, is_anonymous=False)
                user_id_to_tests_options[message.chat.id][0]['question_number'] += 1
            if user_id_to_tests_options[message.chat.id][0]['question_number'] == 4:
                bot.send_message(message.from_user.id, 'Тест завершён.',
                                 reply_markup=types.ReplyKeyboardRemove())


    elif message.text == 'Выбрать тест':
        bot.send_message(message.chat.id, "Вам предстоит выбрать тип клиента и форму коммуникаций",
                         reply_markup=types.ReplyKeyboardRemove())
        keyboard = types.InlineKeyboardMarkup()
        key_loyal = types.InlineKeyboardButton(text='Лояльный', callback_data='loyal_client')
        key_new = types.InlineKeyboardButton(text='Новый', callback_data='new_client')
        key_negative = types.InlineKeyboardButton(text='Негативный', callback_data='negative_client')
        key_doubting = types.InlineKeyboardButton(text='Сомневающийся', callback_data='doubting_client')
        keyboard.add(key_loyal)
        keyboard.add(key_new)
        keyboard.add(key_negative)
        keyboard.add(key_doubting)
        bot.send_message(message.chat.id, 'Вы можете выбрать один из 4 типов клиентов: ', reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, "Я вас не понимаю. Напишите /help.")


# подсчёт правильных ответов на тесты
@bot.poll_answer_handler()
def handle_poll_answer(poll_answer):
    global result
    selected_option = poll_answer.option_ids[0]
    if user_id_to_tests_options[poll_answer.user.id][0]['correct_option'] == selected_option:
        user_id_to_tests_options[poll_answer.user.id][0]['result'] += 1
    if user_id_to_tests_options[poll_answer.user.id][0]['b2b_or_b2c'] == 'boss_test' and \
            user_id_to_tests_options[poll_answer.user.id][0]['question_number'] == \
            user_id_to_num_questions[poll_answer.user.id][0] + 1:
        bot.send_message(poll_answer.user.id, 'Тест завершён.',
                         reply_markup=types.ReplyKeyboardRemove())
        user_id_to_tests_options[poll_answer.user.id][0]['question_number'] = 0
        user_id_to_tests_options[poll_answer.user.id][0]['b2b_or_b2c'] = 5
        result = user_id_to_tests_options[poll_answer.user.id][0]['result']
        bot.send_message(poll_answer.user.id,
                         f'Вы набрали {result} баллов из {user_id_to_num_questions[poll_answer.user.id][0]}')
        queryy = cursor.execute('SElect * from  test_results  WHERE user_id=? AND  test_id=?',
                                (user_id, user_id_to_test_boss_key[poll_answer.user.id][0])).fetchall()
        if len(queryy) > 0:
            cursor.execute('Update  test_results  SET num_of_right_answers=? WHERE user_id=? AND  test_id=?',
                           (result, user_id, user_id_to_test_boss_key[poll_answer.user.id][0]))
            db_users.commit()
        else:
            cursor.execute(
                'INSERT Into test_results(user_id , test_id,  num_of_right_answers, num_of_questions) VALUES(?, ? ,? ,?)',
                (user_id, user_id_to_test_boss_key[poll_answer.user.id][0], result,
                 user_id_to_num_questions[poll_answer.user.id][0]))
            db_users.commit()
        user_id_to_tests_options[poll_answer.user.id][0]['result'] = 0

    # if test_id == 4 and b2b_or_b2c == 0:
    if user_id_to_tests_options[poll_answer.user.id][0]['test_id'] == 25 and \
            user_id_to_tests_options[poll_answer.user.id][0]['b2b_or_b2c'] == 'b2c':
        user_id_to_tests_options[poll_answer.user.id][0]['b2b_or_b2c'] = 'choose_test'
        result = user_id_to_tests_options[poll_answer.user.id][0]['result']
        bot.send_message(poll_answer.user.id, f'Вы набрали {result} баллов из 25')
        if 25 >= user_id_to_tests_options[poll_answer.user.id][0]['result'] >= 23:
            user_id_to_tests_options[poll_answer.user.id][0]['test'] += 300
            user_id_to_tests_options[poll_answer.user.id][0]['level'] += 300
            bot.send_message(poll_answer.user.id,
                             'На данный момент ваш уровень - эксперт. Вам будут предложены тесты из этой категории')

        elif 22 >= user_id_to_tests_options[poll_answer.user.id][0]['result'] >= 20:
            user_id_to_tests_options[poll_answer.user.id][0]['test'] += 200
            user_id_to_tests_options[poll_answer.user.id][0]['level'] += 200
            bot.send_message(poll_answer.user.id,
                             'На данный момент ваш уровень - продвинутый. Вам будут предложены тесты из этой категории')

        elif user_id_to_tests_options[poll_answer.user.id][0]['result'] <= 19:
            user_id_to_tests_options[poll_answer.user.id][0]['test'] += 100
            user_id_to_tests_options[poll_answer.user.id][0]['level'] += 100
            bot.send_message(poll_answer.user.id,
                             'На данный момент ваш уровень - новичок. Вам будут предложены тесты из этой категории')
        user_id_to_tests_options[poll_answer.user.id][0]['result'] = 0

    # elif test_id == 4 and b2b_or_b2c == 1:
    elif user_id_to_tests_options[poll_answer.user.id][0]['test_id'] == 29 and \
            user_id_to_tests_options[poll_answer.user.id][0]['b2b_or_b2c'] == 'b2b':
        user_id_to_tests_options[poll_answer.user.id][0]['b2b_or_b2c'] = 'choose_test'
        result = user_id_to_tests_options[poll_answer.user.id][0]['result']
        bot.send_message(poll_answer.user.id, f'Вы набрали {result} баллов из 28')
        if 28 >= user_id_to_tests_options[poll_answer.user.id][0]['result'] >= 24:
            user_id_to_tests_options[poll_answer.user.id][0]['test'] += 300
            user_id_to_tests_options[poll_answer.user.id][0]['level'] += 300
            bot.send_message(poll_answer.user.id,
                             'На данный момент ваш уровень - эксперт. Вам будут предложены тесты из этой категории')

        elif 23 >= user_id_to_tests_options[poll_answer.user.id][0]['result'] >= 20:
            user_id_to_tests_options[poll_answer.user.id][0]['test'] += 200
            user_id_to_tests_options[poll_answer.user.id][0]['level'] += 200
            bot.send_message(poll_answer.user.id,
                             'На данный момент ваш уровень - продвинутый. Вам будут предложены тесты из этой категории')

        elif user_id_to_tests_options[poll_answer.user.id][0]['result'] <= 19:
            user_id_to_tests_options[poll_answer.user.id][0]['test'] += 100
            user_id_to_tests_options[poll_answer.user.id][0]['level'] += 100
            bot.send_message(poll_answer.user.id,
                             'На данный момент ваш уровень - новичок. Вам будут предложены тесты из этой категории')

        user_id_to_tests_options[poll_answer.user.id][0]['result'] = 0
    elif user_id_to_tests_options[poll_answer.user.id][0]['question_number'] == 4 and \
            user_id_to_tests_options[poll_answer.user.id][0]['b2b_or_b2c'] == 'choose_test':
        cur.execute('UPDATE statistics SET correct_answers=? WHERE test_password=? AND user_id=?',
                    (user_id_to_tests_options[poll_answer.user.id][0]['result'],
                     user_id_to_tests_options[poll_answer.user.id][0]['test'], poll_answer.user.id))
        db_server.commit()
        user_id_to_tests_options[poll_answer.user.id][0]['b2b_or_b2c'] = 'choose_test'
        result = user_id_to_tests_options[poll_answer.user.id][0]['result']
        bot.send_message(poll_answer.user.id, f'Вы набрали {result} баллов из 3')
        user_id_to_tests_options[poll_answer.user.id][0]['result'] = 0


# принятие данных из формы
@bot.message_handler(content_types=['web_app_data'])
def web_app(message: types.Message):
    res = json.loads(message.web_app_data.data)
    first_name = res.get("firstName")
    last_name = res.get("lastName")
    if first_name is not None and last_name is not None:
        for value in cur.execute("SELECT * FROM statistics WHERE first_name = ? AND second_name = ?",
                                 (first_name, last_name,)):
            requests.post('http://127.0.0.1:8080/update', json={"user_id": value[0]})

            hti = Html2Image()
            hti.screenshot(url=f'http://127.0.0.1:8080/?user_id={value[0]}', save_as='statistic.png')
            crop_background('statistic.png')
            bot.send_photo(message.chat.id, photo=open('statistic.png', 'rb'),
                           caption='Статистика')  # бот показывает картинку
            bot.send_message(message.from_user.id, f'Имя: {first_name}\nФамилия: {last_name}',
                             reply_markup=types.ReplyKeyboardRemove())
    else:

        bot.send_message(message.from_user.id, "Данные отсутствуют", reply_markup=types.ReplyKeyboardRemove())


# реакция на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "manager" or "boss":
        us_id = call.from_user.id
        info_user_to = cursor.execute("SELECT * FROM users WHERE user_id = " + str(us_id)).fetchall()
        if len(info_user_to) == 0:
            us_name = call.from_user.first_name
            if call.data == "manager":
                status = "manager"
            else:
                status = "boss"
            username = call.from_user.username
            insert_into_users_table(user_id=us_id, user_name=us_name, user_status=status, username=username)
            if status == 'manager':
                insert_into_boss_to_users(user_id=us_id, user_status=status, user_boss=0)
                send = bot.send_message(call.message.chat.id,
                                        'Введите id вашего руководителя, а в случае его отсутствия введите 0')
                bot.register_next_step_handler(send, set_boss)
            else:
                bot.send_message(call.message.chat.id, 'Вы можете создать свой тест')
        elif call.data == "manager":
            send = bot.send_message(call.message.chat.id, 'Вы уже добавлены в базу данных! Вы готовы продолжить?')
            bot.register_next_step_handler(send, choose_type)
        elif call.data == "boss":
            bot.send_message(call.message.chat.id, 'Вы можете создать свой тест')
    if call.data == "typeofclientb" or call.data == "typeofclientc":
        if call.data == "typeofclientb":
            user_id_to_tests_options[call.message.chat.id][0]['test'] += 1000
            user_id_to_tests_options[call.message.chat.id][0]['b2b_or_b2c'] = 'b2b'
            bot.send_message(call.message.chat.id, 'Отлично! Вы выбрали продажи компании/магазину. Пожалуйста пройдите тест для определения уровня.')
            for value in cur.execute("SELECT * FROM entrance_test_b2b"):
                answers = [value[2], value[3], value[4]]
                user_id_to_tests_options[call.message.chat.id][0]['correct_option'] = value[5]
                bot.send_poll(chat_id=call.message.chat.id, question=value[1], options=answers, type='quiz',
                              correct_option_id=value[5], open_period=30, is_anonymous=False)
                user_id_to_tests_options[call.from_user.id][0]['test_id'] += 1
                break
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_next_question = types.KeyboardButton('Следующий вопрос')
            markup.row(button_next_question)
            bot.send_message(call.message.chat.id,
                             'Когда будете готовы перейти к следующему вопросу, нажмите кнопку "Следующий вопрос" ',
                             reply_markup=markup)

        else:
            user_id_to_tests_options[call.message.chat.id][0]['test'] += 2000
            bot.send_message(call.message.chat.id, 'Отлично! Вы выбрали продажи частному лицу. Пожалуйста пройдите тест для определения уровня.')
            for value in cur.execute("SELECT * FROM entrance_test_b2c"):
                answers = [value[2], value[3], value[4]]
                user_id_to_tests_options[call.from_user.id][0]['correct_option'] = value[5]
                bot.send_poll(chat_id=call.message.chat.id, question=value[1], options=answers, type='quiz',
                              correct_option_id=value[5], open_period=30, is_anonymous=False)
                user_id_to_tests_options[call.from_user.id][0]['test_id'] += 1
                break
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_next_question = types.KeyboardButton('Следующий вопрос')
            markup.row(button_next_question)
            bot.send_message(call.message.chat.id,
                             'Когда будете готовы перейти к следующему вопросу, нажмите кнопку "Следующий вопрос" ',
                             reply_markup=markup)
    elif call.data == 'loyal_client' or call.data == 'new_client' or call.data == 'negative_client' or call.data == 'doubting_client':
        if call.data == 'loyal_client':
            user_id_to_tests_options[call.message.chat.id][0]['test'] += 10
        elif call.data == 'new_client':
            user_id_to_tests_options[call.message.chat.id][0]['test'] += 20
        elif call.data == 'negative_client':
            user_id_to_tests_options[call.message.chat.id][0]['test'] += 30
        elif call.data == 'doubting_client':
            user_id_to_tests_options[call.message.chat.id][0]['test'] += 40
        keyboard = types.InlineKeyboardMarkup()
        key_phone = types.InlineKeyboardButton(text='Телефон', callback_data='phone_communication')
        key_meet = types.InlineKeyboardButton(text='Личная встреча', callback_data='meet_communication')
        key_message = types.InlineKeyboardButton(text='Переписка', callback_data='message_communication')
        keyboard.add(key_phone)
        keyboard.add(key_meet)
        keyboard.add(key_message)
        bot.send_message(call.message.chat.id, 'Давайте выберем форму коммуникации', reply_markup=keyboard)
    elif call.data == 'phone_communication' or call.data == 'meet_communication' or call.data == 'message_communication':
        if call.data == 'phone_communication':
            user_id_to_tests_options[call.message.chat.id][0]['test'] += 1
        elif call.data == 'meet_communication':
            user_id_to_tests_options[call.message.chat.id][0]['test'] += 2
        elif call.data == 'message_communication':
            user_id_to_tests_options[call.message.chat.id][0]['test'] += 3
        bot.send_message(call.message.chat.id, 'Поздравляю! Вы готовы проходить тест. Он будет сгенерирован нашей системой.')
    if user_id_to_tests_options[call.message.chat.id][0]['test'] in [2121, 2122, 2123, 2111, 2112, 2113, 2131, 2132,
                                                                     2133, 2141, 2142, 2143]:
        cnt_of_passed_test = 0
        for value in cur.execute("SELECT * FROM statistics"):
            if call.from_user.username == value[1] and user_id_to_tests_options[call.message.chat.id][0]['test'] == \
                    value[5]:
                cnt_of_passed_test += 1
        if cnt_of_passed_test == 0:
            insert_into_statistics_table(user_id=call.from_user.id, user_name=call.from_user.username,
                          first_name=call.from_user.first_name, second_name=call.from_user.last_name,
                          user_status='manager',
                          test_password=user_id_to_tests_options[call.message.chat.id][0]['test'],
                          correct_answers=0, boss_id=0)
        for value in cur.execute("SELECT * FROM main_tests WHERE test_password=? AND question_number=?",
                                 (user_id_to_tests_options[call.message.chat.id][0]['test'],
                                  user_id_to_tests_options[call.message.chat.id][0]['question_number'],)):
            answers = [value[3], value[4], value[5]]
            user_id_to_tests_options[call.message.chat.id][0]['correct_option'] = value[6]
            bot.send_poll(chat_id=call.message.chat.id, question=value[2], options=answers, type='quiz',
                          correct_option_id=value[6], open_period=30, is_anonymous=False)
            user_id_to_tests_options[call.message.chat.id][0]['question_number'] += 1
            break
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_next_question = types.KeyboardButton('Следующий вопрос')
        markup.row(button_next_question)
        bot.send_message(call.message.chat.id,
                         'Когда будете готовы перейти к следующему вопросу, нажмите кнопку "Следующий вопрос" ',
                         reply_markup=markup)

    if call.data == "bosstest":
        user_id_to_tests_options[call.message.chat.id][0]['b2b_or_b2c'] = 'boss_test'
        msg = bot.send_message(call.message.chat.id, 'введите пароль от теста')
        bot.register_next_step_handler(msg, ask_key_word_bosstest)


def set_boss(message):
    msg = message.text
    user_id = message.from_user.id
    string = 'UPDATE boss_to_users SET user_boss = ? WHERE user_id=? '
    cursor.execute(
        string,
        (msg, user_id))
    db_users.commit()
    send = bot.send_message(message.chat.id, 'Вы успешно добавлены в базу данных! Вы готовы продолжить?')
    bot.register_next_step_handler(send, choose_type)


def choose_type(call):
    cll = call.text
    if (cll == 'да ' or cll == 'Да ' or cll == 'да' or cll == 'Да'):
        cnt_of_users_in_table = 0
        for value in cur.execute("SELECT * FROM statistics WHERE user_status = ?", ('manager',)):
            if call.from_user.username == value[1]:
                cnt_of_users_in_table += 1
        if cnt_of_users_in_table == 0:
            insert_into_statistics_table(user_id=call.from_user.id, user_name=call.from_user.username,
                          first_name=call.from_user.first_name, second_name=call.from_user.last_name,
                          user_status='manager', test_password=0,
                          correct_answers=0, boss_id=0)

        bot.send_message(call.from_user.id, "Вам предстоит выбрать тип продаж или тест от руководителя ")
        b2b_msg = "B2B (Business to Business) – модель, когда клиенты компании – это другие фирмы или предприниматели."
        bot.send_message(call.from_user.id, b2b_msg)
        keyboard = types.InlineKeyboardMarkup()
        key_b2b = types.InlineKeyboardButton(text='B2B', callback_data="typeofclientb")
        keyboard.add(key_b2b)
        key_b2c = types.InlineKeyboardButton(text='B2C', callback_data="typeofclientc")
        keyboard.add(key_b2c)
        key_boss = types.InlineKeyboardButton(text='тест от босса', callback_data="bosstest")
        keyboard.add(key_boss)
        b2c_msg = "B2C(Business to Consumer) предполагает продажу товаров,услуг физическим лицам/конечным потребителям."
        bot.send_message(call.from_user.id, b2c_msg, reply_markup=keyboard)
    else:
        send = bot.send_message(call.chat.id, 'Напишите: да или нет')
        bot.register_next_step_handler(send, choose_type)


keywords_to_amount = defaultdict(list)
keywords_to_amount2 = defaultdict(list)
user_id_to_keywords = defaultdict(list)
keywords_from_user_id = defaultdict(list)
test_id_to_numbers = defaultdict(list)
test_id_to_ans = defaultdict(list)
states = defaultdict(list)
cnt_to_user_id = defaultdict(list)
user_id_to_test_boss_key = defaultdict(list)
user_id_to_num_questions = defaultdict(list)


@bot.message_handler()
def ask_key_word_bosstest(message):
    user_id_to_test_boss_key[message.chat.id].append(message.text)
    # test_boss_key = message.text
    user_id_to_test_boss_key[message.chat.id][0] = int(user_id_to_test_boss_key[message.chat.id][0])
    global user_id
    user_id = message.from_user.id
    msg = bot.send_message(message.chat.id, 'Вы готовы начать? Напишите: да или нет')
    bot.register_next_step_handler(msg, test_from_boss)


@bot.message_handler()
def test_from_boss(message):
    msgg = message.text
    if (msgg == 'да ' or msgg == 'Да ' or msgg == 'да' or msgg == 'Да'):
        user_id_to_num_questions[message.chat.id].append(cursor.execute('SELECT COUNT(*) FROM testbase WHERE test_id=?',
                                                                        (user_id_to_test_boss_key[message.chat.id][
                                                                             0],)).fetchone()[0])
        user_id_to_tests_options[message.chat.id][0]['question_number'] = 1
        user_id_to_tests_options[message.chat.id][0]['result'] = 0
        for value in cursor.execute("SELECT * FROM testbase WHERE question_number=? AND test_id=?",
                                    (user_id_to_tests_options[message.chat.id][0]['question_number'],
                                     user_id_to_test_boss_key[message.chat.id][0],)):
            answers = [value[2], value[3], value[4], value[5]]
            user_id_to_tests_options[message.chat.id][0]['correct_option'] = value[6] - 1
            bot.send_poll(chat_id=message.chat.id, question=value[1], options=answers, type='quiz',
                          correct_option_id=value[6] - 1, open_period=30, is_anonymous=False)
            user_id_to_tests_options[message.chat.id][0]['question_number'] += 1
            break
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_next_question = types.KeyboardButton('Следующий вопрос')
        markup.row(button_next_question)
        bot.send_message(message.chat.id,
                         'Когда будете готовы перейти к следующему вопросу, нажмите кнопку "Следующий вопрос" ',
                         reply_markup=markup)
    else:
        send = bot.send_message(message.chat.id, 'Напишите: да или нет')
        bot.register_next_step_handler(send, test_from_boss)


@bot.message_handler()
def ask_key_word(message):
    keyword = message.text
    user_id = message.from_user.id
    keyword_list = cursor.execute(f"SELECT * FROM testbase WHERE test_id ='{keyword}'").fetchall()
    if len(keyword_list) > 0:
        msg = bot.send_message(message.chat.id, 'Такой  пароль для доступа уже существует, придумайте новый')
        bot.register_next_step_handler(msg, ask_key_word)
    else:
        if (keyword.isdigit() == False):
            send = bot.send_message(message.chat.id, 'Введите число, а не текст')
            bot.register_next_step_handler(send, ask_key_word)
        else:
            user_id = message.from_user.id
            user_id_to_keywords[user_id].append(keyword)
            msg = bot.send_message(message.chat.id, 'Ваш пароль успешно добавлен.')
            cursor.execute(
                'INSERT INTO testbase (question_number,test_id) VALUES (?, ?)',
                (1, keyword))
            db_users.commit()
            msg = bot.send_message(message.chat.id, 'Введите количество вопросов')
            bot.register_next_step_handler(msg, numbers)


@bot.message_handler()
def numbers(message):
    amount = message.text.split()[0]
    user_id = message.from_user.id
    keyword = user_id_to_keywords[user_id][-1]
    if (amount.isdigit() == False):
        send = bot.send_message(message.chat.id, 'Введите число, а не текст')
        bot.register_next_step_handler(send, numbers)
    else:
        test_id_to_numbers[keyword].append(amount)
        keywords_to_amount[keyword].append(amount)
        keywords_to_amount2[keyword].append(amount)
        send = bot.send_message(message.chat.id, 'Введите 1-й вопрос')
        bot.register_next_step_handler(send, read_questions)
        return


users = Queue()


def read_questions(message):
    msg = message.text
    user_id = message.from_user.id
    users.put(user_id)
    keyword = user_id_to_keywords[user_id][-1]
    keywords_from_user_id[keyword] = user_id
    amount = int(test_id_to_numbers[keyword][0])
    if len(test_id_to_numbers[keyword]) == 1:
        test_id_to_numbers[keyword].append(1)
    elif len(test_id_to_numbers[keyword]) == 2:
        test_id_to_numbers[keyword].append(2)
        string = 'INSERT INTO testbase (question_number,test_id) VALUES(?,?)'
        cursor.execute(
            string,
            (2, keyword))
        db_users.commit()
    elif len(test_id_to_numbers[keyword]) > 2:
        quest_num = int(test_id_to_numbers[keyword][-1]) + 1
        test_id_to_numbers[keyword].append(quest_num)
        string = 'INSERT INTO testbase (question_number,test_id) VALUES(?,?)'
        cursor.execute(
            string,
            (quest_num, keyword))
        db_users.commit()

    string = 'UPDATE testbase SET question = ? WHERE test_id=? and question_number=?'
    cursor.execute(
        string,
        (msg, keyword, int(test_id_to_numbers[keyword][-1])))
    db_users.commit()

    with mutex:
        send = bot.send_message(message.chat.id, f'Введите 1-й вариант ответа')
        first_element = users.get()
        bot.register_next_step_handler_by_chat_id(first_element, read_ans)


def read_ans(message):
    msg = message.text
    amount = msg.split()[0]
    user_id = message.from_user.id
    keyword = user_id_to_keywords[user_id][-1]
    cnt_to_user_id[keyword] = 0
    if len(test_id_to_ans[keyword]) != 0:
        if test_id_to_ans[keyword][-1] == 5:
            if amount.isdigit() == False:
                cnt_to_user_id[keyword] = 1
                msg = bot.send_message(message.chat.id, 'Введите число, а не текст')
                bot.register_next_step_handler(msg, read_ans)
    if cnt_to_user_id[keyword] == 0:
        if len(test_id_to_ans[keyword]) == 0:
            test_id_to_ans[keyword].append(2)
        else:
            test_id_to_ans[keyword].append(test_id_to_ans[keyword][-1] + 1)
        if test_id_to_ans[keyword][-1] == 6:
            answer = 'right_ans'
        elif test_id_to_ans[keyword][-1] < 6:
            answer = 'ans_' + str(test_id_to_ans[keyword][-1] - 1)
        if len(test_id_to_ans[keyword]) <= 5:
            string = 'UPDATE testbase SET ' + answer + ' = ? WHERE test_id=? and question_number=?'
            cursor.execute(
                string,
                (msg, keyword, int(test_id_to_numbers[keyword][-1])))
            db_users.commit()
        if test_id_to_ans[keyword][-1] < 5:
            send = bot.send_message(message.chat.id, f'Введите {int(test_id_to_ans[keyword][-1])}-й вариант ответа')
            bot.register_next_step_handler(send, read_ans)
        if test_id_to_ans[keyword][-1] == 5:
            send = bot.send_message(message.chat.id, f'Введите номер правильного варианта ответа')
            bot.register_next_step_handler(send, read_ans)
        if test_id_to_ans[keyword][-1] == 6:
            test_id_to_ans[keyword].clear()
            keywords_to_amount[keyword][0] = int(keywords_to_amount[keyword][0]) - 1
            if keywords_to_amount[keyword][0] > 0:
                send = bot.send_message(message.chat.id,
                                        f'Введите {int(keywords_to_amount2[keyword][0]) - int(keywords_to_amount[keyword][0]) + 1}-й вопрос')
                bot.register_next_step_handler(send, read_questions)
            states[keyword].append('answering')


# передача данных в html код и изменение картинки
app = Flask(__name__)
results = {}


@app.route('/', methods=['GET'])
def get_data():
    user_id = int(request.args.get('user_id', ''))
    matrix = [list(results.get(user_id, {}).values())[i:i + 4] for i in range(0, len(results.get(user_id, {})), 4)]
    return render_template('statistics_page.html', matrix=matrix)


# Комментарий к переменной test: 2000-категория b2c, 1000-категория b2b
# 100-новичок, 200-продвинутый, 300-эксперт
# 10-лояльный, 20-новый, 30-негативный, 40-сомневающийся
# 1-телефон, 2-личная встреча, 3-переписка
@app.route('/update', methods=['POST'])
def update_data():
    user_id = int(request.json['user_id'])
    test_values = {
        2111: 0, 2112: 0, 2113: 0,
        2121: 0, 2122: 0, 2123: 0,
        2131: 0, 2132: 0, 2133: 0,
        2141: 0, 2142: 0, 2143: 0
    }
    for value in cur.execute("SELECT * FROM statistics WHERE user_id = ?", (user_id,)):
        if value[5] in test_values:
            test_values[value[5]] = value[6]

    results[user_id] = {
        "test1": test_values[2111], "test2": test_values[2121], "test3": test_values[2131],
        "test4": test_values[2141], "test5": test_values[2112], "test6": test_values[2122],
        "test7": test_values[2132], "test8": test_values[2142], "test9": test_values[2113],
        "test10": test_values[2123], "test11": test_values[2133], "test12": test_values[2143],
    }
    return 'Updated'


def start_bot():
    set_main_menu()
    bot.polling(none_stop=True, interval=0)


def start_app():
    app.run(debug=False, port=8080)


if __name__ == "__main__":
    # создаем два потока
    thread_bot = threading.Thread(target=start_bot)
    thread_app = threading.Thread(target=start_app)

    # запускаем их
    thread_bot.start()
    thread_app.start()
