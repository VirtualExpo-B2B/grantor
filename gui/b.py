from tkinter import *


class AlltkinterWidgets:
    def __init__(self, master):
        frame = Frame(master, width=500, height=400, bd=1)
        frame.pack()

        iframe3 = Frame(frame, bd=2, relief=GROOVE)
        listbox = Listbox(iframe3, height=4)
        for line in ['Listbox Entry One', 'Entry Two', 'Entry Three', 'Entry Four']:
            listbox.insert(END, line)
        listbox.pack(fill=X, padx=5)
        iframe3.pack(expand=1, fill=X, pady=10, padx=5)

        iframe4 = Frame(frame, bd=2, relief=SUNKEN)
        text = Text(iframe4, height=10, width=65)
        fd = open('b.py')
        lines = fd.read()
        fd.close()
        text.insert(END, lines)
        text.pack(side=LEFT, fill=X, padx=5)
        sb = Scrollbar(iframe4, orient=VERTICAL, command=text.yview)
        sb.pack(side=RIGHT, fill=Y)


        text.configure(yscrollcommand=sb.set)

root = Tk()
all = AlltkinterWidgets(root)
root.title('tkinter Widgets')
root.mainloop()