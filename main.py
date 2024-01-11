import sqlite3
import datetime
import config

import telebot
from telebot import types


bot = telebot.TeleBot(config.BOT_TOKEN)
name = None
phone = None
date = None
id = None

userAct = '0'

db = sqlite3.connect('Users.db', check_same_thread=False)
sql = db.cursor()
sql.execute('CREATE TABLE IF NOT EXISTS Users ('
            'id INTEGER  NOT NULL PRIMARY KEY,'
            'name VARCHAR,'
            'phone VARCHAR,'
            'date DATE,'
            'act TEXT,'
            'time DATE'
            ')')
db.commit()


def fixMsg(msg):
    msg = "'" + msg + "'"
    return msg


def signUp(message):
    bot.send_message(message.chat.id, 'Пожалуйста, введите Ваши ФИО')
    bot.register_next_step_handler(message, getName)


def getName(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Введите контактный номер телефона')
    bot.register_next_step_handler(message, getPhone)


def getPhone(message):
    global phone
    phone = message.text.strip()
    bot.send_message(message.chat.id, 'Напишите удобную Вам дату в формате ДД.ММ.ГГГГ')
    bot.register_next_step_handler(message, getDate)


def getDate(message):
    global date
    timeNow = f"{datetime.datetime.now()}"
    date = message.text.strip()
    sql.execute(f"UPDATE Users SET name = {fixMsg(name)},"
                f"phone = {fixMsg(phone)}, "
                f"date = {fixMsg(date)}, "
                f"act = 'full', "
                f"time = {fixMsg(timeNow)} WHERE id = {id} ")
    db.commit()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Подробнее о нас")
    button2 = types.KeyboardButton("Изменить запись")
    button3 = types.KeyboardButton("Оплатить курс")
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id,
                     'Ваша заявка на пробный урок в нашу онлайн-школу программирования успешно обработана!😃',
                     reply_markup=markup)


# @bot.message_handler(commands=['pay'])
# def pay(message):
#     bot.send_message(message.chat.id,'Покупка курса','Покупка курса по программиранию','invoice', config.PAYMENT_TOKEN, 'RUB',[types.LabeledPrice('Покупка курса',500)] )

@bot.message_handler(commands=['test'])
def test(message):
    bot.send_message(message.chat.id,"test")

@bot.message_handler()
def start(message):
    if message.text.lower() == '/start':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Подробнее о нас")
        button2 = types.KeyboardButton("Записаться")
        button3 = types.KeyboardButton("Оплатить курс")
        markup.add(button1, button2, button3)
        bot.send_message(message.chat.id,
                         f'{message.from_user.first_name}, добро пожаловать в QiwiKids! Мы рады приветствовать вас'
                         f' в нашей онлайн-школе программирования!', reply_markup=markup)
    elif message.text.lower() == 'записаться':
        global id
        id = message.from_user.id
        sql.execute(f"SELECT id FROM users WHERE id = '{id}'")
        if sql.fetchone() is None:
            sql.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", (id, "0", "0", "0", "new","0"))
            db.commit()
        userAct = sql.execute(f"SELECT act FROM Users WHERE id = '{id}'").fetchone()[0]
        if userAct == "new":
            signUp(message)
        elif userAct == "full":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.KeyboardButton("Изменить запись")
            button2 = types.KeyboardButton("Вернуться в главное меню")
            markup.add(button1, button2)
            bot.send_message(message.chat.id,
                             f'{message.from_user.first_name}, Вы уже зарегистрированы. Желаете изменить запись?',
                             reply_markup=markup)
    elif message.text.lower() == 'изменить запись':
        id = message.from_user.id
        sql.execute(f"UPDATE Users SET act = 'new' WHERE id = {id}")
        db.commit()
        signUp(message)

    elif message.text.lower() == 'вернуться в главное меню':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Подробнее о нас")
        button2 = types.KeyboardButton("Записаться")
        button3 = types.KeyboardButton("Оплатить курс")
        markup.add(button1, button2, button3)
        bot.send_message(message.chat.id,
                         'Выберите действие', reply_markup=markup)

    elif message.text.lower() == 'подробнее о нас':
        markup1 = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("Наш сайт", url='https://vk.link/qiwikids')
        markup1.add(button1)
        bot.send_message(message.chat.id,
                         "QiwiKids – место, где дети и подростки получают навыки для успешного будущего и узнают всё о высоких технологиях. 😎\n"
                         "Что умеют дети из QiwiKids?\n"
                         "🟣Разрабатывать сайты, компьютерные игры и приложения.\n"
                         "🟣Проектировать 3D-модели.\n"
                         "🟣Писать чат-боты и работать в графических редакторах.\n"
                         "Присоединиться к QiwiKids можно с любым уровнем знаний.\n"
                         "На первом бесплатном занятии Вы узнаете больше о нашей школе и сможете задать вопросы напрямую преподавателю. А ребенок уже создаст первый мини-проект 🔥 ".format(
                             message.from_user),
                         reply_markup=markup1)



bot.polling(non_stop=True)
