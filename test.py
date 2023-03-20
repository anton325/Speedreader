import tkinter as tk

root = tk.Tk()
root.geometry("200x200")
# create a label widget with some text
label = tk.Label(root, text='Hello, World 12312312!')

# pack the label widget to display it
label.pack()

# get the length of the text in the label
text_length = len(label['text'])

# set the anchor property based on the length of the text
if text_length > 10:
    label.config(anchor='w')
else:
    label.config(anchor='w')

root.mainloop()