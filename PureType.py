from keyboard import on_press
from time import time, sleep
import tkinter as tk
from serial import Serial
from PIL import Image, ImageTk
import requests
from io import BytesIO

global presses
presses = 0
interval = 500
s = round(1000/interval)
measuring = False

minSpeed = 60
maxSpeed = 90
warningRange = 8

wpmTracker = []
def avgLast(n):
    if len(wpmTracker) < 1: return 0
    if n > len(wpmTracker):
        return sum(wpmTracker)/len(wpmTracker)
    
    return sum(wpmTracker[-n:])/n

def wpm():
    return 10 + (presses/delta()) * 60 / 5

delayCharacter = None
def press(event):
    global presses, measuring, delayCharacter
    if event.name in ["backspace", "ctrl"]:
        delayCharacter = event.name
        return
    if not event.name in "abcdefghijklmnopqrstuvwxyz0123456789": return
    if not measuring: measuring = True
    presses += 1
    if len(wpmTracker) < 1: return

on_press(press)
t0 = time()
def delta():
    return time() - t0

try:
    arduino = Serial("COM6", 9600, timeout=1)
except:
    arduino = None
switchedOn = False
jorkBehaviour = False
jorkInterval = 250

def state(modify=None):
    if arduino == None: return
    global switchedOn
    if modify != None:
        if switchedOn == modify: return
        switchedOn = modify
    
    arduino.write(("S90\n" if switchedOn else "S0\n").encode())

buttonPress = False
def fastloop():
    global buttonPress
    buttonPress = False
    if arduino == None: return
    if arduino.in_waiting > 0:
        analog_value = arduino.readline().decode('utf-8').strip()
        buttonPress = int(analog_value) > 600
        
    main.after(1, fastloop)

def mainloop():
    global presses, t0, measuring, wpmTracker, color, labelWPM, main, delayCharacter, jorkBehaviour
    if not measuring:
        main.after(interval, mainloop)
        return
    
    wpmTracker.append(wpm())
    curWpm = avgLast(4*s)
    wpmDisplayOverride = False
    if buttonPress:
        wpmDisplayOverride = True
        color = "red"
        displayWPM.set("can't stop won't stop!")
        displayDirection.set("can't stop won't stop!")
        labelDirection.configure(font=("Impact", 18, "bold"))
        jorkBehaviour = True
        setBluemoji("shock")
    elif len(wpmTracker) > 4*s:
        if delayCharacter == "backspace":
            wpmDisplayOverride = True
            color = "red"
            displayWPM.set("no backspaces!")
            displayDirection.set("be confident!")
            labelDirection.configure(font=("Impact", 18, "bold"))
            jorkBehaviour = True
            setBluemoji("angry")
        elif delayCharacter == "ctrl":
            wpmDisplayOverride = True
            color = "red"
            displayWPM.set("no shortcuts!")
            displayDirection.set("life won't have shortcuts!")
            labelDirection.configure(font=("Impact", 18, "bold"))
            jorkBehaviour = True
            setBluemoji("angry")
        elif curWpm <= minSpeed:
            color = "red"
            displayDirection.set("way too slow!")
            labelDirection.configure(font=("Impact", 24, "bold"))
            jorkBehaviour = True
            setBluemoji("shock")
        elif curWpm <= minSpeed + warningRange:
            color = "yellow"
            displayDirection.set("speed up!")
            jorkBehaviour = False
            labelDirection.configure(font=("Comic Sans MS", 16))
            setBluemoji("warning")
        elif curWpm < maxSpeed - warningRange:
            color = "green"
            displayDirection.set("good speed!")
            jorkBehaviour = False
            labelDirection.configure(font=("Comic Sans MS", 16))
            setBluemoji("good")
        elif curWpm <= maxSpeed:
            color = "yellow"
            displayDirection.set("slow down!")
            labelDirection.configure(font=("Comic Sans MS", 16))
            jorkBehaviour = False
            setBluemoji("warning")
        else:
            color = "red"
            displayDirection.set("way too fast!")
            labelDirection.configure(font=("Impact", 24, "bold"))
            jorkBehaviour = True
            setBluemoji("shock")
            
    else:
        color = "gray"
        displayDirection.set("evaluating speed...")
        labelDirection.configure(font=("Comic Sans MS", 16))
        setBluemoji("detecting")

    if not wpmDisplayOverride:       
        if (avgLast(1*s) <= 15):
            measuring = False
            wpmTracker = []
            displayWPM.set("start typing!")
            displayDirection.set("")
            color = "gray"
            jorkBehaviour = False
            setBluemoji("idle")
        else:
            displayWPM.set(f"{round(curWpm)} WPM")
    
    labelWPM["bg"] = color
    labelDirection["bg"] = color
    main["bg"] = color
    delayCharacter = None
    presses = 0
    t0 = time()
    main.after(interval, mainloop)

def jorkingThePeenorts():
    if jorkBehaviour:
        state(not switchedOn)
    else:
        state(False)
    main.after(jorkInterval, jorkingThePeenorts)

color = "gray"
main = tk.Tk()
main.title("PureType")
main.geometry('300x200')
main.iconbitmap("icon.ico")
main.attributes("-topmost", True)
main.overrideredirect(1)

displayWPM = tk.StringVar()
displayWPM.set("start typing!")
labelWPM = tk.Label(main, textvariable=displayWPM)
labelWPM.configure(font=("Comic Sans MS", 24))
labelWPM.pack(pady=5)

bluemoji = tk.Label(main, width=100, height=100)
bluemoji.pack()
class WebImage:
     def __init__(self,url):
          u = requests.get(url)
          self.image = ImageTk.PhotoImage(
              Image.open(BytesIO(u.content)).resize(
                  (100, 100), Image.Resampling.LANCZOS
                  )
            )
          
     def get(self):
          return self.image

imageSet = {
    "idle": WebImage("https://bluemoji.io/cdn-proxy/646218c67da47160c64a84d5/66b3ec2d6477b8e963f84a4f_04.png"),
    "detecting": WebImage("https://bluemoji.io/cdn-proxy/646218c67da47160c64a84d5/66b3e5d90608f3f68cb0efc5_85.png"),
    "good": WebImage("https://bluemoji.io/cdn-proxy/646218c67da47160c64a84d5/66b3e5d0c2ab246786ca1d5e_86.png"),
    "warning": WebImage("https://bluemoji.io/cdn-proxy/646218c67da47160c64a84d5/66b3ec2515f9e7a640a994d6_07.png"),
    "shock": WebImage("https://bluemoji.io/cdn-proxy/646218c67da47160c64a84d5/66b3eb4819f48592fa6efc03_41.png"),
    "angry": WebImage("https://bluemoji.io/cdn-proxy/646218c67da47160c64a84d5/66b3ea0bbf2717e5d8848926_44.png")
    }
def setBluemoji(state):
    bluemoji["image"] = imageSet[state].get()

setBluemoji("idle")

displayDirection = tk.StringVar()
displayDirection.set("")
labelDirection = tk.Label(main, textvariable=displayDirection)
labelDirection.pack()

labelWPM["bg"] = color
labelDirection["bg"] = color
main["bg"] = color

main.after(0, fastloop)
main.after(0, mainloop)
main.after(jorkInterval, jorkingThePeenorts)
main.mainloop()

