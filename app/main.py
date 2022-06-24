from flask import Flask, request
import telebot
from telebot import types
import sqlite3
from secrets import token

bot = telebot.TeleBot(token)
path_to_db = './database/sqlite_python'
app = Flask(__name__)


def create_or_connect_to_database(chat_id, name_of_database):
    try:
        sqlite_connection = sqlite3.connect(f'{str(name_of_database)}.db')
        cursor = sqlite_connection.cursor()
        bot.send_message(chat_id, "База данных создана и успешно подключена к SQLite", parse_mode='html')
        sqlite_select_query = "select sqlite_version();"
        cursor.execute(sqlite_select_query)
        record = cursor.fetchall()
        bot.send_message(chat_id, f"Версия базы данных SQLite: {record}", parse_mode='html')
        cursor.close()

    except sqlite3.Error as error:
        bot.send_message(chat_id, f"Ошибка при подключении к sqlite {error}", parse_mode='html')
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            bot.send_message(chat_id, "Соединение с SQLite закрыто", parse_mode='html')


def create_new_table_at_database(chat_id, name_of_database):
    try:
        sqlite_connection = sqlite3.connect(f'{str(name_of_database)}.db')
        cursor = sqlite_connection.cursor()
        my_shopping_list_query = '''CREATE TABLE sqlitedb_shoppinglist (
                                        id INTEGER PRIMARY KEY,
                                        name TEXT NOT NULL,
                                        amount integer NOT NULL,
                                        dimension TEXT NOT NULL,
                                        id_user INTEGER);'''
        cursor.execute(my_shopping_list_query)
        sqlite_connection.commit()
        bot.send_message(chat_id, f"Таблица была успешно создана!", parse_mode='html')
        cursor.close()

    except sqlite3.Error as error:
        bot.send_message(chat_id, f"Ошибка при подключении к sqlite {error}", parse_mode='html')
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            bot.send_message(chat_id, "Соединение с SQLite закрыто", parse_mode='html')


def add_new_item(chat_id, name_of_database, parameters):
    try:
        sqlite_connection = sqlite3.connect(f'{str(name_of_database)}.db')
        cursor = sqlite_connection.cursor()
        add_new_item_query = f"""INSERT INTO sqlitedb_shoppinglist
                          (name, amount , dimension, id_user)  VALUES  ('{parameters['name']}', {parameters['amount']}, '{parameters['dimension']}', {parameters['user_id']}) """
        cursor.execute(add_new_item_query)
        sqlite_connection.commit()
        bot.send_message(chat_id,
                         f"Предмет '{parameters['name']}' был успешно добавлен в количестве {parameters['amount']} {parameters['dimension']}.!",
                         parse_mode='html')
        cursor.close()

    except sqlite3.Error as error:
        bot.send_message(chat_id, f"Ошибка при подключении к sqlite {error}", parse_mode='html')
    finally:
        if (sqlite_connection):
            sqlite_connection.close()


def get_list(chat_id, name_of_database, user_id):
    try:
        sqlite_connection = sqlite3.connect(f'{str(name_of_database)}.db')
        cursor = sqlite_connection.cursor()
        add_new_item_query = f"""SELECT id, name, amount, dimension FROM sqlitedb_shoppinglist WHERE id_user == {user_id}"""
        cursor.execute(add_new_item_query)
        record = cursor.fetchall()
        cursor.close()

    except sqlite3.Error as error:
        bot.send_message(chat_id, f"Ошибка при подключении к sqlite {error}", parse_mode='html')
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            return record


def delete_list(chat_id, name_of_database, user_id):
    try:
        sqlite_connection = sqlite3.connect(f'{str(name_of_database)}.db')
        cursor = sqlite_connection.cursor()
        delete_items_query = f"""DELETE FROM sqlitedb_shoppinglist WHERE id_user == {user_id}"""
        cursor.execute(delete_items_query)
        sqlite_connection.commit()
        bot.send_message(chat_id, f"Список покупок успешно удален!", parse_mode='html')
        cursor.close()

    except sqlite3.Error as error:
        bot.send_message(chat_id, f"Ошибка при подключении к sqlite {error}", parse_mode='html')
    finally:
        if (sqlite_connection):
            sqlite_connection.close()


def delete_item_from_database(chat_id, name_of_database, item_id):
    try:
        sqlite_connection = sqlite3.connect(f'{str(name_of_database)}.db')
        cursor = sqlite_connection.cursor()
        delete_item_query = f"""DELETE FROM sqlitedb_shoppinglist WHERE id == {item_id}"""
        cursor.execute(delete_item_query)
        sqlite_connection.commit()
        bot.send_message(chat_id, f"Предмет успешно удален!", parse_mode='html')
        cursor.close()

    except sqlite3.Error as error:
        bot.send_message(chat_id, f"Ошибка при подключении к sqlite {error}", parse_mode='html')
    finally:
        if (sqlite_connection):
            sqlite_connection.close()


def change_data_param_item(message, chat_id, name_of_database, item_id, parameter):
    try:
        sqlite_connection = sqlite3.connect(f'{str(name_of_database)}.db')
        cursor = sqlite_connection.cursor()
        add_new_item_query = f"""UPDATE sqlitedb_shoppinglist SET {parameter} = '{message.text}' WHERE id = {item_id}"""
        cursor.execute(add_new_item_query)
        sqlite_connection.commit()
        bot.send_message(chat_id,
                         f"Предмет был успешно обнавлен!",
                         parse_mode='html')
        cursor.close()
    except sqlite3.Error as error:
        bot.send_message(chat_id, f"Ошибка при подключении к sqlite {error}", parse_mode='html')
    finally:
        if (sqlite_connection):
            sqlite_connection.close()


@bot.message_handler(commands=["start"])
def start(message):
    bot_message = f"<b>Hello,{message.from_user.first_name}</b>"
    bot_json_message = f"{message.json}"
    bot.send_message(message.chat.id, bot_message, parse_mode='html')
    bot.send_message(message.chat.id, bot_json_message, parse_mode='html')
    create_or_connect_to_database(message.chat.id, path_to_db)


@bot.message_handler(commands=["newtable"])
def create_new_table(message):
    create_new_table_at_database(message.chat.id, path_to_db)


@bot.message_handler(commands=['list'])
def shopping_list(message):
    shoppinglist = get_list(message.chat.id, path_to_db, message.from_user.id)
    keyboard = types.InlineKeyboardMarkup()
    for item in shoppinglist:
        keyboard.add(types.InlineKeyboardButton(f'{item[1]} - {item[2]} {item[3]}.', callback_data=f'{item[0]}'))
    bot.send_message(message.chat.id, 'Ваш список покупок:', reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def commands(message):
    commands_list = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    # start_button = types.KeyboardButton('/start')
    help_button = types.KeyboardButton('/help')
    list_button = types.KeyboardButton('/list')
    clean_list_button = types.KeyboardButton('/clean')
    # add_new_table_button = types.KeyboardButton('/newtable')
    # commands_list.add(help_button, start_button, list_button, clean_list_button, add_new_table_button)
    commands_list.add(help_button, list_button, clean_list_button)
    bot.send_message(message.chat.id, "Комманды!", reply_markup=commands_list)


@bot.message_handler(commands=['clean'])
def clean_the_shoppinglist(message):
    delete_list(message.chat.id, path_to_db, message.from_user.id)


@bot.callback_query_handler(func=lambda callback: True and callback.data.split(" ")[0] == 'delete')
def delete_item(callback):
    bot.answer_callback_query(callback.id)
    delete_item_from_database(callback.message.chat.id, path_to_db, callback.data.split(" ")[1])


@bot.callback_query_handler(func=lambda callback: True and (
        callback.data.split(" ")[0] == 'change_name' or callback.data.split(" ")[0] == 'change_amount' or callback.data.split(" ")[0] == 'change_dimension'))
def change_data_item(callback):
    bot.answer_callback_query(callback.id)
    parameter = callback.data.split(" ")[0].split("_")[1]
    data = bot.send_message(callback.message.chat.id, f'{parameter}', parse_mode='html')
    bot.register_next_step_handler(data, change_data_param_item, callback.message.chat.id, path_to_db,
                                   callback.data.split(" ")[1], parameter)


@bot.callback_query_handler(func=lambda callback: True)
def change_item(callback):
    keyboard = types.InlineKeyboardMarkup()
    delete_button = types.InlineKeyboardButton('Удалить!', callback_data=f'delete {callback.data}')
    change_name_button = types.InlineKeyboardButton('Изменить наименование!',
                                                    callback_data=f'change_name {callback.data}')
    change_amount_button = types.InlineKeyboardButton('Изменить количество!',
                                                      callback_data=f'change_amount {callback.data}')
    change_dimension_button = types.InlineKeyboardButton('Изменить размерность!',
                                                      callback_data=f'change_dimension {callback.data}')
    keyboard.add(delete_button)
    keyboard.add(change_name_button)
    keyboard.add(change_amount_button)
    keyboard.add(change_dimension_button)
    bot.answer_callback_query(callback.id)
    bot.send_message(callback.message.chat.id, f'Что вы хотите сделать?', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def add_item_to_database(message):
    items = message.text.split('\n')
    for item in items:
        if len(item.split(' ')) > 2:
            try:
                item_param = {
                    'name': item.split(' ')[0],
                    'amount': item.split(' ')[1],
                    'dimension': item.split(' ')[2],
                    'user_id': message.from_user.id}
                add_new_item(message.chat.id, path_to_db, item_param)
            except Exception:
                bot.send_message(message.chat.id, f"Проверьте правильность составленного списка!", parse_mode='html')
        else:
            bot.send_message(
                message.chat.id,
                "Недосточно аргументов.\nПожалуйста, скорректируйте аргументы команды!",
                parse_mode='html')


@app.route("/" + token, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


bot.remove_webhook()
bot.polling(none_stop=True)
bot.set_webhook('https://test.com/' + token)
app.run()
