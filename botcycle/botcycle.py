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
        #doc = nlp(msg['text'])

        if msg['text'][0] == '/':
            if msg['text'][1] == 'b':
                results = stations_with_bikes

            elif msg['text'][1] == 'f':
                results = stations_with_free

            else:
                bot.sendMessage(chat_id, "i don't understand")

            if user_positions.get(chat_id, None) == None:
                markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Send position', request_location=True)]])
                bot.sendMessage(chat_id, 'Where are you?', reply_markup=markup)

            else:
                res = search_nearest(user_positions[chat_id], results)
                bot.sendMessage(chat_id, res.name + ":\nbikes:" + str(res.bikes) + "\nfree:" + str(res.free))

        else:
            #simpified: user asks by name of station
            station = torino_stations.get(msg['text'], None);
            if station:
                response = "station " + msg['text'] + ":\nbikes:" + str(station.bikes) + "\nfree:" + str(station.free)
                bot.sendMessage(chat_id, response)
            else:
                markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Send position', request_location=True)]])
                bot.sendMessage(chat_id, 'Where are you?', reply_markup=markup)

    elif content_type == 'location':
        user_positions[chat_id] = msg['location']
        bot.sendMessage(chat_id, "Ok I got your position: " + str(user_positions[chat_id]['latitude']) + ";" + str(user_positions[chat_id]['longitude']))
    else:
        bot.sendMessage(chat_id, "why did you send " + content_type + "?")

def update_data():
    torino_bikeshare.update()
    torino_stations = {x.name:x for x in torino_bikeshare.stations}
    stations_with_bikes = [station for station in torino_bikeshare.stations if station.bikes>0]
    stations_with_free = [station for station in torino_bikeshare.stations if station.free>0]

def search_nearest(user_position, results_set):
    distance_sq = float('inf')
    best = -1
    print("results_set has size: " + str(len(results_set)))
    for idx, val in enumerate(results_set):
        d2 = (user_position['latitude']-val.latitude) **2 + (user_position['longitude']-val.longitude) **2
        if d2 < distance_sq:
            distance_sq = d2
            best = idx

    return results_set[best]

# load the token from file
with open('../tokens.json') as tokens_file:
    data = json.load(tokens_file)
    telegram_token = data['telegram']

# TODO enable this fro nlp stuff. Now only dealing with fixed queries
#nlp = spacy.load('en')

torino_bikeshare = pybikes.get('to-bike')
torino_bikeshare.update()
torino_stations = {x.name:x for x in torino_bikeshare.stations}
stations_with_bikes = [station for station in torino_bikeshare.stations if station.bikes>0]
stations_with_free = [station for station in torino_bikeshare.stations if station.free>0]

# TODO persistency
user_positions = {}

bot = telepot.Bot(telegram_token)
pprint(bot.getMe())
bot.message_loop({'chat': on_chat_message})

while 1:
    # keep updating the bike-sharing data every 5 min TODO more fine-grained update
    time.sleep(60*5)
    torino_bikeshare.update()
    torino_stations = {x.name:x for x in torino_bikeshare.stations}
    stations_with_bikes = [station for station in torino_bikeshare.stations if station.bikes>0]
    stations_with_free = [station for station in torino_bikeshare.stations if station.free>0]
