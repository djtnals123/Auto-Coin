from tkinter import *

from frames import MainFrame

class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self._frame = None
        self.geometry('260x260')
        self.switch_frame(MainFrame)

    def switch_frame(self, frame_class, *args, **kwargs):
        new_frame = frame_class(self, *args, **kwargs)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(fill='none', expand=True)
        
def main():
    app = App()
    app.mainloop()
    
if __name__ == '__main__':
    main()