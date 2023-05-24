import smtplib
from email.mime.text import MIMEText
from jinja2 import Template



# to = "katevlchkk@gmail.com"
mas = [{'name': 'john', 'surname': 'ivanov', 'id_of_test': 111, 'result': 3, 'num_of_questions': 5},
       {'name': 'jeff', 'surname': 'pavlov', 'id_of_test': 77, 'result': 9, 'num_of_questions': 15}]


def mas_to_string(mas):
    new_mas = []
    for i in mas:
        s = str(i['name']) + ' ' + str(i['surname']) + ' набрал(а) ' + str(i['result']) + ' баллов из ' + str(
            i['num_of_questions']) + ' в тесте с id ' + str(i['id_of_test']) + ' '
        new_mas.append(s)
    return new_mas


def send_email(to):
    sender = "sales.botik@gmail.com"
    password = "uyxymvvguqtsbrry"
    name = 'чел'
    workers = mas_to_string(mas)
    context = {
        'name': name,
        'workers': workers
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


