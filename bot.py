import config
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from random import randint
import sqlite3 

bot = telebot.TeleBot(config.API_TOKEN)

def senf_info(bot, message, row):
        
        info = f"""
📍Title of movie:   {row[2]}
📍Year:                   {row[3]}
📍Genres:              {row[4]}
📍Rating IMDB:      {row[5]}


🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻
{row[6]}
"""
        bot.send_photo(message.chat.id,row[1])
        bot.send_message(message.chat.id, info, reply_markup=add_to_favorite(row[0]))


def add_to_favorite(id):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton("Добавить фильм в избранное 🌟", callback_data=f'favorite_{id}'))
        return markup


def main_markup():
  markup = ReplyKeyboardMarkup()
  markup.add(KeyboardButton('/random'))
  return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("favorite"):
        id = call.data[call.data.find("_")+1:]


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """Hello! You're welcome to the best Movie-Chat-Bot🎥!
Here you can find 1000 movies 🔥
Click /random to get random movie
Or write the title of movie and I will try to find it! 🎬 """, reply_markup=main_markup())

@bot.message_handler(commands=['random'])
def random_movie(message):
    con = sqlite3.connect("movie_database.db")
    with con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM movies ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchall()[0]
        cur.close()
    senf_info(bot, message, row)


@bot.message_handler(commands=['genre_movies'])
def genre_movies(message):
    def send_info(message, movie):
        # Assuming the movie is a tuple with elements (title, genre, year)
        title = movie[0]
        genre = movie[1]
        year = movie[2]
        movie_info = f"Title: {title}\nGenre: {genre}\nYear: {year}"
        bot.send_message(message.chat.id, movie_info)

    genres = message.text.split()[1:]
    if not genres:
        bot.reply_to(message, "Вы не указали жанры. Пожалуйста, укажите хотя бы один жанр.")
        return

    con = sqlite3.connect("movie_database.db")
    with con:
        cur = con.cursor()
        # Поиск фильмов по выбранным жанрам
        query = "SELECT * FROM movies WHERE "
        query += " OR ".join(["genre LIKE ?" for _ in range(len(genres))])
        cur.execute(query, tuple(f"%{genre}%" for genre in genres))
        movies = cur.fetchall()

    if not movies:
        bot.reply_to(message, "По вашему запросу ничего не найдено.")
        return

    for movie in movies:
        # Инлайним содержимое функции send_info
        title = movie[0]
        genre = movie[1]
        year = movie[2]
        movie_info = f"Title: {title}\nGenre: {genre}\nYear: {year}"
        bot.send_message(message.chat.id, movie_info)


@bot.message_handler(func=lambda message: True)
def echo_message(message):

    con = sqlite3.connect("movie_database.db")
    with con:
        cur = con.cursor()
        cur.execute(f"select * from movies where LOWER(title) = '{message.text.lower()}'")
        row = cur.fetchall()
        if row:
            row = row[0]
            bot.send_message(message.chat.id,"Of course! I know this movie😌")
            senf_info(bot, message, row)
        else:
            bot.send_message(message.chat.id,"I don't know this movie ")

        cur.close()



bot.infinity_polling()
