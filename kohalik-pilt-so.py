# Source - https://stackoverflow.com/q
# Posted by Incognito Possum
# Retrieved 2025-12-09, License - CC BY-SA 3.0
# Kood allalaetud pildi kuvamiseks, pärit StackOverflowst

import tkinter as tk  
from PIL import Image,ImageTk  
root = tk.Tk()  
root.title("display image")  
im=Image.open("haridwar.jpg")  
photo=ImageTk.PhotoImage(im)  
cv = tk.Canvas()  
cv.pack(side='top', fill='both', expand='yes')  
cv.create_image(10, 10, image=photo, anchor='nw')  
root.mainloop()
