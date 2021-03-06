from config import *
from telebot import types
from lang import lang, NUMBER_OF_LISTENING
from dictionary import dictionary
import bd
from flask import Flask
import flask

app = Flask(__name__)


def show_listenings(call, complexity, begin=1, permission=False):
    listenings = bd.select_from_bd_listenings(complexity)
    keyboard = types.InlineKeyboardMarkup()
    if len(listenings[begin:]) != 0:
        for k, listening in enumerate(listenings[begin:], begin):
            if bd.check_user(listening[0], call.message.chat.id) is False:
                keyboard.add(*[types.InlineKeyboardButton(text=str(listening[1]) + ' ❌', callback_data=str(listening[0]) + ' ❌')])
            else:
                keyboard.add(*[types.InlineKeyboardButton(text=str(listening[1]) + ' ✅', callback_data=str(listening[0]) + ' ✅')])
            if k % NUMBER_OF_LISTENING == 0:
                break
        add_navigation(keyboard, begin, complexity)
        if permission is False:
            bot.send_message(call.message.chat.id, lang["listenings_msg"], reply_markup=keyboard)
        else:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=keyboard)


def main_menu(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*[types.InlineKeyboardButton(text=btn, callback_data=btn) for btn in lang['menu_complexity']])
    bot.send_message(message.chat.id, lang["welcome_msg"], reply_markup=keyboard)


def add_navigation(keyboard, begin, complexity):
    keyboard.add(*[types.InlineKeyboardButton(text=btn, callback_data=str(complexity) + ':' + str(begin) + ':' + btn) for btn in lang['navigation_btn']])
    return keyboard


@bot.message_handler(commands=['start'])
def start(message):
    if bd.check_user_to_users(message.chat.username) is False:
        bd.insert_user_to_users(message.chat.username)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Main menu')
    bot.send_message(message.chat.id, 'Hello!', reply_markup=markup)
    main_menu(message)


@bot.message_handler(func=lambda message: message.text == 'Main menu')
def start(message):
    main_menu(message)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, lang["help_msg"])


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data in lang["menu_complexity"]:
        show_listenings(call, call.data.lower())
    elif call.data[:-2].isdigit() and call.data[-2:] in lang["choice"]:
        listening = bd.select_from_bd_listening(int(call.data[:-2]))
        bot.send_audio(call.message.chat.id, audio=open('sounds/' + str(call.data[:-2]) + '.mp3', 'rb'), parse_mode='markdown',
                       caption=lang["information_msg"].format(listening[1], listening[3], listening[4], listening[5], listening[6]))
        for id_question, i in enumerate(dictionary[int(call.data[:-2])]):
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(*[types.InlineKeyboardButton(text=lang['choice_btn'][id_answer], callback_data=call.data[:-2] + ':' + str(
                id_question) + ':' + str(id_answer)) for id_answer, j in enumerate(dictionary[int(call.data[:-2])][i][:-1])])
            bot.send_message(call.message.chat.id, lang['text_msg'].format(i, *dictionary[int(call.data[:-2])][i][:-1]), reply_markup=keyboard)
            global counter
            counter = 0
    elif call.data.split(':')[0].isdigit() and call.data.split(':')[1].isdigit() and call.data.split(':')[2].isdigit() and len(call.data.split(':')) == 3:
        question = list(dictionary[int(call.data.split(':')[0])].keys())[int(call.data.split(':')[1])]
        keyboard = types.InlineKeyboardMarkup()
        if dictionary[int(call.data.split(':')[0])][question][int(call.data.split(':')[2])] == dictionary[int(call.data.split(':')[0])][question][-1]:
            keyboard.add(*[types.InlineKeyboardButton(text=lang['choice_btn'][id_answer] + ' ✅', callback_data=call.data.split(':')[0] + ':' + str(
                call.data.split(':')[1]) + ':' + str(id_answer) + ':✅') if id_answer == int(call.data.split(':')[2]) else types.InlineKeyboardButton(text=lang['choice_btn'][id_answer], callback_data=call.data.split(':')[0] + ':' + str(
                    call.data.split(':')[1]) + ':' + str(id_answer)) for id_answer, j in enumerate(dictionary[int(call.data.split(':')[0])][question][:-1])])
        else:
            keyboard.add(*[types.InlineKeyboardButton(text=lang['choice_btn'][id_answer] + ' ❌', callback_data=call.data.split(':')[0] + ':' + str(
                call.data.split(':')[1]) + ':' + str(id_answer) + ':❌') if id_answer == int(call.data.split(':')[2]) else types.InlineKeyboardButton(text=lang['choice_btn'][id_answer], callback_data=call.data.split(':')[0] + ':' + str(
                    call.data.split(':')[1]) + ':' + str(id_answer)) for id_answer, j in enumerate(dictionary[int(call.data.split(':')[0])][question][:-1])])
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=keyboard)
        counter += 1
        if counter == len(dictionary[int(call.data.split(':')[0])]):
            if bd.check_user(int(call.data.split(':')[0]), call.message.chat.id) is False:
                bd.insert_user(int(call.data.split(':')[0]), call.message.chat.id)
    elif call.data[-3:] in lang["navigation_btn"][1]:
        show_listenings(call, call.data.split(':')[0], int(call.data.split(':')[1]) + NUMBER_OF_LISTENING, True)
    elif call.data[-3:] in lang["navigation_btn"][0] and int(call.data.split(':')[1]) > 1:
        show_listenings(call, call.data.split(':')[0], int(call.data.split(':')[1]) - NUMBER_OF_LISTENING, True)
    else:
        pass


# bot.polling()

@app.route("/", methods=['POST', 'GET'])
def test():
   return 'test'

# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
   if flask.request.headers.get('content-type') == 'application/json':
       json_string = flask.request.get_data().decode('utf-8')
       update = types.Update.de_json(json_string)
       bot.process_new_updates([update])
       return ''
   else:
       flask.abort(403)

if __name__ == "__main__":
   # Start flask server
   # Remove webhook, it fails sometimes the set if there is a previous webhook
   bot.remove_webhook()
   #sleep(1)
   print(bot.get_webhook_info())
   #bot.polling()
   # Set webhook
   bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                 certificate=open(WEBHOOK_SSL_CERT, 'r'))
   app.run(host=WEBHOOK_LISTEN,
           port=WEBHOOK_PORT,
           ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
           threaded=True)
