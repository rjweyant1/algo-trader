
import time
class trades:
    def __init__(self,coin,updated,server_time,ask_prices,ask_volumes,bid_prices,bid_volumes,buy,sell):
        self.coin=coin
        self.updated=updated
        self.server_time=server_time
        self.time=time.strftime('%X')
        self.date=time.strftime('%x')
        self.time_object = time.localtime()
        
        self.ask_prices = ask_prices
        self.ask_volumes = ask_volumes
        self.bid_pries = bid_prices
        self.bid_volumes = bid_volumes
        
        self.buy = buy
        self.sell = sell