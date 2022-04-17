# from sched import scheduler
import configparser
import threading
import time
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror
from pandas import DataFrame
import pyupbit
import datetime as dt
import frames
from util.validator import Validator

class AutoTradeFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.init_config()
        self.init_ui()
        self.init_thread()
        self.init_upbit()
        
        self.CONST_HOUR_9 = dt.timedelta(hours=9)
        
        
    def init_ui(self):
        ticker_lbl = Label(self, text='종목')
        fee_lbl = Label(self, text='수수료')
        k_lbl = Label(self, text='k')
        ma_lbl = Label(self, text='ma')
        access_key_lbl = Label(self, text='액세스키')
        secret_key_lbl = Label(self, text='시크릿키')
        self.k_entry = Entry(self, validate='key', vcmd=(self.register(Validator.isfloat), '%P'), width=10,
                        textvariable=StringVar(value=self.config['auto_trade']['k']))
        self.fee_entry = Entry(self, validate='key', vcmd=(self.register(Validator.isfloat), '%P'), width=10, 
                          textvariable=StringVar(value=self.config['auto_trade']['fee']))
        self.ma_entry = Entry(self, validate='key', vcmd=(self.register(Validator.isdigit), '%P'), width=10, 
                         textvariable=StringVar(value=self.config['auto_trade']['ma']))
        self.access_key_entry = Entry(self, validate='key', vcmd=(self.register(Validator.isdigit), '%P'), width=10, 
                         textvariable=StringVar(value=self.config['auto_trade']['access_key']))
        self.secret_key_entry = Entry(self, validate='key', vcmd=(self.register(Validator.isdigit), '%P'), width=10, 
                         textvariable=StringVar(value=self.config['auto_trade']['secret_key']))
        tickers = pyupbit.get_tickers(fiat="KRW")
        self.tickers_cbo = ttk.Combobox(self, values = tickers, width=10)
        self.tickers_cbo.set(self.config['auto_trade']['ticker'])
        self.run_btn = Button(self, text='시작', command=self.run)
        self.stop_btn = Button(self, text='중단', command=self.do_stop)
        self.stop_btn['state'] = DISABLED
        self.prev_btn = Button(self, text='뒤로가기', command=lambda: self.master.switch_frame(frames.MainFrame))
        
        ticker_lbl.grid(column=0, row=0, sticky=E)
        self.tickers_cbo.grid(column=1, row=0, sticky=W)
        
        fee_lbl.grid(column=0, row=2, sticky=E)
        self.fee_entry.grid(column=1, row=2, sticky=W)
        
        k_lbl.grid(column=0, row=3, sticky=E)
        self.k_entry.grid(column=1, row=3, sticky=W)
        
        ma_lbl.grid(column=0, row=4, sticky=E)
        self.ma_entry.grid(column=1, row=4, sticky=W)
        
        access_key_lbl.grid(column=0, row=5, sticky=E)
        self.access_key_entry.grid(column=1, row=5, sticky=W)
        
        secret_key_lbl.grid(column=0, row=6, sticky=E)
        self.secret_key_entry.grid(column=1, row=6, sticky=W)
        
        self.prev_btn.grid(column=0, row=7)
        self.run_btn.grid(column=1, row=7, sticky=E)
        self.stop_btn.grid(column=2, row=7)
        
        
    def init_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        if(not config.has_section('auto_trade')):
            config['auto_trade'] = {}
        if(not 'ticker' in config['auto_trade']):
            config['auto_trade']['ticker'] = 'KRW-BTC'
        if(not 'fee' in config['auto_trade']):
            config['auto_trade']['fee'] = str(0.05)
        if(not 'ma' in config['auto_trade']):
            config['auto_trade']['ma'] = str(5)
        if(not 'k' in config['auto_trade']):
            config['auto_trade']['k'] = str(0.5)
        if(not 'access_key' in config['auto_trade']):
            config['auto_trade']['access_key'] = 'your access key'
        if(not 'secret_key' in config['auto_trade']):
            config['auto_trade']['secret_key'] = 'your secret key'
            
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        self.config = config
        
        
    def init_thread(self):
        self.thread = threading.Thread(target=self.job)
        self.thread.daemon = True
        
        
    def init_upbit(self):
        access_key = "your_access_key"
        secret_key = "your_secret_key"
        self.upbit = pyupbit.Upbit(access_key, secret_key)
            
        
    def run(self):
        self.run_btn['state'] = DISABLED
        self.stop_btn['state'] = NORMAL
        self.prev_btn['state'] = DISABLED
        self.k_entry['state'] = DISABLED
        self.ma_entry['state'] = DISABLED
        self.fee_entry['state'] = DISABLED
        self.access_key_entry['state'] = DISABLED
        self.secret_key_entry['state'] = DISABLED
        self.tickers_cbo['state'] = DISABLED
        self.save_config()
        self.thread.start()
        
    
    def do_stop(self):
        self.run_btn['state'] = NORMAL
        self.stop_btn['state'] = DISABLED
        self.prev_btn['state'] = NORMAL
        self.k_entry['state'] = NORMAL
        self.ma_entry['state'] = NORMAL
        self.fee_entry['state'] = NORMAL
        self.access_key_entry['state'] = NORMAL
        self.secret_key_entry['state'] = NORMAL
        self.tickers_cbo['state'] = NORMAL
        self.stop = True


    def job(self):
        # scheduler.every().day.at("09:05").do(self.newday)
        self.process_df(self.get_ohlcv())
        self.stop = False
        
        while(not self.stop):
            price = pyupbit.get_current_price(self.tickers_cbo.get())
            if((price > self.df_tail['target'][0]) and self.df_tail['bull'][0]): #매수조건
                self.buy()
                waiting_time = self.get_waiting_time()
                time.sleep(waiting_time)
                self.newday()
            if(not self.is_last_df()):
                self.process_df(self.get_ohlcv())    
            time.sleep(1)
            
    
    def is_last_df(self):
        t1 = self.df_tail.index[-1] - self.CONST_HOUR_9
        t2 = dt.datetime.now() - self.CONST_HOUR_9
        return t1.day == t2.day
        
    
    def newday(self):
        self.process_df(self.get_ohlcv())
        self.sell()
        
    
    def process_df(self, df: DataFrame):
        k = float(self.k_entry.get())
        ma = int(self.ma_entry.get())
        
        df['ma'] = df['close'].rolling(window=ma).mean().shift(1)
        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)
        df['bull'] = df['open'] > df['ma']
        
        self.df_tail = df.tail(n=1)
        
    
    def get_ohlcv(self):
        ma = int(self.ma_entry.get())
        df: DataFrame = pyupbit.get_ohlcv(self.tickers_cbo.get(), count=ma+1)
        self.last_df_date = dt.datetime.now()
        return df
    
        
    def buy(self):
        krw_balance = self.upbit.get_balance('KRW')
        if(krw_balance == None):
            showerror(title='Error', message='요청이 실패하였습니다.')
        fee = 1 - float(self.fee_entry.get()) / 100
        self.upbit.buy_market_order(self.tickers_cbo.get(), krw_balance * fee)
        
        
    def sell(self):
        coin_balance = self.upbit.get_balance(self.tickers_cbo.get())
        if(coin_balance == None):
            showerror(title='Error', message='요청이 실패하였습니다.')
        self.upbit.sell_market_order(self.tickers_cbo.get(), coin_balance)
        
    
    def get_waiting_time(self):
        next_9am = None
        now = dt.datetime.now()
        if(now.hour <= 9 ):
            next_9am = now.replace(hour=9, minute=0, second=0, microsecond=0)
        else:
            next_9am: dt.datetime = now + dt.timedelta(days=1)
            next_9am = next_9am.replace(hour=9, minute=0, second=0, microsecond=0)
        waiting_time = next_9am - now
        
        return waiting_time.seconds
        

    def save_config(self):
        config = self.config['auto_trade']
        config['ticker'] = self.tickers_cbo.get()
        config['fee'] = self.fee_entry.get()
        config['ma'] = self.ma_entry.get()
        config['k'] = self.k_entry.get()
        config['access_key'] = self.access_key_entry.get()
        config['secret_key'] = self.secret_key_entry.get()
        
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)