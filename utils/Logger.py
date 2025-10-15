import tkinter as tk


class Logger:
    def log(self, message, box=None):
        if box:
            box.insert(tk.END, message + "\n")
            box.see(tk.END)
        else:
            print(message)
