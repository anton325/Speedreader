import regex as re
from epub_conversion.utils import open_book, convert_epub_to_lines
import tkinter as tk
import pathlib
import tkinter.filedialog
import pickle as pkl
from Scrollable_frame import VerticalScrolledFrame
import shutil
import numpy as np


class Speedreader:

    ####################################################################################################################################
    ##############################                     FRAME AND DISPLAY RELATED FUNCTIONS                ##############################
    ####################################################################################################################################
    

    """
    __init__
    initializing a bunch of things
    """
    def __init__(self):
        self.SAVE_STATE_EVERY_WORDS = 100
        self.show_number_of_words = 1
        # get root tk instance
        self.master = tk.Tk()

        # Set geometry
        self.width = 800
        self.height = 500
        geo = str(self.width) + "x" + str(self.height)
        self.master.geometry(geo)

        # start as pause
        self.pause = True
        # this refresh rate is 350 words/minute
        self.refresh_rate = float(171)

        # how to react when closing the window
        self.master.protocol("WM_DELETE_WINDOW", self.quit_app)

        # main title
        self.master.title("Read")
        self.current_frame = None
        
        # start with the first frame
        self.set_title_frame()

    def set_title_frame(self):
        self.title_frame = tk.Frame(self.master)
        self.new_frame(self.title_frame)
        self.title_frame_label = tk.Label(self.title_frame,text = "Load a new book or continue reading").grid(column = 0,row = 0)
        self.new_book_button = tk.Button(self.title_frame,text = "Select new book", command=self.select_file).grid(column=0,row=1)
        tk.Label(self.title_frame,text="Your library: ").grid(column=0,row=2)
        self.frame = VerticalScrolledFrame(self.title_frame)
        self.frame.grid(column = 0,row = 3)

        # for each bookin library create button with which we can load and continue reading
        existing_books = self.read_library()
        self.buttons  = []
        r = 4
        for i in range(len(existing_books)):
                self.buttons.append(tk.Button(self.frame.interior, text=str(existing_books[i]).split("/")[-1],command = lambda x = existing_books[i]: self.load_existing_book(x)))
                self.buttons[-1].grid(column = 0, row = r)
                r+=1
        self.title_frame.mainloop()

    def read_library(self):
        dir = pathlib.Path("saved_books")
        return [f for f in dir.iterdir() if f.is_dir()]

    def load_existing_book(self,title):
        self.path_to_saved = pathlib.Path(title)
        with open(self.path_to_saved / "book.pkl","rb") as f:
            self.book = pkl.load(f)
        try:
            with open(self.path_to_saved / "word_index.pkl","rb") as f:
                self.word_index = pkl.load(f)
        except:
            self.word_index = 0
        self.total_words = len(self.book)
        self.set_main_frame()

    """
    select_file
    window to select appropriate google response sheet
    runs ride assign algorithm on loaded information
    """
    def select_file(self):
        filetypes=(("Epub files", "*.epub"),("all files","*.*"))
        filename = tkinter.filedialog.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)
        self.open_and_read_new_book(filename)

    def set_start_frame(self):
        # get frame
        self.start_frame = tk.Frame(self.master)
        # frame management function for new frame:
        self.new_frame(self.start_frame)

        self.word_index = 0
        self.total_words = len(self.book)

        self.question_label = tk.Label(self.start_frame,text = "At what percentage do you want to start ?").grid(column=0,row=0)
        self.user_input = tk.DoubleVar(self.start_frame)
        self.start_percentage_entry = tk.Entry(self.start_frame,textvariable=self.user_input).grid(column=0,row=1)
        self.start_button = tk.Button(self.start_frame,text = "Start reading!",command = self.start_reading).grid(column=0,row=2)
        self.start_frame.mainloop()

    
    def start_reading(self):
        self.start_percentage = self.user_input.get()
        self.word_index = int(self.total_words*self.start_percentage/100)
        self.set_main_frame()

    def set_main_frame(self):
        # get main frame
        self.main_frame = tk.Frame(self.master)
        # frame management function for new frame:
        self.new_frame(self.main_frame)

        self.word_label = tk.Label(self.main_frame,text="", font=("Arial", 35))
        self.word_label.grid(column=1,row=0,columnspan=1,pady = 20)
        self.main_frame.columnconfigure(1,minsize=700)

        self.progress_label = tk.Label(self.main_frame,text = "Progress: %.1f" % (100*self.myround(self.word_index/self.total_words,0.1))+"%")
        self.progress_label.grid(column=1,row=1)

        pady_controlbar_speed = (50,20)
        self.speed_label = tk.Label(self.main_frame,text = "")
        self.speed_label.grid(column=1,row=2,columnspan=1,pady = pady_controlbar_speed)
        self.speed_up_button = tk.Button(self.main_frame,text="+",command= self.speedup)
        self.slow_down_button = tk.Button(self.main_frame,text="-",command= self.slowdown)
        self.speed_up_button.grid(column=2,row=2,columnspan=1,pady = pady_controlbar_speed)
        self.slow_down_button.grid(column=0,row=2,columnspan=1,pady = pady_controlbar_speed)
        pady_controlbar_number_words = (10,20)
        self.remaining_time_label = tk.Label(self.main_frame,text="")
        self.remaining_time_label.grid(column = 1,row = 3)
        self.update_remaining_time()
        
        self.number_of_words_button_label = tk.Label(self.main_frame, text = "Number of words: 1")
        self.number_of_words_button_label.grid(column=1,row=4,columnspan=1,pady = pady_controlbar_number_words)
        self.number_of_words_button_up = tk.Button(self.main_frame,text="+",command= self.show_more_words)
        self.number_of_words_button_down = tk.Button(self.main_frame,text="-",command= self.show_less_words)
        self.number_of_words_button_up.grid(column=2,row=4,columnspan=1,pady = pady_controlbar_number_words)
        self.number_of_words_button_down.grid(column=0,row=4,columnspan=1,pady = pady_controlbar_number_words)
        

        self.skip_by_entry = tk.Entry(self.main_frame,text ="400")
        self.skip_forward = tk.Button(self.main_frame,text=">>",command= self.skip_forwards)
        self.skip_back = tk.Button(self.main_frame,text="<<",command= self.skip_backwards)
        self.skip_by_entry.grid(column=1,row=5,columnspan=1,pady = pady_controlbar_number_words)
        self.skip_forward.grid(column=2,row=5,columnspan=1,pady = pady_controlbar_number_words)
        self.skip_back.grid(column=0,row=5,columnspan=1,pady = pady_controlbar_number_words)

        self.pause_button = tk.Button(self.main_frame,text='Start',pady=0,command=self.pause_unpause)
        self.pause_button.grid(column=1,row=30)
        self.update_word()

        self.main_menu_button = tk.Button(self.main_frame,text="Main menu",command = self.set_title_frame).grid(column = 1,row = 31,pady=20)

        # keybindings
        self.master.bind("<space>", lambda x: self.pause_unpause())
        self.master.bind('<Left>', lambda x: self.slowdown())
        self.master.bind('<Right>', lambda x: self.speedup())

        # launch window
        self.main_frame.mainloop()

    def myround(self,x, base=0.5):
        return base * round(x/base)
    
    def pause_unpause(self):
        if self.pause:
            self.pause = False
            self.pause_button.configure(text = "Pause")
        else:
            self.pause = True
            self.pause_button.configure(text = "Continue")
        
    def speedup(self):
        self.refresh_rate = self.convertToRefreshRate(self.convertToWordsPerMinute(self.refresh_rate)+10)
        self.update_remaining_time()

    def slowdown(self):
        if self.convertToWordsPerMinute(self.refresh_rate)-10 > 50:
            self.refresh_rate = self.convertToRefreshRate(self.convertToWordsPerMinute(self.refresh_rate)-10)
            self.update_remaining_time()
    
    def update_number_words(self):
        self.number_of_words_button_label.configure(text = "Number of words: {}".format(self.show_number_of_words))

    def show_more_words(self):
        self.show_number_of_words += 1
        self.update_number_words()

    def show_less_words(self):
        if self.show_number_of_words > 1:
            self.show_number_of_words -= 1
            self.update_number_words()
    
    def skip_forwards(self):
        skip_by = self.skip_by_entry.get()
        try:
            self.word_index += int(skip_by)
        except:
            pass
    
    def skip_backwards(self):
        skip_by = self.skip_by_entry.get()
        try:
            if self.word_index > int(skip_by):
                self.word_index -= int(skip_by)
            else:
                self.word_index = 0
        except:
            pass
        

    def update_remaining_time(self):
        words_left = len(self.book)-self.word_index
        words_per_minute = self.convertToWordsPerMinute(self.refresh_rate)
        self.remaining_time_label.configure(text="Remaining time: {} min".format(int(words_left/words_per_minute)))


    def update_word(self):
        self.speed_label.configure(text = str(int(self.convertToWordsPerMinute(self.refresh_rate)))+" Words per minute")
        thisWord = self.book[self.word_index:self.word_index+self.show_number_of_words]
        thisWord = " ".join(thisWord)
        self.word_label.configure(text=thisWord)
        if not self.pause:
            if self.word_index < self.total_words-3-self.show_number_of_words:
                self.word_index += self.show_number_of_words
            self.progress_label.configure(text = "Progress: %.1f" % (self.myround(100*self.word_index/self.total_words,0.1))+"%")
            if self.word_index % self.SAVE_STATE_EVERY_WORDS == 0:
                self.save_progress(self.word_index)
            self.update_remaining_time()
        self.main_frame.after(int(self.adjustTimeForWord(thisWord)), self.update_word)

    def save_progress(self,word_index):
        with open(self.path_to_saved / "word_index.pkl","wb") as f:
            pkl.dump(word_index,f)

    def adjustTimeForWord(self,word):
        base_word_length = 4 * self.show_number_of_words
        this_word_length = len(word)
        if this_word_length <= base_word_length:
            return self.refresh_rate
        else:
            return self.refresh_rate/((base_word_length+0.2*base_word_length)/this_word_length)
            # return self.refresh_rate *  np.sqrt(this_word_length-base_word_length-1)/2 + self.refresh_rate

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

    def open_and_read_new_book(self,filename):
        book = open_book(filename)

        lines = convert_epub_to_lines(book)

        self.book = []

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
                    self.book.append(word)
        self.create_folder_and_save_book(filename)
        self.set_start_frame()
    
    def create_folder_and_save_book(self,filename):
        book_title = filename.split("/")[-1].split(".")[0]
        self.path_to_saved = pathlib.Path("saved_books",book_title)
        self.path_to_saved.mkdir(parents=True, exist_ok=True)
        p = self.path_to_saved / "book.pkl"
        with open(p, "wb") as output_file:
            pkl.dump(self.book, output_file)
        shutil.copy(filename,self.path_to_saved)


if __name__ == "__main__":
    sr = Speedreader()