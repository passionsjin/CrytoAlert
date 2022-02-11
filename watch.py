
class Watch:
    def __init__(self):
        self.exchange_list = []
        # self.exchange_name = exchange_name
        # self.ticker = ticker_controller
        # self.symbol = symbol
        # self.upper_limit = float(upper_limit)
        # self.lower_limit = float(lower_limit)

    def add(self, exchange_name, ticker_controller, symbol, upper_limit, lower_limit):

        for exchange in self.exchange_list:
            if exchange['name'] == exchange_name:
                exchange['symbol'] = symbol
                exchange['upper_limit'] = float(upper_limit)
                exchange['lower_limit'] = float(lower_limit)
                return

        exchange = {
            'name': exchange_name,
            'controller': ticker_controller,
            'symbol': symbol,
            'upper_limit': float(upper_limit),
            'lower_limit': float(lower_limit)
        }
        self.exchange_list.append(exchange)

    def watch(self):
        for exchange in self.exchange_list:
            base_price = float(exchange['controller'].tickers[exchange['symbol']])
            print(base_price, exchange['upper_limit'])
            if (base_price > exchange['upper_limit']) or (base_price < exchange['lower_limit']):
                return True
            return False
