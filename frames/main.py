from tkinter import *
import frames

class MainFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        start_btn = Button(self, text='시작', 
                           command=lambda: master.switch_frame(frames.AutoTradeFrame))
        backtest_btn = Button(self, text='백테스트', 
                              command=lambda: master.switch_frame(frames.BacktestFrame))

        start_btn.grid(column=2, row=1, sticky='nesw')
        backtest_btn.grid(column=2, row=2)
        
    