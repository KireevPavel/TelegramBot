import datetime
import sqlite3

import telebot
from telebot import types

import config

bot = telebot.TeleBot(config.BOT_TOKEN)
name = None
phone = None
date = None
id = None
pricePython = types.LabeledPrice(label='Курс по программированию на Python', amount=5000 * 100)
priceJava = types.LabeledPrice(label='Курс по программированию на Java', amount=5000 * 100)
priceHTML = types.LabeledPrice(label='Курс по программированию на HTML', amount=5000 * 100)
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


def payPython(message):
    bot.send_invoice(message.chat.id,
                     title='Курс по Python',
                     description='Оплата курса по Python на месяц',
                     provider_token=config.PAYMENT_TOKEN,
                     currency='rub',
                     photo_url='https://img.freepik.com/premium-photo/school-kid-holding-index-finger-up-with-great'
                               '-new-idea-nerd-pupil-boy-from-elementary-school_545934-43036.jpg?size=626&ext=jpg&ga'
                               '=GA1.1.898993043.1705044857&semt=ais',
                     photo_width=416,
                     photo_height=234,
                     photo_size=416,
                     is_flexible=False,
                     prices=[pricePython],
                     start_parameter='one-month',
                     invoice_payload='test-invoice-payload'
                     )


def payJava(message):
    bot.send_invoice(message.chat.id,
                     title='Курс по Java',
                     description='Оплата курса по Java на месяц',
                     provider_token=config.PAYMENT_TOKEN,
                     currency='rub',
                     photo_url='https://img.freepik.com/premium-photo/smart-boy-in-a-blue-t-shirt-thinking-holding-a'
                               '-laptop-in-his-hands-on-yellow_88135-20272.jpg?size=626&ext=jpg&ga=GA1.1.898993043'
                               '.1705044857&semt=ais',
                     photo_width=416,
                     photo_height=234,
                     photo_size=416,
                     is_flexible=False,
                     prices=[priceJava],
                     start_parameter='one-month',
                     invoice_payload='test-invoice-payload'
                     )


def payHTML(message):
    bot.send_invoice(message.chat.id,
                     title='Курс по HTML',
                     description='Оплата курса по HTML на месяц',
                     provider_token=config.PAYMENT_TOKEN,
                     currency='rub',
                     photo_url='https://img.freepik.com/premium-photo/smart-schoolboy-with-a-laptop-on-a-yellow'
                               '-background_88135-13403.jpg?size=626&ext=jpg&ga=GA1.1.898993043.1705044857&semt=ais',
                     photo_width=416,
                     photo_height=234,
                     photo_size=416,
                     is_flexible=False,
                     prices=[priceHTML],
                     start_parameter='one-month',
                     invoice_payload='test-invoice-payload'
                     )


@bot.pre_checkout_query_handler(lambda query: True)
def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


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
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Вернуться в главное меню", callback_data='menu'))
    bot.send_message(message.chat.id,
                     'Ваша заявка на пробный урок в нашу онлайн-школу программирования успешно обработана!😃',
                     reply_markup=markup)


def menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Подробнее о нас", callback_data='inf'))
    markup.add(types.InlineKeyboardButton("Записаться", callback_data='reg'))
    markup.add(types.InlineKeyboardButton("Оплатить курс", callback_data='pay'))
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Подробнее о нас", callback_data='inf'))
    markup.add(types.InlineKeyboardButton("Записаться", callback_data='reg'))
    markup.add(types.InlineKeyboardButton("Оплатить курс", callback_data='pay'))

    bot.send_message(message.chat.id,
                     f'{message.from_user.first_name}, добро пожаловать в QiwiKids! Мы рады приветствовать вас'
                     f' в нашей онлайн-школе программирования!', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callbackMessage(callback):
    if callback.data == 'reg':
        global id
        id = callback.message.from_user.id
        sql.execute(f"SELECT id FROM users WHERE id = '{id}'")
        if sql.fetchone() is None:
            sql.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", (id, "0", "0", "0", "new", "0"))
            db.commit()
        userAct = sql.execute(f"SELECT act FROM Users WHERE id = '{id}'").fetchone()[0]
        if userAct == "new":
            signUp(callback.message)
        elif userAct == "full":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Изменить запись", callback_data='edit'))
            markup.add(types.InlineKeyboardButton("Вернуться в главное меню", callback_data='menu'))
            bot.send_message(callback.message.chat.id, 'Вы уже зарегистрированы. Желаете изменить запись?',
                             reply_markup=markup)

    elif callback.data == 'inf':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Наш сайт", url='https://vk.link/qiwikids'))
        markup.add(types.InlineKeyboardButton("Вернуться в главное меню", callback_data='menu'))
        bot.send_message(callback.message.chat.id,
                         "QiwiKids – место, где дети и подростки получают навыки для успешного будущего и узнают всё "
                         "о высоких технологиях. 😎\n"
                         "Что умеют дети из QiwiKids?\n"
                         "🟣Разрабатывать сайты, компьютерные игры и приложения.\n"
                         "🟣Проектировать 3D-модели.\n"
                         "🟣Писать чат-боты и работать в графических редакторах.\n"
                         "Присоединиться к QiwiKids можно с любым уровнем знаний.\n"
                         "На первом бесплатном занятии Вы узнаете больше о нашей школе и сможете задать вопросы "
                         "напрямую преподавателю. А ребенок уже создаст первый мини-проект 🔥 ".format(
                             callback.message.from_user),
                         reply_markup=markup)
    elif callback.data == 'menu':
        menu(callback.message)

    elif callback.data == 'edit':
        id = callback.message.from_user.id
        sql.execute(f"UPDATE Users SET act = 'new' WHERE id = {id}")
        db.commit()
        signUp(callback.message)

    elif callback.data == 'pay':
        payPython(callback.message)
        payJava(callback.message)
        payHTML(callback.message)
        menu(callback.message)


bot.polling(non_stop=True)
