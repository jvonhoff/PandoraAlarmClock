import smbus
import datetime
import os
from time import sleep
from evdev import InputDevice, categorize, ecodes
from threading import Thread

def delay(time):
    sleep(time/1000.0)

def delayMicroseconds(time):
    sleep(time/1000000.0)

mode = "Test"
data = "...wait..."

class KeyListener(Thread):
#    def __init__(self,mode):
#        Thread.__init__(self)
#        self.mode = mode

    def run(self):
        global mode
        global data
        dev = InputDevice('/dev/input/event0')
        for event in dev.read_loop():
            if event.type == ecodes.EV_KEY:
                print(mode, event.code, event.value)
                if event.code in (113,114,115):
                    if mode == "Time":
                        if event.code == 113:
                            mode = "Pandora"
                            data = "starting..."
                        if event.code in (114,115):
                            mode = "Volume"
                            data = "75% just kidding"
                    if mode == "Volume":
                        if event.code == 114:
                            mode = "Volume"
                            data = "TurnDownForWhat?"
                        if event.code == 115:
                            mode = "Volume"
                            data = "CrankItUp!"

def main():
    screen = Screen(bus=1, addr=0x27, cols=16, rows=2)
    screen.enable_backlight()

    global mode
    global data
    mode = "Time"
    data = (str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute))

    myKeyListener = KeyListener()
    myKeyListener.daemon = True
    myKeyListener.start()
    
    while True:
        screen.display_data(mode, data)
        if mode != "Time":
            sleep(4)
            mode = "Time"
            data = (str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute))

            #screen.clear()
            #screen.disable_backlight()

def song_change():
	new_song = '''something from pianobar'''
	l1display(new_song.parse_artist(), scroll_left_slow)
	l2display(new_song.parse_song(), scroll_left_slow)
	sleep(5)

def volume_change():
	l1display("Volume")
	l2display('''something from alsamixer''')
	sleep(2)

def menu():
	current="Alarm"
	l1display("-> Alarm")
	l2display("   Music")

	#on PlusPress():

def alarm_set():
    return

def alarm_execute():
    return

class Screen():

    enable_mask = 1<<2
    rw_mask = 1<<1
    rs_mask = 1<<0
    backlight_mask = 1<<3

    data_mask = 0x00

    def __init__(self, cols = 16, rows = 2, addr=0x27, bus=1):
        self.cols = cols
        self.rows = rows        
        self.bus_num = bus
        self.bus = smbus.SMBus(self.bus_num)
        self.addr = addr
        self.display_init()
        
    def enable_backlight(self):
        self.data_mask = self.data_mask|self.backlight_mask
        
    def disable_backlight(self):
        self.data_mask = self.data_mask& ~self.backlight_mask
       
    def display_data(self, *args):
        self.clear()
        for line, arg in enumerate(args):
            self.cursorTo(line, 0)
            self.println(arg[:self.cols].ljust(self.cols))
           
    def cursorTo(self, row, col):
        offsets = [0x00, 0x40, 0x14, 0x54]
        self.command(0x80|(offsets[row]+col))
    
    def clear(self):
        self.command(0x10)

    def println(self, line):
        for char in line:
            self.print_char(char)     

    def print_char(self, char):
        char_code = ord(char)
        self.send(char_code, self.rs_mask)

    def display_init(self):
        delay(1.0)
        self.write4bits(0x30)
        delay(4.5)
        self.write4bits(0x30)
        delay(4.5)
        self.write4bits(0x30)
        delay(0.15)
        self.write4bits(0x20)
        self.command(0x20|0x08)
        self.command(0x04|0x08, delay=80.0)
        self.clear()
        self.command(0x04|0x02)
        delay(3)

    def command(self, value, delay = 50.0):
        self.send(value, 0)
        delayMicroseconds(delay)
        
    def send(self, data, mode):
        self.write4bits((data & 0xF0)|mode)
        self.write4bits((data << 4)|mode)

    def write4bits(self, value):
        value = value & ~self.enable_mask
        self.expanderWrite(value)
        self.expanderWrite(value | self.enable_mask)
        self.expanderWrite(value)        

    def expanderWrite(self, data):
        self.bus.write_byte_data(self.addr, 0, data|self.data_mask)
       

if __name__ == "__main__":
    main()
