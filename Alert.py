import multiprocessing
import os
import sys
import threading
from time import sleep

import telegram
from playsound import playsound


class Alert:
    def play_alarm(self):
        t = threading.Thread(target=PlayAlarm().play)
        t.start()
        t.join()

    def send_msg(self, msg):
        AlertTelegram().send_msg(msg)


class AlertTelegram:
    TOKEN = ''
    ID = ''

    def send_msg(self, msg):
        tel_bot = telegram.Bot(token=self.TOKEN)
        tel_bot.sendMessage(chat_id=self.ID, text=msg)


class PlayAlarm:
    is_mute = False
    is_play = False
    p = None

    def __init__(self):
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(os.path.abspath(sys.executable))
            application_path.decode('CP949')
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
            application_path.decode('CP949')
        print(application_path)
        os.chdir(application_path)
        self.alarm_file_path = os.path.join(application_path, 'alarm.mp3')

    def mute(self, is_mute):
        self.is_mute = is_mute
        if self.is_play and self.is_mute:
            if self.p.is_alive():
                self.p.terminate()

    def play(self):
        if self.is_play:
            return

        if self.mute is not True:
            self.is_play = True
            self.p = multiprocessing.Process(target=playsound, args=(self.alarm_file_path, ))
            self.p.start()
            while self.p.is_alive():
                if self.is_mute is True:
                    self.p.terminate()
            self.is_play = False


# if __name__ == '__main__':
#     Alert().play_alarm()
