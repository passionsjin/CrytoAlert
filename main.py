import multiprocessing
import sys
from time import sleep

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLineEdit, QInputDialog, QLabel, QRadioButton)

from Alert import PlayAlarm
from BittrexTickers import BittrexQthread
from LbankTicker import LBankQthread
from tool import is_integer, is_number, except_hook
from watch import Watch


# class BittrexThread(QThread):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.parent = parent
#
#     def run(self):
#         bittrex_controller.start()
#
#
# class LbankThread(QThread):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.parent = parent
#
#     def run(self):
#         lbank_controller.start()


class UpdateThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        while True:
            self.parent.update_tick()


class WatchThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.watch = Watch()

    def add(self, name, controller, symbol, upper_limit, lower_limit):
        self.watch.add(exchange_name=name,
                       ticker_controller=controller,
                       symbol=symbol,
                       upper_limit=upper_limit,
                       lower_limit=lower_limit)

    def run(self):
        while True:
            if self.watch.watch():
                PlayAlarm().play()
                sleep(3)


class MyApp(QWidget):
    bittrex_target_symbol = None
    lbank_target_symbol = None

    def __init__(self):
        super().__init__()
        self.init_ui()
        # BittrexThread(self).start()
        # LbankThread(self).start()
        self.bittrex_ticker = BittrexQthread(self)
        self.bittrex_ticker.start()
        self.lbank_ticker = LBankQthread(self)
        self.lbank_ticker.start()
        UpdateThread(self).start()
        self.watcher = WatchThread(self)
        self.watcher.start()

    def init_ui(self):
        # Bittrex #####################################################################
        self.bittrex_title_label = QLabel('BITTREX', self)
        self.bittrex_title_label.move(20, 15)
        self.bittrex_title_label.setFixedWidth(300)
        # Watch 시작버튼
        self.bittrex_watch_start_btn = QPushButton('심볼설정', self)
        self.bittrex_watch_start_btn.setEnabled(True)
        self.bittrex_watch_start_btn.move(180, 33)
        self.bittrex_watch_start_btn.clicked.connect(self.select_bittrex_symbol)

        # Watch 심볼 입력
        self.bittrex_symbol_input = QLineEdit(self)
        self.bittrex_symbol_input.move(30, 35)
        self.bittrex_symbol_input.setText('BTC-USDT')
        self.bittrex_info_label = QLabel('Ready...', self)
        self.bittrex_info_label.move(40, 65)
        self.bittrex_info_label.setFixedWidth(300)

        # 기준가 적용버튼
        self.bittrex_watch_start_btn = QPushButton('기준가설정', self)
        self.bittrex_watch_start_btn.setEnabled(True)
        self.bittrex_watch_start_btn.move(180, 123)
        self.bittrex_watch_start_btn.clicked.connect(self.bittrex_input_limit)

        # 기준가 입력
        self.bittrex_watch_base_up_input = QLineEdit(self)
        self.bittrex_watch_base_up_input.move(70, 95)
        self.bittrex_watch_base_up_input.resize(100, 20)
        self.bittrex_watch_base_up_input.setText('')
        self.bittrex_watch_base_down_input = QLineEdit(self)
        self.bittrex_watch_base_down_input.move(70, 125)
        self.bittrex_watch_base_down_input.resize(100, 20)
        self.bittrex_watch_base_down_input.setText('')

        self.bittrex_watch_base_up_label = QLabel('상한', self)
        self.bittrex_watch_base_up_label.move(35, 98)
        self.bittrex_watch_base_down_label = QLabel('하한', self)
        self.bittrex_watch_base_down_label.move(35, 128)
        self.bittrex_watch_base_info_label = QLabel('기준가입력 - ', self)
        self.bittrex_watch_base_info_label.move(40, 155)
        self.bittrex_watch_base_info_label.setFixedWidth(300)

        # Watch 가격 Text - bittrex
        self.bittrex_tick_label = QLabel('0', self)
        self.bittrex_tick_label.move(40, 185)
        self.bittrex_tick_label.setFixedWidth(300)

        # Watch Last Update
        self.bittrex_last_update_label = QLabel('Updated', self)
        self.bittrex_last_update_label.move(30, 215)
        self.bittrex_last_update_label.setFixedWidth(200)
        # ############################################################################

        # Lbank #######################################################################
        self.lbank_title_label = QLabel('LBANK', self)
        self.lbank_title_label.move(320, 15)
        self.lbank_title_label.setFixedWidth(300)
        # Watch 시작버튼
        self.lbank_watch_start_btn = QPushButton('심볼설정', self)
        self.lbank_watch_start_btn.setEnabled(True)
        self.lbank_watch_start_btn.move(480, 33)
        self.lbank_watch_start_btn.clicked.connect(self.select_lbank_symbol)

        # Watch 심볼 입력
        self.lbank_symbol_input = QLineEdit(self)
        self.lbank_symbol_input.move(330, 35)
        self.lbank_symbol_input.setText('BTC_USDT')
        self.lbank_info_label = QLabel('Ready...', self)
        self.lbank_info_label.move(340, 65)
        self.lbank_info_label.setFixedWidth(300)

        # 기준가 적용버튼
        self.lbank_watch_start_btn = QPushButton('기준가설정', self)
        self.lbank_watch_start_btn.setEnabled(True)
        self.lbank_watch_start_btn.move(480, 123)
        self.lbank_watch_start_btn.clicked.connect(self.lbank_input_limit)

        # 기준가 입력
        self.lbank_watch_base_up_input = QLineEdit(self)
        self.lbank_watch_base_up_input.move(370, 95)
        self.lbank_watch_base_up_input.resize(100, 20)
        self.lbank_watch_base_up_input.setText('')
        self.lbank_watch_base_down_input = QLineEdit(self)
        self.lbank_watch_base_down_input.move(370, 125)
        self.lbank_watch_base_down_input.resize(100, 20)
        self.lbank_watch_base_down_input.setText('')

        self.lbank_watch_base_up_label = QLabel('상한', self)
        self.lbank_watch_base_up_label.move(335, 98)
        self.lbank_watch_base_down_label = QLabel('하한', self)
        self.lbank_watch_base_down_label.move(335, 128)
        self.lbank_watch_base_info_label = QLabel('기준가입력 - ', self)
        self.lbank_watch_base_info_label.move(340, 155)
        self.lbank_watch_base_info_label.setFixedWidth(300)

        self.lbank_tick_label = QLabel('0', self)
        self.lbank_tick_label.move(340, 185)
        self.lbank_tick_label.setFixedWidth(300)

        self.lbank_last_update_label = QLabel('Updated', self)
        self.lbank_last_update_label.move(330, 215)
        self.lbank_last_update_label.setFixedWidth(200)

        # #############################################################################

        # Watch Sound on/off
        self.watch_sound_on_radio = QRadioButton('알람 사운드 On', self)
        self.watch_sound_on_radio.move(40, 250)
        self.watch_sound_on_radio.setChecked(True)
        self.watch_sound_on_radio.clicked.connect(self.sound_on)

        # Title
        self.setWindowTitle('다 먹고 살자고 하는건데')
        self.setGeometry(600, 600, 600, 400)
        self.show()

    def select_bittrex_symbol(self):
        # 검증
        symbol = self.bittrex_symbol_input.text()
        symbol = str(symbol).replace(' ', '')
        if self.bittrex_ticker.get_controller.last_update is None:
            self.bittrex_info_label.setText('Bittrex 가격 불러오는 중, 잠시 후 다시 시도.')
            return
        if not self.bittrex_ticker.get_controller.check_symbol(symbol):
            self.bittrex_info_label.setText('Bittrex 가격 불러오는 중, 다시 시도.')
            return

        self.bittrex_info_label.setText(f'Start Watching... [{symbol}]')
        self.bittrex_target_symbol = symbol
        self.update_tick()

    def select_lbank_symbol(self):
        # 검증
        symbol = self.lbank_symbol_input.text()
        symbol = str(symbol).replace(' ', '')
        # if self.lbank_ticker.get_controller.last_update is None:
        #     self.lbank_info_label.setText('Lbank 가격 불러오는 중, 잠시 후 다시 시도.')
        #     return
        # if not self.lbank_ticker.get_controller.check_symbol(symbol):
        #     self.lbank_info_label.setText('Lbank 가격 불러오는 중, 다시 시도.')
        #     return

        self.lbank_info_label.setText(f'Start Watching... [{symbol}]')
        self.lbank_target_symbol = symbol
        self.lbank_ticker.get_controller.get_ticker(symbol)
        self.update_tick()

    def bittrex_input_limit(self):
        if self.bittrex_target_symbol is None:
            return
        if not is_number(self.bittrex_watch_base_up_input.text()) or not is_number(self.bittrex_watch_base_down_input.text()):
            self.bittrex_watch_base_info_label.setText('숫자 변환 오류.')
            return

        self.watcher.add(name='bittrex',
                         symbol=self.bittrex_target_symbol,
                         controller=self.bittrex_ticker.get_controller,
                         upper_limit=self.bittrex_watch_base_up_input.text(),
                         lower_limit=self.bittrex_watch_base_down_input.text())
        self.bittrex_watch_base_info_label.setText(f'기준가입력 - UP({self.bittrex_watch_base_up_input.text()})DOWN({self.bittrex_watch_base_down_input.text()})')

    def lbank_input_limit(self):
        if self.lbank_target_symbol is None:
            return
        if not is_number(self.lbank_watch_base_up_input.text()) or not is_number(self.lbank_watch_base_down_input.text()):
            self.lbank_watch_base_info_label.setText('숫자 변환 오류.')
            return

        self.watcher.add(name='lbank',
                         symbol=self.lbank_target_symbol,
                         controller=self.lbank_ticker.get_controller,
                         upper_limit=self.lbank_watch_base_up_input.text(),
                         lower_limit=self.lbank_watch_base_down_input.text())

        self.lbank_watch_base_info_label.setText(f'기준가입력 - UP({self.lbank_watch_base_up_input.text()})DOWN({self.lbank_watch_base_down_input.text()})')

    def update_tick(self):
        if self.bittrex_target_symbol is not None and self.bittrex_target_symbol in self.bittrex_ticker.get_controller.tickers:
            self.bittrex_tick_label.setText(f'현재가격 : {self.bittrex_ticker.get_controller.tickers[self.bittrex_target_symbol]}')
        if self.lbank_target_symbol is not None and self.lbank_target_symbol in self.lbank_ticker.get_controller.tickers:
            self.lbank_tick_label.setText(f'현재가격 : {self.lbank_ticker.get_controller.tickers[self.lbank_target_symbol]}')
        if self.bittrex_ticker.get_controller.last_update is not None:
            self.bittrex_last_update_label.setText(f'Updated : {self.bittrex_ticker.get_controller.last_update}')

        if self.lbank_ticker.get_controller.last_update is not None:
            self.lbank_last_update_label.setText(f'Updated : {self.lbank_ticker.get_controller.last_update}')

    def sound_on(self):
        if self.watch_sound_on_radio.isChecked():
            PlayAlarm.is_mute = False
        else:
            PlayAlarm.is_mute = True


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.excepthook = except_hook
    sys.exit(app.exec_())