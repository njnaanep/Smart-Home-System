import RPi.GPIO as GPIO
import time
import I2C_LCD_driver
from Adafruit_IO import MQTTClient

from tkinter import *
from datetime import datetime

ws = Tk()
ws.title('Smart Home System')
ws.geometry('500x400')
ws.config(bg='white')

frame = Frame(ws, bg='white')

relays = [17, 27, 22]
btns = [5, 6, 26]
conditions = [True, True, True]

def createBtn(text, row, col):
    btn = Button(frame, text=text, height=2, width=10)
    btn.grid(row=row,column=col,padx=10, pady=10)
    return btn

btn1 = createBtn('Table Light', 1, 0)
btn2 = createBtn('Bed Light', 1, 1)
btn3 = createBtn('Outlet', 1, 2)

GUIbtns = [btn1, btn2, btn3]

lcd = I2C_LCD_driver.lcd()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

for relay in relays:
    GPIO.setup(relay, GPIO.OUT)
    
for createBtn in btns:
    GPIO.setup(createBtn, GPIO.IN)
    
def displayLCD(index, status):
    
    lcd.lcd_clear()

    global topText
    global botText

    if index == 0: topText= 'Table Light'
    if index == 1: topText= 'Bed Light'
    if index == 2: topText= 'Outlet'

    botText = f'turned {status}'
    
    lcd.lcd_display_string(topText,1,0)
    lcd.lcd_display_string(f'is {botText}',2,0)

def displayGUI(index, status):
    global lbl

    text = f'{topText} is {botText}'
    lbl.config(text=text)

    if status=='ON':
        GUIbtns[index].config(background='#90ee90') #green
    else:
        GUIbtns[index].config(background='#ee9090') #red

    time = datetime.now().strftime('%I:%M %p, %a %d %w, %Y ')

    lb.insert(0,f'{topText} was {botText} @ {time}')
        
def relay(index,status):
    conditions[index] = not conditions[index]
    
    if not (status=='ON'):
        GPIO.output(relays[index],1)
    else:
        GPIO.output(relays[index],0)
    
    displayLCD(index, status)
    displayGUI(index, status)
    
    time.sleep(1)
    lcd.lcd_clear()
    
ADAFRUIT_IO_USERNAME = "username"
ADAFRUIT_IO_KEY = "io_key"

def connected(client):
    print('Connected to Adafruit IO!  Listening for changes...')
    # Subscribe to changes on a feed .
    client.subscribe('light1')
    client.subscribe('light2')
    client.subscribe('outlet')
    
    lcd.lcd_display_string('System ON!',1,0)
    time.sleep(1)
    lcd.lcd_clear()

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print(f'Feed {feed_id} received new value: {payload}')

    if(feed_id=='light1'):
        relay(0,payload)

    if(feed_id=='light2'):
        relay(1,payload)

    if(feed_id=='outlet'):
        relay(2,payload)
    
    
# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message
# Connect to the Adafruit IO server.
client.connect()

# allow to run a thread in the background so you can continue doing things in your program.
client.loop_background()

def Publish(condition, feed):
    if condition:
        client.publish(feed, 'ON')
    else:
        client.publish(feed, 'OFF')
        

def btnOne(): Publish(conditions[0], 'light1')
def btnTwo(): Publish(conditions[1], 'light2')
def btnThree(): Publish(conditions[2], 'outlet')

GUIbtns[0].config(command=btnOne)
GUIbtns[1].config(command=btnTwo)
GUIbtns[2].config(command=btnThree)

lbl = Label(frame,
    text='Smart Home System', 
    font=('Arial', 18,'bold'),
    bg='white')

lbl.grid(row=0,column=0,columnspan=3,padx=10, pady=10)

#Create an object of Scrollbar widget
s = Scrollbar()

#Create a horizontal scrollbar
scrollbar = Scrollbar(ws, orient= 'vertical')
scrollbar.pack(side= RIGHT, fill= BOTH)

#Create list box to record activities
lb = Listbox(frame, width=50, height=10)
lb.grid(row=2,column=0,columnspan=3,padx=10, pady=10)

lb.config(yscrollcommand= scrollbar.set)
scrollbar.config(command= lb.yview)

frame.pack(expand=True)

def IOone():
    if not GPIO.input(btns[0]):
        time.sleep(1)
        btnOne()
    
    ws.after(10, IOone)

def IOtwo():
    if not GPIO.input(btns[1]):
        time.sleep(1)
        btnTwo()
    
    ws.after(10, IOtwo)

def IOthree():
    if not GPIO.input(btns[2]):
        time.sleep(1)
        btnThree()
    
    ws.after(10, IOthree)

ws.after(10, IOone)
ws.after(10, IOtwo)
ws.after(10, IOthree)

ws.mainloop()

GPIO.cleanup()
