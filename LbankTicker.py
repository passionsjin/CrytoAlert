import json
import logging
import threading
from datetime import datetime

import gevent
import requests

gevent.monkey.patch_all()
import websocket
from PyQt5.QtCore import QThread


class LBankQthread(QThread):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.lbank_controller = LbankController()
        self.lbank_controller.connect()
        # self.lbank_controller.set_tick('eth_btc')

    @property
    def get_controller(self):
        return self.lbank_controller

    def run(self):
        self.lbank_controller.loop()


class LbankController:
    SOCKET_URL = 'wss://www.lbkex.net/ws/V2/'
    ws = None
    tickers = {}
    last_update = None
    symbol = None

    def connect(self):
        websocket.enableTrace(False)
        # self.ws = websocket.WebSocket()
        # self.ws.connect(self.SOCKET_URL)
        self.ws = websocket.create_connection(self.SOCKET_URL)
        if self.symbol:
            self.set_tick(self.symbol)

    def set_tick(self, symbol):
        self.symbol = symbol
        subscribe_fmt = {
            "action": "subscribe",
            "subscribe": "tick",
            "pair": str(symbol).lower()
        }
        subscribe_data = json.dumps(subscribe_fmt)
        self.ws.send(subscribe_data)

    def get_ticker(self, symbol):
        req = requests.get(f'https://api.lbkex.com/v2/ticker/24hr.do?symbol={str(symbol).lower()}')
        if req.status_code == 200:
            self.tickers[symbol] = req.json()['data'][0]['ticker']['latest']
            self.last_update = str(datetime.now())
            self.set_tick(symbol)

    def update_tickers(self, message):
        # print(message)
        message = json.loads(message)
        if 'tick' in message:
            self.tickers[str(message['pair']).upper()] = message['tick']['latest']
            self.last_update = str(datetime.now())

    def loop(self):
        while True:
            try:
                rcv = self.ws.recv()
                if rcv:
                    self.update_tickers(rcv)
            except Exception as e:
                logging.exception(e)
                self.ws.close()
                self.connect()
                self.set_tick(self.symbol)

    def start(self):
        # self.connect()
        # asyncio.get_event_loop().run_until_complete(self.connect())
        t = threading.Thread(target=self.loop)
        t.start()
        t.join()

# lbank_controller = LbankController()


# if __name__ == '__main__':
#     # asyncio.get_event_loop().run_until_complete(lbank_controller.connect())
#     lbank_controller.connect()
#     lbank_controller.set_tick('eth_btc')
#     lbank_controller.start()