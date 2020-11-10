from os import system
import sys

from requests.sessions import session
from PySide2 import QtCore, QtScxml
import requests
import json
from datetime import date, datetime, timedelta, time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram_bot import TelegramBot
from utils import get_atlondic, get_prefs


class WeatherSystem:
    prefs = get_prefs()
    latlondic = get_atlondic()

    uttdict = {
        "ask_place":"地名はどこ？",
        "ask_date":'日付は？',
        'ask_type':'種類は？'
    }

    current_weather_url = 'http://api.openweathermap.org/data/2.5/weather'
    forecast_url = 'https://api.openweathermap.org/data/2.5/forecast'
    with open('weather_api.txt') as f:
        appid = f.readline()


    def __init__(self):
        app = QtCore.QCoreApplication()
        self.sessiondic ={}

    def get_place(self, text):
        if text in self.prefs:
            return text
        else:
            return ""

    def get_date(self, text):
        if "今日" in text:
            return "今日"
        elif "明日" in text:
            return "明日"
        else:
            return ""

    def get_type(self, text):
        if "天気" in text:
            return "天気"
        elif "気温" in text:
            return "気温"
        else:
            return ""


    def get_current_weather(self, lat,lon):
        response = requests.get("{}?lat={}&lon={}&lang=ja&units=metric&APPID={}".format(
            self.current_weather_url,lat,lon,self.appid
        ))
        return response.json()

    
    def get_tomorrow_weather(self, lat, lon):
        today = datetime.today()
        tomorrow = today + timedelta(days=1)
        tomorrow_noon = datetime.combine(tomorrow, time(12,0))
        timestamp = tomorrow_noon.timestamp()
        response = requests.get("{}?lat={}&lon={}&lang=ja&units=metric&APPID={}".format(
            self.forecast_url,lat,lon,self.appid
        ))
        dic = response.json()
        for i in range(len(dic["list"])):
            dt = float(dic['list'][i]["dt"])

            if dt >= timestamp:
                return dic['list'][i]


    def initial_message(self, input):
        text = input['utt']
        sessionId = input['sessionId']

        self.el = QtCore.QEventLoop()

        sm = QtScxml.QScxmlStateMachine.fromFile('states.scxml')
        self.sessiondic[sessionId] = sm

        sm.start()
        self.el.processEvents()

        current_state = sm.activeStateNames()[0]
        print('current_state=', current_state)
        
        sysutt = self.uttdict[current_state]

        return {'utt':"天気案内システム。"+sysutt, 'end':False}

    def reply(self, input):
        text = input['utt']
        sessionId = input['sessionId']

        sm = self.sessiondic[sessionId]
        current_state = sm.activeStateNames()[0]
        print('current_state=', current_state)

        if current_state == 'ask_place':
            self.place = self.get_place(text)
            if self.place != "":
                sm.submitEvent("place")
                self.el.processEvents()

        elif current_state == 'ask_date':
            self.date = self.get_date(text)
            if self.date != "":
                sm.submitEvent("date")
                self.el.processEvents()

        elif current_state == 'ask_type':
            self._type = self.get_type(text)
            if self._type != "":
                sm.submitEvent("type")
                self.el.processEvents()

        current_state = sm.activeStateNames()[0]
        print('current_state=', current_state)

        if current_state == 'tell_info':
            utts = []
            lat = self.latlondic[self.place][0]
            lon = self.latlondic[self.place][1]

            if self.date =='今日':
                cw = self.get_current_weather(lat,lon)
                if self._type == '天気':
                    utts.append(cw["weather"][0]["description"])
                elif self._type == '気温':
                    utts.append(str(cw["main"]["temp"]))
            elif self.date == '明日':
                tw = self.get_tomorrow_weather(lat,lon)
                if self._type == '天気':
                    utts.append(tw["weather"][0]["description"])
                elif self._type == '気温':
                    utts.append(str(tw["main"]["temp"]))
            return {'utt': utts, 'end':True}

        else:
            sysutt = self.uttdict[current_state]
            return {'utt':sysutt, "end":False}


if __name__ == '__main__':
    system = WeatherSystem()
    bot = TelegramBot(system)
    bot.run()







