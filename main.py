import telebot
from bs4 import BeautifulSoup
import sqlite3
from kek import toyt
import os

bot = telebot.TeleBot("6029681277:AAGWFyVdGOrF4Luaw_xpQPV6CpuVYsupJXw", parse_mode=None)
get_audio = False
find_yt = False

conn = sqlite3.connect('data1.db', check_same_thread=False)
cursor = conn.cursor()
delete = False
dir = "data/"


def db_table_val(name: str, song: str):
    cursor.execute('INSERT INTO test1 (name, song) VALUES (?, ?)',
                   (name, song))
    conn.commit()


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("Открыть плейлист")
    btn2 = telebot.types.KeyboardButton("Найти песню")
    btn3 = telebot.types.KeyboardButton("Загрузить песню")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id,
                     "Привет, ты можешь использовать этого бота для прослушивавния музыки ".format(message.from_user),
                     reply_markup=markup)


@bot.message_handler(content_types=['text', 'document', 'audio'])
def func(message):
    global get_audio, find_yt
    # -----------------------------------------
    if message.text == "Открыть плейлист":
        markup = telebot.types.InlineKeyboardMarkup()
        buttonA = telebot.types.InlineKeyboardButton('Воспроизвести', callback_data='A')
        buttonC = telebot.types.InlineKeyboardButton('Стереть плейлист', callback_data='C')
        markup.add(buttonA, buttonC)
        v = send_playlist(message)
        bot.send_message(message.chat.id, v, reply_markup=markup)

    elif message.text == "Найти песню":
        bot.send_message(message.chat.id, text="Введите название песни")
        find_yt = True
    elif message.text == "Загрузить песню":
        bot.send_message(message.chat.id, text="Загрузите песню, скинув файл или аудио ")
        get_audio = True

    # -----------------------------------------
    elif find_yt is True:
        if message.text != "":
            bot.send_message(message.chat.id, "Подождите, это займет немного времени")
            k = toyt(message.text)
            if k != False and k != 1:
                db_table_val(name=message.from_user.username, song=k)
                bot.send_message(message.chat.id, "Эта песня скачена и добавлена в плейлист")
            else:
                bot.send_message(message.chat.id, "Эта песня уже добавлена в плейлист")

        find_yt = False


    elif get_audio is True:
        if message.content_type == 'document':  # wav
            if message.document.file_name in os.listdir("data/"):
                bot.send_message(message.chat.id, "Эта песня уже есть в плейлисте")
            else:
                db_table_val(message.from_user.username, message.document.file_name)
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)

                src = 'data/' + message.document.file_name
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)

                bot.reply_to(message, "Пожалуй, я сохраню это")
        elif message.content_type == 'audio':  # mp3

            if message.audio.file_name in os.listdir("data/"):
                bot.send_message(message.chat.id, "Эта песня уже есть в плейлисте")
            else:
                db_table_val(message.from_user.username, message.audio.file_name)
                file_info = bot.get_file(message.audio.file_id)
                downloaded_file = bot.download_file(file_info.file_path)

                src = 'data/' + message.audio.file_name
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)

                bot.reply_to(message, "Пожалуй, я сохраню это")


def send_playlist(message):
    all_text = "Ваш плейлист:\n"
    playlist = cursor.execute("SELECT (song) FROM test1").fetchall()
    for j in playlist:
        all_text += f"{str(playlist.index(j) + 1)}: {j[0]}" + "\n"

    return all_text


@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    if call.data == "A":
        k = cursor.execute('SELECT * FROM test1').fetchall()

        conn.commit()
        for (i, j) in k:
            audio = open(f'data/{i}.mp3', 'rb')
            bot.send_message(call.message.chat.id, f"{j} добавил песню:")
            bot.send_audio(call.message.chat.id, audio)

    if call.data == "C":
        cursor.execute(f'DELETE from test1')
        conn.commit()
        bot.send_message(call.message.chat.id, (f"Весь плейлист был удален"))
        dir = 'data/'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
        bot.answer_callback_query(call.id)


bot.polling(True)
