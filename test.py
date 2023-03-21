import pickle as pkl

with open("saved_books/Rule_of_Wolves_-_Leigh_Bardugo/word_index.pkl","rb") as f:
    a = pkl.load(f)
print(a)