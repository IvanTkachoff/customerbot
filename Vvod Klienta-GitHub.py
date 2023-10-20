#!/usr/bin/env python
# coding: utf-8

# In[1]:


import telebot
from telebot import types
import requests
from datetime import datetime
import re

telebot.apihelper.SESSION = requests.Session()
telebot.apihelper.SESSION.timeout = 100

bot = telebot.TeleBot('xxxx') #Enter your API


# In[2]:


import pandas as pd
# df = pd.read_excel("ludget.xlsx")
df = pd.DataFrame(columns=['nomer','otkuda_klient', 'Imya', 'phone', 'zapros', 'time_priem', 'aktivnost'])
df


# In[3]:


user_states = {}
DEACTIVATE_STATE = 404
otkuda_klient = None
imya = None
phone = None
zapros = None

# Команда для начала новой заявки
def handle_new_request(message):
    user_states[message.chat.id] = 0
    bot.send_message(message.chat.id, "Откуда пришла заявка?")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 0)
def handle_question_1(message):
    if message.text == "Отмена":
        user_states[message.chat.id] = None
        return
    global otkuda_klient
    user_states[message.chat.id] = 1
    otkuda_klient = message.text
    bot.send_message(message.chat.id, "Имя клиента?")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 1)
def handle_question_2(message):
    if message.text == "Отмена":
        user_states[message.chat.id] = None
        return
    global imya
    user_states[message.chat.id] = 2
    imya = message.text
    bot.send_message(message.chat.id, "Телефон клиента?")
    
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 2)
def handle_question_3(message):
    if message.text == "Отмена":
        user_states[message.chat.id] = None
        return
    phone_pattern = re.compile(r'^\+?[0-9]+$')  # Регулярное выражение для проверки телефона
    if not phone_pattern.match(message.text) or len(message.text) < 10:
        bot.send_message(message.from_user.id, "Телефон неверен. Введите телефон заново.")
        return
    global phone
    user_states[message.chat.id] = 3
    phone = message.text
    bot.send_message(message.chat.id, "В чем состоит запрос клиента?")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 3)
def handle_question_4(message):
    if message.text == "Отмена":
        user_states[message.chat.id] = None
        return
    if len(message.text) < 10:
        bot.send_message(message.from_user.id, "Требуется больше информации по запросу. Введите запрос заново.")
        return
    global imya, otkuda_klient, phone, zapros
    zapros = message.text
    now = datetime.now()
    global df  # использовать глобальный DataFrame
    df = df.append({
        'nomer': len(df)+1,
        'otkuda_klient': otkuda_klient, 
        'Imya': imya, 
        'phone': phone, 
        'zapros': zapros,
        'time_priem': now.strftime("%d/%m/%Y %H:%M"),
        'aktivnost': 1
    }, ignore_index=True)
    bot.send_message(message.chat.id, "Заявка создана.")
    del user_states[message.chat.id]  # удаляем состояние чата, так как заявка обработана           
    writer = pd.ExcelWriter('ludget.xlsx', engine='xlsxwriter', options={'strings_to_urls': False})
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()


# In[4]:


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global df
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Таблица")
    btn2 = types.KeyboardButton("Новая Заявка")
    btn3 = types.KeyboardButton("Активные заявки")
    btn4 = types.KeyboardButton("Деактивировать номер")
    markup.add(btn1, btn2, btn3, btn4)
    
    if message.from_user.id == xxx or message.from_user.id == xxx: #Enter your Telegram_ID
        current_customer = "man1"
    elif message.from_user.id == xxx:
        current_customer = "man2"
    else:
        bot.send_message(message.from_user.id, "Вы не авторизованы для участия в чате")
        return 
    
    if message.text == "Таблица":
        bot.send_document(message.from_user.id, document=open('ludget.xlsx', 'rb'))
        return
    if message.text == "Новая Заявка":
        handle_new_request(message)
        return
    elif user_states.get(message.chat.id) == 0:
        handle_question_1(message)
        return
    elif user_states.get(message.chat.id) == 1:
        handle_question_2(message)
        return
    elif user_states.get(message.chat.id) == 2:
        handle_question_3(message)
        return
    elif user_states.get(message.chat.id) == 3:
        handle_question_4(message)
        return
    
    if message.text == "Активные заявки":
        for i in range(df.shape[0]):
            if df.iloc[i].aktivnost == 1:
                bot.send_message(message.from_user.id, str(df.iloc[i].nomer) + ". " + str(df.iloc[i].Imya) + " Телефон: " + str(df.iloc[i].phone) + " Запрос: " + str(df.iloc[i].zapros))
        return
        
#         bot.send_message(message.from_user.id, "Откуда пришла заявка?")
#         otkuda_klient = message.text
#         bot.send_message(message.from_user.id, "Имя клиента?")
#         imya = message.text
#         bot.send_message(message.from_user.id, "Телефон Клиента?")
#         phone = message.text
#         now = datetime.now()
#         df = df.append({'otkuda_klient': otkuda_klient, 'Imya': imya, 'phone': phone, 'time_priem': now.strftime("%d/%m/%Y %H:%M")}, ignore_index=True)
#         return
    if message.text == "Деактивировать номер":
        if df.empty:
            bot.send_message(message.from_user.id, "Список пуст, удаление невозможно")
            return
        user_states[message.chat.id] = DEACTIVATE_STATE
        bot.send_message(message.from_user.id, "Введите номер, который хотите деактивировать")
        return
    
    if user_states.get(message.chat.id) == DEACTIVATE_STATE:
        try:
            num_to_deactivate = int(message.text)  # Предполагаем, что номер целочисленный
            if num_to_deactivate in df['nomer'].values:
                df.loc[df['nomer'] == num_to_deactivate, 'aktivnost'] = 0
                bot.send_message(message.from_user.id, f"Номер {num_to_deactivate} деактивирован.")
            else:
                bot.send_message(message.from_user.id, "Такого номера нет в базе.")
        except ValueError:
            bot.send_message(message.from_user.id, "Пожалуйста, введите корректный номер.")
        user_states[message.chat.id] = None  # Сбрасываем состояние
        return
    
    bot.send_message(message.from_user.id, "Чтобы добавить заявку, нажмите: Новая Заявка. Скачать таблицу заявок можно по кнопке Таблица", reply_markup=markup)
     
bot.polling(none_stop=True, interval=0)  # Обязательная для работы бота часть


# In[ ]:




