#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import os
from time import sleep
from datetime import datetime
import Adafruit_CharLCD as LCD


def l1display(string, style):
	display(1, string, style)

def l2display(string, style):
	display(2, string, style)

def clear_display():
	
def display(line, string, style):

def main():
	# Define LCD column and row size for 16x2 LCD.
	lcd_columns = 16
	lcd_rows    = 2
	lcd_address = 27

	# Initialize the LCD using the pins
	lcd = LCD.Adafruit_CharLCDBackpack()

	# Turn backlight on
	lcd.set_backlight(0)

	'''
	### Demo showing the cursor.
	lcd.clear()
	#lcd.show_cursor(True)
	#lcd.blink(True)
	
	### Stop blinking and showing cursor.
	#lcd.show_cursor(False)
	#lcd.blink(False)

	# Demo scrolling message right/left.
	lcd.clear()
	message = 'Scroll'
	lcd.message(message)
	for i in range(lcd_columns-len(message)):
		time.sleep(0.5)
		lcd.move_right()
	for i in range(lcd_columns-len(message)):
		time.sleep(0.5)
		lcd.move_left()
	'''

	show_time()
	show_message()

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

	on PlusPress():
		
		

def alarm_set():
	

def alarm_execute():

if __name__ == '__main__':
	main()
