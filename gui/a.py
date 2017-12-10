import tkinter

F1 = tkinter.Frame()
s = tkinter.Scrollbar(F1)
L = tkinter.Listbox(F1)

s.pack(side=tkinter.RIGHT, fill=tkinter.Y)
L.pack(side=tkinter.LEFT, fill=tkinter.Y)

s['command'] = L.yview
L['yscrollcommand'] = s.set

for i in range(30):
   L.insert(tkinter.END, str(i))

F1.pack(side=tkinter.TOP)

F2 = tkinter.Frame()
lab = tkinter.Label(F2)

def poll():
    lab.after(200, poll)
    sel = L.curselection()

    lab.config(text=str(sel)[1])

lab.pack()
F2.pack(side=tkinter.TOP)

poll()
tkinter.mainloop()