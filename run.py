from components.core import Application

app = Application()
app.pre_build()

app.root.mainloop()


## ToDo ##
#- Sometimes indexes with become 0 on search... (Currently patched with empty list check before search.)