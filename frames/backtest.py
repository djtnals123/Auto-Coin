
import configparser
import datetime
from msilib.schema import ComboBox
from tkinter import *
from tkinter import ttk
import pyupbit
from pandas import DataFrame
import numpy as np

import frames
from tkcalendar import DateEntry

from util.validator import Validator

class BacktestFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.init_config()
        self.init_ui()

        
    def init_ui(self):
        ticker_lbl = Label(self, text='종목')
        term_lbl = Label(self, text='기간')
        fee_lbl = Label(self, text='수수료')
        k_lbl = Label(self, text='k')
        ma_lbl = Label(self, text='ma')
        self.cal1 = DateEntry(self, selectmode='day', date_pattern='yyyy-mm-dd', width=10)
        self.cal2 = DateEntry(self, selectmode='day', date_pattern='yyyy-mm-dd', width=10)
        self.k_entry = Entry(self, validate='key', vcmd=(self.register(Validator.isfloat), '%P'), width=10,
                        textvariable=StringVar(value=self.config['backtest']['k']))
        self.fee_entry = Entry(self, validate='key', vcmd=(self.register(Validator.isfloat), '%P'), width=10, 
                          textvariable=StringVar(value=self.config['backtest']['fee']))
        self.ma_entry = Entry(self, validate='key', vcmd=(self.register(Validator.isdigit), '%P'), width=10, 
                         textvariable=StringVar(value=self.config['backtest']['ma']))
        run_btn = Button(self, text='분석 시작', command=self.run)
        prev_btn = Button(self, text='뒤로가기', command=lambda: self.master.switch_frame(frames.MainFrame))
        tickers = pyupbit.get_tickers(fiat="KRW")
        self.tickers_cbo = ttk.Combobox(self, values = tickers, width=10)
        self.tickers_cbo.set(self.config['backtest']['ticker'])
        
        ticker_lbl.grid(column=0, row=0, sticky=E)
        self.tickers_cbo.grid(column=1, row=0, sticky=W)
        
        term_lbl.grid(column=0, row=1, sticky=E)
        self.cal1.grid(column=1, row=1)
        self.cal2.grid(column=2, row=1)
        
        fee_lbl.grid(column=0, row=2, sticky=E)
        self.fee_entry.grid(column=1, row=2, sticky=W)
        
        k_lbl.grid(column=0, row=3, sticky=E)
        self.k_entry.grid(column=1, row=3, sticky=W)
        
        ma_lbl.grid(column=0, row=4, sticky=E)
        self.ma_entry.grid(column=1, row=4, sticky=W)
        prev_btn.grid(column=0, row=5, sticky=E)
        run_btn.grid(column=2, row=5, sticky=E)
        
        
    def init_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        if(not config.has_section('backtest')):
            config['backtest'] = {}
        if(not 'ticker' in config['backtest']):
            config['backtest']['ticker'] = 'KRW-BTC'
        if(not 'fee' in config['backtest']):
            config['backtest']['fee'] = str(0.05)
        if(not 'ma' in config['backtest']):
            config['backtest']['ma'] = str(5)
        if(not 'k' in config['backtest']):
            config['backtest']['k'] = str(0.5)
            
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        self.config = config
        
              
    def process_df(self, df:DataFrame):
        k = float(self.k_entry.get())
        fee = float(self.fee_entry.get()) / 100
        ma = int(self.ma_entry.get())

        df['ma'] = df['close'].rolling(window=ma).mean().shift(1)
        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)
        df['bull'] = df['open'] > df['ma']

        df['ror'] = np.where((df['high'] > df['target']) & df['bull'],
                                df['close'] / df['target'] - fee,
                                1)
        df['hpr'] = df['ror'].cumprod()
        df.to_excel("backtest.xlsx")
        return df
    
    
    def get_ohlcv(self):
        count = (abs(self.cal1.get_date() - self.cal2.get_date())).days + 1
        to = (max(self.cal1.get_date(), self.cal2.get_date()) + datetime.timedelta(days=1)).strftime("%Y%m%d 09:00:00")
        df: DataFrame = pyupbit.get_ohlcv(self.tickers_cbo.get(), to=to, count=count)
        return df
    
        
    def run(self):
        df = self.process_df(self.get_ohlcv())
        self.save_config()
        self.master.switch_frame(frames.BacktestResultFrame, df, self.tickers_cbo.get())


    def save_config(self):
        config = self.config['backtest']
        config['ticker'] = self.tickers_cbo.get()
        config['fee'] = self.fee_entry.get()
        config['ma'] = self.ma_entry.get()
        config['k'] = self.k_entry.get()
        
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        