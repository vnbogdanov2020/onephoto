from setting import bot_token
from setting import cnx

import telebot
from telebot import types
import requests
import json


KeyWin1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=1)
KeyWin1.row('Мои события')

KeyWin2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=1)
KeyWin2.row('Добавить ')

cursor = cnx.cursor()

bot = telebot.TeleBot(bot_token)

#Первый запуск
@bot.message_handler(commands=['start'])
def start_message(message):
    sql = ("SELECT * FROM users WHERE chat_id= %s")
    cursor.execute(sql, [(message.chat.id)])
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (chat_id) VALUES (%s)", [(message.chat.id)])
        cnx.commit()
        cursor.close()
        cnx.close()

    bot.send_message(message.chat.id,
                     'Привет! Я помогу зафиксировать историю, которая проходит каждый день. Для этого вы можете указать событие и каждый день делать одно фото. Затем можно составить из ваших фото видео-историю, которой можно поделиться с друзьями.',
                     reply_markup=KeyWin1)

#Обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'мои события':
        markup = types.InlineKeyboardMarkup()
        sql = ("SELECT events_id, events_name FROM events WHERE chat_id= %s")
        cursor.execute(sql, [(message.chat.id)])
        events = cursor.fetchall()

        for row in events:
            switch_button = types.InlineKeyboardButton(text=row[1], callback_data=row[0])
            markup.add(switch_button)

        switch_button = types.InlineKeyboardButton(text='Добавить...', callback_data='NewEvent')
        markup.add(switch_button)
        bot.send_message(message.chat.id, "Ваши события", reply_markup=markup)

@bot.callback_query_handler(func=lambda c:True)
def inline(callback):
    #Обрабатываем события
    print(callback)
    if callback.data=='NewEvent':
        send = bot.send_message(callback.message.chat.id, 'Укажите название события')
        bot.register_next_step_handler(send, NewEvent)
        #log(callback.message)


def NewEvent(message):
    bot.send_message(message.chat.id, 'Создано новое событие {NewName}'.format(NewName=message.text))
    newdata = [
        (message.chat.id,message.text),
    ]
    cursor.executemany("INSERT INTO events (chat_id, events_name) VALUES (%s,%s)", newdata)
    cnx.commit()
    cursor.close()
    cnx.close()

bot.polling()