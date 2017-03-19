import sys
import time
import json
from pprint import pprint
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import spacy
import pybikes

def on_chat_message(msg):
    content_type, chat_type, chat_id =telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    if content_type == 'text':
        doc = nlp(msg['text'])

        #simpified: user asks by name of station
        station = torino_stations.get(msg['text'], None);
        if station:
            response = "station " + msg['text'] + ":\nbikes:" + str(station.bikes) + "\nfree:" + str(station.free)
            bot.sendMessage(chat_id, response)
        else:
            markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Send position', request_location=True)]])
            bot.sendMessage(chat_id, 'Where are you?', reply_markup=markup)

    elif content_type == 'position':
        bot.sendMessage(chat_id, "Ok I got your position")

    else:
        bot.sendMessage(chat_id, "why did you send " + content_type + "?")


# load the token from file
with open('../tokens.json') as tokens_file:
    data = json.load(tokens_file)
    telegram_token = data['telegram']

nlp = spacy.load('en')

torino_bikeshare = pybikes.get('to-bike')
torino_bikeshare.update()
torino_stations = {x.name:x for x in torino_bikeshare.stations}

bot = telepot.Bot(telegram_token)
pprint(bot.getMe())
bot.message_loop({'chat': on_chat_message})

while 1:
    # keep updating the bike-sharing data every 5 min
    time.sleep(60*5)
    torino_bikeshare.update()
    torino_stations = {x.name:x for x in torino_bikeshare.stations}
