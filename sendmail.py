import smtplib
from email.mime.text import MIMEText
from jinja2 import Template
import sqlite3
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

import telebot

bot = telebot.TeleBot('5844570225:AAHVbCClhE53DdtM-RpZ1vKjrPPB4j_I538', 'markdown')




@bot.message_handler()
def ask_boss(message):
    email = message.text
    global boss_id
    boss_id = message.from_user.id
    global workers
    workers = make_mas(boss_id)
    workers=list(workers)
    send_email(email)


def make_mas(boss_id):
    result_mas=[]
    qur=cursor.execute("SELECT * FROM boss_to_users WHERE user_boss=?", (boss_id,)).fetchall()
    for i in qur:
        person_id = i[0]
        person_name = cursor.execute("SELECT user_name FROM users WHERE user_id=?", (person_id,)).fetchall()
        name = person_name[0][0]
        worker_tests = cursor.execute("SELECT * FROM test_results WHERE user_id=?", (person_id,)).fetchall()
        for j in worker_tests:
            id_of_test =j[1]
            result = j[2]
            num_of_questions = j[3]
            mas = {'name': name,  'id_of_test': id_of_test, 'result': result, 'num_of_questions': num_of_questions}
            result_mas.append(mas)
    return result_mas
def mas_to_string(mas):
    new_mas = []
    for i in mas:
        s = str(i['name']) + ' ' + ' набрал(а) ' + str(i['result']) + ' баллов из ' + str(
            i['num_of_questions']) + ' в тесте с id ' + str(i['id_of_test']) + ' '
        new_mas.append(s)
    return new_mas


# to = "katevlchkk@gmail.com"
def send_email(to):
    sender = "sales.botik@gmail.com"
    password = "uyxymvvguqtsbrry"
    name = cursor.execute("SELECT user_name FROM users WHERE user_id=?",(boss_id,))
    workers_results = mas_to_string(workers)
    context = {
        'name': name,
        'workers': workers_results
    }

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    with open("templates/email.html") as file:
        template = file.read()
        template = Template(template)
        rendered_template = template.render(**context)
    server.login(sender, password)
    msg = MIMEText(rendered_template, "html")
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = "Статистика подчиненных"
    server.sendmail(sender, to, msg.as_string())
    return "The message was sent successfully!"

