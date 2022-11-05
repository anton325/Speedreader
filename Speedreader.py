import regex as re
from epub_conversion.utils import open_book, convert_epub_to_lines
import tkinter as tk
    
class Speedreader:

    ####################################################################################################################################
    ##############################                     FRAME AND DISPLAY RELATED FUNCTIONS                ##############################
    ####################################################################################################################################



    """
    __init__
    initializing a bunch of things
    """
    def __init__(self,input_book):
        self.book = input_book
        self.word_index = 1000
        # get root tk instance
        self.master = tk.Tk()

        # Set geometry
        self.width = 400
        self.height = 250
        geo = str(self.width) + "x" + str(self.height)
        self.master.geometry(geo)

        self.refresh_rate = float(190)

        # Stop it from changing size
        # self.master.resizable(width=0, height=0)

        # how to react when closing the window
        self.master.protocol("WM_DELETE_WINDOW", self.quit_app)

        # main title
        self.master.title("Read")
        self.current_frame = None
        
        # rollout mode
        # start with the first main frame
        self.set_main_frame()
    
    def set_main_frame(self):
        # get main frame
        self.main_frame = tk.Frame(self.master)
        # frame management function for new frame:
        self.new_frame(self.main_frame)

        self.word_label = tk.Label(self.main_frame,text="", font=("Arial", 20))
        self.word_label.grid(column=0,row=0,columnspan=3,pady = 20)


        pady_controlbar = 120
        self.speed_label = tk.Label(self.main_frame,text = "")
        self.speed_label.grid(column=1,row=1,columnspan=1,pady = pady_controlbar)
        self.speed_up_button = tk.Button(self.main_frame,text="+",command= self.speedup)
        self.slow_down_button = tk.Button(self.main_frame,text="-",command= self.slowdown)
        self.speed_up_button.grid(column=2,row=1,columnspan=1,pady = pady_controlbar)
        self.slow_down_button.grid(column=0,row=1,columnspan=1,pady = pady_controlbar)
        self.update_word()
        # launch window
        self.main_frame.mainloop()

    def speedup(self):
        self.refresh_rate = self.convertToRefreshRate(self.convertToWordsPerMinute(self.refresh_rate)+10)
    def slowdown(self):
        self.refresh_rate = self.convertToRefreshRate(self.convertToWordsPerMinute(self.refresh_rate)-10)
    
    def update_word(self):
        self.speed_label.configure(text = str(int(self.convertToWordsPerMinute(self.refresh_rate)))+" Words per minute")
        self.word_label.configure(text=self.book[self.word_index])
        self.word_index += 1
        self.main_frame.after(int(self.refresh_rate), self.update_word)

    def convertToRefreshRate(self,wordsperminute):
        return 60*1000/wordsperminute
    
    def convertToWordsPerMinute(self,refresh_rate):
        return 60*1000/refresh_rate


    
    def new_frame(self,new):
        # destroy old frame (if any)
        if not (self.current_frame is None):
            self.current_frame.destroy()
        # set new frame as current
        self.current_frame = new
        #pack new frame
        self.current_frame.pack()

    def quit_app(self):
        # print("Programm beendet")
        self.master.destroy()
    

if __name__ == "__main__":
    book = open_book('1_Artemis_Fowl_-_Eoin_Colfer.epub')

    lines = convert_epub_to_lines(book)

    book_processed = []

    for l in lines:
        # process the lines
        l = (re.sub("<.*?>", "",l))
        l = re.sub('(?:\\[rn\]|[\r\n]+)+',"",l)
        l = re.sub('  ','',l)
        l = re.sub('/[“]/g', "",l)
        l = a = l.strip('\“')
        l = a = l.strip('\”')
        if l != '':
            # print(repr(l))
            for word in l.split():
                book_processed.append(word)
    sr = Speedreader(book_processed)