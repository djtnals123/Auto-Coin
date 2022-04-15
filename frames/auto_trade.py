# from sched import scheduler
from faulthandler import disable
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
        ticker_lbl = Label(self, text='종목')
        fee_lbl = Label(self, text='수수료')
        k_lbl = Label(self, text='k')
        ma_lbl = Label(self, text='ma')
        self.k_entry = Entry(self, validate='key', vcmd=(self.register(Validator.isfloat), '%P'), width=10,
                        textvariable=StringVar(value='0.5'))
        self.fee_entry = Entry(self, validate='key', vcmd=(self.register(Validator.isfloat), '%P'), width=10,
                          textvariable=StringVar(value='0.05'))
        self.ma_entry = Entry(self, validate='key', vcmd=(self.register(Validator.isdigit), '%P'), width=10,
                         textvariable=StringVar(value='5'))
        tickers = pyupbit.get_tickers(fiat="KRW")
        self.tickers_cbo = ttk.Combobox(self, values = tickers, width=10)
        self.tickers_cbo.set(tickers[0])
        self.run_btn = Button(self, text='시작', command=self.run)
        self.stop_btn = Button(self, text='중단', command=self.do_stop)
        self.stop_btn['state'] = DISABLED
        self.prev_btn = Button(self, text='뒤로가기', command=lambda: master.switch_frame(frames.MainFrame))
        
        ticker_lbl.grid(column=0, row=0, sticky=E)
        self.tickers_cbo.grid(column=1, row=0, sticky=W)
        
        fee_lbl.grid(column=0, row=2, sticky=E)
        self.fee_entry.grid(column=1, row=2, sticky=W)
        
        k_lbl.grid(column=0, row=3, sticky=E)
        self.k_entry.grid(column=1, row=3, sticky=W)
        
        ma_lbl.grid(column=0, row=4, sticky=E)
        self.ma_entry.grid(column=1, row=4, sticky=W)
        self.prev_btn.grid(column=0, row=5)
        self.run_btn.grid(column=1, row=5, sticky=E)
        self.stop_btn.grid(column=2, row=5)
        
        self.thread = threading.Thread(target=self.job)
        self.thread.daemon = True
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
        self.tickers_cbo['state'] = DISABLED
        self.thread.start()
        
    
    def do_stop(self):
        self.run_btn['state'] = NORMAL
        self.stop_btn['state'] = DISABLED
        self.prev_btn['state'] = NORMAL
        self.k_entry['state'] = NORMAL
        self.ma_entry['state'] = NORMAL
        self.fee_entry['state'] = NORMAL
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
            time.sleep(1)
        
    
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
        
