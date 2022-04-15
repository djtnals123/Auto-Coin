from tkinter import *
import numpy as np
import matplotlib
import frames
from util.etc import is_checked
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


class BacktestResultFrame(Frame):
    def __init__(self, master, df):
        Frame.__init__(self, master)
        lbf=LabelFrame(self, text="그래프")
        self.chk_list = []
        chk_texts = ['시가', '고가', '저가', '종가', '목표가']
        for text in chk_texts:
            chk = Checkbutton(lbf, text=text, command=self.are_any_checked)
            chk.select()
            self.chk_list.append(chk)
        self.graph_btn = Button(lbf, text='그래프 보기', command=self.view_graph)
        hpr_graph_btn = Button(self, text='누적 수익률 그래프 보기', command=self.view_hpr_graph)
        prev_btn = Button(self, text='뒤로가기', command=lambda: master.switch_frame(frames.BacktestFrame))
        
        lbf.grid(column=0, row=0)
        for idx, item in enumerate(self.chk_list):
            item.grid(column=0, row=idx)
        self.graph_btn.grid(column=0, row=idx+1)
        hpr_graph_btn.grid(column=0, row=1)
        prev_btn.grid(column=0, row=2)
        
        self.df = df
        
        
    def view_graph(self):
        item_list = np.array(['open','high','low','close','target'])
        is_checked_list = [is_checked(item) for item in self.chk_list]
        checked_boxes = item_list[is_checked_list]
            
        df = self.df.loc[:,checked_boxes]
        df.plot()
        plt.xlabel('date')
        plt.ylabel('price')
        plt.show()   
        
    
    def view_hpr_graph(self):
        df = self.df.loc[:,['hpr']]
        df.plot()
        plt.xlabel('date')
        plt.ylabel('price')
        plt.show() 
        
        
    def are_any_checked(self):
        is_checked_list = np.array([is_checked(item) for item in self.chk_list])
        any_checked = np.any(is_checked_list == True)
        self.graph_btn['state'] = NORMAL if any_checked else DISABLED
            