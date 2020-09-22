import smbus
import datetime
import os
import sys
from time import time, sleep
from evdev import InputDevice, categorize, ecodes
from threading import Thread,Timer
from subprocess import call,check_output,Popen

def delay(time):
    sleep(time/1000.0)

def delayMicroseconds(time):
    sleep(time/1000000.0)

mode = "Test"
data = "...wait..."
counter = 0
bouncer = 1
alarm_time = "99:99"
fifo_path = "/tmp/pianobar"

def revert():
    global mode, data, screen

    curr_time = "{}".format(str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute).rjust(2,'0'))
    if playing == True:
        mode = " - Music"
        data = get_song_data()
    else:
        mode = ""
        data = ""

    screen.display_data("{}{}".format(curr_time,mode), data)

def music_control(parm):
    global data, playing, fifo

    if "play" in parm:
        if playing == False:
            call(["pianobar"])
            os.mkfifo(fifo_path)
            fifo = open(fifo_path, "w")
        else:
            fifo.write("n") #next

        playing = True
        data = "Starting Music..."

    if "stop" in parm:
        playing = False
        fifo.write("q") #quit
        data = "          Play >"

def alarm_control(parm):
    global alarm_time
    if parm == "set":
        alarm_time = "21:53"
        call("echo '{}' > /media/Alarm/.alarm_time".format(alarm_time), shell=True)
    if parm == "delete":
        alarm_time = "99:99"
        call("rm /media/Alarm/.alarm_time", shell=True)
        

def get_song_data():
    with open('/home/pi/.config/pianobar/nowplaying') as playstatus:
        line = playstatus.readline()
        if re.search('artist=',line):
            artist = line.replace('artist=','')
        if re.search('title=',line):
            title = line.replace('title=','')
        
    song_info = "{} - {}".format(artist,title).decode('unicode_escape').encode('ascii','ignore')
    #print(song_info)
    return song_info.replace('\n','')

def show_volume():
    vol_check = check_output(["mpc", "volume"]).splitlines()[0]
    return "{:^16}".format(vol_check[7:])

def scroll(text):
    global counter, bouncer

    if len(text) <= 16:
        return text
    else:
        if len(text) - abs(counter) > 16 :
            counter += 1 * bouncer
            print("start at {}".format(counter))
        else:
            bouncer = bouncer * -1
            counter += 1 * bouncer
            print("start at {}".format(counter))
        print(text[counter:])
        return text[counter:]


class KeyListener(Thread):
    def __init__(self,mode):
        Thread.__init__(self)
        self.mode = mode

    def run(self):
        global mode, data, screen

        dev = InputDevice('/dev/input/event0')

        for event in dev.read_loop():
            if event.type == ecodes.EV_KEY:
                if event.value != 0L:
                    continue
                if event.code in (113,114,115):
                    print(mode, event.code, event.value)
                    try:
                        t.cancel()
                    except:
                        print("no timer")
                    t = Timer(5, revert)
                    t.start()
                    
                    handleKeypress(event.code)

def handleKeypress(code):
    global mode, data
    
    if code==113:
        if mode == "":
            mode = " - Music"
            data = "< Stop    Play >"
            return

        elif "Music" in mode:
            if "Play" in data:
                mode = " - Alarm"
                data = "< Set   Delete >"
            else:
                mode = " - Music"
                data = "< Stop    Play >"
            return

        elif "Alarm" in mode:
            mode = ""
            data = ""
            return

    if code==114:
        print("down in {} mode".format(mode))
        if mode == "":
            mode = " - Volume"
            data = show_volume()
            return

        elif "Volume" in mode:
            call(["mpc", "-q", "volume", "-5"])
            data = show_volume()
            return

        elif "Music" in mode:
            # stop music
            music_control("stop")
            return

        elif "Alarm" in mode:
            alarm_control("set")
            return

    if code==115:
        print("up in {} mode".format(mode))
        if mode == "":
            mode = " - Volume"
            data = show_volume()
            return

        elif "Volume" in mode:
            call(["mpc", "-q", "volume", "+5"])
            data = show_volume()
            return

        elif "Music" in mode:
            # play or skip music
            music_control("play")
            return

        elif "Alarm" in mode:
            alarm_control("delete")
            return

def main():

    global mode, data, screen, playing, alarm_time
    
    playing = False
    
    try:
        call("mpc ls Local\ media | mpc add", shell=True)
        call(["mpc","-q","volume","30"])
        call(["mpc","-q","random","on"])
    except:
        print("Music not available!")

    try:
        alarm_time = check_output(["cat","/media/Alarm/.alarm_time"]).replace('\n','')
    except:
        alarm_time = "99:99"
        
    screen = Screen(bus=1, addr=0x27, cols=16, rows=2)
    screen.disable_backlight()
    screen.enable_backlight()

    curr_time = "{}".format(str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute).rjust(2,'0'))
    mode = ""
    data = ""
    screen.display_data("{}{}".format(curr_time,mode), data)

    myKeyListener = KeyListener(mode=mode)
    myKeyListener.daemon = True
    myKeyListener.start()
    
    while True:
        curr_time = "{}".format(str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute).rjust(2,'0'))
        data_disp = scroll(data)
        #print(data_disp)
        #print("time = {} mode = {} data = {}".format(curr_time, mode, data))
        try:
            oldTime
            oldMode
            oldData
        except:
            oldTime = curr_time
            oldMode = mode
            oldData = data_disp
        if oldTime != curr_time or oldMode != mode or oldData != data_disp:
            oldTime = curr_time
            oldMode = mode
            oldData = data_disp
            #print("time = {}, {} mode = {}, {} data = {}, {}".format(curr_time, oldTime, mode, oldMode, data_disp, oldData))
            
            print("alarm = {} current = {}".format(alarm_time, curr_time))
            if curr_time[0:5] == alarm_time[0:5]:
                music_control("play")
                sleep(3)
                data_disp = "WAKE UP!"
            screen.display_data("{}{}".format(curr_time,mode), data_disp)

        sleep(1)
        
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


