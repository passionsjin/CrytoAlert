import threading
from datetime import datetime

import gevent.monkey
from PyQt5.QtCore import QThread

from tool import process_message

gevent.monkey.patch_all()

from requests import Session
from signalr import Connection


class BittrexQthread(QThread):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.bittrex_controller = BittrexController()

    @property
    def get_controller(self):
        return self.bittrex_controller

    def run(self):
        while True:
            try:
                self.bittrex_controller.connect()
            except Exception as e:
                pass


class BittrexController:
    URL = 'https://api.bittrex.com/v3'
    SOCKET_URL = 'https://socket-v3.bittrex.com/signalr'
    _session = Session()
    _connection = None

    tickers = {}
    last_update = None
    symbol = None

    def __init__(self):
        pass
        # self.connect()

    @property
    def conn(self):
        return self._connection

    def connect(self):
        self._connection = Connection(self.SOCKET_URL, self._session)
        chat = self._connection.register_hub('c3')
        self._connection.start()

        # create error handler
        def print_error(error):
            print('error: ', error)

        # receive new chat messages from the hub
        chat.client.on('tickers', self.update_tickers)

        # process errors
        self._connection.error += print_error
        chat.server.invoke('Subscribe', ['tickers'])

        with self._connection:
            while True:
                self._connection.wait(1)

    def update_tickers(self, message):
        ticks = process_message(message)
        if 'deltas' not in ticks:
            return

        for tick in ticks['deltas']:
            self.tickers[tick['symbol']] = tick['lastTradeRate']
        self.last_update = str(datetime.now())

    def check_symbol(self, symbol):
        if symbol in self.tickers:
            return True
        return False

    def start(self):
        # self.connect()
        t = threading.Thread(target=self.connect)
        t.daemon = True
        t.start()
        t.join()


# bittrex_controller = BittrexController()
