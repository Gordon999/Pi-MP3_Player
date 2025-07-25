#!/usr/bin/env python3

# Pi_MP3_Player

version = 18.08

"""Copyright (c) 2025
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

global fullscreen
global cutdown
global rotary_vol
global rotary_pos
global touchscreen
global ext_buttons

# set display cutdown format
# 0:800x480, 1:320x240,2:640x480,3:480x800,4:480x320,5:800x480 SIMPLE LAYOUT,only default Playlist
# 6:800x480 List 10 tracks, 7:800x480 with scrollbars, 8:1280x720 with scrollbars
cutdown     = 7 # set the format required
fullscreen  = 0 # set to 1 for fullscreen
rotary_vol  = 0 # set to 1 if using VOLUME   rotary encoder 1 (see connections.jpg for wiring details)
rotary_pos  = 0 # set to 1 if using POSITION rotary encoder 2 (see connections.jpg for wiring details)
ext_buttons = 0 # set to 1 if using external buttons (see connections.jpg for wiring details)
touchscreen = 1 # set to 0 if using the rotary encoders and a non-touchscreen

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import font as tkFont
import os, sys
import time
import datetime
from datetime import timedelta
import subprocess
import signal
import random
from random import shuffle
import re
import glob
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.dsf import DSF
from mutagen.mp4 import MP4
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, TCOM, TCON, TDRC, TRCK, TXXX, TENC
import alsaaudio
import math
import socket
import shutil
from PIL import ImageTk, Image
from gpiozero import Button
from gpiozero import LED
from mplayer import Player
import wave
import contextlib
Player.introspect()
player = Player()

class MP3Player(Frame):
    
    def __init__(self):
        super().__init__() 
        self.initUI()
        
    def initUI(self):
        # find user
        self.h_user = "/home/" + os.getlogin( )
        self.m_user = "/media/" + os.getlogin( )
        # Radio Stations List, add to them by adding a 'name','URL','recordable (yes = 1, no = 0)'
        # or you can add more by putting them in a file called '/home/USERNAME/radio_stns.txt'
        self.Radio_Stns = ["Radio Paradise Rock (192)","http://stream.radioparadise.com/rock-192",2,
                           "Radio Paradise Main (320)","http://stream.radioparadise.com/mp3-320",2,
                           "Radio Paradise Mellow (192)","http://stream.radioparadise.com/mellow-192",2,
                           "Radio Paradise World 192","http://stream.radioparadise.com/world-etc-192",2,
                           "Radio Paradise World","http://stream.radioparadise.com/eclectic-flac",0,
                           "Radio Caroline","http://sc6.radiocaroline.net:10558/",0
                          ]
        # settings
        self.Shutdown_exit  = 1  # set to 1 to shutdown the Pi on pressing SHUTDOWN (left mouse button), 0 to only exit script
        self.Button_Radi_on = 1  # show Radio button,set = 1 to enable
        self.m3u_dir        = self.h_user + "/Documents/"     # where .m3us are stored
        self.mp3sd_search   = self.h_user + "/*/*/*/*.mp3"    # search criteria for mp3s  (/home/USER/USBDrive Name/Artist Name/Album Name/Tracks.mp3)
        self.mp3_search     = self.m_user + "/*/*/*/*.mp3"    # search criteria for mp3s  (/media/USER/USBDrive Name/Artist Name/Album Name/Tracks.mp3)
        self.wav_search     = self.m_user + "/*/*/*/*.wav"    # search criteria for wavs  (/media/USER/USBDrive Name/Artist Name/Album Name/Tracks.wav)
        self.flac_search    = self.m_user + "/*/*/*/*.flac"   # search criteria for flacs (/media/USER/USBDrive Name/Artist Name/Album Name/Tracks.flac)
        self.dsf_search     = self.m_user + "/*/*/*/*.dsf"    # search criteria for dfss  (/media/USER/USBDrive Name/Artist Name/Album Name/Tracks.dsf)
        self.m4a_search     = self.m_user + "/*/*/*/*.m4a"    # search criteria for m4as  (/media/USER/USBDrive Name/Artist Name/Album Name/Tracks.m4a)
        self.mp32_search    = "/media/*/*/*/*.mp3"            # search criteria for mp3s  (/media/Drive/A/Artist Name - Album Name/Tracks.mp3)
        self.flac2_search   = "/media/*/*/*/*.flac"           # search criteria for flacs (/media/Drive/A/Artist Name - Album Name/Tracks.flac)
        self.wav2_search    = "/media/*/*/*/*.wav"            # search criteria for wavs  (/media/Drive/A/Artist Name - Album Name/Tracks.wav)
        self.dsf2_search    = "/media/*/*/*/*.dsf"            # search criteria for dfss  (/media/Drive/A/Artist Name - Album Name/Tracks.dsf)
        self.m4a2_search    = "/media/*/*/*/*.m4a"            # search criteria for m4as  (/media/Drive/A/Artist Name - Album Name/Tracks.m4a)
        self.mp33_search    = self.m_user + "/*/*/*/*/*.mp3"  # search criteria for mp3s  (/media/USER/USBDrive Name/Genre/Artist Name/Album Name/Tracks.mp3)
        self.wav3_search    = self.m_user + "/*/*/*/*/*.wav"  # search criteria for wavs  (/media/USER/USBDrive Name/Genre/Artist Name/Album Name/Tracks.wav)
        self.flac3_search   = self.m_user + "/*/*/*/*/*.flac" # search criteria for flacs (/media/USER/USBDrive Name/Genre/Artist Name/Album Name/Tracks.flac)
        self.dsf3_search    = self.m_user + "/*/*/*/*/*.dsf"  # search criteria for dfss  (/media/USER/USBDrive Name/Genre/Artist Name/Album Name/Tracks.dsf)
        self.m4a3_search    = self.m_user + "/*/*/*/*/*.m4a"  # search criteria for m4as  (/media/USER/USBDrive Name/Genre/Artist Name/Album Name/Tracks.m4a)
        self.m3u_def        = "ALLTracks"                     # name of default .m3u. Limit to 9 characters.
        self.mp3_jpg        = "mp3.jpg"                       # logo including the 'wheel', when inactive
        self.mp3c_jpg       = "mp3c.jpg"                      # blue logo including the 'wheel', when active
        self.radio_jpg      = "radio.jpg"                     # radio logo, shown if no jpg in /home/USERNAME/Documents for Radio Station
        self.Disp_max_time  = 120  # in minutes. Limits time taken to determine playlist length.
        self.volume         = 30   # range 0 - 100. Will be overridden by saved volume in saved config file
        self.gapless_time   = 2    # in seconds. Defines length of track overlap.
        self.scroll_rate    = 3    # scroll rate 1 (slow) to 10 (fast)
        self.Pi7_backlight  = 0    # Pi 7" inch v1 display backlight control (pip3 install rpi_backlight)
        self.LCD_backlight  = 0    # LCD backlight control, set to 1 to activate.
        self.LCD_LED_pin    = 23   # LCD backlight GPIO
        self.HP4_backlight  = 0    # Hyperpixel4 backlight control, set to 1.
        self.light          = 60   # Backlight OFF timer for above, in seconds
        self.dim            = 0.1  # Backlight dim 
        self.bright         = 0.8  # Backlight bright , 1 full brightness
        self.waveshare      = 0    # set to 1 if using a Waveshare 2.8" (A) LCD display with buttons
        
        # initial parameters
        self.trace          = 0
        self.bt_on          = 0
        self.repeat         = 0
        self.play           = 0
        self.stop7          = 0
        self.sleep_time     = 0
        self.sleep_time_min = 0
        self.max_sleep      = 120
        self.record         = 1
        self.record_time    = 0
        self.ram_min        = 150
        self.tracking       = 0
        self.max_record     = 0 
        self.rec_step       = 10
        self.total_record   = 0
        self.Radio          = 0
        self.track_nameX    = ""
        self.oldtrack       = ""
        self.oldtrack2      = ""
        self.record_sleep   = 0
        self.R_Stopped      = 0
        self.roldsecs       = 0
        self.album_sleep    = 0
        self.tunes          = []
        self.muted          = 0
        self.shuffle_on     = 0
        self.sorted         = 0
        self.begin          = time.monotonic()
        self.timer7         = time.monotonic()
        self.m3u_no         = 0
        self.stopstart      = 0
        self.paused         = 0
        self.gapless        = 0
        self.count1         = 0
        self.count2         = 0
        self.countex        = 0
        self.version        = 2
        self.album_time     = 0
        self.album_start    = 0
        self.shutdown       = 0
        self.album_track    = 0
        self.count_dir      = 3 
        self.old_t          = 0
        self.wheel          = 0
        self.sort_no        = 0
        self.wheel_opt      = 0
        self.timer4         = 0
        self.drive_name     = ""
        self.render2        = ""
        self.repeat_track   = 0
        self.repeat_count   = 0
        self.repeat_album   = 0
        self.t              = 0
        self.shuffle_count  = 0
        self.album_length   = 0
        self.plist_length   = 0
        self.plist_trig     = 0
        self.que_dir        = self.m3u_dir + self.m3u_def + ".m3u"
        self.m              = 0
        self.BT             = 0
        self.oldsecs        = 0
        self.model          = 1
        self.light_on       = 0
        self.old_abs_x      = 0
        self.old_abs_y      = 0
        self.track_no       = 0
        self.restart        = 0
        self.piz_timer      = 360
        self.piz_timer2     = time.monotonic()
        self.Radio_ON       = 0
        self.Radio_RON      = 0
        self.cutdown        = cutdown
        self.rotary_pos     = rotary_pos
        self.rotary_vol     = rotary_vol
        self.touchscreen    = touchscreen
        self.ext_buttons    = ext_buttons
        self.tname          = "Unknown"
        self.auto_rec_set   = 0
        self.auto_play      = 0
        self.auto_album     = 0
        self.auto_radio     = 0
        self.auto_record    = 0
        self.auto_rec_time  = 10
        self.usave          = 0
        self.minutes        = 0
        self.seconds        = 10
        self.old_tname      = "x"
        self.p_minutes      = 0
        self.p_seconds      = 0
        self.copy           = 0
        self.trackdata      = []
        self.ac             = 0
        self.bc             = 0
        self.cc             = 0
        self.old_artists    = []
        self.old_list       = []
        self.tracker        = 0
        self.reload         = 0
        self.imgxon         = 0
        self.gpio_enable    = 0
        self.xxx            = 0
        self.ramtest        = 0
        self.artist_name    = ""
        self.album_name     = ""
        self.track_name     = ""
        self.genre_name     = ""
        self.old_rotor1     = 0
        self.old_rotor2     = 0
        self.rot_posp       = 3
        
        if self.cutdown == 0 or self.cutdown == 2 or self.cutdown >= 7 or self.cutdown == 8:
            self.order = [1,2,12,3,4,9,13,10,16,6,7,8,5,14,15,11,0]
        elif self.cutdown == 1:
            self.order = [1,2,12,3,4,10,6,7,8,9,5,11,0]
        elif self.cutdown == 3:
            self.order = [1,2,12,3,4,6,7,8,15,5,9,14,13,10,11,0]
        elif self.cutdown == 4:
            self.order = [1,2,12,3,4,13,10,7,8,6,9,5,11,0]
        elif self.cutdown == 5 or self.cutdown == 6:
            self.order = [0,1,2,3,4,5,6,7,8,9,10,11]
        self.rot_pos  = self.order[self.rot_posp]
        self.rot_mode = 0
        if self.rotary_pos == 1:
            self.ext_buttons = 0

        # check if clock synchronised
        if "System clock synchronized: yes" in os.popen("timedatectl").read().split("\n"):
            self.synced = 1
        else:
            self.synced = 0
        # bind wheel button       
        if self.cutdown != 4 and self.cutdown != 1 and self.cutdown != 5:
            self.master.bind("<Button-1>", self.Wheel_Opt_Button)

        #check Pi model.
        if os.path.exists ('/run/shm/md.txt'): 
            os.remove("/run/shm/md.txt")
        os.system("cat /proc/cpuinfo >> /run/shm/md.txt")
        with open("/run/shm/md.txt", "r") as file:
                line = file.readline()
                while line:
                   line = file.readline()
                   if line[0:5] == "Model":
                       model = line
        if "Zero" in model:
            self.model = 0
        if self.trace > 0:
            print (model,self.model)

        # read radio_stns.txt (Station Name,URL,X)
        if os.path.exists ("radio_stns.txt"): 
            with open("radio_stns.txt","r") as textobj:
                line = textobj.readline()
                while line:
                    if line.count(",") == 2:
                        a,b,c = line.split(",")
                        if a[0:1] != "#":
                            self.Radio_Stns.append(a)
                            self.Radio_Stns.append(b)
                            self.Radio_Stns.append(int(c.strip()))
                    elif line.count(",") == 1:
                        a,b = line.split(",")
                        if a[0:1] != "#":
                            self.Radio_Stns.append(a)
                            self.Radio_Stns.append(b.strip())
                            self.Radio_Stns.append(0)
                    line = textobj.readline()
        # read radio_stns.csv (Station Name,URL,X,)
        elif os.path.exists ("radio_stns.csv"): 
            with open("radio_stns.csv","r") as textobj:
                line = textobj.readline()
                while line:
                    if line.count(",") == 3:
                        a,b,c,d = line.split(",")
                        self.Radio_Stns.append(a)
                        self.Radio_Stns.append(b)
                        self.Radio_Stns.append(int(c))
                    line = textobj.readline()
                    
        # check Lasttrack3.txt exists, if not then write default values. Used for recalling last Radio Station ,volume etc, and restarting if using a Pi Zero.
        if not os.path.exists('Lasttrack3.txt'):
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")

        # read Lasttrack3.txt
        with open("Lasttrack3.txt", "r") as file:
           self.track_no      = int(file.readline())
           self.auto_play     = int(file.readline())
           self.Radio         = int(file.readline())
           self.volume        = int(file.readline())
           self.auto_radio    = int(file.readline())
           self.auto_record   = int(file.readline())
           self.auto_rec_time = int(file.readline())
           self.shuffle_on    = int(file.readline())
           self.auto_album    = int(file.readline())
        if self.auto_album == 1:
            self.auto_albums = 1
            self.rot_posp    = 4
            self.rot_pos     = 4
        else:
            self.auto_albums = 0
        if self.Radio >= int(len(self.Radio_Stns)):
            self.Radio = 0
        if self.auto_play == 0:
            self.start = self.auto_play
        else:
            self.start     = 1
            self.rot_posp  = 3
            self.rot_pos   = 3
        self.auto_rec_set  = 0
        self.f_volume      = self.volume
        self.NewRadio      = -1
        self.auto_rec_time = 0
        
        # wait for internet,if required for auto_radio
        count = 0
        if self.auto_radio == 1:
            print ("Checking for Internet")
            out = False
            while out == False and count < 30:
                out = self.isConnected()
                time.sleep(1)
                count += 1
            rcount = 0
            for r in range(0,len(self.order)):
                if self.order[r] == 8:
                    self.rot_pos  = r
                    self.rot_posp = r
                rcount +=1
                        
        # check for audio mixers
        print (alsaaudio.mixers())
        if len(alsaaudio.mixers()) > 0:
            for mixername in alsaaudio.mixers():
                if str(mixername) == "PCM" or str(mixername) == "DSP Program" or str(mixername) == "Master" or str(mixername) == "Capture" or str(mixername) == "Headphone" or str(mixername) == "HDMI":
                    self.m = alsaaudio.Mixer(mixername)
                else:
                    self.m = alsaaudio.Mixer(alsaaudio.mixers()[0])
                    self.version = 1
                    self.BT      = 1
                    self.gapless = 1
            self.m.setvolume(self.volume)
            self.mixername = mixername
            os.system("amixer -D pulse sset Master " + str(self.volume) + "%")
            if self.mixername == "DSP Program":
                os.system("amixer set 'Digital' " + str(self.volume + 107))
        self.test     = 0
        self.counter5 = 0
       
        # check for HyperPixel4 LCD and if so disable GPIO controls.
        if os.path.exists ('/sys/devices/platform/i2c@0') and self.ext_buttons == 1: 
            self.gpio_enable = 0
            from gpiozero import PWMLED
            self.pwm_pin = 19
            self.LCD_pwm = PWMLED(self.LCD_LED_pin)
            self.dim     = 0.1  # Backlight dim 
            self.bright  = 0.8  # Backlight bright , 1 full brightness
            self.LCD_pwm.value = self.bright
        # enable buttons on Waveshare LCD (A)
        elif self.waveshare == 1 and self.cutdown == 4 and self.ext_buttons == 1:
            self.gpio_enable = 1
            self.voldn           = 23 # external volume down gpio input
            self.volup           = 24 # external volume up gpio input
            self.mute            = 25 # external mute gpio input
            self.button_voldn    = Button(self.voldn)
            self.button_mute     = Button(self.mute)
            self.button_volup    = Button(self.volup)
        # enable buttons or rotary on other displays and cutdowns
        else:
            self.gpio_enable = 2
            if self.rotary_pos == 0 and self.rotary_vol == 0 and self.ext_buttons == 1:
                self.voldn              = 16 # external volume down gpio input
                self.volup              = 12 # external volume up gpio input
                self.mute               = 20  # external mute gpio input
                self.button_voldn       = Button(self.voldn)
                self.button_mute        = Button(self.mute)
                self.button_volup       = Button(self.volup)
                self.start_album        = 13 # external start/stop album gpio input
                self.start_play         = 5  # external start/stop playlist gpio input
                self.start_next         = 6  # external next album / track gpio input
                self.button_start_album = Button(self.start_album)
                self.button_start_play  = Button(self.start_play)
                self.button_start_next  = Button(self.start_next)
            if self.rotary_vol == 1:
                from gpiozero import RotaryEncoder
                self.rotor1 = RotaryEncoder(20,16, wrap=True, max_steps=99)
                self.mute               = 12  # external mute
                self.button_mute        = Button(self.mute)
                if self.ext_buttons == 1 and self.rotary_pos == 0:
                    self.start_album        = 13 # external start/stop album gpio input
                    self.start_play         = 5  # external start/stop playlist gpio input
                    self.start_next         = 6  # external next album / track gpio input
                    self.button_start_album = Button(self.start_album)
                    self.button_start_play  = Button(self.start_play)
                    self.button_start_next  = Button(self.start_next)
            if self.rotary_pos == 1:
                if self.rotary_vol == 0:
                    from gpiozero import RotaryEncoder
                self.rotor2 = RotaryEncoder(6, 5, wrap=True, max_steps=99)
                self.next                   = 13  # external next action
                self.button_next            = Button(self.next)
                if self.ext_buttons == 1 and self.rotary_vol == 0:
                    self.voldn              = 16 # external volume down gpio input
                    self.volup              = 12 # external volume up gpio input
                    self.mute               = 20 # external mute gpio input
                    self.button_voldn       = Button(self.voldn)
                    self.button_mute        = Button(self.mute)
                    self.button_volup       = Button(self.volup)
        # enable LCD backlight (not Pi 7" screen)
        if self.LCD_backlight == 1:
            self.gpio_enable = 1
            from gpiozero import PWMLED
            self.LCD_pwm = PWMLED(self.LCD_LED_pin)
            self.dim     = 0.0  # Backlight dim 
            self.bright  = 0.8  # Backlight bright , 1 full brightness
            self.LCD_pwm.value = self.bright
        # Pi 7" screen backlight
        if self.Pi7_backlight == 1:
            os.system("rpi-backlight -b 100")
        
        # setup GUI
        self.Frame10 = tk.Frame(width=1280, height=720)
        self.Frame10.grid_propagate(0)
        self.Frame10.grid(row=0, column=0)

        # shutdown button left click
        def left_click(event):
            if (self.shuffle_on == 1 and self.sleep_time > 0 and self.play == 0) or self.Shutdown_exit == 0:
                self.exit()
            else:
                os.system("sudo shutdown -h now")
        # shutdown button right click
        def right_click(event):
            self.exit()

        if self.cutdown == 0: # Pi 7" Display 800 x 480
            self.length = 30
            self.helv01 = tkFont.Font(family='Helvetica', size=18, weight='bold') # Names font size
            self.helv02 = tkFont.Font(family='Helvetica', size=12) # Buttons font size
            self.helv03 = tkFont.Font(family='Helvetica', size=11) # RELOAD font size
            self.Button_Start = tk.Button(self.Frame10, text = "PLAY Playlist", bg = "green",fg = "black",width = 8, height = 3,font = self.helv02, command = self.Play, wraplength=80, justify=CENTER)
            self.Button_Start.grid(row = 0, column = 0, padx = 10,pady = 10)
            self.Button_Pause = tk.Button(self.Frame10, text = "Pause",bg = "light blue", width = 8, height = 2,font = self.helv02,command=self.Pause, wraplength=80, justify=CENTER)
            self.Button_Pause.grid(row = 0, column = 2, padx = 0,pady = 10)
            self.Button_Gapless = tk.Button(self.Frame10, text = "Gapped", fg = "black",bg = "light blue", width = 8, height = 2,font = self.helv02,command=self.Gapless, wraplength=80, justify=CENTER)
            self.Button_Gapless.grid(row = 0, column = 3,pady = 10)
            self.Button_TAlbum = tk.Button(self.Frame10, text = "PLAY Album", bg = "blue",fg = "black", width = 8, height = 3,font = self.helv02,command=self.Play_Album, wraplength=80, justify=CENTER)
            self.Button_TAlbum.grid(row = 0, column = 1,pady = 10)
            Button_Volume_Dn =  tk.Button(self.Frame10, text = " < Vol ",    bg = "light green",width = 8, height = 2,font = self.helv02,command = self.volume_DN,repeatdelay=1000, repeatinterval=500)
            Button_Volume_Dn.grid(row = 0, column = 5)
            if self.m == 0:
                self.Button_volume = tk.Button(self.Frame10, text = self.volume, fg = "black",width = 1, height = 2,font = self.helv02,command = self.Mute)
            else:
                self.Button_volume = tk.Button(self.Frame10, text = self.volume, fg = "green",width = 1, height = 2,font = self.helv02,command = self.Mute)
            self.Button_volume.grid(row = 0, column = 6)
            self.Button_Vol_UP =  tk.Button(self.Frame10, text = "Vol >",      bg = "light green",width = 8, height = 2,font = self.helv02,command = self.volume_UP,repeatdelay=1000, repeatinterval=500)
            self.Button_Vol_UP.grid(row = 0, column = 7)
            self.Button_Prev_PList =  tk.Button(self.Frame10, text = "< P-list",   bg = "light blue",width = 8, height = 1,font = self.helv02,command = self.Prev_m3u,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_PList.grid(row = 1, column = 0)
            self.Button_Next_PList =  tk.Button(self.Frame10, text = "P-list >",   bg = "light blue",width = 8, height = 1,font = self.helv02,command = self.Next_m3u,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_PList.grid(row = 1, column = 7)
            self.Button_Prev_Artist =  tk.Button(self.Frame10, text = "< Artist",   bg = "light blue",fg = "black",width = 8, height = 2,font = self.helv02,command = self.Prev_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Artist.grid(row = 2, column = 0)
            self.Button_Next_Artist =  tk.Button(self.Frame10, text = "Artist >",   bg = "light blue",width = 8, height = 2,font = self.helv02,command = self.Next_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Artist.grid(row = 2, column = 7)
            self.Button_Prev_Album =  tk.Button(self.Frame10, text = "< Album",    bg = "light blue",width = 8, height = 2,font = self.helv02,command = self.Prev_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Album.grid(row = 3, column = 0)
            self.Button_Next_Album =  tk.Button(self.Frame10, text = "Album >",     bg = "light blue",width = 8, height = 2,font = self.helv02,command = self.Next_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Album.grid(row = 3, column = 7)
            self.Button_Prev_Track =  tk.Button(self.Frame10, text = "< Track",    bg = "light blue",width = 8, height = 2,font = self.helv02,command = self.Prev_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Track.grid(row = 4, column = 0)
            self.Button_Next_Track = tk.Button(self.Frame10, text = "Track >",    bg = "light blue",width = 8, height = 2,font = self.helv02,command = self.Next_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Track.grid(row = 4, column = 7)
            self.Button_Bluetooth = tk.Button(self.Frame10, text = "Bluetooth",    bg = "light blue",width = 6, height = 1,font = self.helv02,command = self.Bluetooth)
            self.Button_Bluetooth.grid(row = 5, column = 7)
            if self.Button_Radi_on == 1:
                self.Button_Radio = tk.Button(self.Frame10, text = "Radio",    bg = "light blue",width = 8, height = 2,font = self.helv02,command = self.RadioX, wraplength=80, justify=CENTER)
                self.Button_Radio.grid(row = 9, column = 5, columnspan = 2)
                        
            self.Button_Next_AZ = tk.Button(self.Frame10, text = "Next A-Z",   width = 8, height = 2,font = self.helv02,bg = "light blue",command=self.nextAZ,repeatdelay=250, repeatinterval=500)
            self.Button_Next_AZ.grid(row = 7, column = 7)
            if os.path.exists(self.mp3c_jpg):
                self.load = Image.open(self.mp3c_jpg)
                self.renderc = ImageTk.PhotoImage(self.load)
                self.img = tk.Label(self.Frame10, image = self.renderc)
                self.img.grid(row = 5, column = 0, columnspan = 2, rowspan = 5, pady = 2)
            else:
                self.img = tk.Label(self.Frame10)
                self.img.grid(row = 5, column = 0, columnspan = 2, rowspan = 5, pady = 2)
            self.Button_Reload = tk.Button(self.Frame10, text = " RELOAD " + self.m3u_def ,width = 8, height = 2,font = self.helv03, bg = "light blue",command = self.RELOAD_List, wraplength=80, justify=CENTER)
            self.Button_Reload.grid(row = 7, column = 2,padx = 10)
            if self.Shutdown_exit == 1:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "Shutdown",   bg = "gray",width = 8, height = 2,font = self.helv02,command = self.Shutdown, wraplength=80, justify=CENTER)
            else:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "EXIT",   bg = "gray",width = 8, height = 2,font = self.helv02,command = self.Shutdown, wraplength=80, justify=CENTER)
            self.Button_Shutdown.grid(row = 9, column = 7, padx = 8)
            if self.shuffle_on == 0:
                self.Button_Shuffle = tk.Button(self.Frame10, text = "Shuffle", bg = "light blue",width = 8, height = 2,font = self.helv02,command = self.Shuffle_Tracks, wraplength=80, justify=CENTER)
            else:
                self.Button_Shuffle = tk.Button(self.Frame10, text = "Shuffled", bg = "orange",width = 8, height = 2,font = self.helv02,command = self.Shuffle_Tracks, wraplength=80, justify=CENTER)
            self.Button_Shuffle.grid(row = 7, column = 5, columnspan = 2)
            self.Button_AZ_artists = tk.Button(self.Frame10, text = "A-Z Sort",bg = "light blue", fg = "black",width = 8, height = 2,font = self.helv02,command = self.AZ_Tracks, wraplength=80, justify=CENTER)
            self.Button_AZ_artists.grid(row = 7, column = 3)
            self.Button_Sleep = tk.Button(self.Frame10, text = "SLEEP", bg = "light blue",width = 8, height = 2,font = self.helv02,command = self.sleep,repeatdelay=1000, repeatinterval=500)
            self.Button_Sleep.grid(row = 0, column = 4, padx = 0)
            if self.touchscreen == 1:
                self.Button_Track_m3u = tk.Button(self.Frame10, text = "ADD track   to .m3u", bg = "light green",width = 8, height = 2,font = self.helv03,command = self.Track_m3u, wraplength=80, justify=CENTER)
                self.Button_Track_m3u.grid(row = 8, column = 2)
                self.Button_Artist_m3u = tk.Button(self.Frame10, text = "ADD artist   to .m3u", bg = "light green",width = 8, height = 2,font = self.helv03,command = self.Artist_m3u, wraplength=80, justify=CENTER)
                self.Button_Artist_m3u.grid(row = 8, column = 5, columnspan = 2)
                self.Button_Album_m3u = tk.Button(self.Frame10, text = "ADD album   to .m3u", bg = "light green",width = 8, height = 2,font = self.helv03,command = self.Album_m3u, wraplength=80, justify=CENTER)
                self.Button_Album_m3u.grid(row = 8, column = 4)
                self.Button_PList_m3u = tk.Button(self.Frame10, text = "ADD P-list   to .m3u", bg = "light green",width = 8, height = 2,font = self.helv03,command = self.PList_m3u, wraplength=80, justify=CENTER)
                self.Button_PList_m3u.grid(row = 8, column = 7)
                self.Button_DELETE_m3u = tk.Button(self.Frame10, text = "DEL .m3u",width = 6, height = 1,font = self.helv02,command = self.DelPL_m3u)
                self.Button_DELETE_m3u.grid(row = 9, column = 3)
                self.Button_Search_to_m3u = tk.Button(self.Frame10, text = "Search to .m3u",    bg = "light green",width = 8, height = 2,font = self.helv03, wraplength=80,command = self.Search)
                self.Button_Search_to_m3u.grid(row = 9, column = 4, padx = 8)
                self.Button_Add_to_FAV = tk.Button(self.Frame10, text = "Add track to FAV .m3u  " ,width = 8, height = 2,font = self.helv03, bg = "light green",command = self.FAV_List, wraplength=80, justify=CENTER)
                self.Button_Add_to_FAV.grid(row = 9, column = 2)
            self.Button_repeat = tk.Button(self.Frame10, text = "Repeat", bg = "light blue",fg = "black",width = 8, height = 2,font = self.helv02,command = self.Repeat, wraplength=80, justify=CENTER)
            self.Button_repeat.grid(row = 7, column = 4)
            if self.BT == 1:
                self.Button_Pause.config(fg = "light gray",bg = "light gray")
                self.Button_Gapless.config(fg = "light gray",bg = "light gray")
    
            self.L1 = tk.Label(self.Frame10, text="Track:")
            self.L1.grid(row = 5, column = 2, sticky = W)
            self.L2 = tk.Label(self.Frame10, text="of")
            self.L2.grid(row = 5, column = 3, sticky = W, padx = 16)
            self.L3 = tk.Label(self.Frame10, text="Played:")
            self.L3.grid(row = 6, column = 2, sticky = W)
            self.L4 = tk.Label(self.Frame10,text="of")
            self.L4.grid(row = 6, column = 3, sticky = W, padx = 16)
            self.L5 = tk.Label(self.Frame10, text="Drive :")
            self.L5.grid(row = 5, column = 4, sticky = W,padx = 12)
            self.L6 = tk.Label(self.Frame10, text="Playlist :")
            self.L6.grid(row = 6, column = 4, sticky = W,padx = 12)
            if self.touchscreen == 1:
                self.L8 = tk.Label(self.Frame10, text=".m3u")
                self.L8.grid(row = 8, column = 3, sticky = S)
            self.L9 = tk.Label(self.Frame10, text=" ")
            self.L9.grid(row = 6, column = 6, sticky = E)
        
            self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=57,bg='white',   anchor="w", borderwidth=2, relief="groove")
            self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 6)
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=40,bg='white',font = self.helv01, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
            self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 6)
            self.Disp_album_name = tk.Label(self.Frame10, height=1, width=40,bg='white',font = self.helv01, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
            self.Disp_album_name.grid(row = 3, column = 1, columnspan = 6)
            self.Disp_track_name = tk.Label(self.Frame10, height=1, width=40,bg='white',font = self.helv01, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name.grid(row = 4, column = 1, columnspan = 6)
            self.Disp_track_no = tk.Label(self.Frame10, height=1, width = 5)
            self.Disp_track_no.grid(row = 5, column = 2, sticky = E)
            self.Disp_Total_tunes = tk.Label(self.Frame10, height=1, width = 5) 
            self.Disp_Total_tunes.grid(row = 5, column = 3, sticky = E)
            self.Disp_played = tk.Label(self.Frame10, height = 1, width = 5)
            self.Disp_played.grid(row = 6, column = 2, sticky = E)
            self.Disp_track_len = tk.Label(self.Frame10, height=1, width = 5)
            self.Disp_track_len.grid(row = 6, column = 3, sticky = E)
            self.Disp_Drive = tk.Label(self.Frame10, height=1, width=22)
            self.Disp_Drive.grid(row = 5, column = 4, columnspan = 3, sticky = E)
            self.Disp_Name_m3u = tk.Text(self.Frame10,height = 1, width=13)
            self.Disp_Name_m3u.grid(row = 8, column = 3, sticky = N, pady = 10)
            self.Disp_Total_Plist = tk.Label(self.Frame10, height=1, width=7)
            self.Disp_Total_Plist.grid(row = 6, column = 4, columnspan = 2, sticky = E, padx = 50)

        if self.cutdown == 1: # 320 x 240
            self.length = 25
            self.Button_Start = tk.Button(self.Frame10, text = "PLAY Playlist", bg =  'green',fg = "black",width = 4, height = 2, command = self.Play, wraplength=50, justify=CENTER)
            self.Button_Start.grid(row = 0, column = 0)
            self.Button_TAlbum = tk.Button(self.Frame10, text = "PLAY Album", bg = "blue",fg = "black", width = 4, height = 2,command=self.Play_Album, wraplength=50, justify=CENTER)
            self.Button_TAlbum.grid(row = 0, column = 1)
            self.Button_Sleep = tk.Button(self.Frame10, text = "SLEEP", bg = "light blue",width = 4, height = 2,command = self.sleep,repeatdelay=1000, repeatinterval=500)
            self.Button_Sleep.grid(row = 0, column = 4)
            self.Button_Vol_DN =  tk.Button(self.Frame10, text = " < Vol " + "...", wraplength=40,    bg = "light green",width = 4, height = 2,command = self.volume_DN,repeatdelay=1000, repeatinterval=500)
            self.Button_Vol_DN.grid(row = 0, column = 2)
            self.Button_Vol_UP =  tk.Button(self.Frame10, text = "Vol >   " + str(self.volume), wraplength=55,bg = "light green",width = 4, height = 2,command = self.volume_UP,repeatdelay=1000, repeatinterval=500)
            self.Button_Vol_UP.grid(row = 0, column = 3)
            self.Button_Prev_PList =  tk.Button(self.Frame10, text = "<P-list",   bg = "light blue",width = 4, height = 1,command = self.Prev_m3u,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_PList.grid(row = 1, column = 0)
            self.Button_Next_PList =  tk.Button(self.Frame10, text = "P-list>",   bg = "light blue",width = 4, height = 1,command = self.Next_m3u,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_PList.grid(row = 1, column = 4)
            self.Button_Prev_Artist =  tk.Button(self.Frame10, text = "<Artist",   bg = "light blue",width = 4, height = 1,command = self.Prev_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Artist.grid(row = 2, column = 0)
            self.Button_Next_Artist =  tk.Button(self.Frame10, text = "Artist>",   bg = "light blue",fg = "red",width = 4, height = 1,command = self.Next_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Artist.grid(row = 2, column = 4)
            self.Button_Prev_Album =  tk.Button(self.Frame10, text = "<Album",    bg = "light blue",width = 4, height = 1,command = self.Prev_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Album.grid(row = 3, column = 0)
            self.Button_Next_Album =  tk.Button(self.Frame10, text = "Album>",     bg = "light blue",width = 4, height = 1,command = self.Next_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Album.grid(row = 3, column = 4)
            self.Button_Prev_Track =  tk.Button(self.Frame10, text = "<Track",    bg = "light blue",width = 4, height = 1,command = self.Prev_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Track.grid(row = 4, column = 0)
            self.Button_Next_Track = tk.Button(self.Frame10, text = "Track>",    bg = "light blue",width = 4, height = 1,command = self.Next_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Track.grid(row =4, column = 4)
            self.Button_Next_AZ = tk.Button(self.Frame10, text = "NextAZ",   width = 4, height = 1,bg = "light blue",command=self.nextAZ,repeatdelay=250, repeatinterval=500)
            self.Button_Next_AZ.grid(row = 5, column = 4)
            self.Button_Reload = tk.Button(self.Frame10, text = "RELOAD",width = 4, height = 1, bg = "light blue",command = self.RELOAD_List, wraplength=80, justify=CENTER)
            self.Button_Reload.grid(row = 6, column = 0)
            if self.Button_Radi_on == 1:
                self.Button_Radio = tk.Button(self.Frame10, text = "Radio",    bg = "light blue",width = 4, height = 1,command = self.RadioX,repeatdelay=1000, repeatinterval=500)
                self.Button_Radio.grid(row = 6, column = 3)
            if self.Shutdown_exit == 1:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "Shutdn",   bg = "gray",width = 4, height = 1,command = self.Shutdown)
            else:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "EXIT",   bg = "gray",width = 4, height = 1,command = self.Shutdown)
            self.Button_Shutdown.grid(row = 6, column = 4)
            self.Button_Shuffle = tk.Button(self.Frame10, text = "Shuffle", bg = "light blue",width = 4, height = 1,command = self.Shuffle_Tracks, wraplength=80, justify=CENTER)
            self.Button_Shuffle.grid(row = 6, column = 1)
            self.Button_Pause = tk.Button(self.Frame10, text = "Pause",bg = "light blue", width = 4, height = 1,command=self.Pause, wraplength=80, justify=CENTER)
            self.Button_Pause.grid(row = 6, column = 2)
       
            self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
            self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
            self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
            self.Disp_track_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
            self.Disp_track_no = tk.Label(self.Frame10, height=1, width=5)
            self.Disp_track_no.grid(row = 5, column = 0,sticky = W)
            self.Disp_Total_tunes = tk.Label(self.Frame10, height=1, width=7) 
            self.Disp_Total_tunes.grid(row = 5, column = 1,sticky = W) 
            self.Disp_played = tk.Label(self.Frame10, height=1, width=5)
            self.Disp_played.grid(row = 5, column = 2, sticky = E)
            self.Disp_track_len = tk.Label(self.Frame10, height=1, width=5)
            self.Disp_track_len.grid(row = 5, column = 3, sticky = E)
            self.L2 = tk.Label(self.Frame10, text="of")
            self.L2.grid(row = 5, column = 0, sticky = E)
            self.L4 = tk.Label(self.Frame10,text="/")
            self.L4.grid(row = 5, column = 3, sticky = W,padx = 5)

        if self.cutdown == 2: # 640 x 480
            self.length = 30
            self.helv01 = tkFont.Font(family='Helvetica', size=10, weight='bold') # Names font size
            self.helv02 = tkFont.Font(family='Helvetica', size=11) # Buttons font size
            self.helv03 = tkFont.Font(family='Helvetica', size=8)  # other font size
            self.Button_Start = tk.Button(self.Frame10, text = "PLAY Playlist", bg = "green",fg = "black",width = 5, height = 2,font = self.helv02, command = self.Play, wraplength=80, justify=CENTER)
            self.Button_Start.grid(row = 0, column = 0, padx = 10,pady = 10)
            self.Button_Pause = tk.Button(self.Frame10, text = "Pause",bg = "light blue", width = 5, height = 2,font = self.helv02,command=self.Pause, wraplength=80, justify=CENTER)
            self.Button_Pause.grid(row = 0, column = 2, padx = 0,pady = 10)
            self.Button_Gapless = tk.Button(self.Frame10, text = "Gapped", fg = "black",bg = "light blue", width = 5, height = 2,font = self.helv02,command=self.Gapless, wraplength=80, justify=CENTER)
            self.Button_Gapless.grid(row = 0, column = 3,pady = 10)
            self.Button_TAlbum = tk.Button(self.Frame10, text = "PLAY Album", bg = "blue",fg = "black", width = 5, height = 2,font = self.helv02,command=self.Play_Album, wraplength=80, justify=CENTER)
            self.Button_TAlbum.grid(row = 0, column = 1,pady = 10)
            Button_Volume_Dn =  tk.Button(self.Frame10, text = " < Vol ",    bg = "light green",width = 5, height = 2,font = self.helv02,command = self.volume_DN,repeatdelay=1000, repeatinterval=500)
            Button_Volume_Dn.grid(row = 0, column = 5)
            if self.m == 0:
                self.Button_volume = tk.Button(self.Frame10, text = self.volume, fg = "black",width = 1, height = 2,font = self.helv02,command = self.Mute)
            else:
                self.Button_volume = tk.Button(self.Frame10, text = self.volume, fg = "green",width = 1, height = 2,font = self.helv02,command = self.Mute)
            self.Button_volume.grid(row = 0, column = 6)
            self.Button_Vol_UP =  tk.Button(self.Frame10, text = "Vol >",      bg = "light green",width = 5, height = 2,font = self.helv02,command = self.volume_UP,repeatdelay=1000, repeatinterval=500)
            self.Button_Vol_UP.grid(row = 0, column = 7)
            self.Button_Prev_PList =  tk.Button(self.Frame10, text = "< P-list",   bg = "light blue",width = 5, height = 1,font = self.helv02,command = self.Prev_m3u,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_PList.grid(row = 1, column = 0)
            self.Button_Next_PList =  tk.Button(self.Frame10, text = "P-list >",   bg = "light blue",width = 5, height = 1,font = self.helv02,command = self.Next_m3u,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_PList.grid(row = 1, column = 7)
            self.Button_Prev_Artist =  tk.Button(self.Frame10, text = "< Artist",   bg = "light blue",fg = "black",width = 5, height = 1,font = self.helv02,command = self.Prev_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Artist.grid(row = 2, column = 0)
            self.Button_Next_Artist =  tk.Button(self.Frame10, text = "Artist >",   bg = "light blue",width = 5, height = 1,font = self.helv02,command = self.Next_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Artist.grid(row = 2, column = 7)
            self.Button_Prev_Album =  tk.Button(self.Frame10, text = "< Album",    bg = "light blue",width = 5, height = 1,font = self.helv02,command = self.Prev_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Album.grid(row = 3, column = 0)
            self.Button_Next_Album =  tk.Button(self.Frame10, text = "Album >",     bg = "light blue",width = 5, height = 1,font = self.helv02,command = self.Next_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Album.grid(row = 3, column = 7)
            self.Button_Prev_Track =  tk.Button(self.Frame10, text = "< Track",    bg = "light blue",width = 5, height = 1,font = self.helv02,command = self.Prev_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Track.grid(row = 4, column = 0)
            self.Button_Next_Track = tk.Button(self.Frame10, text = "Track >",    bg = "light blue",width = 5, height = 1,font = self.helv02,command = self.Next_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Track.grid(row = 4, column = 7)
            self.Button_Bluetooth = tk.Button(self.Frame10, text = "Bluetooth",    bg = "light blue",width = 5, height = 1,command = self.Bluetooth)
            self.Button_Bluetooth.grid(row = 5, column = 7)
            if self.Button_Radi_on == 1:
                self.Button_Radio = tk.Button(self.Frame10, text = "Radio",    bg = "light blue",width = 5, height = 2,font = self.helv02,command = self.RadioX, wraplength=80, justify=CENTER)
                self.Button_Radio.grid(row = 9, column = 5, columnspan = 2)
                        
            self.Button_Next_AZ = tk.Button(self.Frame10, text = "Next A-Z",   width = 5, height = 2,font = self.helv02,bg = "light blue",command=self.nextAZ,repeatdelay=250, repeatinterval=500)
            self.Button_Next_AZ.grid(row = 7, column = 7)
            if os.path.exists(self.mp3c_jpg):
                self.load = Image.open(self.mp3c_jpg)
                self.load = self.load.resize((150, 150), Image.LANCZOS)
                self.renderc = ImageTk.PhotoImage(self.load)
                self.img = tk.Label(self.Frame10, image = self.renderc)
                self.img.grid(row = 5, column = 0, columnspan = 2, rowspan = 5, pady = 2)
            else:
                self.img = tk.Label(self.Frame10)
                self.img.grid(row = 5, column = 0, columnspan = 2, rowspan = 5, pady = 2)
            self.Button_Reload = tk.Button(self.Frame10, text = " RELOAD " + self.m3u_def ,width = 5, height = 2,font = self.helv03, bg = "light blue",command = self.RELOAD_List, wraplength=80, justify=CENTER)
            self.Button_Reload.grid(row = 7, column = 2,padx = 10)
            if self.Shutdown_exit == 1:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "Shutdown",   bg = "gray",width = 5, height = 2,font = self.helv02,command = self.Shutdown, wraplength=80, justify=CENTER)
            else:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "EXIT",   bg = "gray",width = 5, height = 2,font = self.helv02,command = self.Shutdown, wraplength=80, justify=CENTER)
            self.Button_Shutdown.grid(row = 9, column = 7, padx = 8)
            if self.shuffle_on == 0:
                self.Button_Shuffle = tk.Button(self.Frame10, text = "Shuffle", bg = "light blue",width = 5, height = 2,font = self.helv02,command = self.Shuffle_Tracks, wraplength=80, justify=CENTER)
            else:
                self.Button_Shuffle = tk.Button(self.Frame10, text = "Shuffled", bg = "orange",width = 5, height = 2,font = self.helv02,command = self.Shuffle_Tracks, wraplength=80, justify=CENTER)
            self.Button_Shuffle.grid(row = 7, column = 5, columnspan = 2)
            self.Button_AZ_artists = tk.Button(self.Frame10, text = "A-Z Sort",bg = "light blue", fg = "black",width = 5, height = 2,font = self.helv02,command = self.AZ_Tracks, wraplength=80, justify=CENTER)
            self.Button_AZ_artists.grid(row = 7, column = 3)
            self.Button_Sleep = tk.Button(self.Frame10, text = "SLEEP", bg = "light blue",width = 5, height = 2,font = self.helv02,command = self.sleep,repeatdelay=1000, repeatinterval=500)
            self.Button_Sleep.grid(row = 0, column = 4, padx = 0)
            if self.touchscreen == 1:
                self.Button_Track_m3u = tk.Button(self.Frame10, text = "ADD track to .m3u", bg = "light green",width = 6, height = 2,font = self.helv03,command = self.Track_m3u, wraplength=60, justify=CENTER)
                self.Button_Track_m3u.grid(row = 8, column = 2)
                self.Button_Artist_m3u = tk.Button(self.Frame10, text = "ADD artist to .m3u", bg = "light green",width = 6, height = 2,font = self.helv03,command = self.Artist_m3u, wraplength=60, justify=CENTER)
                self.Button_Artist_m3u.grid(row = 8, column = 5, columnspan = 2)
                self.Button_Album_m3u = tk.Button(self.Frame10, text = "ADD album to .m3u", bg = "light green",width = 6, height = 2,font = self.helv03,command = self.Album_m3u, wraplength=60, justify=CENTER)
                self.Button_Album_m3u.grid(row = 8, column = 4)
                self.Button_PList_m3u = tk.Button(self.Frame10, text = "ADD P-list to .m3u", bg = "light green",width = 6, height = 2,font = self.helv03,command = self.PList_m3u, wraplength=60, justify=CENTER)
                self.Button_PList_m3u.grid(row = 8, column = 7)
                self.Button_DELETE_m3u = tk.Button(self.Frame10, text = "DEL .m3u",width = 5, height = 1,font = self.helv03,command = self.DelPL_m3u)
                self.Button_DELETE_m3u.grid(row = 9, column = 3)
                self.Button_Search_to_m3u = tk.Button(self.Frame10, text = "Search to .m3u",    bg = "light green",width = 6, height = 2,font = self.helv03, wraplength=60,command = self.Search)
                self.Button_Search_to_m3u.grid(row = 9, column = 4, padx = 8)
                self.Button_Add_to_FAV = tk.Button(self.Frame10, text = "Add track to FAV .m3u  " ,width = 6, height = 2,font = self.helv03, bg = "light green",command = self.FAV_List, wraplength=60, justify=CENTER)
                self.Button_Add_to_FAV.grid(row = 9, column = 2)
            self.Button_repeat = tk.Button(self.Frame10, text = "Repeat", bg = "light blue",fg = "black",width = 5, height = 2,font = self.helv02,command = self.Repeat, wraplength=80, justify=CENTER)
            self.Button_repeat.grid(row = 7, column = 4)
            if self.BT == 1:
                self.Button_Pause.config(fg = "light gray",bg = "light gray")
                self.Button_Gapless.config(fg = "light gray",bg = "light gray")
    
            self.L1 = tk.Label(self.Frame10, text="Track:",font = self.helv03)
            self.L1.grid(row = 5, column = 2, sticky = W)
            self.L2 = tk.Label(self.Frame10, text="of",font = self.helv03)
            self.L2.grid(row = 5, column = 3, sticky = W, padx = 16)
            self.L3 = tk.Label(self.Frame10, text="Played:",font = self.helv03)
            self.L3.grid(row = 6, column = 2, sticky = W)
            self.L4 = tk.Label(self.Frame10,text="of",font = self.helv03)
            self.L4.grid(row = 6, column = 3, sticky = W, padx = 16)
            self.L5 = tk.Label(self.Frame10, text="Drive :",font = self.helv03)
            self.L5.grid(row = 5, column = 4, sticky = W,padx = 12)
            self.L6 = tk.Label(self.Frame10, text="Playlist :",font = self.helv03)
            self.L6.grid(row = 6, column = 4, sticky = W,padx = 12)
            if self.touchscreen == 1:
                self.L8 = tk.Label(self.Frame10, text=".m3u",font = self.helv03)
                self.L8.grid(row = 8, column = 3, sticky = S)
            self.L9 = tk.Label(self.Frame10, text=" ",font = self.helv03)
            self.L9.grid(row = 6, column = 6, sticky = E)
        
            self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=40,bg='white',   anchor="w", borderwidth=2, relief="groove")
            self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 6)
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=50,bg='white',font = self.helv01, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
            self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 6)
            self.Disp_album_name = tk.Label(self.Frame10, height=1, width=50,bg='white',font = self.helv01, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
            self.Disp_album_name.grid(row = 3, column = 1, columnspan = 6)
            self.Disp_track_name = tk.Label(self.Frame10, height=1, width=50,bg='white',font = self.helv01, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name.grid(row = 4, column = 1, columnspan = 6)
            self.Disp_track_no = tk.Label(self.Frame10, height=1, width = 5,font = self.helv03)
            self.Disp_track_no.grid(row = 5, column = 2, sticky = E)
            self.Disp_Total_tunes = tk.Label(self.Frame10, height=1, width = 5,font = self.helv03) 
            self.Disp_Total_tunes.grid(row = 5, column = 3, sticky = E)
            self.Disp_played = tk.Label(self.Frame10, height = 1, width = 5,font = self.helv03)
            self.Disp_played.grid(row = 6, column = 2, sticky = E)
            self.Disp_track_len = tk.Label(self.Frame10, height=1, width = 5,font = self.helv03)
            self.Disp_track_len.grid(row = 6, column = 3, sticky = E)
            self.Disp_Drive = tk.Label(self.Frame10, height=1, width=22,font = self.helv03)
            self.Disp_Drive.grid(row = 5, column = 4, columnspan = 3, sticky = E)
            self.Disp_Name_m3u = tk.Text(self.Frame10,height = 1, width=13,font = self.helv03)
            self.Disp_Name_m3u.grid(row = 8, column = 3, sticky = N, pady = 5)
            self.Disp_Total_Plist = tk.Label(self.Frame10, height=1, width=7,font = self.helv03)
            self.Disp_Total_Plist.grid(row = 6, column = 4, columnspan = 2, sticky = E, padx = 50)
            
        if self.cutdown == 3: # 480 x 800
            self.length = 35
            self.Button_Start = tk.Button(self.Frame10, text = "PLAY Playlist", bg = "green",fg = "black",width = 7, height = 2, command = self.Play, wraplength=50, justify=CENTER)
            self.Button_Start.grid(row = 0, column = 0)
            if self.Button_Radi_on == 1:
                self.Button_Radio = tk.Button(self.Frame10, text = "Radio",    bg = "light blue",width = 7, height = 2,command = self.RadioX, wraplength=80, justify=CENTER)
                self.Button_Radio.grid(row = 15, column = 3)
            self.Button_TAlbum = tk.Button(self.Frame10, text = "PLAY Album", bg = "blue",fg = "black", width = 7, height = 2,command=self.Play_Album, wraplength=50, justify=CENTER)
            self.Button_TAlbum.grid(row = 0, column = 2,pady = 0)
            self.Button_Pause = tk.Button(self.Frame10, text = "Pause",bg = "light blue",fg = "blue", width = 7, height = 2,command=self.Pause, wraplength=80, justify=CENTER)
            self.Button_Pause.grid(row = 6, column = 2)
            self.Button_Gapless = tk.Button(self.Frame10, text = "Gapped", fg = "black", width = 7, height = 2,command=self.Gapless, wraplength=80, justify=CENTER)
            self.Button_Gapless.grid(row = 15, column = 2)
            self.Button_Vol_DN =  tk.Button(self.Frame10, text = " < Vol " + "...", wraplength=40,    bg = "light green",width = 7, height = 2,command = self.volume_DN,repeatdelay=1000, repeatinterval=500)
            self.Button_Vol_DN.grid(row = 0, column = 3)
            self.Button_Vol_UP =  tk.Button(self.Frame10, text = "Vol > " + str(self.volume), wraplength=55,bg = "light green",width = 7, height = 2,command = self.volume_UP,repeatdelay=1000, repeatinterval=500)
            self.Button_Vol_UP.grid(row = 0, column = 4)
            self.Button_Prev_PList =  tk.Button(self.Frame10, text = "<P-list",   bg = "light blue",width = 5, height = 2,command = self.Prev_m3u,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_PList.grid(row = 1, column = 0)
            self.Button_Next_PList =  tk.Button(self.Frame10, text = "P-list>",   bg = "light blue",width = 5, height = 2,command = self.Next_m3u,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_PList.grid(row = 1, column = 4)
            self.Button_Prev_Artist =  tk.Button(self.Frame10, text = "<Artist",   bg = "light blue",width = 5, height = 2,command = self.Prev_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Artist.grid(row = 2, column = 0)
            self.Button_Next_Artist =  tk.Button(self.Frame10, text = "Artist>",   bg = "light blue",fg = "red",width = 5, height = 2,command = self.Next_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Artist.grid(row = 2, column = 4)
            self.Button_Prev_Album =  tk.Button(self.Frame10, text = "<Album",    bg = "light blue",width = 5, height = 2,command = self.Prev_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Album.grid(row = 3, column = 0)
            self.Button_Next_Album =  tk.Button(self.Frame10, text = "Album>",     bg = "light blue",width = 5, height = 2,command = self.Next_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Album.grid(row = 3, column = 4)
            self.Button_Prev_Track =  tk.Button(self.Frame10, text = "<Track",    bg = "light blue",width = 5, height = 2,command = self.Prev_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Track.grid(row = 4, column = 0)
            self.Button_Next_Track = tk.Button(self.Frame10, text = "Track>",    bg = "light blue",width = 5, height = 2,command = self.Next_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Track.grid(row =4, column = 4)
            self.Button_Next_AZ = tk.Button(self.Frame10, text = "NextAZ",   width = 5, height = 2,bg = "light blue",command=self.nextAZ,repeatdelay=250, repeatinterval=500)
            self.Button_Next_AZ.grid(row = 5, column = 4, pady = 0)
            self.Button_Reload = tk.Button(self.Frame10, text = "RELOAD",width = 6, height = 2, bg = "light blue",command = self.RELOAD_List, wraplength=80, justify=CENTER)
            self.Button_Reload.grid(row = 6, column = 0)
            if self.Shutdown_exit == 1:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "Shutdown",   bg = "gray",width = 5, height = 2,command = self.Shutdown)
            else:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "EXIT",   bg = "gray",width = 5, height = 2,command = self.Shutdown)
            self.Button_Shutdown.grid(row = 15, column = 4)
            self.Button_Shuffle = tk.Button(self.Frame10, text = "Shuffle", bg = "light blue",width = 6, height = 2,command = self.Shuffle_Tracks, wraplength=80, justify=CENTER)
            self.Button_Shuffle.grid(row = 6, column = 3)
            if os.path.exists(self.mp3c_jpg):
                self.load = Image.open(self.mp3c_jpg)
                self.renderc = ImageTk.PhotoImage(self.load)
                self.img = tk.Label(self.Frame10, image = self.renderc)
                self.img.grid(row = 8, column = 0, columnspan = 3, rowspan = 5, pady = 2)
            else:
                self.img = tk.Label(self.Frame10)
                self.img.grid(row = 5, column = 0, columnspan = 2, rowspan = 5, pady = 2)
            self.Button_AZ_artists = tk.Button(self.Frame10, text = "A-Z Sort",bg = "light blue", fg = "black",width = 5, height = 2,command = self.AZ_Tracks, wraplength=80, justify=CENTER)
            self.Button_AZ_artists.grid(row = 6, column = 4)
            self.Button_Sleep = tk.Button(self.Frame10, text = "SLEEP", bg = "light blue",width = 5, height = 2,command = self.sleep,repeatdelay=1000, repeatinterval=500)
            self.Button_Sleep.grid(row = 15, column = 0)
            self.Button_repeat = tk.Button(self.Frame10, text = "Repeat", bg = "light blue",fg = "black",width = 6, height = 2,command = self.Repeat, wraplength=80, justify=CENTER)
            self.Button_repeat.grid(row = 6, column = 1)
            self.Button_Track_m3u = tk.Button(self.Frame10, text = "ADD track   to .m3u", bg = "light green",width = 7, height = 2,command = self.Track_m3u, wraplength=80, justify=CENTER)
            self.Button_Track_m3u.grid(row = 13, column = 0)
            self.Button_Artist_m3u = tk.Button(self.Frame10, text = "ADD artist   to .m3u", bg = "light green",width = 7, height = 2,command = self.Artist_m3u, wraplength=80, justify=CENTER)
            self.Button_Artist_m3u.grid(row = 13, column = 1)
            self.Button_Album_m3u = tk.Button(self.Frame10, text = "ADD album   to .m3u", bg = "light green",width = 7, height = 2,command = self.Album_m3u, wraplength=80, justify=CENTER)
            self.Button_Album_m3u.grid(row = 13, column = 2)
            self.Button_PList_m3u = tk.Button(self.Frame10, text = "ADD P-list   to .m3u", bg = "light green",width = 7, height = 2,command = self.PList_m3u, wraplength=80, justify=CENTER)
            self.Button_PList_m3u.grid(row = 13, column = 3)
            self.Button_DELETE_m3u = tk.Button(self.Frame10, text = "DEL .m3u", bg = "light grey",width = 7, height = 1,command = self.DelPL_m3u)
            self.Button_DELETE_m3u.grid(row = 14, column = 0)
            self.Button_Add_to_FAV = tk.Button(self.Frame10, text = "Add track to FAV .m3u  " ,width = 7, height = 2, bg = "light green",command = self.FAV_List, wraplength=80, justify=CENTER)
            self.Button_Add_to_FAV.grid(row =13, column = 4)

            self.L2 = tk.Label(self.Frame10, text="of")
            self.L2.grid(row = 5, column = 1, sticky = W)
            self.L4 = tk.Label(self.Frame10,text="of")
            self.L4.grid(row = 5, column = 3, sticky = W)
            self.L5 = tk.Label(self.Frame10, text="DR:")
            self.L5.grid(row = 8, column = 2, sticky = E)
            self.L6 = tk.Label(self.Frame10, text="Playlist :")
            self.L6.grid(row = 7, column = 3, sticky = E)
            if self.touchscreen == 1:
                self.L8 = tk.Label(self.Frame10, text=".m3u")
                self.L8.grid(row = 14, column = 2, sticky = W)
        
            self.Disp_plist_name = tk.Label(self.Frame10, height=2, width=32,bg='white',   anchor="w", borderwidth=2, relief="groove")
            self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=32,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
            self.Disp_album_name = tk.Label(self.Frame10, height=2, width=32,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
            self.Disp_track_name = tk.Label(self.Frame10, height=2, width=32,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
            self.Disp_track_no = tk.Label(self.Frame10, height=1, width=5,bg='white', borderwidth=2, relief="groove")
            self.Disp_track_no.grid(row = 5, column = 0)
            self.Disp_Total_tunes = tk.Label(self.Frame10, height=1, width=5,bg='white', borderwidth=2, relief="groove")
            self.Disp_Total_tunes.grid(row = 5, column = 1)
            self.Disp_played = tk.Label(self.Frame10, height=1, width=5,bg='white', borderwidth=2, relief="groove")
            self.Disp_played.grid(row = 5, column = 2)
            self.Disp_track_len = tk.Label(self.Frame10, height=1, width=5,bg='white' ,borderwidth=2, relief="groove")
            self.Disp_track_len.grid(row = 5, column = 3)
            self.Disp_Name_m3u = tk.Text(self.Frame10,height = 1, width=12,bg= 'white', borderwidth=2, relief="groove")
            self.Disp_Name_m3u.grid(row = 14, column = 1,sticky = N,pady = 10)
            self.Disp_Total_Plist = tk.Label(self.Frame10, height=1, width=7,bg='white',font = 40, borderwidth=2, relief="groove")
            self.Disp_Total_Plist.grid(row = 7, column = 4, columnspan = 2, sticky = W)
            self.Disp_Drive = tk.Label(self.Frame10, height=1, width=17,bg= 'white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_Drive.grid(row = 8, column = 3, columnspan = 3, sticky = E, padx = 15)

        if self.cutdown == 4: # 480 x 320
            self.length = 36
            self.Button_Start = tk.Button(self.Frame10, text = "PLAY Playlist", bg = "green",fg = "black",width = 6, height = 3, command = self.Play, wraplength=50, justify=CENTER)
            self.Button_Start.grid(row = 0, column = 0)
            self.Button_TAlbum = tk.Button(self.Frame10, text = "PLAY Album", bg = "blue",fg = "black", width = 6, height = 3,command=self.Play_Album, wraplength=50, justify=CENTER)
            self.Button_TAlbum.grid(row = 0, column = 1,pady = 0)
            self.Button_Gapless = tk.Button(self.Frame10, text = "Gapped", fg = "black",bg = "light blue", width = 6, height = 3,command=self.Gapless, wraplength=80, justify=CENTER)
            self.Button_Gapless.grid(row = 0, column = 2)
            self.Button_Vol_DN =  tk.Button(self.Frame10, text = " < Vol " + "...", wraplength=40,    bg = "light green",width = 6, height = 3,command = self.volume_DN,repeatdelay=1000, repeatinterval=500)
            self.Button_Vol_DN.grid(row = 0, column = 3)
            self.Button_Vol_UP =  tk.Button(self.Frame10, text = "Vol > " + str(self.volume), wraplength=55,bg = "light green",width = 6, height = 3,command = self.volume_UP,repeatdelay=1000, repeatinterval=500)
            self.Button_Vol_UP.grid(row = 0, column = 4)
            self.Button_Prev_PList =  tk.Button(self.Frame10, text = "<P-list",   bg = "light blue",width = 6, height = 1,command = self.Prev_m3u,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_PList.grid(row = 1, column = 0)
            self.Button_Next_PList =  tk.Button(self.Frame10, text = "P-list>",   bg = "light blue",width = 6, height = 1,command = self.Next_m3u,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_PList.grid(row = 1, column = 4)
            self.Button_Prev_Artist =  tk.Button(self.Frame10, text = "<Artist",   bg = "light blue",width = 6, height = 2,command = self.Prev_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Artist.grid(row = 2, column = 0)
            self.Button_Next_Artist =  tk.Button(self.Frame10, text = "Artist>",   bg = "light blue",fg = "red",width = 6, height = 2,command = self.Next_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Artist.grid(row = 2, column = 4)
            self.Button_Prev_Album =  tk.Button(self.Frame10, text = "<Album",    bg = "light blue",width = 6, height = 2,command = self.Prev_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Album.grid(row = 3, column = 0)
            self.Button_Next_Album =  tk.Button(self.Frame10, text = "Album>",     bg = "light blue",width = 6, height = 2,command = self.Next_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Album.grid(row = 3, column = 4)
            self.Button_Prev_Track =  tk.Button(self.Frame10, text = "<Track",    bg = "light blue",width = 6, height = 2,command = self.Prev_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Track.grid(row = 4, column = 0)
            self.Button_Next_Track = tk.Button(self.Frame10, text = "Track>",    bg = "light blue",width = 6, height = 2,command = self.Next_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Track.grid(row =4, column = 4)
            self.Button_Next_AZ = tk.Button(self.Frame10, text = "NextAZ",   width = 5, height = 2,bg = "light blue",command=self.nextAZ,repeatdelay=250, repeatinterval=500)
            self.Button_Next_AZ.grid(row = 6, column = 3, pady = 0)
            self.Button_Reload = tk.Button(self.Frame10, text = "RELOAD",width = 6, height = 2, bg = "light blue",command = self.RELOAD_List, wraplength=80, justify=CENTER)
            self.Button_Reload.grid(row = 6, column = 0)
            if self.Shutdown_exit == 1:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "Shutdown",   bg = "gray",width = 5, height = 2,command = self.Shutdown)
            else:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "EXIT",   bg = "gray",width = 5, height = 2,command = self.Shutdown)
            self.Button_Shutdown.grid(row = 6, column = 5)
            self.Button_Shuffle = tk.Button(self.Frame10, text = "Shuffle", bg = "light blue",width = 6, height = 2,command = self.Shuffle_Tracks, wraplength=80, justify=CENTER)
            self.Button_Shuffle.grid(row = 6, column = 1)
            self.Button_Pause = tk.Button(self.Frame10, text = "Pause",bg = "light blue", width = 6, height = 2,command=self.Pause, wraplength=80, justify=CENTER)
            self.Button_Pause.grid(row = 6, column = 2)

            self.L2 = tk.Label(self.Frame10, text="of")
            self.L2.grid(row = 5, column = 1, sticky = W)
            self.L4 = tk.Label(self.Frame10,text="of")
            self.L4.grid(row = 5, column = 2, sticky = E)
            self.L9 = tk.Label(self.Frame10, text=" ")
            self.L9.grid(row = 5, column = 3, sticky = E)
        
            self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
            self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
            self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
            self.Disp_track_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
            self.Disp_track_no = tk.Label(self.Frame10, height=1, width=5)
            self.Disp_track_no.grid(row = 5, column = 0, sticky = E)
            self.Disp_Total_tunes = tk.Label(self.Frame10, height=1, width=5)
            self.Disp_Total_tunes.grid(row = 5, column = 1)
            self.Disp_played = tk.Label(self.Frame10, height=1, width=5)
            self.Disp_played.grid(row = 5, column = 2)
            self.Disp_track_len = tk.Label(self.Frame10, height=1, width=5)
            self.Disp_track_len.grid(row = 5, column = 3, sticky = W, padx = 5)
            self.Disp_Name_m3u = tk.Text(self.Frame10,height = 1, width=8,bg= 'light gray')
            self.Disp_Name_m3u.grid(row = 5, column = 5)

            self.Button_PList_m3u = tk.Button(self.Frame10, text = "P-list   to .m3u", bg = "light green",width = 5, height = 1,command = self.PList_m3u, wraplength=80, justify=CENTER)
            self.Button_PList_m3u.grid(row = 1, column = 5)
            self.Button_Track_m3u = tk.Button(self.Frame10, text = "track   to .m3u", bg = "light green",width = 5, height = 2,command = self.Track_m3u, wraplength=80, justify=CENTER)
            self.Button_Track_m3u.grid(row = 4, column = 5)
            self.Button_Artist_m3u = tk.Button(self.Frame10, text = "artist   to .m3u", bg = "light green",width = 5, height = 2,command = self.Artist_m3u, wraplength=80, justify=CENTER)
            self.Button_Artist_m3u.grid(row = 2, column = 5)
            self.Button_Album_m3u = tk.Button(self.Frame10, text = "album   to .m3u", bg = "light green",width = 5, height = 2,command = self.Album_m3u, wraplength=80, justify=CENTER)
            self.Button_Album_m3u.grid(row = 3, column = 5)
            if self.Button_Radi_on == 1:
                self.Button_Radio = tk.Button(self.Frame10, text = "Radio",    bg = "light blue",width = 5, height = 2,command = self.RadioX, wraplength=60, justify=CENTER)
                self.Button_Radio.grid(row = 6, column = 4)
            self.Button_Sleep = tk.Button(self.Frame10, text = "SLEEP", bg = "light blue",width = 5, height = 3,command = self.sleep,repeatdelay=1000, repeatinterval=500)
            self.Button_Sleep.grid(row = 0, column = 5)

        if self.cutdown == 5: # Pi 7" Display 800 x 480 (Simple layout)
            self.length = 25
            self.helv01 = tkFont.Font(family='Helvetica', size=25, weight='bold')
            self.helv02 = tkFont.Font(family='Helvetica', size=13, weight='bold')
            self.Button_Start = tk.Button(self.Frame10, text = "PLAY Playlist", font = self.helv01,bg = "green",fg = "black",width = 7, height = 2, command = self.Play, wraplength=120, justify=CENTER)
            self.Button_Start.grid(row = 0, column = 0)
            self.Button_TAlbum = tk.Button(self.Frame10, text = "PLAY Album", font = self.helv01, bg = "blue",fg = "black", width = 7, height = 2,command=self.Play_Album, wraplength=120, justify=CENTER)
            self.Button_TAlbum.grid(row = 0, column = 1,pady = 0)
            self.Button_Sleep = tk.Button(self.Frame10, text = "SLEEP", font = self.helv01, bg = "light blue",width = 7, height = 2,command = self.sleep,repeatdelay=1000, repeatinterval=500)
            self.Button_Sleep.grid(row = 6, column = 1)
            self.Button_Vol_DN =  tk.Button(self.Frame10, text = " < Vol ", wraplength=100,    bg = "light green", font = self.helv01,width = 6, height = 2,command = self.volume_DN,repeatdelay=1000, repeatinterval=500)
            self.Button_Vol_DN.grid(row = 0, column = 3)
            self.Button_Vol_UP =  tk.Button(self.Frame10, text = "Vol > " + str(self.volume), wraplength=120,bg = "light green", font = self.helv01,width = 7, height = 2,command = self.volume_UP,repeatdelay=1000, repeatinterval=500)
            self.Button_Vol_UP.grid(row = 0, column = 4)
            self.Button_Prev_Artist =  tk.Button(self.Frame10, text = "<Artist", font = self.helv01,   bg = "light blue",width = 7, height = 2,command = self.Prev_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Artist.grid(row = 2, column = 0)
            self.Button_Next_Artist =  tk.Button(self.Frame10, text = "Artist>", font = self.helv01,   bg = "light blue",fg = "red",width = 7, height = 2,command = self.Next_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Artist.grid(row = 2, column = 4)
            self.Button_Prev_Album =  tk.Button(self.Frame10, text = "<Album", font = self.helv01,    bg = "light blue",width = 7, height = 2,command = self.Prev_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Album.grid(row = 3, column = 0)
            self.Button_Next_Album =  tk.Button(self.Frame10, text = "Album>", font = self.helv01,     bg = "light blue",width = 7, height = 2,command = self.Next_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Album.grid(row = 3, column = 4)
            self.Button_Prev_Track =  tk.Button(self.Frame10, text = "<Track", font = self.helv01,    bg = "light blue",width = 7, height = 2,command = self.Prev_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Track.grid(row = 4, column = 0)
            self.Button_Next_Track = tk.Button(self.Frame10, text = "Track>", font = self.helv01,    bg = "light blue",width = 7, height = 2,command = self.Next_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Track.grid(row =4, column = 4)
            self.Button_Next_AZ = tk.Button(self.Frame10, text = "NextAZ", font = self.helv01,   width = 6, height = 1,bg = "light blue",command=self.nextAZ,repeatdelay=250, repeatinterval=500)
            self.Button_Next_AZ.grid(row = 5, column = 4, pady = 0)
            self.Button_Reload = tk.Button(self.Frame10, text = "RELOAD", font = self.helv01,width = 7, bg = "light blue", height = 2,command = self.RELOAD_List, wraplength=160, justify=CENTER)
            self.Button_Reload.grid(row = 6, column = 0)
            if self.Button_Radi_on == 1:
                self.Button_Radio = tk.Button(self.Frame10, text = "Radio",    bg = "light blue", font = self.helv01,width = 6, height = 2,command = self.RadioX, wraplength=160, justify=CENTER)
                self.Button_Radio.grid(row = 6, column = 3)
            if self.Shutdown_exit == 1:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "Shutdn",   bg = "gray",font = self.helv02,width = 7, height = 2,command = self.Shutdown)
            else:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "EXIT",   bg = "gray",font = self.helv02,width = 7, height = 2,command = self.Shutdown)
            self.Button_Shutdown.grid(row = 6, column = 4)
            self.Button_Shuffle = tk.Button(self.Frame10, text = "Shuffle", font = self.helv01, bg = "light blue",width = 7, height = 2,command = self.Shuffle_Tracks, wraplength=160, justify=CENTER)
            self.Button_Shuffle.grid(row = 0, column = 2)
            self.Button_Pause = tk.Button(self.Frame10, text = "Pause", font = self.helv01,bg = "light blue", width = 7, height = 2,command=self.Pause, wraplength=160, justify=CENTER)
            self.Button_Pause.grid(row = 6, column = 2)
        
            self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
            self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
            self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
            self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
            self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
            self.Disp_track_no = tk.Label(self.Frame10, height=2, width=5,font = self.helv02)
            self.Disp_track_no.grid(row = 5, column = 0, sticky = E)
            self.Disp_Total_tunes = tk.Label(self.Frame10, height=2, width=5,font = self.helv02) 
            self.Disp_Total_tunes.grid(row = 5, column = 1, sticky = W,padx = 30) 
            self.Disp_played = tk.Label(self.Frame10, height=2, width=6,font = self.helv02)
            self.Disp_played.grid(row = 5, column = 2,sticky = E)
            self.Disp_track_len = tk.Label(self.Frame10, height=2, width=6,font = self.helv02)
            self.Disp_track_len.grid(row = 5, column = 3)
            self.L1 = tk.Label(self.Frame10, text="Track:",font = self.helv02)
            self.L1.grid(row = 5, column = 0, sticky = W, padx = 20)
            self.L2 = tk.Label(self.Frame10, text="of",font = self.helv02)
            self.L2.grid(row = 5, column = 1, sticky = W)
            self.L3 = tk.Label(self.Frame10, text="Played:",font = self.helv02)
            self.L3.grid(row = 5, column = 2, sticky = W, padx = 10)
            self.L4 = tk.Label(self.Frame10,text="of",font = self.helv02)
            self.L4.grid(row = 5, column = 3, sticky = W, padx = 20)

        if self.cutdown == 6: # Pi 7" Display 800 x 480 (Album Layout)
            self.length = 60
            self.Button_Start = tk.Button(self.Frame10, text = "PLAY Playlist", font = 50,bg = "green",fg = "black",width = 15, height = 2, command = self.Play, wraplength=60, justify=CENTER)
            self.Button_Start.grid(row = 0, column = 0)
            self.Button_TAlbum = tk.Button(self.Frame10, text = "PLAY Album", font = 50, bg = "blue",fg = "black", width = 15, height = 2,command=self.Play_Album, wraplength=60, justify=CENTER)
            self.Button_TAlbum.grid(row = 0, column = 1,pady = 0)
            self.Button_Sleep = tk.Button(self.Frame10, text = "SLEEP", font = 50, bg = "light blue",width = 15, height = 2,command = self.sleep,repeatdelay=1000, repeatinterval=500)
            self.Button_Sleep.grid(row = 19, column = 1)
            self.Button_Vol_DN =  tk.Button(self.Frame10, text = " < Vol ", wraplength=50,    bg = "light green", font = 50,width = 15, height = 2,command = self.volume_DN,repeatdelay=1000, repeatinterval=500)
            self.Button_Vol_DN.grid(row = 0, column = 3)
            self.Button_Vol_UP =  tk.Button(self.Frame10, text = "Vol > " + str(self.volume), wraplength=60,bg = "light green", font = 50,width = 15, height = 2,command = self.volume_UP,repeatdelay=1000, repeatinterval=500)
            self.Button_Vol_UP.grid(row = 0, column = 4)
            self.Button_Prev_Artist =  tk.Button(self.Frame10, text = "<Artist", font = 50,   bg = "light blue",width = 15, height = 1,command = self.Prev_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Artist.grid(row = 2, column = 0)
            self.Button_Next_Artist =  tk.Button(self.Frame10, text = "Artist>", font = 50,   bg = "light blue",fg = "red",width = 15, height = 1,command = self.Next_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Artist.grid(row = 2, column = 1)
            self.Button_Prev_Album =  tk.Button(self.Frame10, text = "<Album", font = 50,    bg = "light blue",width = 15, height = 1,command = self.Prev_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Album.grid(row = 3, column = 0)
            self.Button_Next_Album =  tk.Button(self.Frame10, text = "Album>", font = 50,     bg = "light blue",width = 15, height = 1,command = self.Next_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Album.grid(row = 3, column = 1)
            self.Button_Prev_Track =  tk.Button(self.Frame10, text = "<Track", font = 50,    bg = "light blue",width = 15, height = 1,command = self.Prev_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Track.grid(row = 4, column = 0)
            self.Button_Next_Track = tk.Button(self.Frame10, text = "Track>", font = 50,    bg = "light blue",width = 15, height = 1,command = self.Next_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Track.grid(row =4, column = 1)
            self.Button_Next_AZ = tk.Button(self.Frame10, text = "Info", font = 50,   width = 10, height = 1,bg = "light blue",command=self.PopupInfo,repeatdelay=250, repeatinterval=500)
            self.Button_Next_AZ.grid(row = 18, column = 4, pady = 0)
            self.Button_Reload = tk.Button(self.Frame10, text = "RELOAD", font = 50,width = 10, bg = "light blue", height = 2,command = self.RELOAD_List, wraplength=80, justify=CENTER)
            self.Button_Reload.grid(row = 19, column = 0)
            if self.Button_Radi_on == 1:
                self.Button_Radio = tk.Button(self.Frame10, text = "Radio", font = 50,    bg = "light blue",width = 15, height = 2,command = self.RadioX, wraplength=80, justify=CENTER)
                self.Button_Radio.grid(row = 19, column = 3)
            if self.Shutdown_exit == 1:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "Shutdn",   bg = "gray",width = 15, height = 2,command = self.Shutdown)
            else:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "EXIT",   bg = "gray",width = 15, height = 2,command = self.Shutdown)
            self.Button_Shutdown.grid(row = 19, column = 4)
            self.Button_Shuffle = tk.Button(self.Frame10, text = "Shuffle", font = 50, bg = "light blue",width = 15, height = 2,command = self.Shuffle_Tracks, wraplength=80, justify=CENTER)
            self.Button_Shuffle.grid(row = 0, column = 2)
            if self.auto_play == 0 and self.auto_radio == 0 and self.auto_record == 0 and self.auto_album == 0:
                self.Button_Pause = tk.Button(self.Frame10, text = "NextAZ", font = 50,bg = "light blue", width = 15, height = 2,command=self.Pause, wraplength=80, justify=CENTER)
            else:
                self.Button_Pause = tk.Button(self.Frame10, text = "Pause", font = 50,bg = "light blue", width = 15, height = 2,command=self.Pause, wraplength=80, justify=CENTER)
            self.Button_Pause.grid(row = 19, column = 2)
            if os.path.exists(self.mp3c_jpg):
                self.load = Image.open(self.mp3c_jpg)
                self.renderc = ImageTk.PhotoImage(self.load)
                self.img = tk.Label(self.Frame10, image = self.renderc)
                self.img.grid(row = 5, column = 0, columnspan = 2, rowspan = 9)
            else:
                self.img = tk.Label(self.Frame10)
                self.img.grid(row = 5, column = 0, columnspan = 2, rowspan = 9)
        
            self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=47,bg='white',font = 50, anchor="w", borderwidth=2, relief="groove")
            self.Disp_artist_name.grid(row = 2, column = 2,columnspan = 3)
            self.Disp_album_name = tk.Label(self.Frame10, height=1, width=47,bg='white',font = 50, anchor="w", borderwidth=2, relief="groove")
            self.Disp_album_name.grid(row = 3, column = 2, columnspan = 3)
            self.Disp_track_name = tk.Label(self.Frame10, height=1, width=47,bg='white',font = 50, anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name.grid(row = 4, column = 2, columnspan = 3)
            self.Disp_track_name1 = tk.Label(self.Frame10, height=1, width=52,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name1.grid(row = 5, column = 2, columnspan = 3)
            self.Disp_track_name2 = tk.Label(self.Frame10, height=1, width=52,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name2.grid(row = 6, column = 2, columnspan = 3)
            self.Disp_track_name3 = tk.Label(self.Frame10, height=1, width=52,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name3.grid(row = 7, column = 2, columnspan = 3)
            self.Disp_track_name4 = tk.Label(self.Frame10, height=1, width=52,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name4.grid(row = 8, column = 2, columnspan = 3)
            self.Disp_track_name5 = tk.Label(self.Frame10, height=1, width=52,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name5.grid(row = 9, column = 2, columnspan = 3)
            self.Disp_track_name6 = tk.Label(self.Frame10, height=1, width=52,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name6.grid(row = 10, column = 2, columnspan = 3)
            self.Disp_track_name7 = tk.Label(self.Frame10, height=1, width=52,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name7.grid(row = 11, column = 2, columnspan = 3)
            self.Disp_track_name8 = tk.Label(self.Frame10, height=1, width=52,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name8.grid(row = 12, column = 2, columnspan = 3)
            self.Disp_track_name9 = tk.Label(self.Frame10, height=1, width=52,bg='white', anchor="w", borderwidth=2, relief="groove")
            self.Disp_track_name9.grid(row = 13, column = 2, columnspan = 3)
            self.Disp_track_no = tk.Label(self.Frame10, height=2, width=5,font = 50)
            self.Disp_track_no.grid(row = 18, column = 0, sticky = E)
            self.Disp_Total_tunes = tk.Label(self.Frame10, height=2, width=10,font = 50) 
            self.Disp_Total_tunes.grid(row = 18, column = 1, sticky = W,padx = 30) 
            self.Disp_played = tk.Label(self.Frame10, height=2, width=5,font = 50)
            self.Disp_played.grid(row = 18, column = 2, sticky = E)
            self.Disp_track_len = tk.Label(self.Frame10, height=2, width=5,font = 50)
            self.Disp_track_len.grid(row = 18, column = 3,padx = 20) 
            self.L1 = tk.Label(self.Frame10, text="Track:",font = 50)
            self.L1.grid(row = 18, column = 0, sticky = W, padx = 20)
            self.L2 = tk.Label(self.Frame10, text="of",font = 50)
            self.L2.grid(row = 18, column = 1, sticky = W)
            self.L3 = tk.Label(self.Frame10, text="Played:",font = 50)
            self.L3.grid(row = 18, column = 2, sticky = W)
            self.L4 = tk.Label(self.Frame10,text="of",font = 50)
            self.L4.grid(row = 18, column = 3, sticky = W, padx = 20)


        if self.cutdown == 7: # Pi 7" Display 800 x 480 with scrollbars
            self.length = 40
            if scr_width == 800 and scr_height == 600:
                hei = 3
                hei2 = 3
            else:
                hei = 1
                hei2 = 2
            Artist_variable = ""
            self.Artist_options = [""]
            self.Artist_variable = StringVar(self.Frame10)
            self.Disp_artist_name = ttk.Combobox(self.Frame10, textvariable=Artist_variable, values=self.Artist_options)
            self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 6)
            self.Disp_artist_name.bind("<<ComboboxSelected>>",self.artist_callback2)
            self.Disp_artist_name.configure(width=40, font="Verdana 16")
            Album_variable = ""
            self.Album_options = [""]
            self.Album_variable = StringVar(self.Frame10)
            self.Disp_album_name = ttk.Combobox(self.Frame10, textvariable=Album_variable, values=self.Album_options)
            self.Disp_album_name.grid(row = 3, column = 1, columnspan = 6)
            self.Disp_album_name.bind("<<ComboboxSelected>>",self.album_callback2)
            self.Disp_album_name.configure(width=40, font="Verdana 16")
            Track_variable = ""
            self.Track_options = [""]
            self.Track_variable = StringVar(self.Frame10)
            self.Disp_track_name = ttk.Combobox(self.Frame10, textvariable=Track_variable, values=self.Track_options)
            self.Disp_track_name.grid(row = 4, column = 1,columnspan = 6)
            self.Disp_track_name.bind("<<ComboboxSelected>>",self.callback2)
            self.Disp_track_name.configure(width=40, font="Verdana 16")
            self.Button_Start = tk.Button(self.Frame10, text = "PLAY Playlist", bg = "green",fg = "black",width = 7, height = hei2,font = 18, command = self.Play, wraplength=80, justify=CENTER)
            self.Button_Start.grid(row = 0, column = 0, padx = 10,pady = 10)
            self.Button_Pause = tk.Button(self.Frame10, text = "Pause",bg = "light blue", width = 7, height = hei2,command=self.Pause, wraplength=80, justify=CENTER)
            self.Button_Pause.grid(row = 0, column = 2, padx = 0,pady = 10)
            self.Button_Gapless = tk.Button(self.Frame10, text = "Gapped", fg = "black",bg = "light blue", width = 7, height = hei2,command=self.Gapless, wraplength=80, justify=CENTER)
            self.Button_Gapless.grid(row = 0, column = 3,pady = 10)
            self.Button_TAlbum = tk.Button(self.Frame10, text = "PLAY Album", bg = "blue",fg = "black", width = 7, height = hei2,font = 18,command=self.Play_Album, wraplength=80, justify=CENTER)
            self.Button_TAlbum.grid(row = 0, column = 1,pady = 10)
            Button_Volume_Dn =  tk.Button(self.Frame10, text = " < Vol ",    bg = "light green",width = 7, height = hei2,command = self.volume_DN,repeatdelay=1000, repeatinterval=500)
            Button_Volume_Dn.grid(row = 0, column = 5)
            if self.m == 0:
                self.Button_volume = tk.Button(self.Frame10, text = self.volume, fg = "black",width = 4, height = hei2,command = self.Mute)
            else:
                self.Button_volume = tk.Button(self.Frame10, text = self.volume, fg = "green",width = 4, height = hei2,command = self.Mute)
            self.Button_volume.grid(row = 0, column = 6)
            self.Button_Vol_UP =  tk.Button(self.Frame10, text = "Vol >",      bg = "light green",width = 7, height = hei2,command = self.volume_UP,repeatdelay=1000, repeatinterval=500)
            self.Button_Vol_UP.grid(row = 0, column = 7)
            self.Button_Prev_PList =  tk.Button(self.Frame10, text = "< P-list",   bg = "light blue",width = 7, height = hei,command = self.Prev_m3u,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_PList.grid(row = 1, column = 0)
            self.Button_Next_PList =  tk.Button(self.Frame10, text = "P-list >",   bg = "light blue",width = 7, height = hei,command = self.Next_m3u,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_PList.grid(row = 1, column = 7)
            self.Button_Prev_Artist =  tk.Button(self.Frame10, text = "< Artist",   bg = "light blue",width = 7, height = hei2,command = self.Prev_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Artist.grid(row = 2, column = 0)
            self.Button_Next_Artist =  tk.Button(self.Frame10, text = "Artist >",   bg = "light blue",fg = "red",width = 7, height = hei2,command = self.Next_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Artist.grid(row = 2, column = 7)
            self.Button_Prev_Album =  tk.Button(self.Frame10, text = "< Album",    bg = "light blue",width = 7, height = hei2,command = self.Prev_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Album.grid(row = 3, column = 0)
            self.Button_Next_Album =  tk.Button(self.Frame10, text = "Album >",     bg = "light blue",width = 7, height = hei2,command = self.Next_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Album.grid(row = 3, column = 7)
            self.Button_Prev_Track =  tk.Button(self.Frame10, text = "< Track",    bg = "light blue",width = 7, height = 2,command = self.Prev_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Track.grid(row = 4, column = 0)
            self.Button_Next_Track = tk.Button(self.Frame10, text = "Track >",    bg = "light blue",width = 7, height = 2,command = self.Next_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Track.grid(row = 4, column = 7)
            self.Button_Bluetooth = tk.Button(self.Frame10, text = "Bluetooth",    bg = "light blue",width = 6, height = 1,command = self.Bluetooth)
            self.Button_Bluetooth.grid(row = 5, column = 7)
            if self.Button_Radi_on == 1:
                self.Button_Radio = tk.Button(self.Frame10, text = "Radio",    bg = "light blue",width = 7, height = 2,command = self.RadioX, wraplength=80, justify=CENTER)
                self.Button_Radio.grid(row = 9, column = 5, columnspan = 2)
            if self.touchscreen == 1:
                self.Button_Search_to_m3u = tk.Button(self.Frame10, text = "Search to .m3u",    bg = "light green",width = 7, height = 2, wraplength=80,command = self.Search)
                self.Button_Search_to_m3u.grid(row = 9, column = 4, padx = 8)
            
            self.Button_Next_AZ = tk.Button(self.Frame10, text = "Next A-Z",   width = 7, height = 2,bg = "light blue",command=self.nextAZ,repeatdelay=250, repeatinterval=500)
            self.Button_Next_AZ.grid(row = 7, column = 7)
            if os.path.exists(self.mp3c_jpg):
                self.load = Image.open(self.mp3c_jpg)
                self.renderc = ImageTk.PhotoImage(self.load)
                self.img = tk.Label(self.Frame10, image = self.renderc)
                self.img.grid(row = 5, column = 0, columnspan = 2, rowspan = 5, pady = 2)
            else:
                self.img = tk.Label(self.Frame10)
                self.img.grid(row = 5, column = 0, columnspan = 2, rowspan = 5, pady = 2)
            self.Button_Reload = tk.Button(self.Frame10, text = " RELOAD " + self.m3u_def ,width = 7, height = 2, bg = "light blue",command = self.RELOAD_List, wraplength=80, justify=CENTER)
            self.Button_Reload.grid(row = 7, column = 2,padx = 10, pady = 0)
            if self.Shutdown_exit == 1:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "Shutdown",   bg = "gray",width = 7, height = 2,command = self.Shutdown, wraplength=80, justify=CENTER)
            else:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "EXIT",   bg = "gray",width = 7, height = 2,command = self.Shutdown, wraplength=80, justify=CENTER)
            self.Button_Shutdown.grid(row = 9, column = 7, padx = 8)
            if self.shuffle_on == 0:
                self.Button_Shuffle = tk.Button(self.Frame10, text = "Shuffle", bg = "light blue",width = 7, height = 2,command = self.Shuffle_Tracks, wraplength=80, justify=CENTER)
            else:
                self.Button_Shuffle = tk.Button(self.Frame10, text = "Shuffled", bg = "orange",width = 7, height = 2,command = self.Shuffle_Tracks, wraplength=80, justify=CENTER)
            self.Button_Shuffle.grid(row = 7, column = 5, columnspan = 2)
            self.Button_AZ_artists = tk.Button(self.Frame10, text = "A-Z Sort",bg = "light blue", fg = "black",width = 7, height = 2,command = self.AZ_Tracks, wraplength=80, justify=CENTER)
            self.Button_AZ_artists.grid(row = 7, column = 3)
            self.Button_Sleep = tk.Button(self.Frame10, text = "SLEEP", bg = "light blue",width = 7, height = hei2,command = self.sleep,repeatdelay=1000, repeatinterval=500)
            self.Button_Sleep.grid(row = 0, column = 4, padx = 0)
            if self.touchscreen == 1:
                self.Button_Add_to_FAV = tk.Button(self.Frame10, text = "Add track to FAV .m3u  " ,width = 7, height = 2, bg = "light green",command = self.FAV_List, wraplength=80, justify=CENTER)
                self.Button_Add_to_FAV.grid(row = 9, column = 2)
                self.Button_Track_m3u = tk.Button(self.Frame10, text = "ADD track   to .m3u", bg = "light green",width = 7, height = 2,command = self.Track_m3u, wraplength=80, justify=CENTER)
                self.Button_Track_m3u.grid(row = 8, column = 2)
                self.Button_Artist_m3u = tk.Button(self.Frame10, text = "ADD artist   to .m3u", bg = "light green",width = 7, height = 2,command = self.Artist_m3u, wraplength=80, justify=CENTER)
                self.Button_Artist_m3u.grid(row = 8, column = 5, columnspan = 2)
                self.Button_Album_m3u = tk.Button(self.Frame10, text = "ADD album   to .m3u", bg = "light green",width = 7, height = 2,command = self.Album_m3u, wraplength=80, justify=CENTER)
                self.Button_Album_m3u.grid(row = 8, column = 4)
                self.Button_PList_m3u = tk.Button(self.Frame10, text = "ADD P-list   to .m3u", bg = "light green",width = 7, height = 2,command = self.PList_m3u, wraplength=80, justify=CENTER)
                self.Button_PList_m3u.grid(row = 8, column = 7)
                self.Button_DELETE_m3u = tk.Button(self.Frame10, text = "DEL .m3u",width = 6, height = 1,command = self.DelPL_m3u)
                self.Button_DELETE_m3u.grid(row = 9, column = 3)
            self.Button_repeat = tk.Button(self.Frame10, text = "Repeat", bg = "light blue",fg = "black",width = 7, height = 2,command = self.Repeat, wraplength=80, justify=CENTER)
            self.Button_repeat.grid(row = 7, column = 4)
            if self.BT == 1:
                self.Button_Pause.config(fg = "light gray",bg = "light gray")
                self.Button_Gapless.config(fg = "light gray",bg = "light gray")
    
            self.L1 = tk.Label(self.Frame10, text="Track:")
            self.L1.grid(row = 5, column = 2, sticky = W)
            self.L2 = tk.Label(self.Frame10, text="of")
            self.L2.grid(row = 5, column = 3, sticky = W, padx = 16)
            self.L3 = tk.Label(self.Frame10, text="Played:")
            self.L3.grid(row = 6, column = 2, sticky = W)
            self.L4 = tk.Label(self.Frame10,text="of")
            self.L4.grid(row = 6, column = 3, sticky = W, padx = 16)
            self.L5 = tk.Label(self.Frame10, text="Drive :")
            self.L5.grid(row = 5, column = 4, sticky = W,padx = 12)
            self.L6 = tk.Label(self.Frame10, text="Playlist :")
            self.L6.grid(row = 6, column = 4, sticky = W,padx = 12)
            if self.touchscreen == 1:
                self.L8 = tk.Label(self.Frame10, text=".m3u")
                self.L8.grid(row = 8, column = 3, sticky = S)
            self.L9 = tk.Label(self.Frame10, text=" ")
            self.L9.grid(row = 6, column = 6, sticky = E)
        
            self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=57,bg='white',   anchor="w", borderwidth=2, relief="groove")
            self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 6)
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_track_no = tk.Label(self.Frame10, height=1, width=5)
            self.Disp_track_no.grid(row = 5, column = 2, sticky = E)
            self.Disp_Total_tunes = tk.Label(self.Frame10, height=1, width=5) 
            self.Disp_Total_tunes.grid(row = 5, column = 3, sticky = E)
            self.Disp_played = tk.Label(self.Frame10, height=1, width=5)
            self.Disp_played.grid(row = 6, column = 2, sticky = E)
            self.Disp_track_len = tk.Label(self.Frame10, height=1, width=5)
            self.Disp_track_len.grid(row = 6, column = 3, sticky = E)
            self.Disp_Drive = tk.Label(self.Frame10, height=1, width=21)
            self.Disp_Drive.grid(row = 5, column = 4, columnspan = 3, sticky = E)
            self.Disp_Name_m3u = tk.Text(self.Frame10,height = 1, width=13)
            self.Disp_Name_m3u.grid(row = 8, column = 3, sticky = N, pady = 10)
            self.Disp_Total_Plist = tk.Label(self.Frame10, height=1, width=7)
            self.Disp_Total_Plist.grid(row = 6, column = 4, columnspan = 2, sticky = E, padx = 50)

        if self.cutdown == 8: # Pi 7" v2 Display 1280 x 720 with scrollbars
            self.length = 40
            if scr_width == 800 and scr_height == 600:
                hei = 3
                hei2 = 3
            else:
                hei = 2
                hei2 = 3
            Artist_variable = ""
            self.Artist_options = [""]
            self.Artist_variable = StringVar(self.Frame10)
            self.Disp_artist_name = ttk.Combobox(self.Frame10, textvariable=Artist_variable, values=self.Artist_options)
            self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 6)
            self.Disp_artist_name.bind("<<ComboboxSelected>>",self.artist_callback2)
            self.Disp_artist_name.configure(width=40, font="Verdana 26")
            Album_variable = ""
            self.Album_options = [""]
            self.Album_variable = StringVar(self.Frame10)
            self.Disp_album_name = ttk.Combobox(self.Frame10, textvariable=Album_variable, values=self.Album_options)
            self.Disp_album_name.grid(row = 3, column = 1, columnspan = 6)
            self.Disp_album_name.bind("<<ComboboxSelected>>",self.album_callback2)
            self.Disp_album_name.configure(width=40, font="Verdana 26")
            Track_variable = ""
            self.Track_options = [""]
            self.Track_variable = StringVar(self.Frame10)
            self.Disp_track_name = ttk.Combobox(self.Frame10, textvariable=Track_variable, values=self.Track_options)
            self.Disp_track_name.grid(row = 4, column = 1,columnspan = 6)
            self.Disp_track_name.bind("<<ComboboxSelected>>",self.callback2)
            self.Disp_track_name.configure(width=40, font="Verdana 26")
            self.Button_Start = tk.Button(self.Frame10, text = "PLAY Playlist", bg = "green",fg = "black",width = 15, height = hei2,font = 18, command = self.Play, wraplength=80, justify=CENTER)
            self.Button_Start.grid(row = 0, column = 0, padx = 10,pady = 10)
            self.Button_Pause = tk.Button(self.Frame10, text = "Pause",bg = "light blue", width = 15, height = hei2,command=self.Pause, wraplength=80, justify=CENTER)
            self.Button_Pause.grid(row = 0, column = 2, padx = 0,pady = 10)
            self.Button_Gapless = tk.Button(self.Frame10, text = "Gapped", fg = "black",bg = "light blue", width = 15, height = hei2,command=self.Gapless, wraplength=80, justify=CENTER)
            self.Button_Gapless.grid(row = 0, column = 3,pady = 10)
            self.Button_TAlbum = tk.Button(self.Frame10, text = "PLAY Album", bg = "blue",fg = "black", width = 15, height = hei2,font = 18,command=self.Play_Album, wraplength=80, justify=CENTER)
            self.Button_TAlbum.grid(row = 0, column = 1,pady = 10)
            Button_Volume_Dn =  tk.Button(self.Frame10, text = " < Vol ",    bg = "light green",width = 12, height = hei2,command = self.volume_DN,repeatdelay=1000, repeatinterval=500)
            Button_Volume_Dn.grid(row = 0, column = 5)
            if self.m == 0:
                self.Button_volume = tk.Button(self.Frame10, text = self.volume, fg = "black",width = 4, height = hei2,command = self.Mute)
            else:
                self.Button_volume = tk.Button(self.Frame10, text = self.volume, fg = "green",width = 4, height = hei2,command = self.Mute)
            self.Button_volume.grid(row = 0, column = 6)
            self.Button_Vol_UP =  tk.Button(self.Frame10, text = "Vol >",      bg = "light green",width = 12, height = hei2,command = self.volume_UP,repeatdelay=1000, repeatinterval=500)
            self.Button_Vol_UP.grid(row = 0, column = 7)
            self.Button_Prev_PList =  tk.Button(self.Frame10, text = "< P-list",   bg = "light blue",width = 15, height = hei2,command = self.Prev_m3u,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_PList.grid(row = 1, column = 0)
            self.Button_Next_PList =  tk.Button(self.Frame10, text = "P-list >",   bg = "light blue",width = 15, height = hei2,command = self.Next_m3u,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_PList.grid(row = 1, column = 7)
            self.Button_Prev_Artist =  tk.Button(self.Frame10, text = "< Artist",   bg = "light blue",width = 15, height = hei2,command = self.Prev_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Artist.grid(row = 2, column = 0)
            self.Button_Next_Artist =  tk.Button(self.Frame10, text = "Artist >",   bg = "light blue",fg = "red",width = 15, height = hei2,command = self.Next_Artist,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Artist.grid(row = 2, column = 7)
            self.Button_Prev_Album =  tk.Button(self.Frame10, text = "< Album",    bg = "light blue",width = 15, height = hei2,command = self.Prev_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Album.grid(row = 3, column = 0)
            self.Button_Next_Album =  tk.Button(self.Frame10, text = "Album >",     bg = "light blue",width = 15, height = hei2,command = self.Next_Album,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Album.grid(row = 3, column = 7)
            self.Button_Prev_Track =  tk.Button(self.Frame10, text = "< Track",    bg = "light blue",width = 15, height = hei2,command = self.Prev_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Prev_Track.grid(row = 4, column = 0)
            self.Button_Next_Track = tk.Button(self.Frame10, text = "Track >",    bg = "light blue",width = 15, height = hei2,command = self.Next_Track,repeatdelay=1000, repeatinterval=500)
            self.Button_Next_Track.grid(row = 4, column = 7)
            self.Button_Bluetooth = tk.Button(self.Frame10, text = "Bluetooth",    bg = "light blue",width = 6, height = 1,command = self.Bluetooth)
            self.Button_Bluetooth.grid(row = 5, column = 7)
            if self.Button_Radi_on == 1:
                self.Button_Radio = tk.Button(self.Frame10, text = "Radio",    bg = "light blue",width = 15, height = 3,command = self.RadioX, wraplength=80, justify=CENTER)
                self.Button_Radio.grid(row = 9, column = 5, columnspan = 2)
            if self.touchscreen == 1:
                self.Button_Search_to_m3u = tk.Button(self.Frame10, text = "Search to .m3u",    bg = "light green",width = 7, height = 3, wraplength=80,command = self.Search)
                self.Button_Search_to_m3u.grid(row = 9, column = 4, padx = 8)
            
            self.Button_Next_AZ = tk.Button(self.Frame10, text = "Next A-Z",   width = 15, height = 3,bg = "light blue",command=self.nextAZ,repeatdelay=250, repeatinterval=500)
            self.Button_Next_AZ.grid(row = 7, column = 7)
            if os.path.exists(self.mp3c_jpg):
                self.load = Image.open(self.mp3c_jpg)
                self.load = self.load.resize((320, 320), Image.LANCZOS)
                self.renderc = ImageTk.PhotoImage(self.load)
                self.img = tk.Label(self.Frame10, image = self.renderc)
                self.img.grid(row = 5, column = 0, columnspan = 2, rowspan = 5, pady = 2)
            else:
                self.img = tk.Label(self.Frame10)
                self.img.grid(row = 5, column = 0, columnspan = 2, rowspan = 5, pady = 2)
            self.Button_Reload = tk.Button(self.Frame10, text = " RELOAD " + self.m3u_def ,width = 15, height = 3, bg = "light blue",command = self.RELOAD_List, wraplength=80, justify=CENTER)
            self.Button_Reload.grid(row = 7, column = 2,padx = 10, pady = 0)
            if self.Shutdown_exit == 1:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "Shutdown",   bg = "gray",width = 15, height = 3,command = self.Shutdown, wraplength=80, justify=CENTER)
            else:
                self.Button_Shutdown = tk.Button(self.Frame10, text = "EXIT",   bg = "gray",width = 15, height = 3,command = self.Shutdown, wraplength=80, justify=CENTER)
            self.Button_Shutdown.grid(row = 9, column = 7, padx = 8)
            if self.shuffle_on == 0:
                self.Button_Shuffle = tk.Button(self.Frame10, text = "Shuffle", bg = "light blue",width = 15, height = 3,command = self.Shuffle_Tracks, wraplength=80, justify=CENTER)
            else:
                self.Button_Shuffle = tk.Button(self.Frame10, text = "Shuffled", bg = "orange",width = 15, height = 3,command = self.Shuffle_Tracks, wraplength=80, justify=CENTER)
            self.Button_Shuffle.grid(row = 7, column = 5, columnspan = 2)
            self.Button_AZ_artists = tk.Button(self.Frame10, text = "A-Z Sort",bg = "light blue", fg = "black",width = 15, height = 3,command = self.AZ_Tracks, wraplength=80, justify=CENTER)
            self.Button_AZ_artists.grid(row = 7, column = 3)
            self.Button_Sleep = tk.Button(self.Frame10, text = "SLEEP", bg = "light blue",width = 15, height = hei2,command = self.sleep,repeatdelay=1000, repeatinterval=500)
            self.Button_Sleep.grid(row = 0, column = 4, padx = 0)
            if self.touchscreen == 1:
                self.Button_Add_to_FAV = tk.Button(self.Frame10, text = "Add track to FAV .m3u  " ,width = 7, height = 3, bg = "light green",command = self.FAV_List, wraplength=80, justify=CENTER)
                self.Button_Add_to_FAV.grid(row = 9, column = 2)
                self.Button_Track_m3u = tk.Button(self.Frame10, text = "ADD track   to .m3u", bg = "light green",width = 7, height = 3,command = self.Track_m3u, wraplength=80, justify=CENTER)
                self.Button_Track_m3u.grid(row = 8, column = 2)
                self.Button_Artist_m3u = tk.Button(self.Frame10, text = "ADD artist   to .m3u", bg = "light green",width = 7, height = 3,command = self.Artist_m3u, wraplength=80, justify=CENTER)
                self.Button_Artist_m3u.grid(row = 8, column = 5, columnspan = 2)
                self.Button_Album_m3u = tk.Button(self.Frame10, text = "ADD album   to .m3u", bg = "light green",width = 7, height = 3,command = self.Album_m3u, wraplength=80, justify=CENTER)
                self.Button_Album_m3u.grid(row = 8, column = 4)
                self.Button_PList_m3u = tk.Button(self.Frame10, text = "ADD P-list   to .m3u", bg = "light green",width = 7, height = 3,command = self.PList_m3u, wraplength=80, justify=CENTER)
                self.Button_PList_m3u.grid(row = 8, column = 7)
                self.Button_DELETE_m3u = tk.Button(self.Frame10, text = "DEL .m3u",width = 6, height = 1,command = self.DelPL_m3u)
                self.Button_DELETE_m3u.grid(row = 9, column = 3)
            self.Button_repeat = tk.Button(self.Frame10, text = "Repeat", bg = "light blue",fg = "black",width = 15, height = 3,command = self.Repeat, wraplength=80, justify=CENTER)
            self.Button_repeat.grid(row = 7, column = 4)
            if self.BT == 1:
                self.Button_Pause.config(fg = "light gray",bg = "light gray")
                self.Button_Gapless.config(fg = "light gray",bg = "light gray")
    
            self.L1 = tk.Label(self.Frame10, text="Track:")
            self.L1.grid(row = 5, column = 2, sticky = W)
            self.L2 = tk.Label(self.Frame10, text="of")
            self.L2.grid(row = 5, column = 3, sticky = W, padx = 16)
            self.L3 = tk.Label(self.Frame10, text="Played:")
            self.L3.grid(row = 6, column = 2, sticky = W)
            self.L4 = tk.Label(self.Frame10,text="of")
            self.L4.grid(row = 6, column = 3, sticky = W, padx = 16)
            self.L5 = tk.Label(self.Frame10, text="Drive :")
            self.L5.grid(row = 5, column = 4, sticky = W,padx = 12)
            self.L6 = tk.Label(self.Frame10, text="Playlist :")
            self.L6.grid(row = 6, column = 4, sticky = W,padx = 12)
            if self.touchscreen == 1:
                self.L8 = tk.Label(self.Frame10, text=".m3u")
                self.L8.grid(row = 8, column = 3, sticky = S)
            self.L9 = tk.Label(self.Frame10, text=" ")
            self.L9.grid(row = 6, column = 6, sticky = E)
        
            self.Disp_plist_name = tk.Label(self.Frame10, height=2, width=57,bg='white',   anchor="w", borderwidth=2, relief="groove")
            self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 6)
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_track_no = tk.Label(self.Frame10, height=1, width=5)
            self.Disp_track_no.grid(row = 5, column = 2, sticky = E)
            self.Disp_Total_tunes = tk.Label(self.Frame10, height=1, width=5) 
            self.Disp_Total_tunes.grid(row = 5, column = 3, sticky = E)
            self.Disp_played = tk.Label(self.Frame10, height=1, width=5)
            self.Disp_played.grid(row = 6, column = 2, sticky = E)
            self.Disp_track_len = tk.Label(self.Frame10, height=1, width=5)
            self.Disp_track_len.grid(row = 6, column = 3, sticky = E)
            self.Disp_Drive = tk.Label(self.Frame10, height=1, width=21)
            self.Disp_Drive.grid(row = 5, column = 4, columnspan = 3, sticky = E)
            self.Disp_Name_m3u = tk.Text(self.Frame10,height = 1, width=13)
            self.Disp_Name_m3u.grid(row = 8, column = 3, sticky = N, pady = 10)
            self.Disp_Total_Plist = tk.Label(self.Frame10, height=1, width=7)
            self.Disp_Total_Plist.grid(row = 6, column = 4, columnspan = 2, sticky = E, padx = 50)
            
        self.Button_Shutdown.bind("<Button-1>", left_click)
        self.Button_Shutdown.bind("<Button-3>", right_click)
        
        if self.cutdown != 1  and self.cutdown != 5 and self.cutdown != 6 and self.model != 0:                
            self.s = ttk.Style()
            self.s.theme_use('default')
            self.s.layout("LabeledProgressbar",[('LabeledProgressbar.trough',
               {'children': [('LabeledProgressbar.pbar',{'side': 'left', 'sticky': 'ns'}),("LabeledProgressbar.label",{"sticky": ""})],'sticky': 'nswe'})])
            self.s.configure("LabeledProgressbar", text="0 %      ", background='red')
            if self.cutdown == 0 or self.cutdown >= 7:
                self.progress=ttk.Progressbar(self.Frame10,style="LabeledProgressbar",orient=HORIZONTAL,length=90,mode='determinate')
                self.progress.grid(row = 6, column = 7)
            elif self.cutdown == 2:
                self.progress=ttk.Progressbar(self.Frame10,style="LabeledProgressbar",orient=HORIZONTAL,length=80,mode='determinate')
                self.progress.grid(row = 6, column = 6)
            elif self.cutdown == 3:
                self.progress=ttk.Progressbar(self.Frame10,style="LabeledProgressbar",orient=HORIZONTAL,length=70,mode='determinate')
                self.progress.grid(row = 7, column = 0)
            elif self.cutdown == 4:
                self.progress=ttk.Progressbar(self.Frame10,style="LabeledProgressbar",orient=HORIZONTAL,length=77,mode='determinate')
                self.progress.grid(row = 5, column = 4)
        
        if os.path.exists(self.mp3_jpg) and (self.cutdown != 1 or self.cutdown != 4):
            self.load = Image.open(self.mp3_jpg)
            if self.cutdown == 2:
                self.load = self.load.resize((150, 150), Image.LANCZOS)
            elif self.cutdown == 8:
                self.load = self.load.resize((320,320), Image.LANCZOS)
            else:
                self.load = self.load.resize((218, 218), Image.LANCZOS)
            self.render = ImageTk.PhotoImage(self.load)
            
        # start check wheel and buttons                       
        self.Check_Wheel()
        self.Check_buttons()
        
        # check default .m3u exists, if not then make it
        if not os.path.exists(self.que_dir):
            self.track_no = 0
            self.RELOAD_List()
        else:
            # if it does exist then load default m3u
            Tracks = []
            with open(self.que_dir,"r") as textobj:
               line = textobj.readline()
               while line:
                  Tracks.append(line.strip())
                  line = textobj.readline()
            self.tunes = []
            for counter in range (0,len(Tracks)):
                counter2 = Tracks[counter].count('/')
                if counter2 == 6:
                    self.genre_name = "None"
                    z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                    self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)
                    if self.cutdown >= 7:
                        self.Artist_options.append(self.artist_name)
                elif counter2 == 7:
                    z,self.drive_name1,self.drive_name2,self.drive_name,self.genre_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                    self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)
                    if self.cutdown >= 7:
                        self.Artist_options.append(self.artist_name)
                elif counter2 == 5:
                    self.genre_name = "None"
                    self.drive_name1,self.drive_name2,self.drive_name,self.artist_name3,self.album_name3,self.track_name  = Tracks[counter].split('/')
                    if self.album_name3.count(" - ") == 1:
                        self.artist_name,self.album_name = self.album_name3.split(" - ")
                        self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.artist_name3 + "*^" + self.drive_name2 + "^" + self.drive_name + "^" + self.genre_name)
                        if self.cutdown >= 7:
                            self.Artist_options.append(self.artist_name)
            self.tunes.sort()
            if self.cutdown >= 7:
                self.Artist_options.sort()
                self.Artist_options = list(dict.fromkeys(self.Artist_options))
                self.Disp_artist_name["values"] = self.Artist_options
            if  self.shuffle_on == 1:
                shuffle(self.tunes)
                if self.rotary_pos== 0:
                    self.Button_Shuffle.config(bg = "orange",fg = "black",text = "Shuffled")
                else:
                    self.Button_Shuffle.config(bg = "orange",fg = "black",text = "Shuffled")
                
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.total = 0
            if self.track_no > len(self.tunes) - 1:
                self.track_no = 0

        # auto play/radio/play album    
        if self.auto_album == 1:
            self.Play_Album()
        elif self.auto_radio == 1:
            self.RadioX()
        elif self.auto_radio == 0 and self.auto_play == 1:
            self.Play()
        else:
            self.Time_Left_Play()
            
        # start Rotary
        if self.rotary_vol == 1:
            self.Read_Rotary_VOL()
        if self.rotary_pos == 1:
            self.Read_Rotary_POS()
        if self.rotary_pos == 1 and self.rot_mode == 0:
            if self.rot_posp == 3:
                self.Button_Start.config(bg = 'yellow')
            elif self.rot_posp == 4:
                self.Button_TAlbum.config(bg = 'yellow')

    def Read_Rotary_VOL(self):
        if self.old_rotor1 != self.rotor1.value:
            self.light_on = time.monotonic()
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 100")
            if self.rotor1.value > self.old_rotor1:
                self.old_rotor1 = self.rotor1.value
                self.volume +=2
            else:
                self.old_rotor1 = self.rotor1.value
                self.volume -=2
            self.volume = max(self.volume,0)
            self.volume = min(self.volume,100)
            self.f_volume = self.volume
            self.m.setvolume(self.volume)
            os.system("amixer -D pulse sset Master " + str(self.volume) + "%")
            if self.mixername == "DSP Program":
                os.system("amixer set 'Digital' " + str(self.volume + 107))
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2:
                self.Button_volume.config(text = self.volume)
            else:
                self.Button_Vol_UP.config(text = "Vol >   " + str(self.volume))
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            #time.sleep(.2)
        self.after(250, self.Read_Rotary_VOL)

    def Read_Rotary_POS(self):
        if self.old_rotor2 != self.rotor2.value:
            self.light_on = time.monotonic()
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 100")
            if self.rotor2.value > self.old_rotor2:
                self.old_rotor2 = self.rotor2.value
                if self.rot_mode == 0:
                    self.rot_posp -=1
                    #print(self.rot_posp)
                    if self.rot_posp < 0:
                        self.rot_posp = 16
                    if self.cutdown > 4 and self.cutdown < 7 and self.rot_posp > 11:
                        self.rot_posp = 11
                    elif self.cutdown == 1 and self.rot_posp > 12:
                        self.rot_posp = 12
                    elif self.cutdown == 4 and self.rot_posp > 13:
                        self.rot_posp = 13
                    if self.stopstart == 1 and self.album_start == 0 and self.rot_posp == 4:
                        self.rot_posp = 3
                    if self.Radio_ON == 1 and self.rot_posp == 0:
                        self.rot_posp = 11
                    if self.cutdown == 1 or self.cutdown == 4:
                        if self.album_start == 1:
                            if self.rot_posp == 3:
                                self.rot_posp = 12
                        if self.Radio_ON == 1:
                            if self.rot_posp == 4:
                                self.rot_posp = 1
                            if self.rot_posp == 10 and self.cutdown == 1:
                                self.rot_posp = 9
                            if self.Radio_RON == 1:
                                if self.rot_posp == 1:
                                    self.rot_posp = 9
                    elif self.cutdown == 5 or self.cutdown == 6:
                        if self.Radio_ON == 1:
                            if self.rot_posp == 5:
                                self.rot_posp = 2
                            elif self.rot_posp == 1:
                                self.rot_posp = 10
                            if self.rot_posp == 9 and self.Radio_Stns[self.Radio + 2] == 0:
                                self.rot_posp = 8
                        if self.Radio_RON == 1:
                            if self.rot_posp == 2:
                                self.rot_posp = 10
                        if self.album_start == 1:
                            if self.rot_posp == 3:
                                self.rot_posp = 0
                    elif self.cutdown >= 7 or self.cutdown == 0 or self.cutdown == 2:
                        if self.stopstart == 1:
                            if self.rot_posp == 8:
                                self.rot_posp = 7
                        if self.album_start == 1:
                            if self.rot_posp == 8:
                                self.rot_posp = 7
                            elif self.rot_posp == 3:
                                self.rot_posp = 16
                            elif self.rot_posp == 13:
                                self.rot_posp = 12
                        if self.Radio_ON == 1:
                            if self.rot_posp == 6 and self.Radio_Stns[self.Radio + 2]  > 0:
                                self.rot_posp = 5
                            if self.rot_posp == 6:
                                self.rot_posp = 1
                            if self.rot_posp == 4 and self.Radio_Stns[self.Radio + 2]  > 0:
                                self.rot_posp = 1
                            if self.rot_posp == 8:
                                self.rot_posp = 7
                        if self.Radio_RON == 1:
                            if self.rot_posp == 1:
                                self.rot_posp = 11
                           
                    self.rot_pos = self.order[self.rot_posp]
                    if self.album_start == 0:
                        if self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 0:
                            if self.bt_on == 0:
                                self.Button_Bluetooth.config(bg = 'light blue')
                            else:
                                self.Button_Bluetooth.config(bg = 'red')
                        if self.Radio_RON == 0:
                            self.Button_Prev_Artist.config(bg = 'light blue')
                            self.Button_Prev_Album.config(bg = 'light blue')
                        else:
                            self.Button_Prev_Artist.config(bg = 'light gray')
                            self.Button_Prev_Album.config(bg = 'light gray')
                        if self.stopstart == 0:
                            self.Button_Reload.config(bg = 'light blue')
                        else:
                            self.Button_Reload.config(bg = 'light blue')
                            if self.gapless == 0:
                                self.Button_Reload.config(bg = 'light blue')
                            else:
                                self.Button_Reload.config(bg = 'light gray')
                        self.Button_Next_AZ.config(bg = 'light blue')
                        if (self.cutdown < 5 or self.cutdown > 6):
                            self.Button_Prev_PList.config(bg = 'light blue')
                        if (self.cutdown < 5 or self.cutdown > 6) and self.cutdown != 1:
                            self.Button_Gapless.config(bg = 'light blue')
                        if (self.cutdown < 4 or self.cutdown > 6) and self.cutdown != 1:
                            self.Button_repeat.config(bg = 'light blue')
                            self.Button_AZ_artists.config(bg = 'light blue')
                    if self.stopstart == 1:
                        if self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 0:
                            self.Button_Bluetooth.config(bg = 'light gray')
                    if self.album_start == 1:
                        if self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 0:
                            if self.bt_on == 0:
                                self.Button_Bluetooth.config(bg = 'light gray')
                            else:
                                self.Button_Bluetooth.config(bg = 'red')
                        self.Button_Prev_Artist.config(bg = 'light gray')
                        self.Button_Prev_Album.config(bg = 'light gray')
                        if self.gapless == 0:
                            self.Button_Reload.config(bg = 'light blue')
                        else:
                            self.Button_Reload.config(bg = 'light gray')
                        self.Button_Next_AZ.config(bg = 'light blue')
                        if (self.cutdown < 5 or self.cutdown > 6):
                            self.Button_Prev_PList.config(bg = 'light gray')
                        if (self.cutdown < 5 or self.cutdown > 6) and self.cutdown != 1:
                            self.Button_Gapless.config(bg = 'light blue')
                        if (self.cutdown < 4 or self.cutdown > 6) and self.cutdown != 1:
                            self.Button_repeat.config(bg = 'light blue')
                            if self.Radio_ON == 0:
                                self.Button_AZ_artists.config(bg = 'light gray')
                    if self.Radio_ON == 1:
                        self.Button_Radio.config(bg = 'light blue')
                        self.Button_Prev_Track.config(bg = 'light gray')
                        self.Button_Prev_Album.config(bg = 'light gray')
                        self.Button_Reload.config(bg = 'light gray')
                        if self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 0:
                            if self.bt_on == 0:
                                self.Button_Bluetooth.config(bg = 'light gray')
                            else:
                                self.Button_Bluetooth.config(bg = 'red')
                        if (self.cutdown < 5 or self.cutdown > 6):
                            self.Button_Prev_PList.config(bg = 'light gray')
                        if (self.cutdown < 5 or self.cutdown > 6) and self.cutdown != 1:
                            self.Button_Gapless.config(bg = 'light gray')
                        if (self.cutdown < 4 or self.cutdown > 6) and self.cutdown != 1:
                            self.Button_repeat.config(bg = 'light gray')
                            self.Button_AZ_artists.config(bg = 'light gray')
                        if self.Radio_Stns[self.Radio + 2]  > 0:
                            self.Button_Pause.config(bg = 'light blue')
                        else:
                            self.Button_Pause.config(bg = 'light gray')
                    elif self.Radio_ON == 0:
                        if self.bt_on == 1:
                            self.Button_Radio.config(bg = 'light gray')
                        else:
                            self.Button_Radio.config(bg = 'light blue')
                        self.Button_Pause.config(bg = 'light blue')
                        self.Button_Shuffle.config(bg = 'light blue')
                        self.Button_Prev_Track.config(bg = 'light blue')
                        if self.bt_on == 1:
                            self.Button_Start.config(bg = 'light gray')
                        elif self.album_start == 0:
                            self.Button_Start.config(bg = 'green')
                        if self.stopstart == 1 or self.bt_on == 1:
                            self.Button_TAlbum.config(bg = 'light gray')
                        else:
                            self.Button_TAlbum.config(bg = 'blue')
                        if self.album_start == 1:
                            self.Button_TAlbum.config(bg = 'blue')
                    self.Button_Shutdown.config(bg = 'grey')
                    self.Button_Sleep.config(bg = 'light blue')
                    
                    if self.rot_pos == 2:
                        self.Button_Prev_Artist.config(bg = 'yellow')
                    elif self.rot_pos == 1:
                        self.Button_Prev_Album.config(bg = 'yellow')
                    elif self.rot_pos == 0:
                        self.Button_Prev_Track.config(bg = 'yellow')
                    elif self.rot_pos == 3:
                        self.Button_Start.config(bg = 'yellow')
                    elif self.rot_pos == 4:
                        self.Button_TAlbum.config(bg = 'yellow')
                    elif self.rot_pos == 5:
                        self.Button_Shuffle.config(bg = 'yellow')
                    elif self.rot_pos == 6:
                        self.Button_Next_AZ.config(bg = 'yellow')
                    elif self.rot_pos == 7:
                        self.Button_Shutdown.config(bg = 'yellow')
                    elif self.rot_pos == 8:
                        self.Button_Radio.config(bg = 'yellow')
                    elif self.rot_pos == 9:
                        self.Button_Pause.config(bg = 'yellow')
                    elif self.rot_pos == 10:
                        self.Button_Sleep.config(bg = 'yellow')
                    elif self.rot_pos == 11:
                        self.Button_Reload.config(bg = 'yellow')
                    elif self.rot_pos == 12:
                        self.Button_Prev_PList.config(bg = 'yellow')
                    elif self.rot_pos == 13:
                        self.Button_Gapless.config(bg = 'yellow')
                    elif self.rot_pos == 14:
                        self.Button_repeat.config(bg = 'yellow')
                    elif self.rot_pos == 15:
                        self.Button_AZ_artists.config(bg = 'yellow')
                    elif self.rot_pos == 16:
                        self.Button_Bluetooth.config(bg = 'yellow')
                #print("rot- ",self.rot_posp,self.rot_pos)
                if self.rot_mode == 2 and self.rot_pos == 2:
                    self.wheel_opt = 0
                    self.Prev_Artist()
                elif self.rot_mode == 1 and self.rot_pos == 1:
                    self.wheel_opt = 1
                    self.Prev_Album()
                elif self.rot_mode == 1 and self.rot_pos == 0:
                    self.wheel_opt = 2
                    self.Prev_Track()
                elif self.rot_mode == 1 and self.rot_pos == 6:
                    #self.wheel_opt = 0
                    self.nextAZ()
                elif self.rot_mode == 1 and self.rot_pos == 2:
                    self.wheel_opt = 0
                    self.prevAZ()
                elif self.rot_mode == 1 and self.rot_pos == 12:
                    self.wheel_opt = 3
                    self.Next_m3u()
            else:
                self.old_rotor2 = self.rotor2.value
                if self.rot_mode == 0:
                    self.rot_posp +=1
                    #print(self.rot_posp)
                    if self.rot_posp > 16:
                        self.rot_posp = 0
                    if self.cutdown > 4 and self.cutdown < 7 and self.rot_posp > 11:
                        self.rot_posp = 0
                    elif self.cutdown == 1 and self.rot_posp > 12:
                        self.rot_posp = 0
                    elif self.cutdown == 4 and self.rot_posp > 13:
                        self.rot_posp = 0
                    if self.stopstart == 1 and self.album_start == 0 and self.rot_posp == 4:
                        self.rot_posp = 5
                    if self.album_start == 1 and self.rot_posp == 1:
                        self.rot_posp = 4
                    if self.album_start == 1 and self.rot_posp > 16:
                        self.rot_posp = 0
                    if self.cutdown == 1 or self.cutdown == 4:
                        if self.album_start == 1:
                            if self.rot_posp == 0:
                                self.rot_posp = 4
                        if self.Radio_ON == 1:
                            if self.cutdown == 1 and self.rot_posp == 10:
                                self.rot_posp = 1
                            elif self.cutdown == 4 and self.rot_posp == 9:
                                self.rot_posp = 10
                            elif self.cutdown == 4 and self.rot_posp == 11:
                                self.rot_posp = 1
                            if self.rot_posp == 2:
                                self.rot_posp = 5
                            if self.Radio_RON == 1:
                                if self.rot_posp == 1:
                                    self.rot_posp = 5
                    elif self.cutdown == 5 or self.cutdown == 6:
                        if self.Radio_ON == 1:
                            if self.rot_posp == 11:
                                self.rot_posp = 2
                            elif self.rot_posp == 3:
                                self.rot_posp = 6
                            if self.rot_posp == 9 and self.Radio_Stns[self.Radio + 2] == 0:
                                self.rot_posp = 10
                            if self.Radio_RON == 1:
                                if self.rot_posp == 2:
                                    self.rot_posp = 6
                    elif self.cutdown >= 7 or self.cutdown == 0 or self.cutdown == 2:
                        if self.stopstart == 1:
                            if self.rot_posp == 8:
                                self.rot_posp = 9
                        if self.album_start == 1:
                            if self.rot_posp == 8:
                                self.rot_posp = 9
                            elif self.rot_posp == 0:
                                self.rot_posp = 4
                            elif self.rot_posp == 13:
                                self.rot_posp = 14
                        elif self.Radio_ON == 1:
                            if self.rot_posp == 12:
                                self.rot_posp = 1
                            if self.rot_posp == 2 and self.Radio_Stns[self.Radio + 2] == 0:
                                self.rot_posp = 7
                            elif self.rot_posp == 2:
                                self.rot_posp = 5
                            if self.rot_posp == 6:
                                self.rot_posp = 7
                            elif self.rot_posp == 8:
                                self.rot_posp = 9
                            if self.Radio_RON == 1:
                                if self.rot_posp == 1:
                                    self.rot_posp = 5
                    self.rot_pos = self.order[self.rot_posp]
                    if self.album_start == 0:
                        if self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 0:
                            if self.bt_on == 0:
                                self.Button_Bluetooth.config(bg = 'light blue')
                            else:
                                self.Button_Bluetooth.config(bg = 'red')
                        if self.Radio_RON == 0:
                            self.Button_Prev_Artist.config(bg = 'light blue')
                            self.Button_Prev_Album.config(bg = 'light blue')
                        else:
                            self.Button_Prev_Artist.config(bg = 'light gray')
                            self.Button_Prev_Album.config(bg = 'light gray')
                        if self.stopstart == 0:
                            self.Button_Reload.config(bg = 'light blue')
                        else:
                            self.Button_Reload.config(bg = 'light blue')
                            if self.gapless == 0:
                                self.Button_Reload.config(bg = 'light blue')
                            else:
                                self.Button_Reload.config(bg = "light gray")
                        self.Button_Next_AZ.config(bg = 'light blue')
                        self.Button_Pause.config(bg = 'light blue')
                        if self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 0:
                            if self.bt_on == 0:
                                self.Button_Bluetooth.config(bg = 'light blue')
                            else:
                                self.Button_Bluetooth.config(bg = 'red')
                        if (self.cutdown < 5 or self.cutdown > 6):
                            self.Button_Prev_PList.config(bg = 'light blue')
                        if (self.cutdown < 5 or self.cutdown > 6) and self.cutdown != 1:
                            self.Button_Gapless.config(bg = 'light blue')
                        if (self.cutdown < 4 or self.cutdown > 6) and self.cutdown != 1:
                            self.Button_repeat.config(bg = 'light blue')
                            if self.Radio_ON == 0:
                                self.Button_AZ_artists.config(bg = 'light blue')
                    if self.stopstart == 1:
                        if self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 0:
                            self.Button_Bluetooth.config(bg = 'light gray')
                    if self.album_start == 1:
                        self.Button_Prev_Artist.config(bg = 'light gray')
                        self.Button_Prev_Album.config(bg = 'light gray')
                        self.Button_Radio.config(bg = 'light gray')
                        if self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 0:
                            if self.bt_on == 0:
                                self.Button_Bluetooth.config(bg = 'light gray')
                            else:
                                self.Button_Bluetooth.config(bg = 'red')
                        if self.gapless == 0:
                            self.Button_Reload.config(bg = 'light blue')
                        else:
                            self.Button_Reload.config(bg = 'light gray')
                        self.Button_Next_AZ.config(bg = 'light blue')
                        self.Button_Pause.config(bg = 'light blue')
                        if (self.cutdown < 5 or self.cutdown > 6):
                            self.Button_Prev_PList.config(bg = 'light gray')
                        if (self.cutdown < 5 or self.cutdown > 6) and self.cutdown != 1:
                            self.Button_Gapless.config(bg = 'light blue')
                        if (self.cutdown < 4 or self.cutdown > 6) and self.cutdown != 1:
                            self.Button_repeat.config(bg = 'light blue')
                            self.Button_AZ_artists.config(bg = 'light gray')
                    if self.Radio_ON == 1:
                        self.Button_Radio.config(bg = 'light blue')
                        if self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 0:
                            if self.bt_on == 0:
                                self.Button_Bluetooth.config(bg = 'light gray')
                            else:
                                self.Button_Bluetooth.config(bg = 'red')
                        if self.Radio_RON == 0:
                            self.Button_Prev_Artist.config(bg = 'light blue')
                            self.Button_Prev_Album.config(bg = 'light gray')
                        else:
                            self.Button_Prev_Artist.config(bg = 'light gray')
                            self.Button_Prev_Album.config(bg = 'light gray')
                        self.Button_Prev_Track.config(bg = 'light gray')
                        if self.Radio_Stns[self.Radio + 2]  > 0:
                            self.Button_Pause.config(bg = 'light blue')
                        else:
                            self.Button_Pause.config(bg = 'light gray')
                        self.Button_Reload.config(bg = 'light gray')
                        if (self.cutdown < 5 or self.cutdown > 6):
                            self.Button_Prev_PList.config(bg = 'light gray')
                        if (self.cutdown < 5 or self.cutdown > 6) and self.cutdown != 1:
                            self.Button_Gapless.config(bg = 'light gray')
                        if (self.cutdown < 4 or self.cutdown > 6) and self.cutdown != 1:
                            self.Button_repeat.config(bg = 'light gray')
                            self.Button_AZ_artists.config(bg = 'light gray')
                    elif self.Radio_ON == 0:
                        self.Button_Prev_Track.config(bg = 'light blue')
                        if self.bt_on == 1:
                            self.Button_Radio.config(bg = 'light gray')
                        else:
                            self.Button_Radio.config(bg = 'light blue')
                        if self.bt_on == 1:
                            self.Button_Start.config(bg = 'light gray')
                        elif self.album_start == 0:
                            self.Button_Start.config(bg = 'green')
                        if (self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 0) and self.album_start == 1:
                            if self.bt_on == 0:
                                self.Button_Bluetooth.config(bg = 'light gray')
                            else:
                                self.Button_Bluetooth.config(bg = 'red')
                        if self.stopstart == 1 or self.bt_on == 1:
                            self.Button_TAlbum.config(bg = 'light gray')
                        else:
                            self.Button_TAlbum.config(bg = 'blue')
                        if self.album_start == 1:
                            self.Button_TAlbum.config(bg = 'blue')
                        self.Button_Shuffle.config(bg = 'light blue')
                    self.Button_Shutdown.config(bg = 'grey')
                    self.Button_Sleep.config(bg = 'light blue')
                    
                    if self.rot_pos == 2:
                        self.Button_Prev_Artist.config(bg = 'yellow')
                    elif self.rot_pos == 1:
                        self.Button_Prev_Album.config(bg = 'yellow')
                    elif self.rot_pos == 0:
                        self.Button_Prev_Track.config(bg = 'yellow')
                    elif self.rot_pos == 3:
                        self.Button_Start.config(bg = 'yellow')
                    elif self.rot_pos == 4:
                        self.Button_TAlbum.config(bg = 'yellow')
                    elif self.rot_pos == 5:
                        self.Button_Shuffle.config(bg = 'yellow')
                    elif self.rot_pos == 6:
                        self.Button_Next_AZ.config(bg = 'yellow')
                    elif self.rot_pos == 7:
                        self.Button_Shutdown.config(bg = 'yellow')
                    elif self.rot_pos == 8:
                        self.Button_Radio.config(bg = 'yellow')
                    elif self.rot_pos == 9:
                        self.Button_Pause.config(bg = 'yellow')
                    elif self.rot_pos == 10:
                        self.Button_Sleep.config(bg = 'yellow')
                    elif self.rot_pos == 11:
                        self.Button_Reload.config(bg = 'yellow')
                    elif self.rot_pos == 12:
                        self.Button_Prev_PList.config(bg = 'yellow')
                    elif self.rot_pos == 13:
                        self.Button_Gapless.config(bg = 'yellow')
                    elif self.rot_pos == 14:
                        self.Button_repeat.config(bg = 'yellow')
                    elif self.rot_pos == 15:
                        self.Button_AZ_artists.config(bg = 'yellow')
                    elif self.rot_pos == 16:
                        self.Button_Bluetooth.config(bg = 'yellow')
                #print("rot+ ",self.rot_posp,self.rot_pos)
                if self.rot_mode == 2 and self.rot_pos == 2:
                    self.wheel_opt = 0
                    self.Next_Artist()
                elif self.rot_mode == 1 and self.rot_pos == 1:
                    self.wheel_opt = 1
                    self.Next_Album()
                elif self.rot_mode == 1 and self.rot_pos == 0:
                    self.wheel_opt = 2
                    self.Next_Track()
                elif self.rot_mode == 1 and self.rot_pos == 6:
                    self.nextAZ()
                elif self.rot_mode == 1 and self.rot_pos == 2:
                    self.wheel_opt = 0
                    self.nextAZ()
                elif self.rot_mode == 1 and self.rot_pos == 12:
                    self.wheel_opt = 3
                    self.Next_m3u()
        self.after(250, self.Read_Rotary_POS)

    def Check_buttons(self):
        # check the external switches
        if self.rotary_vol == 0 and self.ext_buttons == 1:
            if self.trace > 1:
                print("check buttons")
            if self.button_volup.is_pressed:
                self.light_on = time.monotonic()
                if self.Pi7_backlight == 1:
                    os.system("rpi-backlight -b 100")
                self.volume_UP()
            elif self.button_voldn.is_pressed:
                self.light_on = time.monotonic()
                if self.Pi7_backlight == 1:
                    os.system("rpi-backlight -b 100")
                self.volume_DN()
            elif self.button_mute.is_pressed:
                self.light_on = time.monotonic()
                if self.Pi7_backlight == 1:
                    os.system("rpi-backlight -b 100")
                self.Mute()
        if self.gpio_enable == 2  and self.rotary_vol == 1 and self.button_mute.is_pressed:
            self.light_on = time.monotonic()
            self.rot_mode = 0
            self.Mute()
        if self.gpio_enable == 2 and self.rotary_pos == 1 and self.album_start == 0 and self.button_next.is_pressed and self.rot_mode == 0 and (self.rot_pos < 3 or self.rot_pos > 4) and self.rot_pos < 16 and self.stopstart == 0:
            # not playing mp3
            self.light_on = time.monotonic()
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 100")
            self.rot_mode = 1
            self.Button_Prev_Artist.config(bg = 'light blue')
            if self.Radio_ON == 0:
                self.Button_Prev_PList.config(bg = 'light blue')
                self.Button_Prev_Album.config(bg = 'light blue')
                self.Button_Prev_Track.config(bg = 'light blue')
            self.Button_Next_AZ.config(bg = 'light blue')
            if (self.cutdown < 5 or self.cutdown > 6):
                self.Button_Prev_PList.config(bg = 'light blue')
            if (self.cutdown < 5 or self.cutdown > 6) and self.cutdown != 1:
                self.Button_Gapless.config(bg = 'light blue')
            if self.rot_pos == 2:
                self.Button_Prev_Artist.config(bg = '#c5c')
                if self.Radio_ON == 1:
                    self.Button_Prev_Track.config(bg = 'light gray')
                    self.Button_Prev_Album.config(bg = 'light gray')
                    self.Button_Gapless.config(bg = 'light gray')
                    if (self.cutdown < 5 or self.cutdown > 6):
                        self.Button_Prev_PList.config(bg = 'light gray')
            elif self.rot_pos == 1:
                self.Button_Prev_Album.config(bg = 'red')
            elif self.rot_pos == 0:
                self.Button_Prev_Track.config(bg = 'red')
                
            elif self.rot_pos == 6:
                if self.Radio_ON == 0:
                    self.Button_Next_AZ.config(bg = 'red')
                else:
                    self.rot_mode = 0
                    self.Button_Next_AZ.config(bg = 'yellow')
                    self.Button_Gapless.config(bg = 'light gray')
                    self.Button_Prev_PList.config(bg = 'light gray')
                    self.Button_Prev_Album.config(bg = 'light gray')
                    self.Button_Prev_Track.config(bg = 'light gray')
                    self.nextAZ()
            elif self.rot_pos == 5:
                self.rot_mode = 0
                self.Shuffle_Tracks()
            elif self.rot_pos == 7:
                self.Shutdown_exit = 0
                self.Shutdown()
            elif self.rot_pos == 8:
                self.rot_mode = 0
                self.Button_Gapless.config(bg = 'light gray')
                self.RadioX()
            elif self.rot_pos == 9:
                self.rot_mode = 0
                if self.Radio_ON == 0 :
                    self.Button_Prev_Artist.config(bg = 'light blue')
                    self.Button_Prev_Album.config(bg = 'light blue')
                else:
                    self.Button_Prev_Artist.config(bg = 'light gray')
                    self.Button_Prev_Album.config(bg = 'light gray')
                    self.Button_Prev_Track.config(bg = 'light gray')
                    if (self.cutdown < 5 or self.cutdown > 6):
                        self.Button_Prev_PList.config(bg = 'light gray')
                self.Pause()
            elif self.rot_pos == 10:
                self.rot_mode = 0
                self.sleep()
            elif self.rot_pos == 11:
                self.rot_mode = 0
                self.Button_Reload.config(bg = 'red')
                self.RELOAD_List()
            elif self.rot_pos == 12:
                self.Button_Prev_PList.config(bg = 'red')
            elif self.rot_pos == 13:
                self.rot_mode = 0
                self.Gapless()
            elif self.rot_pos == 14:
                self.rot_mode = 0
                self.Repeat()
            elif self.rot_pos == 15:
                self.rot_mode = 0
                self.AZ_Tracks()
 
            
        elif self.gpio_enable == 2 and self.rotary_pos == 1 and self.button_next.is_pressed and self.rot_mode == 0 and (self.rot_pos < 3 or self.rot_pos > 4)  and self.rot_pos < 16 and (self.stopstart == 1 or self.album_start == 1):
            # playing mp3
            self.light_on = time.monotonic()
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 100")
            self.rot_mode = 1
            self.Button_Prev_Artist.config(bg = 'light blue')
            self.Button_Prev_Album.config(bg = 'light blue')
            self.Button_Prev_Track.config(bg = 'light blue')
            self.Button_Next_AZ.config(bg = 'light blue')
            if (self.cutdown < 5 or self.cutdown > 6):
                self.Button_Prev_PList.config(bg = 'light blue')
            if (self.cutdown < 5 or self.cutdown > 6) and self.cutdown != 1:
                self.Button_Gapless.config(bg = 'light blue')
            if self.rot_pos == 2:
                self.Button_Prev_Artist.config(bg = 'red')
            elif self.rot_pos == 1:
                self.Button_Prev_Album.config(bg = 'red')
            elif self.rot_pos == 0:
                self.Button_Prev_Track.config(bg = 'red')
            elif self.rot_pos == 6:
                if self.Radio_ON == 0:
                    self.rot_mode = 0
                    self.nextAZ()
                else:
                    self.rot_mode = 0
                    self.Button_Prev_Album.config(bg = 'light gray')
                    self.Button_Prev_Track.config(bg = 'light gray')
            elif self.rot_pos == 5:
                self.rot_mode = 0
                self.Shuffle_Tracks()
            elif self.rot_pos == 7:
                self.Shutdown_exit = 0
                self.Shutdown()
            elif self.rot_pos == 8:
                self.rot_mode = 0
                self.RadioX()
            elif self.rot_pos == 9:
                self.rot_mode = 0
                if self.album_start == 1:
                    self.Button_Prev_Artist.config(bg = 'light gray')
                    self.Button_Prev_Album.config(bg = 'light gray')
                    if (self.cutdown < 5 or self.cutdown > 6):
                        self.Button_Prev_PList.config(bg = 'light gray')
                self.Pause()
            elif self.rot_pos == 10:
                self.rot_mode = 0
                self.sleep()
            elif self.rot_pos == 11: # skip forward
                self.rot_mode = 0
                self.RELOAD_List()
            elif self.rot_pos == 12:
                self.Button_Prev_PList.config(bg = 'red')
            elif self.rot_pos == 13:
                self.rot_mode = 0
                self.Gapless()
            elif self.rot_pos == 14:
                self.rot_mode = 0
                self.Repeat()
            elif self.rot_pos == 15:
                self.rot_mode = 0
                self.AZ_Tracks()

        elif self.gpio_enable == 2 and self.rotary_pos == 1 and self.button_next.is_pressed and self.rot_mode == 1 and self.rot_pos == 2 and self.stopstart == 0 and self.album_start == 0: # and self.Radio_ON == 0:
            # Next Artist mode
            self.rot_mode = 2
            self.light_on = time.monotonic()
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 100")
            self.Button_Prev_Artist.config(bg = 'red')

        elif self.gpio_enable == 2 and self.rotary_pos == 1 and self.button_next.is_pressed and self.rot_mode == 2 and self.rot_pos == 2 and self.stopstart == 0 and self.album_start == 0: # and self.Radio_ON == 0:
            # Exit Artist mode
            self.rot_mode = 0
            self.light_on = time.monotonic()
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 100")
            self.Button_Prev_Artist.config(bg = 'yellow')
                 
        elif self.gpio_enable == 2 and self.rotary_pos == 1 and self.button_next.is_pressed and self.rot_mode > 0 and (self.rot_pos < 3 or self.rot_pos > 4)   and self.rot_pos < 16 and self.stopstart == 0 and self.album_start == 0 :
            self.rot_mode = 0
            self.light_on = time.monotonic()
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 100")
            self.Button_Prev_Artist.config(bg = 'light blue')
            self.Button_Prev_Album.config(bg = 'light blue')
            self.Button_Prev_Track.config(bg = 'light blue')
            self.Button_Next_AZ.config(bg = 'light blue')
            if (self.cutdown < 5 or self.cutdown > 6):
                self.Button_Prev_PList.config(bg = 'light blue')
            if (self.cutdown < 5 or self.cutdown > 6) and self.cutdown != 1:
                self.Button_Gapless.config(bg = 'light blue')
            if self.rot_pos == 2:
                self.Button_Prev_Artist.config(bg = 'yellow')
                if self.Radio_ON == 1:
                    self.Button_Prev_Track.config(bg = 'light gray')
                    self.Button_Prev_Album.config(bg = 'light gray')
                    if (self.cutdown < 5 or self.cutdown > 6):
                        self.Button_Prev_PList.config(bg = 'light gray')
            elif self.rot_pos == 1:
                self.Button_Prev_Album.config(bg = 'yellow')
            elif self.rot_pos == 0:
                self.Button_Prev_Track.config(bg = 'yellow')
            elif self.rot_pos == 6:
                self.Button_Next_AZ.config(bg = 'yellow')
            elif self.rot_pos == 12:
                self.Button_Prev_PList.config(bg = 'yellow')
                
        elif self.gpio_enable == 2 and self.rotary_pos == 1 and self.button_next.is_pressed and self.rot_mode == 1 and (self.rot_pos < 3 or self.rot_pos > 4) and self.rot_pos < 16 and (self.stopstart == 1 or self.album_start == 1):
            self.rot_mode = 0
            self.light_on = time.monotonic()
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 100")
            self.Button_Prev_Artist.config(bg = 'light blue')
            self.Button_Prev_Album.config(bg = 'light blue')
            self.Button_Prev_Track.config(bg = 'light blue')
            self.Button_Next_AZ.config(bg = 'light blue')
            if (self.cutdown < 5 or self.cutdown > 6):
                self.Button_Prev_PList.config(bg = 'light blue')
            if (self.cutdown < 5 or self.cutdown > 6) and self.cutdown != 1:
                self.Button_Gapless.config(bg = 'light blue')
            if self.rot_pos == 2:
                self.Button_Prev_Artist.config(bg = 'yellow')
            elif self.rot_pos == 1:
                self.Button_Prev_Album.config(bg = 'yellow')
            elif self.rot_pos == 0:
                self.Button_Prev_Track.config(bg = 'yellow')
            elif self.rot_pos == 6:
                self.Button_Next_AZ.config(bg = 'yellow')
            elif self.rot_pos == 12:
                self.Button_Prev_PList.config(bg = 'yellow')
        elif self.gpio_enable == 2 and self.rotary_pos == 1 and self.button_next.is_pressed and self.Radio_ON == 0 and self.rot_posp == 8 and self.album_start == 0:
            # Bluetooth
            self.light_on = time.monotonic()
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 100")
            self.Bluetooth()
            
        elif self.gpio_enable == 2 and self.rotary_pos == 1 and self.button_next.is_pressed and self.Radio_ON == 0 and self.rot_pos == 3 and self.stopstart == 0 and self.album_start == 0:
            self.rot_mode = 0
            self.light_on = time.monotonic()
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 100")
            self.rot_pos = 3
            self.rot_posp = 3
            self.Button_Start.config(bg = 'yellow')
            self.Play()
        elif self.gpio_enable == 2 and self.rotary_pos == 1 and self.button_next.is_pressed and self.Radio_ON == 0 and self.rot_pos == 3 and self.stopstart == 1 and self.album_start == 0:
            self.rot_mode = 0
            self.light_on = time.monotonic()
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 100")
            self.rot_pos = 3
            self.rot_posp = 3
            self.Play()
        elif self.gpio_enable == 2 and self.rotary_pos == 1 and self.button_next.is_pressed and self.Radio_ON == 0 and self.rot_pos == 4 and self.album_start == 0:
            self.rot_mode = 0
            self.light_on = time.monotonic()
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 100")
            self.rot_pos = 4
            self.Button_Next_AZ.config(bg = 'light blue', text = "Info")
            self.Play_Album()
        elif self.gpio_enable == 2 and self.rotary_pos == 1 and self.button_next.is_pressed and self.Radio_ON == 0 and self.rot_pos == 4 and self.album_start == 1:
            self.rot_mode = 0
            self.light_on = time.monotonic()
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 100")
            self.rot_pos = 4
            self.Button_TAlbum.config(bg = 'yellow')
            self.Button_Next_AZ.config(bg = 'light blue', text = "NextAZ")
            self.Play_Album()
        elif self.ext_buttons == 1:
            if self.gpio_enable == 2 and self.rotary_pos == 0 and self.button_start_play.is_pressed :
                self.light_on = time.monotonic()
                if self.Pi7_backlight == 1:
                    os.system("rpi-backlight -b 100")
                self.Play()
            if self.gpio_enable == 2 and self.rotary_pos == 0 and self.button_start_album.is_pressed :
                self.light_on = time.monotonic()
                if self.Pi7_backlight == 1:
                    os.system("rpi-backlight -b 100")
                self.Play_Album()
            if self.gpio_enable == 2 and self.rotary_pos == 0 and self.button_start_next.is_pressed and self.play == 1:
                self.light_on = time.monotonic()
                if self.Pi7_backlight == 1:
                    os.system("rpi-backlight -b 100")
                self.Next_Track()
            if self.gpio_enable == 2 and self.rotary_pos == 0 and self.button_start_next.is_pressed and self.play == 0:
                self.light_on = time.monotonic()
                if self.Pi7_backlight == 1:
                    os.system("rpi-backlight -b 100")
                self.Next_Album()

        self.after(500, self.Check_buttons) # set for 500mS
        
    def plist_callback(self):
      if len(self.tunes) > 0:
        if self.trace > 0:
            print ("plist callback",self.track_no,len(self.tunes))
        self.artistdata = []
        self.Disp_artist_name["values"] = self.artistdata
        if self.shuffle_on == 0 and self.Radio_ON == 0 and self.tracker == 0:
            for x in range(0,len(self.tunes)):
                self.artist_name_1,self.album_name_1,self.track_name_1,self.drive_name_1,self.drive_name1_1,self.drive_name2_1,self.genre_name  = self.tunes[x].split('^')
                self.artistdata.append(self.artist_name_1)
            self.artistdata = list(dict.fromkeys(self.artistdata))
            self.artistdata.sort()
            self.Disp_artist_name["values"] = self.artistdata
            if self.auto_albums == 1 or self.reload == 1:
                self.Disp_artist_name.set(self.artist_name)
                self.reload = 0
        elif self.Radio_ON == 1:
            for x in range(0,len(self.Radio_Stns),3):
                self.artistdata.append(self.Radio_Stns[x])
            self.Disp_artist_name["values"] = self.artistdata
        if self.Radio_ON == 0 and self.tracker == 0:
            self.artist_callback(0)
        self.tracker = 0

    def artist_callback(self,a):
        if self.trace > 0:
            print ("artist callback",self.track_no,self.ac,self.bc,self.cc)
        if self.play == 0:
            self.artist_name3,self.album_name3,self.track_name3,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[self.track_no].split('^')
        else:
            self.artist_name3,self.album_name3,self.track_name3,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[self.track_no + 1].split('^')
        self.albumdata = []
        self.Disp_album_name["values"] = self.albumdata
        if (self.shuffle_on == 0 and self.album_start == 0 and self.Radio_ON == 0) or self.auto_albums == 1:
            for x in range(0,len(self.tunes)):
                self.artist_name_1,self.album_name_1,self.track_name_1,self.drive_name_1,self.drive_name1_1,self.drive_name2_1,self.genre_name  = self.tunes[x].split('^')
                if self.artist_name_1 == self.artist_name3:
                    self.albumdata.append(self.album_name_1)
            self.albumdata = list(dict.fromkeys(self.albumdata))
            self.albumdata.sort()
            self.Disp_album_name["values"] = self.albumdata
            if self.ac == 0 and self.bc == 0:
                self.Disp_album_name.set(self.albumdata[0])
        elif self.Radio_ON == 1:
            stop = 0
            k = 0
            while stop == 0 and k < len(self.Radio_Stns):
                if self.Radio_Stns[k] == self.Disp_artist_name.get():
                    stop = 1
                    self.NewRadio = k
                k +=1
            self.Next_Artist()
        if self.Radio_ON == 0:
            self.album_callback(0)

    def album_callback(self,a):
      if len(self.tunes) > 0:
        if self.trace > 0:
            print ("album callback",self.track_no)
        self.trackdata = []
        self.Disp_track_name["values"] = self.trackdata
        if self.play == 0:
            self.artist_name3,self.album_name3,self.track_name3,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[self.track_no].split('^')
        else:
            self.artist_name3,self.album_name3,self.track_name3,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[self.track_no + 1].split('^')
        if self.shuffle_on == 0 or self.album_start == 1:
            for x in range(0,len(self.tunes)):
                self.artist_name_1,self.album_name_1,self.track_name_1,self.drive_name_1,self.drive_name1_1,self.drive_name2_1,self.genre_name  = self.tunes[x].split('^')
                if self.artist_name_1 == self.artist_name3 and self.album_name_1[:-1] == self.album_name3[:-1]:
                    self.trackdata.append(self.track_name_1)
            self.trackdata = list(dict.fromkeys(self.trackdata))
            self.Disp_track_name["values"] = self.trackdata

        self.ac = 0
        self.bc = 0
        self.Disp_artist_name.set(self.artist_name3)
        self.Disp_album_name.set(self.album_name3)
        tpath = self.artist_name3 + "^" + self.album_name3 + "^" + self.track_name3
        if self.trace > 0:
            print ("album callback track",tpath)
        stop = 0
        k = 0
        while stop == 0 and k < len(self.tunes) - 1:
            a,b,c,d,e,f,g = self.tunes[k].split("^")
            if tpath == a + "^" + b + "^" + c :
                stop = 1
                self.track_no = k
            k +=1
        self.Disp_track_no.config(text = self.track_no + 1)
        self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[self.track_no].split('^')
        if self.drive_name[-1] == "*":
            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name[:-1], self.artist_name + " - " + self.album_name, self.track_name)
        elif self.genre_name == "None":
            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name, self.artist_name, self.album_name, self.track_name)
        else:
            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name,self.genre_name, self.artist_name, self.album_name, self.track_name)
        if os.path.exists(self.track):
                if self.track[-4:] == ".mp3":
                    audio = MP3(self.track)
                    self.track_len = audio.info.length
                elif self.track[-4:] == "flac":
                    audio = FLAC(self.track)
                    self.track_len = audio.info.length
                elif self.track[-4:] == ".dsf":
                    audio = DSF(self.track)
                    self.track_len = audio.info.length
                elif self.track[-4:] == ".wav":
                    with contextlib.closing(wave.open(self.track,'r')) as f:
                        frames = f.getnframes()
                        rate = f.getframerate()
                        self.track_len = frames / float(rate)
                minutes = int(self.track_len // 60)
                seconds = int (self.track_len - (minutes * 60))
                self.Disp_track_len.config(text ="%03d:%02d" % (minutes, seconds % 60))        
        if self.trace > 0:
            print ("album callback exit",self.track_no)
        self.auto_albums = 0
        if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3 or self.cutdown == 6:
                self.render2 = ""
                if self.drive_name[-1] == "*":
                    path = "/" + self.drive_name1 + "/" +self.drive_name2 + "/" + self.drive_name[:-1] + "/" + self.artist_name + " - " + self.album_name + "/" +  "*.jpg"
                elif self.genre_name == "None":
                    path = "/" + self.drive_name1 + "/" +self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
                else:
                    path = "/" + self.drive_name1 + "/" +self.drive_name2 + "/" + self.drive_name + "/" + self.genre_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
                pictures = glob.glob(path)
                if self.trace > 0:
                    print(path)
                if len(pictures) > 0: 
                    if len(pictures) > 1:
                        r = random.randrange(len(pictures))
                        self.image = pictures[r]
                    else:
                        self.image = pictures[0]
                    self.load = Image.open(self.image)
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS) 
                    self.render2 = ImageTk.PhotoImage(self.load)
                    if self.timer4 == 0:
                        self.img.config(image = self.render2)
                elif self.version == 2: 
                    if os.path.exists(self.mp3c_jpg):
                        self.img.config(image = self.renderc)
                else:
                    if os.path.exists(self.mp3_jpg):
                        self.img.config(image = self.render)
        if self.stopstart == 1:
            self.track_no -=1
            if self.trace > 0:
                print (self.track_no)

    def callback(self,a):
      if len(self.tunes) > 0:
        if self.trace > 0:
            print ("callback",self.track_no)
        tpath = self.Disp_artist_name.get() + "^" + self.Disp_album_name.get() + "^" + self.Disp_track_name.get()
        if self.trace > 0:
            print ("callback exit",tpath)
        stop = 0
        k = 0
        while stop == 0 and k < len(self.tunes) - 1:
           a,b,c,d,e,f,g = self.tunes[k].split("^")
           if tpath == a + "^" + b + "^" + c :
              stop = 1
              self.track_no = k
           k +=1
        self.Disp_track_no.config(text = self.track_no + 1) ###
        self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[self.track_no].split('^')
        if self.drive_name[-1] == "*":
            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name[:-1], self.artist_name + " - " + self.album_name, self.track_name)
        elif self.genre_name == "None":
            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name, self.artist_name, self.album_name, self.track_name)
        else:
            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name,self.genre_name,self.artist_name, self.album_name, self.track_name)
        if os.path.exists(self.track):
            if self.track[-4:] == ".mp3":
                audio = MP3(self.track)
                self.track_len = audio.info.length
            elif self.track[-4:] == "flac":
                audio = FLAC(self.track)
                self.track_len = audio.info.length
            elif self.track[-4:] == ".dsf":
                audio = DSF(self.track)
                self.track_len = audio.info.length
            elif self.track[-4:] == ".wav":
                with contextlib.closing(wave.open(self.track,'r')) as f:
                    frames = f.getnframes()
                    rate = f.getframerate()
                    self.track_len = frames / float(rate)
            minutes = int(self.track_len // 60)
            seconds = int (self.track_len - (minutes * 60))
            self.Disp_track_len.config(text ="%03d:%02d" % (minutes, seconds % 60))
        if self.trace > 0:
            print ("callback exit",self.track_no)
        if self.play == 1:
            self.track_no -=1
            self.Next_Track()

    def plist_callback2(self):
      if len(self.tunes) > 0:
        if self.trace > 0:
            print ("plist callback",self.track_no,len(self.tunes))
        self.artistdata = []
        self.Disp_artist_name["values"] = self.artistdata
        if self.shuffle_on == 0 and self.Radio_ON == 0 and self.tracker == 0:
            for x in range(0,len(self.tunes)):
                self.artist_name_1,self.album_name_1,self.track_name_1,self.drive_name_1,self.drive_name1_1,self.drive_name2_1,self.genre_name  = self.tunes[x].split('^')
                self.artistdata.append(self.artist_name_1)
            self.artistdata = list(dict.fromkeys(self.artistdata))
            self.artistdata.sort()
            self.Disp_artist_name["values"] = self.artistdata
            if self.auto_albums == 1 or self.reload == 1:
                self.Disp_artist_name.set(self.artist_name)
                self.reload = 0
        elif self.Radio_ON == 1:
            for x in range(0,len(self.Radio_Stns),3):
                self.artistdata.append(self.Radio_Stns[x])
            self.Disp_artist_name["values"] = self.artistdata
        if self.Radio_ON == 0 and self.tracker == 0:
            self.artist_callback2(0)
        self.tracker = 0

    def artist_callback2(self,a):
      if len(self.tunes) > 0:
        if self.trace > 0:
            print ("artist callback2",self.track_no,self.ac)
        self.albumdata = []
        self.Disp_album_name["values"] = self.albumdata
        if (self.shuffle_on == 0 and self.album_start == 0 and self.Radio_ON == 0) or self.auto_albums == 1:
            for x in range(0,len(self.tunes)):
                self.artist_name_1,self.album_name_1,self.track_name_1,self.drive_name_1,self.drive_name1_1,self.drive_name2_1,self.genre_name  = self.tunes[x].split('^')
                if self.artist_name_1 == self.Disp_artist_name.get():
                    self.albumdata.append(self.album_name_1)
            self.albumdata = list(dict.fromkeys(self.albumdata))
            self.albumdata.sort()
            self.Disp_album_name["values"] = self.albumdata
            if self.ac == 0 and self.bc == 0:
                self.Disp_album_name.set(self.albumdata[0])
        elif self.Radio_ON == 1:
            stop = 0
            k = 0
            while stop == 0 and k < len(self.Radio_Stns):
                if self.Radio_Stns[k] == self.Disp_artist_name.get():
                    stop = 1
                    self.NewRadio = k
                k +=1
            self.Next_Artist()
        if self.Radio_ON == 0:
            self.album_callback2(0)

    def album_callback2(self,a):
      if len(self.tunes) > 0:
        if self.trace > 0:
            print ("album callback2",self.track_no)
        self.trackdata = []
        self.Disp_track_name["values"] = self.trackdata
        self.Disp_track_name.set("Choose a Track")
        if self.shuffle_on == 0 or self.album_start == 1:
            for x in range(0,len(self.tunes)):
                self.artist_name_1,self.album_name_1,self.track_name_1,self.drive_name_1,self.drive_name1_1,self.drive_name2_1,self.genre_name  = self.tunes[x].split('^')
                if self.artist_name_1 == self.Disp_artist_name.get() and self.album_name_1[:-1] == self.Disp_album_name.get()[:-1]:
                    self.trackdata.append(self.track_name_1)
            self.trackdata = list(dict.fromkeys(self.trackdata))
            self.Disp_track_name["values"] = self.trackdata
            if self.ac == 0 and len(self.trackdata) > 0:
                self.Disp_track_name.set(self.trackdata[0])
        self.ac = 0
        self.bc = 0
        tpath = self.Disp_artist_name.get() + "^" + self.Disp_album_name.get() + "^" + self.Disp_track_name.get()
        if self.trace > 0:
            print ("album callback track2",tpath)
        stop = 0
        k = 0
        while stop == 0 and k < len(self.tunes) - 1:
            a,b,c,d,e,f,g = self.tunes[k].split("^")
            if tpath == a + "^" + b + "^" + c :
                stop = 1
                self.track_no = k
            k +=1
        self.Disp_track_no.config(text = self.track_no + 1) 
        self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[self.track_no].split('^')
        if self.drive_name[-1] == "*":
            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name[:-1], self.artist_name + " - " + self.album_name, self.track_name)
        elif self.genre_name == "None":
            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name, self.artist_name, self.album_name, self.track_name)
        else:
            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name,self.genre_name, self.artist_name, self.album_name, self.track_name)
        if os.path.exists(self.track):
                if self.track[-4:] == ".mp3":
                    audio = MP3(self.track)
                    self.track_len = audio.info.length
                elif self.track[-4:] == "flac":
                    audio = FLAC(self.track)
                    self.track_len = audio.info.length
                elif self.track[-4:] == ".dsf":
                    audio = DSF(self.track)
                    self.track_len = audio.info.length
                elif self.track[-4:] == ".wav":
                    with contextlib.closing(wave.open(self.track,'r')) as f:
                        frames = f.getnframes()
                        rate = f.getframerate()
                        self.track_len = frames / float(rate)
                minutes = int(self.track_len // 60)
                seconds = int (self.track_len - (minutes * 60))
                self.Disp_track_len.config(text ="%03d:%02d" % (minutes, seconds % 60))        
        if self.trace > 0:
            print ("album callback exit2",self.track_no)
        self.auto_albums = 0
        if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3 or self.cutdown == 6:
                self.render2 = ""
                if self.drive_name[-1] == "*":
                    path = "/" + self.drive_name1 + "/" +self.drive_name2 + "/" + self.drive_name[:-1] + "/" + self.artist_name + " - " + self.album_name + "/" +  "*.jpg"
                elif self.genre_name == "None":
                    path = "/" + self.drive_name1 + "/" +self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
                else:
                    path = "/" + self.drive_name1 + "/" +self.drive_name2 + "/" + self.drive_name + "/" + self.genre_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
                pictures = glob.glob(path)
                if self.trace > 0:
                    print(path)
                    print(pictures)
                if len(pictures) > 0: 
                    if len(pictures) > 1:
                        r = random.randrange(len(pictures))
                        self.image = pictures[r]
                    else:
                        self.image = pictures[0]
                    self.load = Image.open(self.image)
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS)
                    self.render2 = ImageTk.PhotoImage(self.load)
                    if self.timer4 == 0:
                        self.img.config(image = self.render2)
                elif self.version == 2: 
                    if os.path.exists(self.mp3c_jpg):
                        self.img.config(image = self.renderc)
                else:
                    if os.path.exists(self.mp3_jpg):
                        self.img.config(image = self.render)


    def callback2(self,a):
      if len(self.tunes) > 0:
        if self.trace > 0:
            print ("callback2",self.track_no)
        tpath = self.Disp_artist_name.get() + "^" + self.Disp_album_name.get() + "^" + self.Disp_track_name.get()
        if self.trace > 0:
            print ("callback exit2",tpath)
        stop = 0
        k = 0
        while stop == 0 and k < len(self.tunes) - 1:
           a,b,c,d,e,f,g = self.tunes[k].split("^")
           if tpath == a + "^" + b + "^" + c :
              stop = 1
              self.track_no = k
           k +=1
        self.Disp_track_no.config(text = self.track_no + 1)
        self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[self.track_no].split('^')
        if self.drive_name[-1] == "*":
            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name[:-1], self.artist_name + " - " + self.album_name, self.track_name)
        elif self.genre_name == "None":
            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name, self.artist_name, self.album_name, self.track_name)
        else:
            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name,self.genre_name,self.artist_name, self.album_name, self.track_name)
        if os.path.exists(self.track):
            if self.track[-4:] == ".mp3":
                audio = MP3(self.track)
                self.track_len = audio.info.length
            elif self.track[-4:] == "flac":
                audio = FLAC(self.track)
                self.track_len = audio.info.length
            elif self.track[-4:] == ".dsf":
                audio = DSF(self.track)
                self.track_len = audio.info.length
            elif self.track[-4:] == ".wav":
                with contextlib.closing(wave.open(self.track,'r')) as f:
                    frames = f.getnframes()
                    rate = f.getframerate()
                    self.track_len = frames / float(rate)
            minutes = int(self.track_len // 60)
            seconds = int (self.track_len - (minutes * 60))
            self.Disp_track_len.config(text ="%03d:%02d" % (minutes, seconds % 60))
        if self.trace > 0:
            print ("callback exit2",self.track_no)
        if self.play == 1:
            self.track_no -=1
            self.Next_Track()

  
    def Show_Track(self):
        if self.trace > 0:
            print ("Show Track", self.track_no,self.play)
        if len(self.tunes) > 0:
            if self.album_start == 0:
                self.Disp_Total_tunes.config(text =len(self.tunes))
                self.Disp_track_no.config(text =self.track_no + 1)
            self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[self.track_no].split('^')
            if self.drive_name[-1] == "*":
                self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name[:-1], self.artist_name + " - " + self.album_name, self.track_name)
            elif self.genre_name == "None":
                self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name, self.artist_name, self.album_name, self.track_name)
            else:
                self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name,self.genre_name, self.artist_name, self.album_name, self.track_name)
            if (self.cutdown != 7 and self.cutdown != 8) and self.imgxon == 0:
                self.Disp_artist_name.config(fg = "black",text =self.artist_name)
                self.Disp_album_name.config(fg = "black",text =self.album_name)
                if self.track[-4:] == ".mp3" or self.track[-4:] == ".wav" or self.track[-4:] == ".dsf" or self.track[-4:] == ".m4a":
                    self.Disp_track_name.config(fg = "black",text =self.track_name[:-4])
                elif self.track[-4:] == "flac":
                    self.Disp_track_name.config(fg = "black",text =self.track_name[:-5])
            self.Disp_played.config(fg = "black",text ="000:00")
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3 or self.cutdown == 2:
                self.Disp_Drive.config(fg = 'black')
                if self.drive_name1 == "run":
                    self.Disp_Drive.config(text = "RAM")
                else:
                    self.Disp_Drive.config(text = "/" + self.drive_name1 + "/" + self.drive_name2  + "/" + self.drive_name)
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3 or self.cutdown == 6:
                self.render2 = ""
                if self.drive_name[-1] == "*":
                    path = "/" + self.drive_name1 + "/" +self.drive_name2 + "/" + self.drive_name[:-1] + "/" + self.artist_name + " - " + self.album_name + "/" +  "*.jpg"
                elif self.genre_name == "None":
                    path = "/" + self.drive_name1 + "/" +self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
                else:
                    path = "/" + self.drive_name1 + "/" +self.drive_name2 + "/" + self.drive_name + "/" + self.genre_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
                pictures = glob.glob(path)
                if self.trace > 0:
                    print(path)
                    print(pictures)
                if len(pictures) > 0: 
                    if len(pictures) > 1:
                        r = random.randrange(len(pictures))
                        self.image = pictures[r]
                    else:
                        self.image = pictures[0]
                    self.load = Image.open(self.image)
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS)
                    self.render2 = ImageTk.PhotoImage(self.load)
                    if self.timer4 == 0:
                        self.img.config(image = self.render2)
                elif self.version == 2: 
                    if os.path.exists(self.mp3c_jpg):
                        self.img.config(image = self.renderc)
                else:
                    if os.path.exists(self.mp3_jpg):
                        self.img.config(image = self.render)
            if os.path.exists(self.track):
                if self.track[-4:] == ".mp3":
                    audio = MP3(self.track)
                    self.track_len = audio.info.length
                elif self.track[-4:] == "flac":
                    audio = FLAC(self.track)
                    self.track_len = audio.info.length
                elif self.track[-4:] == ".dsf":
                    audio = DSF(self.track)
                    self.track_len = audio.info.length
                elif self.track[-4:] == ".m4a":
                    audio = MP4(self.track)
                    self.track_len = audio.info.length
                elif self.track[-4:] == ".wav":
                    with contextlib.closing(wave.open(self.track,'r')) as f:
                        frames = f.getnframes()
                        rate = f.getframerate()
                        self.track_len = frames / float(rate)
                minutes = int(self.track_len // 60)
                seconds = int (self.track_len - (minutes * 60))
                self.Disp_track_len.config(text ="%03d:%02d" % (minutes, seconds % 60))
    
                if self.cutdown < 6:
                    if self.track[-4:] == "flac" and len(audio) > 0:
                        try:
                            track_title = audio["title"]
                            track_number = audio["tracknumber"]
                            track = str(track_number )[2:-2]
                            if track_number < 10:
                                track = "0" + track
                            self.Disp_track_name.config(text = track + " " + str(track_title)[2:-2])
                        except:
                            pass
                    elif self.track[-4:] == ".mp3" and len(audio) > 0:
                        try:
                            track_title = audio["TIT2"].text
                            track_number = audio["TRCK"].text
                            if track_number.count('/') == 1:
                                tn1,tn2 = track_number.split("/")
                                track = str(tn1 )[2:]
                                track_title = track_title[2:-2]
                            else:
                                tn1 = int(track_number[0])
                                track = int(track_number[0])
                                track_title = track_title[0]
                            if tn1 < 10:
                                 track = "0" + str(tn1)
                            if self.cutdown >= 7:
                                 self.Disp_track_name.set(track + " " + str(track_title))
                            else:
                                self.Disp_track_name.config(text = track + " " + str(track_title))
                        except:
                            pass
                elif self.cutdown >= 7:
                    self.Disp_artist_name.set(self.artist_name)
                    if self.cc == 1:
                        self.bc = 1
                        self.cc = 0
                    self.Disp_album_name.set(self.album_name)
                    self.Disp_track_name.set(self.track_name)
                    self.Disp_track_no.config(text = self.track_no + 1)
                    self.plist_callback()
                else:
                    if self.track_no < len(self.tunes) - 1:
                        self.artist_name_1,self.album_name_1,self.track_name_1,self.drive_name_1,self.drive_name1_1,self.drive_name2_1,self.genre_name1 = self.tunes[self.track_no + 1].split('^')
                        if self.artist_name_1 == self.artist_name and self.album_name_1[:-1] == self.album_name[:-1]:
                            self.Disp_track_name1.config(fg = "black",bg = "white",text =self.track_name_1[:-4], borderwidth=2, relief="groove")
                        elif self.album_start == 0:
                            self.Disp_track_name1.config(fg = "#666",bg = "white",text =self.artist_name_1 + " - " + self.track_name_1[:-4], borderwidth=2, relief="groove")
                        else:
                            self.Disp_track_name1.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    else:
                        self.Disp_track_name1.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if self.track_no < len(self.tunes) - 2:
                        self.artist_name_2,self.album_name_2,self.track_name_2,self.drive_name_2,self.drive_name1_2,self.drive_name2_2,self.genre_name2  = self.tunes[self.track_no + 2].split('^')
                        if self.artist_name_2 == self.artist_name and self.album_name_2[:-1] == self.album_name[:-1]:
                            self.Disp_track_name2.config(fg = "black",bg = "white",text =self.track_name_2[:-4], borderwidth=2, relief="groove")
                        elif self.album_start == 0:
                            self.Disp_track_name2.config(fg = "#666",bg = "white",text =self.artist_name_2 + " - " + self.track_name_2[:-4], borderwidth=2, relief="groove")
                        else:
                            self.Disp_track_name2.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    else:
                        self.Disp_track_name2.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if self.track_no < len(self.tunes) - 3:
                        self.artist_name_3,self.album_name_3,self.track_name_3,self.drive_name_3,self.drive_name1_3,self.drive_name2_3,self.genre_name3  = self.tunes[self.track_no + 3].split('^')
                        if self.artist_name_3 == self.artist_name and self.album_name_3[:-1] == self.album_name[:-1]:
                            self.Disp_track_name3.config(fg = "black",bg = "white",text =self.track_name_3[:-4], borderwidth=2, relief="groove")
                        elif self.album_start == 0:
                            self.Disp_track_name3.config(fg = "#666",bg = "white",text =self.artist_name_3 + " - " + self.track_name_3[:-4], borderwidth=2, relief="groove")
                        else:
                            self.Disp_track_name3.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    else:
                        self.Disp_track_name3.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if self.track_no < len(self.tunes) - 4:
                        self.artist_name_4,self.album_name_4,self.track_name_4,self.drive_name_4,self.drive_name1_4,self.drive_name2_4,self.genre_name4  = self.tunes[self.track_no + 4].split('^')
                        if self.artist_name_4 == self.artist_name and self.album_name_4[:-1] == self.album_name[:-1]:
                            self.Disp_track_name4.config(fg = "black",bg = "white",text =self.track_name_4[:-4], borderwidth=2, relief="groove")
                        elif self.album_start == 0:
                            self.Disp_track_name4.config(fg = "#666",bg = "white",text =self.artist_name_4 + " - " + self.track_name_4[:-4], borderwidth=2, relief="groove")
                        else:
                            self.Disp_track_name4.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    else:
                        self.Disp_track_name4.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if self.track_no < len(self.tunes) - 5:
                        self.artist_name_5,self.album_name_5,self.track_name_5,self.drive_name_5,self.drive_name1_5,self.drive_name2_5,self.genre_name5  = self.tunes[self.track_no + 5].split('^')
                        if self.artist_name_5 == self.artist_name and self.album_name_5[:-1] == self.album_name[:-1]:
                            self.Disp_track_name5.config(fg = "black",bg = "white",text =self.track_name_5[:-4], borderwidth=2, relief="groove")
                        elif self.album_start == 0:
                            self.Disp_track_name5.config(fg = "#666",bg = "white",text =self.artist_name_5 + " - " + self.track_name_5[:-4], borderwidth=2, relief="groove")
                        else:
                            self.Disp_track_name5.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    else:
                        self.Disp_track_name5.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if self.track_no < len(self.tunes) - 6:
                        self.artist_name_6,self.album_name_6,self.track_name_6,self.drive_name_6,self.drive_name1_6,self.drive_name2_6,self.genre_name6  = self.tunes[self.track_no + 6].split('^')
                        if self.artist_name_6 == self.artist_name and self.album_name_6[:-1] == self.album_name[:-1]:
                            self.Disp_track_name6.config(fg = "black",bg = "white",text =self.track_name_6[:-4], borderwidth=2, relief="groove")
                        elif self.album_start == 0:
                            self.Disp_track_name6.config(fg = "#666",bg = "white",text =self.artist_name_6 + " - " + self.track_name_6[:-4], borderwidth=2, relief="groove")
                        else:
                            self.Disp_track_name6.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    else:
                        self.Disp_track_name6.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if self.track_no < len(self.tunes) - 7:
                        self.artist_name_7,self.album_name_7,self.track_name_7,self.drive_name_7,self.drive_name1_7,self.drive_name2_7,self.genre_name7  = self.tunes[self.track_no + 7].split('^')
                        if self.artist_name_7 == self.artist_name and self.album_name_7[:-1] == self.album_name[:-1]:
                            self.Disp_track_name7.config(fg = "black",bg = "white",text =self.track_name_7[:-4], borderwidth=2, relief="groove")
                        elif self.album_start == 0:
                            self.Disp_track_name7.config(fg = "#666",bg = "white",text =self.artist_name_7 + " - " + self.track_name_7[:-4], borderwidth=2, relief="groove")
                        else:
                            self.Disp_track_name7.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    else:
                        self.Disp_track_name7.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if self.track_no < len(self.tunes) - 8:
                        self.artist_name_8,self.album_name_8,self.track_name_8,self.drive_name_8,self.drive_name1_8,self.drive_name2_8,self.genre_name8  = self.tunes[self.track_no + 8].split('^')
                        if self.artist_name_8 == self.artist_name and self.album_name_8[:-1] == self.album_name[:-1]:
                            self.Disp_track_name8.config(fg = "black",bg = "white",text =self.track_name_8[:-4], borderwidth=2, relief="groove")
                        elif self.album_start == 0:
                            self.Disp_track_name8.config(fg = "#666",bg = "white",text =self.artist_name_8 + " - " + self.track_name_8[:-4], borderwidth=2, relief="groove")
                        else:
                            self.Disp_track_name8.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    else:
                        self.Disp_track_name8.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if self.track_no < len(self.tunes) - 9:
                        self.artist_name_9,self.album_name_9,self.track_name_9,self.drive_name_9,self.drive_name1_9,self.drive_name2_9,self.genre_name9  = self.tunes[self.track_no + 9].split('^')
                        if self.artist_name_9 == self.artist_name and self.album_name_9[:-1] == self.album_name[:-1]:
                            self.Disp_track_name9.config(fg = "black",bg = "white",text =self.track_name_9[:-4], borderwidth=2, relief="groove")
                        elif self.album_start == 0:
                            self.Disp_track_name9.config(fg = "#666",bg = "white",text =self.artist_name_9 + " - " + self.track_name_9[:-4], borderwidth=2, relief="groove")
                        else:
                            self.Disp_track_name9.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    else:
                        self.Disp_track_name9.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                            
            elif self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3:
                if self.m3u_no != 0:
                    self.Disp_Drive.config(text = "MISSING")
            else:
                self.Disp_artist_name.config(fg = "red",text =self.artist_name)
                self.Disp_album_name.config(fg = "red",text =self.album_name)
                if self.track[-4:] == ".mp3" or self.track[-4:] == ".wav" or self.track[-4:] == ".dsf" or self.track[-4:] == ".m4a":
                    if self.cutdown != 7 and self.cutdown != 8:
                        self.Disp_track_name.config(fg = "black",text =self.track_name[:-4])
                    else:
                        self.Disp_track_name.set(self.track_name[:-4])
                elif self.track[-4:] == "flac":
                    if self.cutdown != 7 and self.cutdown != 8:
                        self.Disp_track_name.config(fg = "black",text =self.track_name[:-5])
                    else:
                        self.Disp_track_name.set(self.track_name[:-5])
            
            
    def Play(self):
      if self.bt_on == 0:
        if self.trace > 0:
            print ("Play")
        self.light_on = time.monotonic()
        self.f_volume = self.volume
        self.Button_Next_AZ.config(bg = 'light blue', text = "Info")
        if self.cutdown != 4 and self.cutdown != 5  and self.cutdown != 6 and self.cutdown != 1 and self.Radio_ON == 0:
            self.L6.config(text= "Playlist :")
        if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2:
            self.Button_volume.config(text = self.volume)
        else:
            self.Button_Vol_UP.config(text = "Vol >   " + str(self.volume))
        self.muted     = 0
        self.R_Stopped = 0
        # check for audio mixers
        if len(alsaaudio.mixers()) > 0:
            for mixername in alsaaudio.mixers():
                if str(mixername) == "PCM" or str(mixername) == "DSP Program" or str(mixername) == "Master" or str(mixername) == "Capture" or str(mixername) == "Headphone" or str(mixername) == "HDMI":
                    self.m = alsaaudio.Mixer(mixername)
                    if self.Radio_ON == 0:
                        if (self.cutdown == 0 or self.cutdown == 2 or cutdown == 3) and self.gapless == 0:
                            self.Button_Gapless.config(fg = "black",bg = "light blue")
                        self.Button_Pause.config(fg = "black",bg = "light blue")
                else:
                    self.m = alsaaudio.Mixer(alsaaudio.mixers()[0])
                    self.version = 1
                    self.BT      = 1
                    self.gapless = 1
                    if self.Radio_ON == 0:
                        if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or cutdown == 3:
                            self.Button_Gapless.config(fg = "light gray",bg = "light gray")
                        self.Button_Pause.config(fg = "light gray",bg = "light gray")
            self.m.setvolume(self.volume)
            self.mixername = mixername
            os.system("amixer -D pulse sset Master " + str(self.volume) + "%")
            if self.mixername == "DSP Program":
                os.system("amixer set 'Digital' " + str(self.volume + 107))
            
        if self.album_start == 0 and self.stopstart != 1 and len(self.tunes) > 0 and self.Radio_ON == 0:
            self.stopstart = 1
            self.light_on = time.monotonic()
            self.play = 0
            self.start2 = time.monotonic()
            self.wheel = 0
            if self.BT == 0:
                player.time_pos
            self.start_track_no = self.track_no
            if self.cutdown >= 7 or self.cutdown == 0 or self.cutdown == 2:
                self.Button_Bluetooth.config(bg = 'light gray')
            if self.cutdown == 6 or self.cutdown == 4 or self.cutdown == 5:
                self.Button_Pause.config(text = "Pause")
                if self.repeat == 0 and self.repeat_album == 0:
                    self.Button_Radio.config(bg = "light blue", fg = "black", text = "Repeat")
                elif self.repeat == 1 and self.repeat_album == 0:
                    self.Button_Radio.config(bg = "green", fg = "black", text = "Repeat")
                elif self.repeat == 1 and self.repeat_album == 1:
                    self.Button_Radio.config(bg = "green", fg = "black", text = "Repeat Album")
            else:
                self.Button_Radio.config(bg = "light grey", fg = "black") 
            self.auto_play = 1
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            self.Start_Play()
        elif self.stopstart == 1 and self.album_start == 0:
            self.Radio_ON  = 0
            self.auto_play = 0
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            self.Stop_Play()

    def Wheel_Opt_Button(self,u):
        if self.cutdown != 1 and self.cutdown != 4 and self.cutdown != 5 :
            if os.path.exists(self.mp3_jpg):
                if self.gapless == 0 and self.paused == 0:
                    if os.path.exists(self.mp3c_jpg) and self.Radio_ON == 0:
                        self.img.config(image = self.renderc)
                else:
                    if os.path.exists(self.mp3_jpg):
                        self.img.config(image = self.render)
                self.timer4 = time.monotonic()
            x = self.master.winfo_pointerx()
            y = self.master.winfo_pointery()
            abs_x = self.master.winfo_pointerx() - self.master.winfo_rootx()
            abs_y = self.master.winfo_pointery() - self.master.winfo_rooty()
            if abs_x > 314 and abs_x < 514 and abs_y > 152 and abs_y < 369 and self.cutdown == 6 and self.Radio_ON == 0:
                y_pos = int((abs_y - 152)/24)
                self.track_no += y_pos
                if self.album_start == 1:
                    if self.track_no > self.tcount:
                        self.track_no = self.tcount
                    elif self.track_no > len(self.tunes) - 1:
                        self.track_no = len(self.tunes) - 1
                if self.stopstart == 1 :
                    self.track_no -= 1
                if self.track_no > len(self.tunes) -1:
                   self.track_no = 0 
                if self.play == 1:
                   if self.version == 1:
                       self.p.kill()
                   else:
                       player.stop()
                   self.start = 0
                   if self.album_start == 0:
                       self.count1 = 0
                       self.count2 = 0
                       self.Time_Left_Play()
                   else:
                       self.Play()
                else:
                    self.count1 = 0
                    self.count2 = 0
                    self.Time_Left_Play()
            if abs_x > 314 and abs_x < 514 and abs_y > 152 and abs_y < 369 and self.cutdown == 6 and self.Radio_ON == 1 and self.Radio_RON == 0:
                y_pos = int((abs_y - 152)/24) + 1
               

                self.copy = 0
                if self.cutdown != 7 and self.cutdown != 8:
                    self.Disp_track_name.config(text = "")
                else:
                    self.Disp_track_name.set("")
                if self.Radio_Stns[self.Radio + 2] == 0:
                    self.q.kill()
                else:
                    self.q.kill()
                    self.r.kill()
                self.Radio = (y_pos -1) * 3
                if self.Radio > len(self.Radio_Stns) - 1:
                    self.Radio = 0
                if self.Radio_Stns[self.Radio + 2] == 0:
                    self.q = subprocess.Popen(["mplayer", "-nocache", self.Radio_Stns[self.Radio + 1]] , shell=False)
                else:
                    self.r = subprocess.Popen(["streamripper", self.Radio_Stns[self.Radio + 1],"-r","--xs_offset=-9000","-z","-l", "99999","-d", "/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings","-a",self.Radio_Stns[self.Radio]], shell=False)
                    time.sleep(1)
                    self.q = subprocess.Popen(["mplayer", "-nocache", "http://localhost:8000"] , shell=False)
                    track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
                    if len(track) == 0:
                        time.sleep(2)
                if self.Radio_Stns[self.Radio + 2]  > 0 and self.record == 1:
                    self.Button_Pause.config(fg = "black", bg = "light blue", text = "RECORD")
                    if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and  self.cutdown != 6 and self.touchscreen == 1:
                        self.L8.config(text = ".mp3")
                else:
                    self.Button_Pause.config(fg = "black", bg = "light grey", text = "Pause")
                    if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and  self.cutdown != 6 and self.touchscreen == 1:
                        self.L8.config(text = "")
                self.Name = self.Radio_Stns[self.Radio]
                self.Disp_artist_name.config(text = self.Name)
                if self.cutdown != 4 and self.cutdown !=5 and self.cutdown !=1:
                    if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg"):
                        self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".jpg")
                        if self.cutdown != 2:
                            if self.cutdown == 8:
                                self.load = self.load.resize((320,320), Image.LANCZOS)
                            else:
                                self.load = self.load.resize((218, 218), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((150, 150), Image.LANCZOS)
                        self.render2 = ImageTk.PhotoImage(self.load)
                        self.img.config(image = self.render2)
                    elif os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                        self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".png")
                        if self.cutdown != 2:
                            if self.cutdown == 8:
                                self.load = self.load.resize((320,320), Image.LANCZOS)
                            else:
                                self.load = self.load.resize((218, 218), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((150, 150), Image.LANCZOS)
                        self.render2 = ImageTk.PhotoImage(self.load)
                        self.img.config(image = self.render2)
                    elif os.path.exists(self.radio_jpg):
                        self.load = Image.open(self.radio_jpg)
                        if self.cutdown != 2:
                            if self.cutdown == 8:
                                self.load = self.load.resize((320,320), Image.LANCZOS)
                            else:
                                self.load = self.load.resize((218, 218), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((150, 150), Image.LANCZOS)
                        self.render3 = ImageTk.PhotoImage(self.load)
                        self.img.config(image = self.render3)
                track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
                with open('Lasttrack3.txt', 'w') as f:
                    f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
                self.Check_Record()
                if len(track) == 0  and self.Radio_Stns[self.Radio + 2]  > 0:
                    if self.rotary_pos== 0:
                        messagebox.showinfo("WARNING!","Check Recordable entry set correctly for this stream")
            else:
                if cutdown == 0 or cutdown == 2 or self.cutdown == 7:
                    x2 = abs_x - 107
                    y2 = abs_y - 356
                elif cutdown == 8:
                    x2 = abs_x - 171
                    y2 = abs_y - 546
                elif cutdown == 6:
                    x2 = abs_x - 147
                    y2 = abs_y - 259
                else:
                    x2 = abs_x - 142
                    y2 = abs_y - 494
                if math.sqrt((x2*x2)+ (y2*y2)) < 30 and self.stopstart == 0 and self.Radio_ON == 0:
                    self.wheel_opt +=1
                    if (self.wheel_opt > 4 and (self.cutdown == 6 or self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3 or self.cutdown == 2)) or (self.wheel_opt > 3 and (self.cutdown != 6 and self.cutdown != 0 and( self.cutdown != 7 and self.cutdown != 8) and self.cutdown != 3 and self.cutdown != 2)):
                        self.wheel_opt = 0
                    if self.cutdown != 5 and self.cutdown != 6:
                        self.Button_Prev_PList.config(fg = "black")
                    self.Button_Prev_Artist.config(fg = "black")
                    self.Button_Prev_Album.config(fg = "black")
                    self.Button_Prev_Track.config(fg = "black")
                    if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3 or self.cutdown == 2 or self.cutdown == 6:
                        self.Button_Next_AZ.config(fg = "black")
                    if self.wheel_opt == 0:
                        self.Button_Next_Artist.config(fg = "red")
                    if self.wheel_opt == 1:
                        self.Button_Next_Album.config(fg = "red")
                    if self.wheel_opt == 2:
                        self.Button_Next_Track.config(fg = "red")
                    if self.wheel_opt == 3  and self.cutdown != 6:
                        self.Button_Next_PList.config(fg = "red")
                    if self.wheel_opt == 4 and (self.cutdown == 0 or self.cutdown == 3 or self.cutdown == 2 or self.cutdown == 6):
                        self.Button_Next_AZ.config(fg = "red")
                elif (math.sqrt((x2*x2)+ (y2*y2)) < 30 and self.Radio_ON == 0) or (math.sqrt((x2*x2)+ (y2*y2)) < 100 and self.Radio_ON == 1):
                    self.Mute()


    def Bluetooth(self):
      if self.Radio_ON == 0 and self.album_start == 0 and self.stopstart != 1: 
          if self.bt_on == 0:
              os.system("bluetoothctl power on")
              self.Button_Bluetooth.config(bg = "red")
              self.Button_Start.config(bg  = "light grey", fg = "black")
              self.Button_TAlbum.config(bg  = "light grey", fg = "black")
              if self.Button_Radi_on == 1:
                  self.Button_Radio.config(bg  = "light grey", fg = "black")
              self.bt_on = 1
          else:
              os.system("bluetoothctl power off")
              if self.rotary_pos== 0:
                  self.Button_Bluetooth.config(bg = "light blue")
              else:
                  self.Button_Bluetooth.config(bg = "yellow")
              self.Button_Start.config(bg  = "green", fg = "black")
              self.Button_TAlbum.config(bg  = "blue", fg = "black")
              if self.Button_Radi_on == 1:
                  self.Button_Radio.config(bg  = "light blue", fg = "black")
              self.bt_on = 0

        
    def Start_Play(self):
        with open('Lasttrack3.txt', 'w') as f:
            f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
        if self.album_start == 0 and self.Radio_ON == 0 and self.Radio_ON == 0:
            if self.cutdown != 5 and self.cutdown != 6:
                self.Button_Next_PList.config(fg = "black")
            self.Button_Next_Artist.config(fg = "black")
            self.Button_Next_Album.config(fg = "black")
            self.Button_Next_Track.config(fg = "black")
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3 or self.cutdown == 2:
                self.Button_Next_AZ.config(fg = "black")
            if self.cutdown == 4:
                self.Button_Track_m3u.config(bg = "light grey", fg = "black")
                self.Button_Artist_m3u.config(bg = "light grey", fg = "black")
                self.Button_Album_m3u.config(bg = "light grey", fg = "black")
                self.Button_PList_m3u.config(bg = "light grey", fg = "black")
             
        if len(self.tunes) > 0 and self.play == 0 and self.paused == 0 and self.Radio_ON == 0:
          if self.trace > 0:
              print ("Start_Play",self.track_no)
          with open('Lasttrack3.txt', 'w') as f:
              f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
          self.Disp_track_no.config(text =self.track_no + 1)
          if self.cutdown != 7 and self.cutdown != 8:
              self.Show_Track()
          self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[self.track_no].split('^')
          if self.drive_name[-1] == "*":
              self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name[:-1], self.artist_name + " - " + self.album_name, self.track_name)
          elif self.genre_name == "None":
              self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name, self.artist_name, self.album_name, self.track_name)
          else:
              self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name,self.genre_name, self.artist_name, self.album_name, self.track_name)
          if self.cutdown >= 7:
              self.Disp_artist_name.set(self.artist_name)
              self.Disp_album_name.set(self.album_name)
              self.Disp_track_name.set(self.track_name)
          if os.path.exists(self.track):  
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3:
                self.Disp_Drive.config(fg = 'black')
                if self.drive_name1 == "run":
                    self.Disp_Drive.config(text = "RAM")
                else:
                    self.Disp_Drive.config(text = "/" + self.drive_name1 + "/" + self.drive_name2  + "/" + self.drive_name) 
                self.Disp_Name_m3u.config(background="light gray", foreground="black")
                self.Disp_Name_m3u.delete('1.0','20.0')
            if os.path.exists(self.track):
                if self.trace > 0:
                    print ("Start_Play - Track exists", self.track)
                if self.cutdown == 4:
                    self.Button_Next_AZ.config(text = "NextAZ", bg = "light grey", fg = "black")
                if self.version == 2:
                    if self.rotary_pos== 0:
                        self.Button_Reload.config(bg = "light blue", fg = "black", text = "Skip Fwd")
                    else:
                        if self.rot_pos == 11:
                            self.Button_Reload.config(bg = "yellow", fg = "black", text = "Skip Fwd")
                        else:
                            self.Button_Reload.config(bg = "light blue", fg = "black", text = "Skip Fwd")
                            
                else:
                    self.Button_Reload.config(bg = "light grey", fg = "black", text = "Skip Fwd")
                if self.version == 2:
                    player.loadfile(self.track)
                    player.time_pos = 0
                else:
                    self.p = subprocess.Popen(["mplayer",self.track], shell=False)
                if self.track[-4:] == ".mp3":
                    audio = MP3(self.track)
                    self.track_len = audio.info.length
                elif self.track[-4:] == "flac":
                    audio = FLAC(self.track)
                    self.track_len = audio.info.length
                elif self.track[-4:] == ".dsf":
                    audio = DSF(self.track)
                    self.track_len = audio.info.length
                elif self.track[-4:] == ".m4a":
                    audio = MP4(self.track)
                    self.track_len = audio.info.length
                elif self.track[-4:] == ".wav":
                    with contextlib.closing(wave.open(self.track,'r')) as f:
                        frames = f.getnframes()
                        rate = f.getframerate()
                        self.track_len = frames / float(rate)
                minutes = int(self.track_len // 60)
                seconds = int (self.track_len - (minutes * 60))
                self.Disp_track_len.config(text ="%03d:%02d" % (minutes, seconds % 60))
                self.play = 1
                self.start = time.monotonic()
                self.pstart = time.monotonic()
                if self.album_start == 1:
                    if self.rotary_pos == 0:
                        self.Button_TAlbum.config(bg = "red",fg = "black",text = "STOP")
                    elif self.rotary_pos == 1 and self.rot_pos == 4:
                        self.Button_TAlbum.config(bg = "yellow",fg = "black",text = "STOP")
                    else:
                        self.Button_TAlbum.config(bg = "blue",fg = "black",text = "STOP")
                    self.Button_Start.config(bg = "light gray",fg = "black",text = "PLAY Playlist")
                else:
                    if self.rotary_pos == 0:
                        self.Button_Start.config(bg = "red",fg = "black",text = "STOP")
                    elif rotary_pos == 1 and self.rot_pos == 3:
                        self.Button_Start.config(bg = "yellow",fg = "black",text = "STOP")
                    elif self.rotary_pos == 1 :
                        self.Button_Start.config(bg = "green",fg = "black",text = "STOP")
                    self.Button_TAlbum.config(bg = "light gray",fg = "black",text = "PLAY Album")
                self.Start_Play2()
            else:
                if self.trace > 0:
                    print ("Start_Play - Track NOT exists")
                self.Disp_artist_name.config(fg = "red",text =self.artist_name)
                self.Disp_album_name.config(fg = "red",text =self.album_name)
                self.Disp_track_name.config(fg = "red",text =self.track_name[:-4])
                if self.cutdown == 0 or self.cutdown == 3 or self.cutdown >= 7:
                    self.Disp_Drive.config(text = "MISSING")
                stop = 0
                while (self.tunes[self.track_no].split('^')[3]) == self.drive_name and stop == 0:
                    self.track_no +=1
                    if self.track_no > len(self.tunes) - 1:
                        self.track_no = 0
                        if self.trace > 0:
                            print ("Start_Play - Stopped Play (No track found)")
                        self.play = 1
                        stop = 1
                    else:
                        self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[self.track_no].split('^')
                        if self.drive_name[-1] == "*":
                            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name[:-1], self.artist_name + " - " + self.album_name, self.track_name)
                        elif self.genre_name == "None":
                            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name, self.artist_name, self.album_name, self.track_name)
                        else:
                            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name,self.genre_name, self.artist_name, self.album_name, self.track_name)
                        if self.trace > 0:
                            print ("Checking Next Track...", self.track_no)
                        if os.path.exists(self.track):
                            if self.trace > 0:
                                print ("Start_Play - Play Track (next Track found)")
                            self.play = 0
                            stop = 1
                if self.play == 0:
                    self.Start_Play()
                else:
                    self.Stop_Play()
          else:
              print("No track")
              self.album_start = 0
              self.stopstart = 0
              self.Button_TAlbum.config(bg = "blue",fg = "black",text = "PLAY Album")
              self.Show_Track()
                    
        elif self.album_start == 1 and self.Radio_ON == 0:
            self.Start_Play2()
            
    def Start_Play2(self):
        self.stop = 0
        if self.album_start == 0:
            if self.trace > 0:
                print ("Start_Play2",self.track_no)
            self.total = 0
            self.count1 = 0
            self.count2 = 0
            counter = self.track_no + 1
            self.minutes = 0
            while counter < len(self.tunes) and self.stop == 0:
                self.artist_name1,self.album_name1,self.track_name1,self.drive_name10,self.drive_name11,self.drive_name21,self.genre_name2 = self.tunes[counter].split('^')
                counter +=1
                if self.drive_name10[-1] == "*":
                    self.track = os.path.join("/" + self.drive_name11,self.drive_name21,self.drive_name10[:-1], self.artist_name1 + " - " + self.album_name1, self.track_name1)
                elif self.genre_name2 == "None":
                    self.track = os.path.join("/" + self.drive_name11,self.drive_name21,self.drive_name10, self.artist_name1, self.album_name1, self.track_name1)
                else:
                    self.track = os.path.join("/" + self.drive_name11,self.drive_name21,self.drive_name10,self.genre_name,self.artist_name1, self.album_name1, self.track_name1)
                if os.path.exists(self.track):
                    if self.track[-4:] == ".mp3":       
                        audio = MP3(self.track)
                        self.total += audio.info.length
                    if self.track[-4:] == "flac":       
                        audio = FLAC(self.track)
                        self.total += audio.info.length
                    if self.track[-4:] == ".dsf":
                        audio = DSF(self.track)
                        self.total += audio.info.length
                    if self.track[-4:] == ".m4a":
                        audio = MP4(self.track)
                        self.total += audio.info.length
                    if self.track[-4:] == ".wav":
                        with contextlib.closing(wave.open(self.track,'r')) as f:
                            frames = f.getnframes()
                            rate = f.getframerate()
                            self.track_len = frames / float(rate)
                        self.total += self.track_len
                    if self.total > self.Disp_max_time * 60:
                        self.stop = 1
        else:
            stop = 0
            self.album_time = 0
            self.album_track += 1
            counter = self.track_no + 1
            if counter > len(self.tunes) - 1:
                stop = 2
            while stop == 0 and (self.tunes[counter].split('^')[1][0:-1]) == self.album_name[0:-1] and self.tunes[counter].split('^')[0] == self.artist_name:
                self.artist_name1,self.album_name1,self.track_name1,self.drive_name10,self.drive_name11,self.drive_name21,self.genre_name  = self.tunes[counter].split('^')
                if self.drive_name[-1] == "*":
                    self.track = os.path.join("/" + self.drive_name11,self.drive_name21,self.drive_name10[:-1], self.artist_name1 + " - " + self.album_name1, self.track_name1)
                elif self.genre_name == "None":
                    self.track = os.path.join("/" + self.drive_name11,self.drive_name21,self.drive_name10, self.artist_name1, self.album_name1, self.track_name1)
                else:
                    self.track = os.path.join("/" + self.drive_name11,self.drive_name21,self.drive_name10,self.genre_name, self.artist_name1, self.album_name1, self.track_name1)
                
                if os.path.exists(self.track):
                    if self.track[-4:] == ".mp3":       
                        audio = MP3(self.track)
                        self.album_time += audio.info.length
                    if self.track[-4:] == "flac":       
                        audio = FLAC(self.track)
                        self.album_time += audio.info.length
                    if self.track[-4:] == ".dsf":
                        audio = DSF(self.track)
                        self.album_time += audio.info.length
                    if self.track[-4:] == ".m4a":
                        audio = MP4(self.track)
                        self.album_time += audio.info.length
                    if self.track[-4:] == ".wav":
                        with contextlib.closing(wave.open(self.track,'r')) as f:
                            frames = f.getnframes()
                            rate = f.getframerate()
                            self.track_len = frames / float(rate)
                        self.album_time += self.track_len
                counter +=1
                if counter > len(self.tunes) - 1:
                    counter -=1
                    stop = 2
            if stop == 2:
                counter -=1
            self.Disp_track_no.config (text = (self.track_no - self.scount) + 1)
            if self.album_track == 1 and len(self.tunes) > 1:
                self.countex = counter - self.track_no + stop
                self.Disp_Total_tunes.config(text = counter - self.track_no + stop)
                
            self.total = self.album_time
        self.start2 = time.monotonic()
        self.render2 = ""
        if self.drive_name[-1] == "*":
            path = "/" + self.drive_name1 + "/" +self.drive_name2 + "/" + self.drive_name[:-1] + "/" + self.artist_name + " - " + self.album_name + "/" +  "*.jpg"
        elif self.genre_name == "None":
            path = "/" + self.drive_name1 + "/" +self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
        else:
            path = "/" + self.drive_name1 + "/" +self.drive_name2 + "/" + self.drive_name + "/" + self.genre_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
        if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3 or self.cutdown == 6:
            pictures = glob.glob(path)
            self.render2 = ""
            if len(pictures) > 0:
                if len(pictures) > 1:
                   r = random.randrange(len(pictures))
                   self.image = pictures[r]
                else:
                   self.image = pictures[0]
                self.load = Image.open(self.image)
                if self.cutdown != 2:
                    if self.cutdown == 8:
                        self.load = self.load.resize((320,320), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((218, 218), Image.LANCZOS)
                else:
                    self.load = self.load.resize((150, 150), Image.LANCZOS)
                self.render2 = ImageTk.PhotoImage(self.load)
                self.img.config(image = self.render2)
            elif self.gapless == 0:
                if os.path.exists(self.mp3c_jpg):
                    self.img.config(image = self.renderc)
            else:
                if os.path.exists(self.mp3_jpg):
                    self.img.config(image = self.render)
        elif self.cutdown == 1:
            pictures = glob.glob(path)
            self.render2 = ""
            if len(pictures) > 0:
                if len(pictures) > 1:
                   r = random.randrange(len(pictures))
                   self.image = pictures[r]
                else:
                   self.image = pictures[0]
                self.load = Image.open(self.image)
                self.load = self.load.resize((100,100), Image.LANCZOS) 
                self.renderc = ImageTk.PhotoImage(self.load)
                if self.imgxon == 0:
                    self.imgx = tk.Label(self.Frame10, image = self.renderc)
                    self.imgx.grid(row = 1, column = 1, columnspan = 3, rowspan = 3, pady = 0)
                    self.imgxon = 1
                    self.Disp_plist_name.after(100, self.Disp_plist_name.destroy())
                    self.Disp_artist_name.after(100, self.Disp_artist_name.destroy())
                    self.Disp_album_name.after(100, self.Disp_album_name.destroy())
                self.imgx.config(image = self.renderc)
        elif self.cutdown == 4 or self.cutdown == 5:
            pictures = glob.glob(path)
            self.render2 = ""
            if len(pictures) > 0:
                if len(pictures) > 1:
                   r = random.randrange(len(pictures))
                   self.image = pictures[r]
                else:
                   self.image = pictures[0]
                self.load = Image.open(self.image)
                if self.cutdown == 4:
                    self.load = self.load.resize((130,130), Image.LANCZOS)
                else:
                    self.load = self.load.resize((170,170), Image.LANCZOS) 
                self.renderc = ImageTk.PhotoImage(self.load)
                if self.imgxon == 0:
                    self.imgx = tk.Label(self.Frame10, image = self.renderc)
                    self.imgx.grid(row = 1, column = 1, columnspan = 3, rowspan = 3, pady = 0)
                    self.imgxon = 1
                    if self.cutdown == 4:
                        self.Disp_plist_name.after(100, self.Disp_plist_name.destroy())
                    self.Disp_artist_name.after(100, self.Disp_artist_name.destroy())
                    self.Disp_album_name.after(100, self.Disp_album_name.destroy())
                self.imgx.config(image = self.renderc)
        self.track_name7 = self.track_name[:-4] + "  "
        self.album_name7 = self.album_name + "  "
        self.artist_name7 = self.artist_name + "  "
        self.count7 = 0
        self.artist_name1,self.album_name1,self.track_name1,self.drive_name10,self.drive_name11,self.drive_name21,self.genre_name  = self.tunes[self.track_no].split('^')
        if self.drive_name10[-1] == "*":
            self.track = os.path.join("/" + self.drive_name11,self.drive_name21,self.drive_name10[:-1], self.artist_name1 + " - " + self.album_name1, self.track_name1)
        elif self.genre_name == "None":
            self.track = os.path.join("/" + self.drive_name11,self.drive_name21,self.drive_name10, self.artist_name1, self.album_name1, self.track_name1)
        else:
            self.track = os.path.join("/" + self.drive_name11,self.drive_name21,self.drive_name10,self.genre_name, self.artist_name1, self.album_name1, self.track_name1)
        self.PStart()

    def PStart(self):
        if time.monotonic() - self.pstart > 0.2:
            self.pstart = time.monotonic()
            self.playing()
        if self.play == 1:
            self.after(500, self.PStart)

    def playing(self):
        if self.genre_name == "None":
            self.track2 = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name, self.artist_name, self.album_name, self.track_name[:-4] + ".txt")
        else:
            self.track2 = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name,self.genre_name, self.artist_name, self.album_name, self.track_name[:-4] + ".txt")
        if os.path.exists(self.track2):
           names = []
           with open(self.track2, "r") as file:
               line = file.readline()
               while line:
                   names.append(line.strip())
                   line = file.readline()
           x = len(names) - 1
           stop = 0
           while x > -1 and stop == 0:
               dtime = names[x][0:6]
               dname = names[x][7:]
               pstime = int(dtime[0:3]) * 60 + int(dtime[4:6])
               if (self.p_minutes * 60) + self.p_seconds > pstime and dtime != "000:00":
                   if self.cutdown >= 7:
                       self.Disp_track_name.set(dname)
                   else:
                       self.Disp_track_name.config(text = dname)
                   stop = 1
               x -=1
                    
        # backlight off
        if time.monotonic() - self.light_on > self.light and (self.HP4_backlight == 1 or self.LCD_backlight == 1 or self.Pi7_backlight == 1):
            if self.trace > 0:
                print ("backlight off")
            if self.HP4_backlight == 1 or self.LCD_backlight == 1:
                self.LCD_pwm.value = self.dim
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 0")
        
        if self.model != 0:
            self.count7 += 1
            # scroll artist name
            if len(self.artist_name7) > self.length and self.count7 == 1 and self.imgxon == 0:
                self.artist_name7 += self.artist_name7[0]
                self.artist_name7 = self.artist_name7[1:len(self.artist_name7)]
                if self.cutdown != 7 and self.cutdown != 8:
                    self.Disp_artist_name.config(text = self.artist_name7)
                else:
                    self.Disp_artist_name.set(self.artist_name7)
            # scroll album name
            if len(self.album_name7) > self.length and self.count7 == 1 and self.imgxon == 0:
                self.album_name7 += self.album_name7[0]
                self.album_name7 = self.album_name7[1:len(self.album_name7)]
                if self.cutdown != 7 and self.cutdown != 8:
                    self.Disp_album_name.config(text = self.album_name7)
                else:
                    self.Disp_album_name.set(self.album_name7)
            # scroll track name
            if len(self.track_name7) > self.length and self.count7 == 1:
                self.track_name7 += self.track_name7[0]
                self.track_name7 = self.track_name7[1:len(self.track_name7)]
                if self.cutdown != 7 and self.cutdown != 8:
                    self.Disp_track_name.config(text = self.track_name7)
                else:
                    self.Disp_track_name.set(self.track_name7)

            if self.count7 > (11 - self.scroll_rate):
                self.count7 = 0
            
                   
        # end of album (no repeat)
        if self.album_start == 1:
            if self.minutes == 0 and ((self.gapless == 0 and self.seconds <= 1 and self.BT == 0) or (self.gapless == 1 and self.seconds == (2 * self.BT) and self.BT == 1) or (self.gapless == self.gapless_time and self.seconds <= self.gapless_time)) and self.album_start == 1 and self.repeat_album == 0:
                if self.trace > 0:
                    print ("End of Album (no repeat)")
                if self.imgxon == 1:
                    self.imgx.after(100, self.imgx.destroy())
                    self.imgxon = 0
                    if cutdown == 1:
                        self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                        self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                        self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                        self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                        self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                        self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                        self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    elif cutdown == 4:
                        self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                        self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                        self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                        self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                        self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                        self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                        self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    elif cutdown == 5:
                        self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                        self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                        self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                        self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                        self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                        self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
                self.play = 2
                self.stopstart  = 0
                self.plist_trig = 0
                self.album_trig = 0
                if self.cutdown != 1  and self.cutdown != 5 and self.model != 0 and self.cutdown != 6:
                    self.L9.config(text= "   ")
                    self.s.configure("LabeledProgressbar", text="0 %      ", background='red')
                    self.progress['value'] = 0
                if self.cutdown != 5 and self.cutdown != 6:
                    self.Button_Prev_PList.config(bg = "light blue", fg = "black")
                    self.Button_Next_PList.config(bg = "light blue", fg = "black")
                if self.cutdown == 6:
                    self.Button_Pause.config(text = "NextAZ")
                if self.cutdown >= 7 or self.cutdown == 0 or self.cutdown == 2:
                    self.Button_Bluetooth.config(bg = 'light blue')
                self.Button_Prev_Artist.config(bg = "light blue", fg = "black")
                self.Button_Next_Artist.config(bg = "light blue", fg = "red")
                self.Button_Prev_Album.config(bg = "light blue", fg = "black")
                self.Button_Next_Album.config(bg = "light blue", fg = "black")
                self.Button_Prev_Track.config(bg = "light blue", fg = "black")
                self.Button_Next_Track.config(bg = "light blue", fg = "black")
                self.Button_Reload.config(bg = "light blue", fg = "black", text = "RELOAD")
                self.Button_Next_AZ.config(bg = 'light blue', fg = "black",text = "NextAZ")
                self.Button_Shuffle.config(fg = "black",bg = "light blue")
                if self.cutdown != 1 and self.cutdown != 4 and self.cutdown != 5 and self.cutdown != 6:
                    self.Button_AZ_artists.config(fg = "black",bg = "light blue")
                    self.Button_repeat.config(fg = "black",bg = "light blue", text = "Repeat")
                    self.L6.config(text= "Playlist :")
                self.wheel_opt   = 0
                self.album_start = 0
                self.album_time  = 0 
                self.Button_Start.config(bg = "green",fg = "black",text = "PLAY Playlist")
                self.Button_TAlbum.config(bg = "blue", fg = "black", text = "PLAY Album")
                self.Button_Shuffle.config(bg = "light blue",fg = "black",text = "Shuffle")
                self.Button_Radio.config(bg = "light blue", fg = "black", text = "Radio")
                self.gapless = 0
                if self.shuffle_on == 1:
                    self.shuffle_on = 0
                    self.tunes[self.track_no - self.album_track + 1:self.tcount]=sorted(self.tunes[self.track_no  - self.album_track + 1:self.tcount])
                self.Disp_Total_tunes.config(text = len(self.tunes))
                self.Disp_track_no.config(text = self.track_no + 1)
                self.auto_album = 0
                with open('Lasttrack3.txt', 'w') as f:
                    f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
                self.Time_Left_Play()
                
           # end of album (repeat)
            if self.minutes == 0 and ((self.gapless == 0 and self.seconds == 0 and self.BT == 0) or (self.gapless == 1 and self.seconds == (2 * self.BT) and self.BT == 1) or (self.gapless == self.gapless_time and self.seconds <= self.gapless_time)) and self.album_start == 1 and self.repeat_album == 1:
                if self.trace > 0:
                    print ("End of Album (repeat)")
                self.play = 0
                self.minutes = 1
                self.album_start = 0
                self.album_trig  = 0
                self.stopstart   = 0
                if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 4:
                    self.L9.config(text= "   ")
                self.Play_Album()
                
        # end of track
        if os.path.exists(self.track):
            # fade out track if using Bluetooth
            if time.monotonic() - self.start > (self.track_len - self.gapless) - 4 and self.play == 1 and self.paused == 0 and self.BT == 1:
                if self.trace > 0:
                    print ("Fade Out...")
                self.Fade()
            # stop track (early if using Bluetooth)
            if (((time.monotonic() - self.start > (self.track_len - self.gapless) - self.BT) or self.xxx == 1) and self.play == 1 and self.paused == 0) or self.stop7 == 1:
                self.xxx = 0
                self.stop7 = 0
                if self.imgxon == 1:
                    self.imgx.after(100, self.imgx.destroy())
                    self.imgxon = 0
                    if cutdown == 1:
                        self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                        self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                        self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                        self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                        self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                        self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                        self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    elif cutdown == 4:
                        self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                        self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                        self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                        self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                        self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                        self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                        self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    elif cutdown == 5:
                        self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                        self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                        self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                        self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                        self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                        self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
                if self.trace > 0:
                    print ("End of track",self.track_no)
                self.play = 0
                if self.cutdown != 1  and self.cutdown != 5 and self.model != 0 and self.cutdown != 6:
                    self.s.configure("LabeledProgressbar", text="0 %      ", background='red')
                    self.progress['value'] = 0
                if self.repeat_track == 0:
                    self.track_no +=1
                if self.version == 1:
                    poll = self.p.poll()
                    if poll is None:
                        self.p.kill()
                else:
                    player.stop()
                self.volume = self.f_volume
                self.m.setvolume(self.volume)
                os.system("amixer -D pulse sset Master " + str(self.volume) + "%")
                if self.mixername == "DSP Program":
                    os.system("amixer set 'Digital' " + str(volume + 107))
                if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2:
                    self.Button_volume.config(text =self.volume)
                else:
                    self.Button_Vol_UP.config(text = "Vol >   " + str(self.volume))
                # stop if playlist last track and repeat OFF
                if self.track_no > len(self.tunes) - 1 and self.repeat == 0 and self.repeat_album == 0:
                    if self.trace > 0:
                       print ("End of track - Last Track in playlist",self.track_no)
                    self.play = 2
                    self.stopstart = 0
                    if self.cutdown == 6:
                        self.Button_Pause.config(text = "NextAZ")
                    self.Button_Reload.config(bg = "light blue", fg = "black", text = "RELOAD")
                    self.Button_Start.config(bg = "green",fg = "black",text = "PLAY Playlist")
                    self.Button_TAlbum.config(bg = "blue", fg = "black", text = "PLAY Album")
                    self.Button_Radio.config(bg = "light blue", fg = "black", text = "Radio")
                    self.gapless = 0
                    self.track_no -=1
                    self.Time_Left_Play()
                    
                # repeat if playlist last track and repeat ON
                if self.track_no > len(self.tunes) - 1 and self.repeat == 1:
                    self.track_no = 0
                # patch for Pi Zero and CPU load.
                if self.model == 0 and self.play != 2 and time.monotonic() - self.piz_timer2 > self.piz_timer:
                    self.piz_timer2 = time.monotonic()
                    if os.path.exists ('/run/shm/up.txt'): 
                        os.remove("/run/shm/up.txt")
                    os.system("uptime >> /run/shm/up.txt")
                    with open("/run/shm/up.txt", "r") as file:
                        line = file.readline()[0:-1]
                    a,b,c,d,e,= line.split(", ")
                    if self.trace > 0:
                        print (float(c[14:19]),float(d[0:4]),float(e[0:4]))
                        self.Disp_plist_name.config(text = str(a) + "," + str(c)[13:18] + "," + str(d) + "," + str(e))
                    if float(d[0:4]) > 2.0: 
                        with open('Lasttrack3.txt', 'w') as f:
                            f.write(str(self.track_no) + "\n" + "1" + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
                        self.restart = 1
                        self.Stop_Play()
                    else:
                        if self.trace > 0:
                           print ("1")
                        self.Start_Play()
                else:
                    if self.trace > 0:
                        print ("2")
                    self.Start_Play()

            # display times (and bar charts if applicable)
            if self.play == 1 : 
                if self.paused == 0:
                    self.played = time.monotonic() - self.start
                self.p_minutes = int(self.played // 60)
                self.p_seconds = int (self.played - (self.p_minutes * 60))
                if self.album_start == 0:
                    if self.cutdown != 1 and self.cutdown != 5 and self.cutdown != 6 and self.model != 0:
                        if self.cutdown != 3:
                            self.L9.config(text= " T :")
                        self.s.configure("LabeledProgressbar", text="{0} %      ".format(int((self.played/self.track_len)*100)), background='blue')
                        self.progress['value'] = (self.played/self.track_len)*100
                if self.p_seconds != self.oldsecs:
                    self.Disp_played.config(text ="%03d:%02d" % (self.p_minutes, self.p_seconds % 60),fg = "red")
                    self.oldsecs = self.p_seconds

            if self.play == 1 and self.paused == 0: 
                self.tplaylist = self.total + self.track_len
                if self.stop == 0:
                    self.tplaylist = (self.total + self.track_len - (time.monotonic() - self.start2))
                self.minutes = int(self.tplaylist// 60)
                self.seconds = int (self.tplaylist - (self.minutes * 60))
                if self.album_start == 1:
                    if self.album_track == 1 and self.album_trig == 0:
                        self.album_length = self.total + self.track_len
                        self.album_trig = 1
                    if self.cutdown != 1 and self.cutdown != 5 and self.cutdown != 6  and self.model != 0:
                        if self.cutdown != 3:
                            self.L9.config(text= " A :")
                        self.s.configure("LabeledProgressbar", text="{0} %      ".format(100-int((self.tplaylist/(self.album_length))*100)), background='green')
                        self.progress['value'] = 100 - (self.tplaylist/(self.album_length))*100

                if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and self.cutdown != 6 :
                    if self.minutes < 0 or self.seconds < 0:
                        self.Disp_Total_Plist.config(text = " 00:00 " )
                    elif self.stop == 0 or self.stop == 2:
                        self.Disp_Total_Plist.config(text ="%03d:%02d" % (self.minutes, self.seconds % 60))
                    else:
                        self.Disp_Total_Plist.config(text = ">" + str(self.Disp_max_time) + ":00" )
                    
                if self.cutdown == 4:
                    if self.minutes < 0 or self.seconds < 0:
                        self.Disp_Name_m3u.delete('1.0','20.0')
                        self.Disp_Name_m3u.insert(INSERT," 00:00 ")
                    elif self.stop == 0 or self.stop == 2:
                        self.Disp_Name_m3u.delete('1.0','20.0')
                        self.Disp_Name_m3u.insert(INSERT,"  " + "%03d:%02d" % (self.minutes, self.seconds % 60))
                    else:
                        self.Disp_Name_m3u.delete('1.0','20.0')
                        self.Disp_Name_m3u.insert(INSERT,">" + str(self.Disp_max_time) + ":00" )
            #if self.play == 1:
            #    self.after(500, self.playing)
        elif self.play == 1:
            if self.trace > 0:
                print ("Playing - No track")
            self.Start_Play()

    def Pause(self):
        # Next AZ BUtton
        if self.cutdown == 6 and self.Radio_ON == 0 and self.stopstart == 0 and self.album_start == 0:
            self.nextAZ()
        # RECORD Button
        if self.Radio_ON == 1 and self.Radio_RON == 0 and self.Radio_Stns[self.Radio + 2]  > 0 and self.record == 1:
            if self.trace > 0:
                print ("Start Record")
            if "System clock synchronized: yes" in os.popen("timedatectl").read().split("\n"):
                self.synced = 1
            else:
                self.synced = 0
            self.rems2 = glob.glob("/run/shm/music/*/*/*/*/*.mp3")
            for x in range(0,len(self.rems2)):
                os.remove(self.rems2[x])
            self.rems2 = glob.glob("/run/shm/music/*/*/*.mp3")
            for x in range(0,len(self.rems2)):
                if os.path.exists(self.rems2[x]):
                    os.remove(self.rems2[x])
            self.rems3 = glob.glob("/run/shm/music/*/*/*.cue")
            for x in range(0,len(self.rems3)):
                os.remove(self.rems3[x])
            self.Name = ""
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 5:
                self.L1.config(text = "RAM: ")
                if self.cutdown >= 7:
                    self.artistdata = []
                    self.Disp_artist_name["values"] = self.artistdata
            if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and  self.cutdown != 6:
                if self.touchscreen == 1:
                    self.L8.config(text = ".mp3")
                self.Disp_Name_m3u.config(background="light gray", foreground="black")
                self.Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
            self.Button_Reload.config(text = "RELOAD", bg = "light grey", fg = "black")
            self.Button_Shuffle.config(text = "CLR RAM",bg = "light grey", fg = "black")
            if len(self.Name) == 0 or self.Name == "Name ?":
                now = datetime.datetime.now()
                self.Name = now.strftime("%y%m%d_%H%M%S")
                if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and  self.cutdown != 6:
                    self.Disp_Name_m3u.delete('1.0','20.0')
                    self.Disp_Name_m3u.insert(INSERT,self.Name)
            if self.Radio_Stns[self.Radio + 2] == 0:
                self.q.kill()
            else:
                self.q.kill()
                self.r.kill()
            self.Radio_RON   = 1
            self.auto_record = 1
            self.auto_radio  = 1
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            if self.cutdown != 4 and self.cutdown != 1 and self.cutdown != 3 and self.cutdown != 2:
                self.L3.config(text = "Rec'd:")
            self.rec_begin = time.monotonic()
            now = datetime.datetime.now()
            self.start_record = now
            if self.cutdown == 6:
                self.Disp_track_name1.config(fg = "#777",bg = "#ddd")
                self.Disp_track_name2.config(fg = "#777",bg = "#ddd")
                self.Disp_track_name3.config(fg = "#777",bg = "#ddd")
                self.Disp_track_name4.config(fg = "#777",bg = "#ddd")
                self.Disp_track_name5.config(fg = "#777",bg = "#ddd")
                self.Disp_track_name6.config(fg = "#777",bg = "#ddd")
                self.Disp_track_name7.config(fg = "#777",bg = "#ddd")
                self.Disp_track_name8.config(fg = "#777",bg = "#ddd")
                self.Disp_track_name9.config(fg = "#777",bg = "#ddd")
            self.Button_Prev_Artist.config(fg = "black", bg = "light grey")
            self.Button_Next_Artist.config(fg = "black", bg = "light grey")
            if self.imgxon == 0:
                self.Disp_album_name.config(text = "Radio")
            self.Disp_track_name.config(text = self.Name)
            self.record_time = self.rec_step
            self.stop_record = now + timedelta(minutes=self.rec_step)
            if self.auto_rec_set == 1:
                self.record_time = self.auto_rec_time
            self.total_record = self.record_time * 60
            self.record_time_min = self.record_time * 60
            self.Disp_track_len.config(text ="010:00")
            if self.cutdown == 6 or self.cutdown == 4 or self.cutdown == 2 or self.cutdown == 0 or self.cutdown >= 7:
                self.Button_Next_AZ.config(text = "Info", bg = "light blue", fg = "black")
            self.L4.config(text="/")
            self.Button_Pause.config(fg = "yellow", bg = "red", text = str(self.stop_record)[11:16])
            if (self.cutdown >= 7 or self.cutdown == 0) and self.synced == 1:
                self.L6.config(text = "(" + str(self.stop_record)[11:16] + ")")
            if self.cutdown != 1:
                if self.rotary_pos== 0:
                    self.Button_Radio.config(bg = "red",fg = "black", text = "STOP RECORD")
                else:
                    self.Button_Radio.config(bg = "light blue",fg = "black", text = "STOP RECORD")
            else:
                self.Button_Radio.config(bg = "red",fg = "black", text = "STOP R")
            track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
            counter = 0
            track_name = [" - .mp3"]
            if len(track) > 0 and self.Radio_ON == 1:
                counter = track[0].count('/')
                track_name = track[0].split("/",counter)
            if track_name != self.track_nameX or track_name[counter] == " - .mp3":
                rems = glob.glob("/run/shm/music/*/*/*/*/*.mp3")
                for x in range(0,len(rems)):
                    os.remove(rems[x])
            rems = glob.glob("/run/shm/music/*/*/*.cue")
            for x in range(0,len(rems)):
                os.remove(rems[x])
            if self.Radio_Stns[self.Radio + 2] == 0:
                self.q = subprocess.Popen(["mplayer", "-nocache", self.Radio_Stns[self.Radio + 1]] , shell=False)
                time.sleep(1)
            else:
                self.r = subprocess.Popen(["streamripper",self.Radio_Stns[self.Radio + 1],"-r","--xs_offset=-9000","-z","-l","99999","-d","/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings","-a",self.Name], shell=False)
                time.sleep(1)
                self.q = subprocess.Popen(["mplayer","-nocache","http://localhost:8000"] , shell=False)
                time.sleep(1)
                track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
                if len(track) == 0:
                   time.sleep(2)
            # check RAM space and set self.max_record
            st = os.statvfs("/run/shm/")
            self.freeram1 = (st.f_bavail * st.f_frsize)/1100000
            self.timer7 = time.monotonic()
            free2 = int((self.freeram1 - self.ram_min)/10) * 10
            self.max_record = min(free2,990)
            self.ramtest = 1

        elif self.Radio_ON == 1 and self.Radio_RON == 1 and self.Radio_Stns[self.Radio + 2]  > 0 and self.record == 1:
            if self.trace > 0:
                print ("Increase Record Time")
            self.record_time = int(self.record_time + self.rec_step)
            self.old_rs = self.record_time
            self.total_record += self.rec_step * 60
            if self.record_time <= self.max_record:
                self.stop_record += timedelta(minutes=self.rec_step)
            if self.trace == 1:
                print(self.stop_record)
            if self.total_record > (self.max_record * 60):
                self.record_time -= int((self.total_record - (self.max_record * 60))/60)
                self.total_record = (self.max_record * 60)
            if self.record_time > self.max_record:
                self.record_time = self.rec_step
                self.total_record = self.record_time * 60
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            self.record_time_min = self.record_time * 60
            t_minutes = int(self.total_record // 60)
            t_seconds = int (self.total_record - (t_minutes * 60))
            self.Disp_track_len.config(text ="%03d:%02d" % (t_minutes, t_seconds % 60))
            self.record_current = int((self.total_record - (time.monotonic() - self.rec_begin))/60)
            self.Button_Pause.config(fg = "yellow", bg = "red", text = str(self.stop_record)[11:16])
            if (self.cutdown >= 7 or self.cutdown == 0) and self.synced == 1:
                self.L6.config(text = "(" + str(self.stop_record)[11:16] + ")")
            if self.Radio_ON == 1 and self.Radio_RON == 1 and self.shutdown == 1 and self.record_sleep == 1:
                self.sleep_time_min = (self.record_current *60) + 60
                self.sleep_time = int(self.sleep_time_min / 60)
        #=======================================================================================================================
        # PAUSE BUTTON
        if self.BT == 0 and self.Radio_ON == 0:
            if self.trace > 0:
                print ("Pause")
            # if playing and using self.version 1 (mplayer) then close it and switch to self.version 2 (player)
            if self.version == 1 and self.play == 1 and self.counter5 == 0:
                self.p.kill()
                self.play = 0
                self.version = 2
                if self.album_start  == 1:
                    self.album_track -=1
                self.Start_Play()
            # if not playing and using self.version 1 (mplayer) then switch to self.version 2 (player)
            if self.version == 1 and self.play == 0 and self.counter5 == 0:
                self.version = 2
                self.gapless = 0
                if self.cutdown != 1  and self.cutdown != 5 and self.cutdown != 6:
                    self.Button_Gapless.config(fg = "black",bg = "light blue", text ="Gapless")
                if self.cutdown == 6:
                    self.Button_Radio.config(fg = "black",bg = "light blue", text ="Gapless")
                self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                self.paused = 0
            # if playing and self.paused not set then set it and pause
            if self.paused == 0 and self.stopstart == 1:
                self.paused = 1
                self.gapless = 0
                if self.cutdown != 1 and self.cutdown != 5 and self.cutdown != 6:
                    self.Button_Gapless.config(fg = "black",bg = "light blue", text ="Gapless")
                if self.cutdown == 5:
                    self.Button_Radio.config(fg = "black",bg = "light blue", text ="Repeat")
                if self.cutdown == 6:
                    self.Button_Radio.config(fg = "black",bg = "light blue", text ="Gapless")
                self.time1 = time.monotonic()
                self.Button_Pause.config(fg = "black",bg = "orange", text ="Unpause")
                if os.path.exists(self.mp3_jpg) and self.cutdown !=1  and self.cutdown != 4 and self.cutdown != 5:
                    self.img.config(image = self.render)
                player.pause()
            # if playing and self.paused set (paused) then unset it and Unpause
            elif self.paused == 1 and self.stopstart == 1 and self.counter5 == 0:
                self.paused = 0
                self.time2 = time.monotonic()
                self.start = self.start + (self.time2 - self.time1)
                self.start2 = self.start2 + (self.time2 - self.time1)
                self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                if self.rotary_pos == 1 and self.rot_pos == 9:
                    self.Button_Pause.config(fg = "black",bg = "yellow", text ="Pause")
                if self.cutdown != 1 and self.cutdown != 5 and self.cutdown != 6 and self.album_start == 0:
                    self.Button_Gapless.config(fg = "black",bg = "light blue", text ="Gapless")
                if self.cutdown == 6:
                    self.Button_Radio.config(fg = "black",bg = "light blue", text ="Gapless")
                if os.path.exists(self.mp3c_jpg) and self.cutdown !=1 and self.cutdown != 4 and self.cutdown != 5:
                    self.img.config(image = self.renderc)
                player.pause()

    def R_record(self):
        if self.trace > 0:
            print ("R_Record")
        if self.Radio_ON == 1 and self.Radio_RON == 1 and self.Radio_Stns[self.Radio + 2]  > 0 and self.record == 1:
            self.record_time = int(self.record_time - self.rec_step)
            if self.record_time < self.rec_step:
                self.record_time = self.rec_step
            self.total_record -= self.rec_step * 60
            if self.total_record < self.rec_step * 60:
                self.total_record += self.rec_step * 60    
            if self.record_time >= self.rec_step and self.old_rs != self.record_time:
                self.stop_record -= timedelta(minutes=self.rec_step)
                self.old_rs = self.record_time
            if self.trace == 1:
                print(self.record_time,self.total_record,self.stop_record)
            self.auto_rec_time = self.record_time
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            self.record_time_min = self.record_time * 60
            t_minutes = int(self.total_record // 60)
            t_seconds = int (self.total_record - (t_minutes * 60))
            self.Disp_track_len.config(text ="%03d:%02d" % (t_minutes, t_seconds % 60))
            self.record_current = int((self.total_record - (time.monotonic() - self.rec_begin))/60)
            self.Button_Pause.config(fg = "yellow", bg = "red", text = str(self.stop_record)[11:16])
            if (self.cutdown >= 7 or self.cutdown == 0) and self.synced == 1:
                self.L6.config(text = "(" + str(self.stop_record)[11:16] + ")")
            if self.Radio_ON == 1 and self.Radio_RON == 1 and self.shutdown == 1 and self.record_sleep == 1:
                self.sleep_time_min = (self.record_current *60) + 60
                self.sleep_time = int(self.sleep_time_min / 60)

    def Gapless(self):
        if self.BT == 0 and self.Radio_ON == 0:
            # if playing using self.version 2 (player), not paused, then close it and  switch to self.version 1 (mplayer)
            if self.version == 2 and self.play == 1 and self.paused == 0: 
                player.stop()
                self.play = 0
                self.version = 1
                if self.album_start == 1:
                    self.album_track -= 1
                self.Start_Play()
            # if gapless not ON, pause not ON then set gapless ON
            if self.gapless == 0 and self.paused == 0: 
                self.gapless = self.gapless_time
                self.paused = 0
                self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                if self.cutdown != 6 and self.cutdown != 5:
                     self.Button_Gapless.config(fg = "black",bg = "orange", text ="Gapless")
                else:
                     self.Button_Radio.config(fg = "black",bg = "orange", text ="Gapless")
                self.version = 1
                if self.cutdown != 4 and self.cutdown != 5:
                    self.img.config(image = self.render)
            # if gapless set ON and not paused then switch gapless OFF.
            elif self.gapless == self.gapless_time and self.paused == 0:
                self.gapless = 0
                self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                if self.album_start == 0:
                    if self.cutdown != 6 and self.cutdown != 5:
                        self.Button_Gapless.config(fg = "black",bg = "light blue", text ="Gapped")
                    else:
                        self.Button_Radio.config(fg = "black",bg = "light blue", text ="Gapped")
                else:
                    if self.cutdown != 6 and self.cutdown != 5:
                        self.Button_Gapless.config(fg = "black",bg = "light blue", text ="Gapped")
                    else:
                        self.Button_Radio.config(fg = "black",bg = "light blue", text ="Gapped")
                self.version = 2
                if self.play == 1:
                    self.p.kill()
                    self.play = 0
                    if self.album_start == 1:
                        self.album_track -= 1
                    self.Start_Play()
                if self.cutdown != 4 and self.cutdown != 5:
                    self.img.config(image = self.renderc)
            # if gapless set OFF and not paused then switch gapless ON.
            elif self.gapless == 0 and self.paused == 0 and self.version == 1:
                self.gapless = self.gapless_time
                if self.cutdown != 6 and self.cutdown != 5:
                    self.Button_Gapless.config(fg = "black",bg = "orange", text ="Gapless")
                else:
                    self.Button_Radio.config(fg = "black",bg = "orange", text ="Gapless")
                if self.cutdown != 4 and self.cutdown != 5:
                    self.img.config(image = self.render)
            if self.rotary_pos == 1 and self.rot_pos == 13 :
                self.Button_Gapless.config(bg = 'yellow')

    def Play_Album(self):
      if self.bt_on == 0:
        if self.trace > 0:
            print ("Play Album",self.track_no)
        if (self.cutdown >= 7 or self.cutdown == 0 or self.cutdown == 2) and self.bt_on == 0:
            self.Button_Bluetooth.config(bg = 'light gray')
        if self.cutdown >= 7 and len(self.tunes) > 0:
            self.artist_name  = (self.tunes[self.track_no].split('^')[0])
            self.album_name   = (self.tunes[self.track_no].split('^')[1])
        self.light_on = time.monotonic()
        self.f_volume = self.volume
        if self.cutdown != 4 and self.cutdown != 5  and self.cutdown != 6 and self.cutdown != 1 and self.Radio_ON == 0:
            self.L6.config(text= "Playlist :")
        if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2:
            self.Button_volume.config(text = self.volume)
        else:
            self.Button_Vol_UP.config(text = "Vol >   " + str(self.volume))
        self.muted     = 0
        self.R_Stopped = 0
        self.m.setvolume(self.volume)
        os.system("amixer -D pulse sset Master " + str(self.volume) + "%")
        if self.mixername == "DSP Program":
            os.system("amixer set 'Digital' " + str(volume + 107))
        if self.paused == 0 and len(self.tunes) > 0 and self.album_start == 0 and self.stopstart == 0 and self.Radio_ON == 0:
            if self.auto_album == 1:
                self.artist_name  = (self.tunes[self.track_no].split('^')[0])
                self.album_name   = (self.tunes[self.track_no].split('^')[1])
            self.start_track_no = self.track_no
            self.auto_album = 1
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            self.album_length  = 0
            self.plist_length  = 0
            self.album_trig    = 0
            self.plist_trig    = 0
            if self.cutdown == 4:
                self.Button_Next_AZ.config(text = "NextAZ", bg = "light grey", fg = "black")
            if self.cutdown == 6 or self.cutdown == 5 or self.cutdown >= 7 or self.cutdown == 0:
                self.Button_Pause.config(text = "Pause", bg = "light blue", fg = "black")
                self.Button_Next_AZ.config(text = "Info", bg = "light blue", fg = "black")
            else:
                self.Button_Next_AZ.config(bg = "light grey", fg = "black")
            if self.cutdown != 5 and self.cutdown != 6 :
                self.Button_Prev_PList.config(bg  = "light grey", fg = "black")
                self.Button_Next_PList.config(bg  = "light grey", fg = "black")
            self.Button_Prev_Artist.config(bg  = "light grey", fg = "black")
            self.Button_Next_Artist.config(bg  = "light grey", fg = "black")
            self.Button_Prev_Album.config(bg  = "light grey", fg = "black")
            self.Button_Next_Album.config(bg  = "light grey", fg = "black")
            if self.rotary_pos== 0:
                self.Button_Prev_Track.config(bg  = "light blue", fg = "black")
            self.Button_Next_Track.config(bg  = "light blue", fg = "black")
            if self.cutdown == 6 or self.cutdown == 4 or self.cutdown == 5:
                if self.repeat == 0 and self.repeat_album == 0:
                    self.Button_Radio.config(bg = "light blue", fg = "black", text = "Repeat")
                elif self.repeat == 1 and self.repeat_album == 0:
                    self.Button_Radio.config(bg = "green", fg = "black", text = "Repeat")
                elif self.repeat == 1 and self.repeat_album == 1:
                    self.Button_Radio.config(bg = "green", fg = "black", text = "Repeat Album")
            else:
                self.Button_Radio.config(bg = "light grey", fg = "black")
            if self.cutdown == 4:
                self.Button_Track_m3u.config(bg = "light grey", fg = "black")
                self.Button_Artist_m3u.config(bg = "light grey", fg = "black")
                self.Button_Album_m3u.config(bg = "light grey", fg = "black")
                self.Button_PList_m3u.config(bg = "light grey", fg = "black")
            if self.cutdown == 0 or self.cutdown >= 7:
                self.L6.config(text= "Album :")
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3:
                self.Button_AZ_artists.config(fg = "black",bg = "light grey")
                self.Button_repeat.config(bg = "light blue",fg = "black",text = "Repeat Album")
            self.Button_TAlbum.config(fg = "black",bg = "light grey")
            self.Button_Shuffle.config(bg = "light blue",fg = "black",text = "Shuffle")
            self.repeat_count = 0
            self.repeat = 0
            self.repeat_track = 0
            if self.trace > 0:
                print ("Play Album1",self.track_no,self.artist_name, self.album_name)
            if len(self.tunes) > 2:
                self.shuffle_on = 0
                if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3:
                    self.Disp_Name_m3u.config(background="light gray", foreground="black")
                    self.Disp_Name_m3u.delete('1.0','20.0')
                self.sort_no = 0
                self.tunes.sort()
                stop = 0
                counter = 0
                while stop == 0:
                    self.artist_name2  = (self.tunes[counter].split('^')[0])
                    self.album_name2   = (self.tunes[counter].split('^')[1][0:-1])
                    if self.artist_name == self.artist_name2 and self.album_name[0:-1] == self.album_name2:
                        stop = 1
                    counter +=1
                self.track_no = counter - 1
            artist_name3,album_name3,track_name,drive_name,drive_name1,drive_name2,genre_name  = self.tunes[self.track_no].split('^')
            if drive_name[-1] == "*":
                track = os.path.join("/" + drive_name1,drive_name2,drive_name[:-1],artist_name3 + " - " + album_name3, track_name)
            elif self.genre_name == "None":
                track = os.path.join("/" + drive_name1,drive_name2,drive_name,artist_name3,album_name3,track_name)
                album = os.path.join("/" + drive_name1,drive_name2,drive_name,artist_name3,album_name3)
            else:
                track = os.path.join("/" + drive_name1,drive_name2,drive_name,genre_name,artist_name3,album_name3,track_name)
                album = os.path.join("/" + drive_name1,drive_name2,drive_name,genre_name,artist_name3,album_name3)
            stop = 0
            trk = self.track_no
            if len(self.tunes) > 0:
                stop = 0
                if self.track_no == 0:
                    stop = 1
                while stop == 0:
                    self.artist_name2  = (self.tunes[self.track_no].split('^')[0])
                    self.album_name2   = (self.tunes[self.track_no].split('^')[1][0:-1])
                    if self.artist_name != self.artist_name2 or self.album_name[0:-1] != self.album_name2:
                        self.track_no +=2
                        stop = 1
                    self.track_no -=1
                    if self.track_no < 0:
                       stop = 1
                       self.track_no +=1
                if len(self.tunes) > 1:
                    stop = 0
                    self.scount = self.track_no
                    self.tcount = self.track_no
                    while stop == 0:
                        self.artist_name2  = (self.tunes[self.tcount].split('^')[0])
                        self.album_name2   = (self.tunes[self.tcount].split('^')[1][0:-1])
                        if self.artist_name != self.artist_name2 or self.album_name[0:-1] != self.album_name2:
                            self.tcount -=2
                            stop = 1
                        self.tcount +=1
                        if self.tcount >= len(self.tunes):
                            stop = 1
                else:
                    self.tcount = self.track_no
                self.album_track = 0
                self.album_start = 1
                if self.cutdown >= 7:
                    self.ac = 0
                    if self.auto_albums == 1:
                        if self.shuffle_on == 0:
                            self.plist_callback2()
                        else:
                            self.plist_callback2()
                    else:
                        if self.shuffle_on == 0:
                            self.album_callback2(0)
                        else:
                            self.album_callback2(0)
                    self.artistdata = []
                    self.Disp_artist_name["values"] = self.artistdata
                    self.albumdata = []
                    self.Disp_album_name["values"] = self.albumdata

                self.album_trig = 0
                self.stopstart = 1
                self.play = 0
                if self.trace > 0:
                    print ("Play Album2",self.track_no)
                    
                self.Start_Play()
        elif self.album_start == 1:
            self.auto_album = 0
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            if self.cutdown == 6:
                self.Button_Next_AZ.config(text = "NextAZ", bg = "light blue", fg = "black")
            self.Stop_Play()

    def Stop_Play(self):
        if self.trace > 0:
            print("Stop")
        self.Button_Next_AZ.config(bg = 'light blue', text = "NextAZ")
        if self.imgxon == 1:
            self.imgx.after(100, self.imgx.destroy())
            self.imgxon = 0
            if cutdown == 1:
                self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
            elif cutdown == 4:
                self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
            elif cutdown == 5:
                self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
            
        if self.cutdown >= 7:
            self.shuffle_on = 0
            self.Disp_artist_name.set(self.artist_name)
            self.ac = 0
            self.bc = 1
            self.cc = 1
            self.plist_callback()
            self.Disp_album_name.set(self.album_name)
            self.Disp_track_name.set(self.track_name)
        if self.cutdown != 1 and self.cutdown != 5 and self.cutdown != 6 :
            self.Disp_Name_m3u.config(background="light gray", foreground="black")
            self.Disp_Name_m3u.delete('1.0','20.0')
            if self.cutdown != 1  and self.cutdown != 5 and self.cutdown != 6 and self.model != 0:
                if self.cutdown != 3:
                   self.L9.config(text= "   ")
                self.s.configure("LabeledProgressbar", text="0 %      ", background='red')
                self.progress['value'] = 0
        self.stopstart    = 0
        self.wheel        = 0
        self.shutdown     = 0
        self.plist_trig   = 0
        self.album_trig   = 0
        self.album_length = 0
        self.album_sleep  = 0
        self.plist_length = 0
        if self.cutdown >= 7 or self.cutdown == 0 or self.cutdown == 2:
             self.Button_Bluetooth.config(bg = 'light blue')
        if self.cutdown != 5 and self.cutdown != 6 :
            self.Button_Prev_PList.config(bg = "light blue", fg = "black")
            self.Button_Next_PList.config(bg = "light blue", fg = "black")
        if self.cutdown == 6:
            self.Button_Pause.config(text = "NextAZ", bg = "light blue", fg = "black")
            self.Button_Next_AZ.config(text = "Info", bg = "light blue", fg = "black")
        if self.cutdown == 4:
            self.Button_Next_AZ.config(text = "NextAZ", bg = "light blue", fg = "black")
        if self.rotary_pos== 0:
            self.Button_Prev_Artist.config(bg = "light blue", fg = "black")
            self.Button_Start.config(bg = "green",fg = "black",text = "PLAY Playlist")
        else:
            self.Button_Prev_Artist.config(bg = "light blue", fg = "black")
            if self.rot_pos == 3 and self.rotary_pos == 1:
                self.Button_Start.config(bg = "yellow",text = "PLAY Playlist")
            elif self.rot_pos == 4:
                self.Button_TAlbum.config(bg = "yellow",text = "PLAY Album")
        self.Button_Next_Artist.config(bg = "light blue", fg = "black")
        self.Button_Prev_Album.config(bg = "light blue", fg = "black")
        self.Button_Next_Album.config(bg = "light blue", fg = "black")
        self.Button_Prev_Track.config(bg = "light blue", fg = "black")
        if self.shuffle_on == 0:
            self.Button_Shuffle.config(bg = "light blue",fg = "black")
        self.gapless = 0
        self.Button_Radio.config(bg = "light blue", fg = "black", text = "Radio")
        if self.cutdown == 4:
            self.Button_PList_m3u.config(bg = "light green", fg = "black")
            self.Button_Track_m3u.config(bg = "light green", fg = "black")
            self.Button_Artist_m3u.config(bg = "light green", fg = "black")
            self.Button_Album_m3u.config(bg = "light green", fg = "black")
        if self.wheel_opt == 0:
            self.Button_Next_Artist.config(fg = "red")
        if self.wheel_opt == 1:
            self.Button_Next_Album.config(fg = "red")
        if self.wheel_opt == 2:
            self.Button_Next_Track.config(fg = "red")
        if self.wheel_opt == 3:
            self.Button_Next_PList.config(fg = "red")
        self.Button_Next_Track.config(bg = "light blue", fg = "black")
        self.Button_Reload.config(bg = "light blue", fg = "black", text = "RELOAD")
        if self.cutdown != 6:
            self.Button_Next_AZ.config(bg = "light blue", fg = "black")
        if self.cutdown != 1 and self.cutdown != 4 and self.cutdown != 5 and self.cutdown != 6 :
            self.Button_AZ_artists.config(fg = "black",bg = "light blue")
            self.Button_repeat.config(fg = "black",bg = "light blue", text = "Repeat")
        if self.cutdown == 0 or self.cutdown >= 7:
            self.L6.config(text= "Playlist :")
        self.Button_TAlbum.config(fg = "black",bg = "blue",text = "PLAY Album",)
        if self.album_start == 1 and self.shuffle_on == 1:
            self.shuffle_on = 0
            self.tunes[self.track_no - self.album_track + 1:self.tcount]=sorted(self.tunes[self.track_no  - self.album_track + 1:self.tcount])
            self.Button_Shuffle.config(bg = "light blue",fg = "black",text = "Shuffle")
        if self.BT == 0:
            player.time_pos = 0
        if self.paused == 1:
           if self.BT == 0:
               if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 4:
                   self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                   self.paused = 0
               player.pause()
               time.sleep(.25)
        if self.album_start > 0:
            self.album_start = 0
            self.album_track = 0
            self.album_time = 0
            self.sleep_time_min = 0
            self.sleep_time = 0
            self.Button_Sleep.config(bg = "light blue", text = "SLEEP")
            if self.rot_pos == 3 and self.rotary_pos == 1:
                self.Button_Start.config(bg = "yellow",text = "PLAY Playlist")
                self.Button_TAlbum.config(bg = "blue",text = "PLAY Album")
            elif self.rot_pos == 4:
                self.Button_TAlbum.config(bg = "yellow",text = "PLAY Album")
                self.Button_Start.config(bg = "green",text = "PLAY Playlist")
            self.Disp_Total_tunes.config(text =len(self.tunes))
        if self.play == 1:
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2:
                self.Button_volume.config(fg = "green")
            self.wheel_opt = 0
            self.Button_Next_Artist.config(fg = "red")
            self.Button_Next_Album.config(bg = "light blue", fg = "black")
            if self.cutdown != 5 and self.cutdown != 6 :
                self.Button_Next_PList.config(bg = "light blue", fg = "black")
            self.Button_Next_Track.config(bg = "light blue", fg = "black")
            self.play = 0
            if self.version == 1:
                self.p.kill()
            else:
                player.stop()
                self.paused = 0
                if self.BT == 0 and (self.cutdown == 0 or self.cutdown == 2):
                    self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
            self.shutdown = 0
            self.sleep_time = 0
            self.sleep_time_min = 0
            self.Button_Sleep.config(bg = "light blue", text = "SLEEP")
        if self.cutdown != 1 and self.cutdown != 4 and self.cutdown != 5 and self.cutdown != 6 :
            self.Disp_Name_m3u.delete('1.0','20.0')
        if self.restart == 1:
            self.restart = 0
            self.R_Play()
        else:
            self.Time_Left_Play()

    def R_Play(self):
        self.after(1000, self.Play)

    def Check_Wheel(self):
        # read mouse position
        x = self.master.winfo_pointerx()
        y = self.master.winfo_pointery()
        abs_x = self.master.winfo_pointerx() - self.master.winfo_rootx()
        abs_y = self.master.winfo_pointery() - self.master.winfo_rooty()
        #print(abs_x,abs_y)
        
        # switch backlight on (if enabled)
        if (self.LCD_backlight == 1 or self.HP4_backlight == 1 or self.Pi7_backlight == 1) and (self.old_abs_x != abs_x or self.old_abs_y != abs_y) :
            if self.HP4_backlight == 1 or self.LCD_backlight == 1:
                self.LCD_pwm.value = self.bright
            self.light_on = time.monotonic()
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 100")
        self.old_abs_x = abs_x
        self.old_abs_y = abs_y

        # backlight off
        if time.monotonic() - self.light_on > self.light and (self.HP4_backlight == 1 or self.LCD_backlight == 1 or self.Pi7_backlight == 1):
            if self.HP4_backlight == 1 or self.LCD_backlight == 1:
                self.LCD_pwm.value = self.dim
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 0")
                   
        # Read the Wheel position
        if self.cutdown != 1 and self.cutdown != 4 and self.cutdown != 5 and self.Radio_ON == 0:
          #Reshow Album cover jpg (assuming one present) after 2 second delay
          if time.monotonic() - self.timer4 > 2 and self.drive_name != "":
              if self.render2 != "":
                  self.img.config(image = self.render2)
                  self.timer4 = 0
          if self.cutdown != 5 and self.cutdown != 1:
            if self.cutdown == 0 or self.cutdown == 7:
                x2 = abs_x - 107
                y2 = abs_y - 356
                c_min = 40
                c_max = 100
            elif cutdown == 8:
                x2 = abs_x - 171
                y2 = abs_y - 546
                c_min = 50
                c_max = 140
            elif cutdown == 6:
                x2 = abs_x - 160
                y2 = abs_y - 280
                c_min = 40
                c_max = 100
            elif cutdown == 2:
                x2 = abs_x - 78
                y2 = abs_y - 294
                c_min = 24
                c_max = 67
            else:
                x2 = abs_x - 142
                y2 = abs_y - 494
                c_min = 40
                c_max = 100
            if x2 >= 0 and y2 < 0:
                self.t = (0 - math.atan(x2/y2))
                self.t = int(self.t * 4)
            elif x2 >= 0 and y2 > 0:
                self.t =  ((3.06 - math.atan(x2/y2)))
                self.t = int(self.t * 4)
            elif x2 <= 0 and y2 > 0:
                self.t =  (3.06 + (0- math.atan(x2/y2)))
                self.t = int(self.t * 4)
            elif x2 <= 0 and y2 < 0:
                self.t = (6.12 - math.atan(x2/y2))
                self.t = int(self.t * 4)
            #print(math.sqrt((x2*x2)+ (y2*y2)))    
            # if cursor on the wheel position
            if math.sqrt((x2*x2)+ (y2*y2)) > c_min and math.sqrt((x2*x2)+ (y2*y2)) < c_max :
                if self.gpio_enable == 0 and (self.HP4_backlight == 1 or self.LCD_backlight == 1):
                    self.LCD_pwm.value = self.bright
                    self.light_on = time.monotonic()
                # show the wheel (instead of album cover)
                if self.cutdown != 1 and self.cutdown != 4 and self.cutdown != 5:
                    if os.path.exists(self.mp3_jpg):
                        if self.gapless == 0 and self.paused == 0:
                            if os.path.exists(self.mp3c_jpg):
                                self.img.config(image = self.renderc)
                        else:
                            if os.path.exists(self.mp3_jpg):
                                self.img.config(image = self.render)
                        self.timer4 = time.monotonic()
                self.wheel = 1
                if self.old_t > 19 and self.t < 5:
                    self.old_t = 0
                elif self.old_t < 5 and self.t > 19:
                    self.old_t = 24
                step = min(abs(self.t - self.old_t),5)
                if self.t > self.old_t and self.t - self.old_t < 14 and self.t - self.old_t > -14:
                    if self.wheel_opt == 0 and self.stopstart == 0:
                        self.Next_Artist()
                    elif self.wheel_opt == 1 and self.stopstart == 0:
                        self.Next_Album()
                    elif self.wheel_opt == 2 and self.stopstart == 0:
                        self.Next_Track()
                    elif self.wheel_opt == 3 and self.stopstart == 0:
                        self.Next_m3u()
                    elif self.wheel_opt == 4 and self.stopstart == 0:
                        if self.model == 4:
                            for ky in range(0,step):
                                self.nextAZ()
                        else:
                            self.nextAZ()
                    elif self.play == 1 and self.version == 2 and self.paused == 0:
                        self.skip = 10 * step
                        if self.skip + self.played < self.track_len  - self.skip:
                            self.start -= self.skip
                            self.total -= self.skip
                            if self.sleep_time_min > self.skip and self.shutdown == 1 and self.album_start == 1:
                                self.sleep_time_min -= self.skip
                            if self.BT == 0:
                                player.time_pos = self.skip + self.played
                elif self.t < self.old_t and self.t - self.old_t < 14 and self.t - self.old_t > -14:
                   if self.wheel_opt == 0 and self.stopstart == 0:
                       self.Prev_Artist()
                   elif self.wheel_opt == 1 and self.stopstart == 0:
                       self.Prev_Album()
                   elif self.wheel_opt == 2 and self.stopstart == 0:
                       self.Prev_Track()
                   elif self.wheel_opt == 3 and self.stopstart == 0:
                       self.Prev_m3u()
                   elif self.wheel_opt == 4 and self.stopstart == 0:
                       if self.model == 4:
                           for ky in range(0,step):
                               self.RnextAZ()
                       else:
                           self.RnextAZ()
                   elif self.play == 1 and self.version == 2 and self.paused == 0:
                       self.skip = 10 * step
                       if self.played - self.skip >= self.skip:
                           self.start += self.skip
                           self.total += self.skip
                           if self.sleep_time_min > self.skip and self.shutdown == 1 and self.album_start == 1:
                               self.sleep_time_min += self.skip
                           if self.BT == 0:
                               player.time_pos = self.played - self.skip
                self.old_t = self.t
        self.after(100, self.Check_Wheel)

    def Fade(self):
        if self.m != 0:
            self.volume -=2
            if self.volume < 0:
                self.volume = 0
            self.m.setvolume(self.volume)
            os.system("amixer -D pulse sset Master " + str(self.volume) + "%")
            if self.mixername == "DSP Program":
                os.system("amixer set 'Digital' " + str(self.volume + 107))
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2:
                self.Button_volume.config(text = self.volume)
            else:
                self.Button_Vol_UP.config(text = "Vol >   " + str(self.volume))

 
    def volume_DN(self):
        if self.m != 0:
            self.volume -=2
            self.volume = max(self.volume,0)
            self.f_volume = self.volume
            self.m.setvolume(self.volume)
            os.system("amixer -D pulse sset Master " + str(self.volume) + "%")
            if self.mixername == "DSP Program":
                os.system("amixer set 'Digital' " + str(self.volume + 107))
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2:
                self.Button_volume.config(text =self.volume)
            else:
                self.Button_Vol_UP.config(text = "Vol >   " + str(self.volume))
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            time.sleep(.2)

    def volume_UP(self):
        if self.m != 0:
            self.volume +=2
            self.volume = min(self.volume,100)
            self.f_volume = self.volume
            self.m.setvolume(self.volume)
            os.system("amixer -D pulse sset Master " + str(self.volume) + "%")
            if self.mixername == "DSP Program":
                os.system("amixer set 'Digital' " + str(self.volume + 107))
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2:
                self.Button_volume.config(text =self.volume)
            else:
                self.Button_Vol_UP.config(text = "Vol >   " + str(self.volume))
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            time.sleep(.2)

    def Mute(self):
        if self.m != 0:
            if self.muted == 0:
                self.muted = 1
                volume = 0
            else:
                self.muted = 0
                volume = self.volume
            self.m.setvolume(volume)
            os.system("amixer -D pulse sset Master " + str(volume) + "%")
            if self.mixername == "DSP Program":
                os.system("amixer set 'Digital' " + str(volume + 107))
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2:
                self.Button_volume.config(text = volume)
            else:
                self.Button_Vol_UP.config(text = "Vol >   " + str(volume))
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            time.sleep(.2)

    def Prev_m3u(self):
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir) and self.Radio_ON == 0:
            if self.imgxon == 1:
                self.imgx.after(100, self.imgx.destroy())
                self.imgxon = 0
                if cutdown == 1:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 4:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
            print(self.wheel_opt)
            if self.rotary_pos != 1:
                self.wheel_opt = 3
            print(self.wheel_opt)
            if self.cutdown != 5 and self.cutdown != 6:
                self.Button_Next_PList.config(fg = "red")
            self.Button_Next_Artist.config(fg = "black")
            self.Button_Next_Album.config(fg = "black")
            self.Button_Next_Track.config(fg = "black")
            self.Button_Reload.config(bg = "light blue", fg = "black")
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3 or self.cutdown == 2:
                self.Button_Next_AZ.config(fg = "black")
                self.Disp_Name_m3u.config(background="light gray", foreground="black")
            if self.play == 1:
                if self.version == 1:
                    poll = self.p.poll()
                    if poll is None:
                        self.p.kill()
                else:
                    player.stop()
                    self.paused = 0
                    if self.BT == 0 and (self.cutdown == 0 or self.cutdown == 2 or self.cutdown == 3):
                        self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                self.Button_Start.config(bg = "green",fg = "black",text = "PLAY Playlist")
            self.play = 0
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")
            self.m3u_no -=1
            if self.m3u_no < 0:
                self.m3u_no = len(self.m3us) - 1
            self.que_dir = self.m3us[self.m3u_no]
            Tracks = []
            with open(self.que_dir,"r") as textobj:
                line = textobj.readline()
                while line:
                    Tracks.append(line.strip())
                    line = textobj.readline()
            self.tunes = []
            self.Artist_options = []
            for counter in range (0,len(Tracks)):
                counter2 = Tracks[counter].count('/')
                if counter2 == 6:
                    self.genre_name = "None"
                    z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                    self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)
                    self.Artist_options.append(self.artist_name)
                if counter2 == 7:
                    z,self.drive_name1,self.drive_name2,self.drive_name,self.genre_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                    self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)
                    self.Artist_options.append(self.artist_name)
                if counter2 == 5:
                    self.genre_name = "None"
                    self.drive_name1,self.drive_name2,self.drive_name,self.artist_name3,self.album_name3,self.track_name  = Tracks[counter].split('/')
                    if self.album_name3.count(" - ") == 1:
                        self.artist_name,self.album_name = self.album_name3.split(" - ")
                        self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.artist_name3 + "*^" + self.drive_name2 + "^" + self.drive_name + "^" + self.genre_name)
                        self.Artist_options.append(self.artist_name)
            if self.cutdown >= 7:
                self.Artist_options.sort()
                self.Artist_options = list(dict.fromkeys(self.Artist_options))
                self.Disp_artist_name["values"] = self.Artist_options 
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.total = 0
            self.track_no = 0
            self.shuffle_on = 0
            self.tunes.sort()
            self.Button_Shuffle.config(bg = "light blue",fg = "black",text = "Shuffle")
            self.sorted = 0
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3:
                self.Button_AZ_artists.config(bg = "light blue",fg = "black",text = "A-Z Sort")
            self.Time_Left_Play()

    def Next_m3u(self):
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir) and self.Radio_ON == 0:
            if self.imgxon == 1:
                self.imgx.after(100, self.imgx.destroy())
                self.imgxon = 0
                if cutdown == 1:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 4:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
            if self.rotary_pos != 1:
                self.wheel_opt = 3
            if self.cutdown != 5 and self.cutdown != 6:
                self.Button_Next_PList.config(fg = "red")
            self.Button_Next_Artist.config(fg = "black")
            self.Button_Next_Album.config(fg = "black")
            self.Button_Next_Track.config(fg = "black")
            self.Button_Reload.config(bg = "light blue", fg = "black")
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3 or self.cutdown == 2:
                self.Button_Next_AZ.config(fg = "black")
                self.Disp_Name_m3u.config(background="light gray", foreground="black")
            if self.play == 1:
                if self.version == 1:
                    poll = self.p.poll()
                    if poll is None:
                        self.p.kill()
                else:
                    player.stop()
                    self.paused = 0
                    if self.BT == 0 and (self.cutdown == 0 or self.cutdown == 2 or self.cutdown == 3):
                        self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                self.Button_Start.config(bg = "green",fg = "black",text = "PLAY Playlist")
            self.play = 0
            self.m3u_no +=1
            if self.m3u_no > len(self.m3us)-1:
                self.m3u_no = 0
            self.que_dir = self.m3us[self.m3u_no]
            Tracks = []
            
            with open(self.que_dir,"r") as textobj:
               line = textobj.readline()
               while line:
                  Tracks.append(line.strip())
                  line = textobj.readline()
            self.tunes = []
            self.Artist_options = []
            for counter in range (0,len(Tracks)):
                counter2 = Tracks[counter].count('/')
                if counter2 == 6:
                    self.genre_name = "None"
                    z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                    self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)
                    self.Artist_options.append(self.artist_name)
                if counter2 == 7:
                    z,self.drive_name1,self.drive_name2,self.drive_name,self.genre_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                    self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)
                    self.Artist_options.append(self.artist_name)
                if counter2 == 5:
                    self.genre_name = "None"
                    self.drive_name1,self.drive_name2,self.drive_name,self.artist_name3,self.album_name3,self.track_name  = Tracks[counter].split('/')
                    if self.album_name3.count(" - ") == 1:
                        self.artist_name,self.album_name = self.album_name3.split(" - ")
                        self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.artist_name3 + "*^" + self.drive_name2 + "^" + self.drive_name + "^" + self.genre_name)
                        self.Artist_options.append(self.artist_name)
            if self.cutdown >= 7:
                self.Artist_options.sort()
                self.Artist_options = list(dict.fromkeys(self.Artist_options))
                self.Disp_artist_name["values"] = self.Artist_options
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.track_no = 0
            self.shuffle_on = 0
            self.tunes.sort()
            self.Button_Shuffle.config(bg = "light blue",fg = "black",text = "Shuffle")
            self.sorted = 0
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3:
                self.Button_AZ_artists.config(bg = "light blue",fg = "black",text = "A-Z Sort")
            self.Time_Left_Play()

    def Prev_Artist(self):
        # Previous Radio Station
        if self.Radio_ON == 1 and self.Radio_RON == 0:
            self.copy = 0
            if self.cutdown >= 7:
                self.Disp_track_name.set("  ")
            else:
                self.Disp_track_name.config(text = " ")
            if cutdown == 1:
                self.Disp_track_len.config(text =int(len(self.Radio_Stns)/3))
                self.L4.config(text="of")
            if self.Radio_Stns[self.Radio + 2] == 0:
                self.q.kill()
            else:
                self.q.kill()
                self.r.kill()
            self.Radio -= 3
            if self.Radio < 0:
                self.Radio = len(self.Radio_Stns) - 3
            if cutdown == 1:
                self.Disp_played.config(text = int((self.Radio)/3)+1)
            self.playlist = "-nocache"
            if ".pls" in self.Radio_Stns[self.Radio + 1]  or ".m3u"  in self.Radio_Stns[self.Radio + 1]  :
                    self.playlist = "-playlist"
                    self.Radio_Stns[self.Radio + 2] = 0
            if self.Radio_Stns[self.Radio + 2] == 0:
                self.q = subprocess.Popen(["mplayer",self.playlist, self.Radio_Stns[self.Radio + 1]] , shell=False)
            else:
                self.r = subprocess.Popen(["streamripper", self.Radio_Stns[self.Radio + 1],"-r","--xs_offset=-9000","-z","-l", "99999","-d", "/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings","-a",self.Radio_Stns[self.Radio]], shell=False)
                time.sleep(1)
                self.q = subprocess.Popen(["mplayer", "-nocache", "http://localhost:8000"] , shell=False)
                track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
                if len(track) == 0:
                    time.sleep(2)
            if self.Radio_Stns[self.Radio + 2]  > 0 and self.record == 1:
                self.Button_Pause.config(fg = "black", bg = "light blue", text = "RECORD")
                if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and  self.cutdown != 6 and self.touchscreen == 1:
                    self.L8.config(text = ".mp3")
            else:
                self.Button_Pause.config(fg = "black", bg = "light grey", text = "Pause")
                if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and  self.cutdown != 6 and self.touchscreen == 1:
                    self.L8.config(text = "")
            if self.cutdown == 1 or self.cutdown == 4 or self.cutdown == 5:
                self.Disp_track_len.config(text = int(len(self.Radio_Stns)/3))
                self.Disp_played.config(text = int((self.Radio)/3)+1)
                self.L4.config(text="of")
                if self.cutdown == 1:
                    self.Disp_Total_tunes.config(text = "        Stn:")
                if self.cutdown == 1:
                    self.Disp_Total_tunes.config(text = "        Stn:")
                elif self.cutdown == 4:
                    self.Disp_Total_tunes.config(text = "    Stn:")
                else:   
                    self.L3.config(text = "Stn:")
            self.Name = self.Radio_Stns[self.Radio]
            if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg") or os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                self.imgxon = 0
            if self.imgxon == 1:
                self.imgx.after(100, self.imgx.destroy())
                self.imgxon = 0
                if cutdown == 1:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 4:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                elif cutdown == 5:
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)

            elif self.imgxon == 0 and (self.cutdown == 1 or self.cutdown == 4 or self.cutdown == 5):
                    if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg"):
                        self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".jpg")
                        if self.cutdown == 1:
                            self.load = self.load.resize((100, 100), Image.LANCZOS)
                        elif self.cutdown == 4:
                            self.load = self.load.resize((130, 130), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((170, 170), Image.LANCZOS)
                        self.render2 = ImageTk.PhotoImage(self.load)
                        if self.imgxon == 0:
                            self.imgx = tk.Label(self.Frame10, image = self.render2)
                            self.imgx.grid(row = 1, column = 1, columnspan = 3, rowspan = 3, pady = 0)
                            self.imgxon = 1
                            if self.cutdown == 1 or self.cutdown == 4:
                                self.Disp_plist_name.after(100, self.Disp_plist_name.destroy())
                            self.Disp_artist_name.after(100, self.Disp_artist_name.destroy())
                            self.Disp_album_name.after(100, self.Disp_album_name.destroy())
                        self.imgx.config(image = self.render2)
                    elif os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                        self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".png")
                        if self.cutdown == 1:
                            self.load = self.load.resize((100, 100), Image.LANCZOS)
                        elif self.cutdown == 4:
                            self.load = self.load.resize((130, 130), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((170, 170), Image.LANCZOS)
                        self.render2 = ImageTk.PhotoImage(self.load)
                        if self.imgxon == 0:
                            self.imgx = tk.Label(self.Frame10, image = self.render2)
                            self.imgx.grid(row = 1, column = 1, columnspan = 3, rowspan = 3, pady = 0)
                            self.imgxon = 1
                            if self.cutdown == 1 or self.cutdown == 4:
                                self.Disp_plist_name.after(100, self.Disp_plist_name.destroy())
                            self.Disp_artist_name.after(100, self.Disp_artist_name.destroy())
                            self.Disp_album_name.after(100, self.Disp_album_name.destroy())
                        self.imgx.config(image = self.render2)
            if( self.cutdown != 7 and self.cutdown != 8) and self.imgxon == 0:
                self.Disp_artist_name.config(text = self.Name)
                self.Disp_track_name.config(text = " ")
            elif self.imgxon == 0:
                self.Disp_artist_name.set(self.Name)
                self.Disp_track_name.set("  ")
            if self.cutdown != 4 and self.cutdown != 5 and self.cutdown != 1:
                if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg"):
                    self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".jpg")
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS)
                    self.render2 = ImageTk.PhotoImage(self.load)
                    self.img.config(image = self.render2)
                elif os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                    self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".png")
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS)
                    self.render2 = ImageTk.PhotoImage(self.load)
                    self.img.config(image = self.render2)
                elif os.path.exists(self.radio_jpg):
                    self.load = Image.open(self.radio_jpg)
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS)
                    self.render3 = ImageTk.PhotoImage(self.load)
                    self.img.config(image = self.render3)
            track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            # check RAM space and set self.max_record
            st = os.statvfs("/run/shm/")
            self.freeram1 = (st.f_bavail * st.f_frsize)/1100000
            self.timer7 = time.monotonic()
            free2 = int((self.freeram1 - self.ram_min)/10) * 10
            self.max_record = min(free2,991)
            self.ramtest = 1
            self.Check_Record()
            if len(track) == 0  and self.Radio_Stns[self.Radio + 2]  > 0:
                if self.rotary_pos== 0:
                    messagebox.showinfo("WARNING!","Check Recordable entry set correctly for this stream")
        # Previous Artist
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir) and self.Radio_ON == 0:
            if self.imgxon == 1:
                self.imgx.after(100, self.imgx.destroy())
                self.imgxon = 0
                if cutdown == 1:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 4:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 5:
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
            if self.rotary_pos != 1:
                self.wheel_opt = 0
            self.Button_Next_Artist.config(fg = "red")
            if self.cutdown != 5 and self.cutdown != 6:
                self.Button_Next_PList.config(fg = "black")
            self.Button_Next_Album.config(fg = "black")
            self.Button_Next_Track.config(fg = "black")
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3 or self.cutdown == 2:
                self.Button_Next_AZ.config(fg = "black")
                self.Disp_Name_m3u.config(background="light gray", foreground="black")
            if self.play == 2 and self.album_start == 1:
                self.play = 0
            stop = 0
            if len(self.tunes) > 0:
                while (self.tunes[self.track_no].split('^')[0]) == self.artist_name and stop == 0:
                    self.track_no -=1
                    if self.track_no < 0:
                        self.track_no = 0
                        stop = 1
                new_artist_name = self.tunes[self.track_no].split('^')[0]
                stop = 0
                while (self.tunes[self.track_no].split('^')[0]) == new_artist_name and stop == 0:
                    self.track_no -=1
                    if self.track_no < 0:
                        self.track_no = -1 
                        stop = 1
                if self.play == 0:
                   self.track_no +=1
                if self.track_no > len(self.tunes) - 1:
                   self.track_no = 0
                if self.play == 1:
                    if self.version == 1:
                        poll = self.p.poll()
                        if poll is None:
                            self.p.kill()
                    else:
                        player.stop()
                    self.start = 0
                    self.stop7 = 1
                self.count1 = 0
                self.count2 = 0
                self.Time_Left_Play()

    def Next_Artist(self):
        # Next Radio Station
        if self.Radio_ON == 1 and self.Radio_RON == 0:
            self.copy = 0
            if self.cutdown >= 7:
                self.Disp_track_name.set("  ")
            else:
                self.Disp_track_name.config(text = " ")
            if cutdown == 1:
                self.Disp_track_len.config(text =int(len(self.Radio_Stns)/3))
                self.L4.config(text="of")
            if self.Radio_Stns[self.Radio + 2] == 0:
                self.q.kill()
            else:
                self.q.kill()
                self.r.kill()
            if self.NewRadio == -1:
                self.Radio += 3
            else:
                self.Radio = self.NewRadio
                self.NewRadio = -1
            if self.Radio > len(self.Radio_Stns) - 1:
                self.Radio = 0
            if cutdown == 1:
                self.Disp_played.config(text = int((self.Radio)/3)+1)
            self.playlist = "-nocache"
            if ".pls" in self.Radio_Stns[self.Radio + 1]  or ".m3u"  in self.Radio_Stns[self.Radio + 1]  :
                    self.playlist = "-playlist"
                    self.Radio_Stns[self.Radio + 2] = 0
            if self.Radio_Stns[self.Radio + 2] == 0:
                self.q = subprocess.Popen(["mplayer",self.playlist, self.Radio_Stns[self.Radio + 1]] , shell=False)
            else:
                self.r = subprocess.Popen(["streamripper", self.Radio_Stns[self.Radio + 1],"-r","--xs_offset=-9000","-z","-l", "99999","-d", "/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings","-a",self.Radio_Stns[self.Radio]], shell=False)
                time.sleep(1)
                self.q = subprocess.Popen(["mplayer", "-nocache", "http://localhost:8000"] , shell=False)
                track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
                if len(track) == 0:
                    time.sleep(2)
            if self.Radio_Stns[self.Radio + 2]  > 0 and self.record == 1:
                self.Button_Pause.config(fg = "black", bg = "light blue", text = "RECORD")
                if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and  self.cutdown != 6 and self.touchscreen == 1:
                    self.L8.config(text = ".mp3")
            else:
                self.Button_Pause.config(fg = "black", bg = "light grey", text = "Pause")
                if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and  self.cutdown != 6 and self.touchscreen == 1:
                    self.L8.config(text = "")
            if self.cutdown == 1 or self.cutdown == 4 or self.cutdown == 5:
                self.Disp_track_len.config(text = int(len(self.Radio_Stns)/3))
                self.Disp_played.config(text = int((self.Radio)/3)+1)
                self.L4.config(text="of")
                if self.cutdown == 1:
                    self.Disp_Total_tunes.config(text = "        Stn:")
                if self.cutdown == 1:
                    self.Disp_Total_tunes.config(text = "        Stn:")
                elif self.cutdown == 4:
                    self.Disp_Total_tunes.config(text = "    Stn:")
                else:   
                    self.L3.config(text = "Stn:")
            self.Name = self.Radio_Stns[self.Radio]
            if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg") or os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                self.imgxon = 0
            if self.imgxon == 1:
                self.imgx.after(100, self.imgx.destroy())
                self.imgxon = 0
                if cutdown == 1:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 4:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 5:
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
                    
            elif self.imgxon == 0 and (self.cutdown == 1 or self.cutdown == 4 or self.cutdown == 5):
                    if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg"):
                        self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".jpg")
                        if self.cutdown == 1:
                            self.load = self.load.resize((100, 100), Image.LANCZOS)
                        elif self.cutdown == 4:
                            self.load = self.load.resize((130, 130), Image.LANCZOS)
                        elif self.cutdown == 5:
                            self.load = self.load.resize((170, 170), Image.LANCZOS)
                        self.render2 = ImageTk.PhotoImage(self.load)
                        if self.imgxon == 0:
                            self.imgx = tk.Label(self.Frame10, image = self.render2)
                            self.imgx.grid(row = 1, column = 1, columnspan = 3, rowspan = 3, pady = 0)
                            self.imgxon = 1
                            if self.cutdown == 1 or self.cutdown == 4:
                                self.Disp_plist_name.after(100, self.Disp_plist_name.destroy())
                            self.Disp_artist_name.after(100, self.Disp_artist_name.destroy())
                            self.Disp_album_name.after(100, self.Disp_album_name.destroy())
                        self.imgx.config(image = self.render2)
                    elif os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                        self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".png")
                        if self.cutdown == 1:
                            self.load = self.load.resize((100, 100), Image.LANCZOS)
                        elif self.cutdown == 4:
                            self.load = self.load.resize((130, 130), Image.LANCZOS)
                        elif self.cutdown == 5:
                            self.load = self.load.resize((170, 170), Image.LANCZOS)
                        self.render2 = ImageTk.PhotoImage(self.load)
                        if self.imgxon == 0:
                            self.imgx = tk.Label(self.Frame10, image = self.render2)
                            self.imgx.grid(row = 1, column = 1, columnspan = 3, rowspan = 3, pady = 0)
                            self.imgxon = 1
                            if self.cutdown == 1 or self.cutdown == 4:
                                self.Disp_plist_name.after(100, self.Disp_plist_name.destroy())
                            self.Disp_artist_name.after(100, self.Disp_artist_name.destroy())
                            self.Disp_album_name.after(100, self.Disp_album_name.destroy())
                        self.imgx.config(image = self.render2)
            if( self.cutdown != 7 and self.cutdown != 8) and self.imgxon == 0:
                self.Disp_artist_name.config(text = self.Name)
                self.Disp_track_name.config(text = " ")
            elif self.imgxon == 0:
                self.Disp_artist_name.set(self.Name)
                self.Disp_track_name.set("  ")
            if self.cutdown != 4 and self.cutdown !=5 and self.cutdown !=1:
                if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg"):
                    self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".jpg")
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS)
                    self.render2 = ImageTk.PhotoImage(self.load)
                    self.img.config(image = self.render2)
                elif os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                    self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".png")
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS)
                    self.render2 = ImageTk.PhotoImage(self.load)
                    self.img.config(image = self.render2)
                elif os.path.exists(self.radio_jpg):
                    self.load = Image.open(self.radio_jpg)
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS)
                    self.render3 = ImageTk.PhotoImage(self.load)
                    self.img.config(image = self.render3)
            track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            # check RAM space and set self.max_record
            st = os.statvfs("/run/shm/")
            self.freeram1 = (st.f_bavail * st.f_frsize)/1100000
            self.timer7 = time.monotonic()
            free2 = int((self.freeram1 - self.ram_min)/10) * 10
            self.max_record = min(free2,991)
            self.ramtest = 1
            self.Check_Record()
            if len(track) == 0  and self.Radio_Stns[self.Radio + 2]  > 0:
                if self.rotary_pos== 0:
                    messagebox.showinfo("WARNING!","Check Recordable entry set correctly for this stream")
        # Next Artist
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir) and self.Radio_ON == 0:
            if self.imgxon == 1:
                self.imgx.after(100, self.imgx.destroy())
                self.imgxon = 0
                if cutdown == 1:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 4:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 5:
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
            self.wheel_opt = 0
            self.Button_Next_Artist.config(fg = "red")
            if self.cutdown != 5 and self.cutdown != 6:
                self.Button_Next_PList.config(fg = "black")
            self.Button_Next_Album.config(fg = "black")
            self.Button_Next_Track.config(fg = "black")
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3 or self.cutdown == 2:
                self.Button_Next_AZ.config(fg = "black")
                self.Disp_Name_m3u.config(background="light gray", foreground="black")
            if self.play == 2:
                self.play = 0
            stop = 0
            if len(self.tunes) > 0:
                while (self.tunes[self.track_no].split('^')[0]) == self.artist_name and stop == 0:
                    self.track_no +=1
                    if self.track_no > len(self.tunes) - 1:
                        self.track_no = 0
                        stop = 1
                if self.play == 1:
                    if self.track_no != 0:
                        self.track_no -=1
                    if self.version == 1:
                        poll = self.p.poll()
                        if poll is None:
                            self.p.kill()
                    else:
                        player.stop()
                    self.start = 0
                    self.stop7 = 1
                self.count1 = 0
                self.count2 = 0
                self.Time_Left_Play()

    def Prev_Album(self):
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir) and self.Radio_ON == 0:
            if self.imgxon == 1:
                self.imgx.after(100, self.imgx.destroy())
                self.imgxon = 0
                if cutdown == 1:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 4:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 5:
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
            if self.rotary_pos != 1:
                self.wheel_opt = 1
            self.Button_Next_Album.config(fg = "red")
            self.Button_Next_Artist.config(fg = "black")
            if self.cutdown != 5 and self.cutdown != 6:
                self.Button_Next_PList.config(fg = "black")
            self.Button_Next_Track.config(fg = "black")
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3 or self.cutdown == 2:
                self.Button_Next_AZ.config(fg = "black")
                self.Disp_Name_m3u.config(background="light gray", foreground="black")
            if self.play == 2:
                self.play = 0
            if self.version == 2:
                self.paused = 0
                if self.BT == 0 and (self.cutdown == 0 or self.cutdown == 2 or self.cutdown == 3):
                    self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
            stop = 0
            if len(self.tunes) > 0:
                while (self.tunes[self.track_no].split('^')[0]) == self.artist_name and (self.tunes[self.track_no].split('^')[1]) == self.album_name and stop == 0:
                    self.track_no -=1
                    if self.track_no < 0:
                        self.track_no = 0 
                        stop = 1
                new_album_name  = self.tunes[self.track_no].split('^')[1]
                new_artist_name = self.tunes[self.track_no].split('^')[0]
                stop = 0
                while (self.tunes[self.track_no].split('^')[0]) == new_artist_name and (self.tunes[self.track_no].split('^')[1]) == new_album_name and stop == 0:
                    self.track_no -=1
                    if self.track_no < 0:
                        self.track_no = -1 
                        stop = 1
                if self.play == 0:
                    self.track_no +=1
                if self.track_no > len(self.tunes) - 1:
                    self.track_no = 0
                if self.play == 1:
                    if self.version == 1:
                        poll = self.p.poll()
                        if poll is None:
                            self.p.kill()
                    else:
                        player.stop()
                    self.start = 0
                    self.stop7 = 1
                self.bc = 1
                self.count1 = 0
                self.count2 = 0
                self.Time_Left_Play()

    def Next_Album(self):
        if self.trace > 0:
            print ("Next Album entry ", self.track_no,self.play)
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir) and self.Radio_ON == 0:
            if self.imgxon == 1:
                self.imgx.after(100, self.imgx.destroy())
                self.imgxon = 0
                if cutdown == 1:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 4:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 5:
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
            self.wheel_opt = 1
            self.Button_Next_Album.config(fg = "red")
            self.Button_Next_Artist.config(fg = "black")
            if self.cutdown != 5 and self.cutdown != 6:
                self.Button_Next_PList.config(fg = "black")
            self.Button_Next_Track.config(fg = "black")
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3 or self.cutdown == 2:
                self.Button_Next_AZ.config(fg = "black")
                self.Disp_Name_m3u.config(background="light gray", foreground="black")
            if self.play == 2:
                self.play = 0
            if self.version == 2:
                self.paused = 0
                if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3:
                    self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
            stop = 0
            if len(self.tunes) > 0:
                if self.trace > 0:
                    print(self.track_no,(self.tunes[self.track_no].split('^')[1]),self.album_name )
                while (self.tunes[self.track_no].split('^')[0]) == self.artist_name and (self.tunes[self.track_no].split('^')[1]) == self.album_name and stop == 0:
                    self.track_no +=1
                    if self.track_no > len(self.tunes) - 1:
                        self.track_no = 0
                        stop = 1
                if self.trace > 0:
                    print("==========================================================================")
                    print(self.track_no,(self.tunes[self.track_no].split('^')[1]),self.album_name )
                if self.play == 1:
                    self.track_no -=1
                if self.trace > 0:
                    print(self.track_no,(self.tunes[self.track_no].split('^')[1]),self.album_name )
                if self.play == 1:
                    if self.version == 1:
                        poll = self.p.poll()
                        if poll is None:
                            self.p.kill()
                    else:
                        player.stop()
                    self.start = 0
                    self.stop7 = 1
                self.bc = 1
                self.count1 = 0
                self.count2 = 0
                self.Time_Left_Play()
        if self.trace > 0:
            print ("Next Album exit ", self.track_no,self.play)
            
    def Prev_Track(self):
        if self.album_track != 1 and os.path.exists(self.que_dir) and self.Radio_ON == 0:
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3:
                self.Disp_Name_m3u.config(background="light gray", foreground="black")
            if self.imgxon == 1:
                self.imgx.after(100, self.imgx.destroy())
                self.imgxon = 0
                if cutdown == 1:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 4:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 5:
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
            if self.paused == 0:
                if self.album_start == 0:
                    if self.rotary_pos != 1:
                        self.wheel_opt = 2
                    self.Button_Next_Track.config(fg = "red")
                    self.Button_Next_Artist.config(fg = "black")
                    self.Button_Next_Album.config(fg = "black")
                    if self.cutdown != 5 and self.cutdown != 6:
                        self.Button_Next_PList.config(fg = "black")
                    if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3 or self.cutdown == 2:
                        self.Button_Next_AZ.config(fg = "black")
                if self.play == 2:
                    self.play = 0
                if self.version == 2 and (self.cutdown == 0 or self.cutdown == 2 or self.cutdown == 3):
                    self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                if self.play == 1:
                   if self.version == 1:
                        poll = self.p.poll()
                        if poll is None:
                            self.p.kill()
                   else:
                        player.stop()
                   self.start = 0
                   self.stop7 = 1
                   self.xxx = 1
                   self.track_no -=2
                   if self.track_no < -1:
                       self.track_no = len(self.tunes) - 1
                   if self.album_start == 0:
                       self.count1 = 0
                       self.count2 = 0
                   if self.album_start == 0:
                       self.Time_Left_Play()
                   else:
                       self.album_track -=2
                       if self.album_track < 0:
                           self.album_track = 0
                       self.Play()
                else:
                    self.track_no -=1
                    if self.track_no < 0:
                        self.track_no = len(self.tunes) - 1
                    self.count1 = 0
                    self.count2 = 0
                    self.tracker = 0 ###
                    self.Time_Left_Play()
                    

    def Next_Track(self):
        if self.trace > 0:
            print ("Next_Track",self.album_start)
        if (self.album_start == 0 and os.path.exists(self.que_dir)) or (self.album_start == 1 and self.track_no != self.tcount and os.path.exists(self.que_dir)):
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3:
                self.Disp_Name_m3u.config(background="light gray", foreground="black")
            if self.paused == 0 and self.Radio_ON == 0:
                if self.imgxon == 1:
                    self.imgx.after(100, self.imgx.destroy())
                    self.imgxon = 0
                    if cutdown == 1:
                        self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                        self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                        self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                        self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                        self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                        self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                        self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    elif cutdown == 4:
                        self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                        self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                        self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                        self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                        self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                        self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                        self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    elif cutdown == 5:
                        self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                        self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                        self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                        self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                        self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                        self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
                if self.album_start == 0:
                    self.wheel_opt = 2
                    self.Button_Next_Track.config(fg = "red")
                    self.Button_Next_Artist.config(fg = "black")
                    self.Button_Next_Album.config(fg = "black")
                    if self.cutdown != 5 and self.cutdown != 6:
                        self.Button_Prev_PList.config(fg = "black")
                    if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3 or self.cutdown == 2:
                        self.Button_Next_AZ.config(fg = "black")
                if self.play == 2:
                    self.play = 0
                if self.version == 2 and (self.cutdown == 0 or self.cutdown == 2):
                    self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                if self.play == 1 :
                    if self.version == 1:
                        poll = self.p.poll()
                        if poll is None:
                            self.p.kill()
                    else:
                        player.stop()
                    self.start = 0
                    self.stop7 = 1
                    self.xxx = 1
                    if self.album_start == 0:
                        self.count1 = 0
                        self.count2 = 0
                        self.Time_Left_Play()
                    else:
                        self.Play()
                else:
                    self.track_no +=1
                    if self.track_no > len(self.tunes) -1:
                        self.track_no = 0
                    self.count1  = 0
                    self.count2  = 0
                    self.tracker = 0
                    self.Time_Left_Play()

    def Time_Left_Play(self):
         if self.trace > 0 and len(self.tunes) > 0:
             print ("Time Left Play ",self.tunes[self.track_no])
         self.start2 = time.monotonic()
         self.total = 0
         stop = 0
         counter = self.track_no 
         if self.play == 1:
             counter +=1
         if self.play == 2:
             counter = 0
         self.minutes = 0
         while counter < len(self.tunes) and stop == 0:
             self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[counter].split('^')
             counter +=1
             if self.drive_name[-1] == "*":
                self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name[:-1], self.artist_name + " - " + self.album_name, self.track_name)
             elif self.genre_name == "None":
                self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name, self.artist_name, self.album_name, self.track_name)
             else:
                self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name,self.genre_name, self.artist_name, self.album_name, self.track_name)
             if os.path.exists(self.track):
                 if self.track[-4:] == ".mp3":
                     audio = MP3(self.track)
                     self.total += audio.info.length
                 if self.track[-4:] == "flac":       
                     audio = FLAC(self.track)
                     self.total += audio.info.length
                 if self.track[-4:] == ".dsf":
                    audio = DSF(self.track)
                    self.total += audio.info.length
                 if self.track[-4:] == ".m4a":
                    audio = MP4(self.track)
                    self.total += audio.info.length
                 elif self.track[-4:] == ".wav":
                     with contextlib.closing(wave.open(self.track,'r')) as f:
                         frames = f.getnframes()
                         rate = f.getframerate()
                         self.track_len = frames / float(rate)
                         self.total += self.track_len
                 if self.total > self.Disp_max_time * 60:
                    stop = 1
         self.minutes = int(self.total // 60)
         self.seconds = int (self.total - (self.minutes * 60))
         if self.trace > 0:
             print ("Time Left Play",self.minutes,self.seconds)
         if self.cutdown != 1 and self.cutdown != 4 and self.cutdown != 5  and self.cutdown != 6:
             if stop == 0:
                 self.Disp_Total_Plist.config(text ="%03d:%02d" % (self.minutes, self.seconds % 60))
             else:
                 self.Disp_Total_Plist.config(text = ">" + str(self.Disp_max_time) + ":00" )
         if self.cutdown == 4 and (self.album_start == 1 or self.stopstart == 1):
             if stop == 0:
                 self.Disp_Name_m3u.delete('1.0','20.0')
                 self.Disp_Name_m3u.insert(INSERT,"  " + "%03d:%02d" % (self.minutes, self.seconds % 60))
             else:
                 self.Disp_Name_m3u.delete('1.0','20.0')
                 self.Disp_Name_m3u.insert(INSERT,">" + str(self.Disp_max_time) + ":00" )
         if self.play == 1:
             #self.bc = 1
             self.ac = 1
             self.Show_Track()
             self.Start_Play()
         else:
             self.stopstart = 0
             self.Show_Track()

    def nextAZ(self):
        if (self.Radio_RON == 1 or self.album_start == 1 or self.stopstart == 1):
            self.PopupInfo()
            if self.rotary_pos == 1:
                self.Button_Next_AZ.config(bg = "yellow")
            if self.Radio_RON == 1:
                self.Button_Prev_Album.config(bg = 'light gray')
                self.Button_Prev_Track.config(bg = 'light gray')
        elif self.album_start == 0 and self.stopstart == 0 and len(self.tunes) > 1 and self.Radio_ON == 0:
            stop = 0
            if self.wheel_opt == 0 or self.wheel_opt == 3 or self.rot_mode == 2:
                while (self.tunes[self.track_no].split('^')[0][0]) == self.artist_name[0] and stop == 0:
                    self.track_no +=1
                    if self.track_no > len(self.tunes) - 1:
                        self.track_no = 0
                        stop = 1
            elif self.wheel_opt == 1:
                while (self.tunes[self.track_no].split('^')[1][0]) == self.album_name[0] and stop == 0:
                    self.track_no +=1
                    if self.track_no > len(self.tunes) - 1:
                        self.track_no = 0
                        stop = 1
            elif self.wheel_opt == 2:
                while (self.tunes[self.track_no].split('^')[2][3]) == self.track_name[3] and stop == 0:
                    self.track_no +=1
                    if self.track_no > len(self.tunes) - 1:
                        self.track_no = 0
                        stop = 1
            elif self.wheel_opt == 4:
                while (self.tunes[self.track_no].split('^')[0][0][0:1]) == self.artist_name[0][0:1] and stop == 0:
                    self.track_no +=1
                    if self.track_no > len(self.tunes) - 1:
                        self.track_no = 0
                        stop = 1
            self.Time_Left_Play()
        elif self.album_start == 0 and self.stopstart == 0 and self.Radio_ON == 1 and self.rot_mode == 1:
             # Next A-Z Radio Station
            self.copy = 0
            self.Disp_track_name.config(text = "")
            if cutdown == 1:
                self.Disp_track_len.config(text =int(len(self.Radio_Stns)/3))
                self.L4.config(text="of")
            if self.Radio_Stns[self.Radio + 2] == 0:
                self.q.kill()
            else:
                self.q.kill()
                self.r.kill()
            if self.NewRadio == -1:
                stop = 0
                while self.Name[0:1] == self.Radio_Stns[self.Radio][0:1] and stop == 0:
                    self.Radio += 3
                    if self.Radio > len(self.Radio_Stns) - 1:
                        self.Radio = 0
                        stop = 1
            else:
                self.Radio = self.NewRadio
                self.NewRadio = -1
            if cutdown == 1:
                self.Disp_played.config(text = int((self.Radio)/3)+1)
            if self.Radio_Stns[self.Radio + 2] == 0:
                self.q = subprocess.Popen(["mplayer", "-nocache", self.Radio_Stns[self.Radio + 1]] , shell=False)
            else:
                self.r = subprocess.Popen(["streamripper", self.Radio_Stns[self.Radio + 1],"-r","--xs_offset=-9000","-z","-l", "99999","-d", "/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings","-a",self.Radio_Stns[self.Radio]], shell=False)
                time.sleep(1)
                self.q = subprocess.Popen(["mplayer", "-nocache", "http://localhost:8000"] , shell=False)
                track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
                if len(track) == 0:
                    time.sleep(2)
            if self.Radio_Stns[self.Radio + 2]  > 0 and self.record == 1:
                self.Button_Pause.config(fg = "black", bg = "light blue", text = "RECORD")
                if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and  self.cutdown != 6 and self.touchscreen == 1:
                    self.L8.config(text = ".mp3")
            else:
                self.Button_Pause.config(fg = "black", bg = "light grey", text = "Pause")
                if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and  self.cutdown != 6 and self.touchscreen == 1:
                    self.L8.config(text = "")
            if self.cutdown == 1 or self.cutdown == 4 or self.cutdown == 5:
                self.Disp_track_len.config(text = int(len(self.Radio_Stns)/3))
                self.Disp_played.config(text = int((self.Radio)/3)+1)
                self.L4.config(text="of")
                if self.cutdown == 1:
                    self.Disp_Total_tunes.config(text = "        Stn:")
                if self.cutdown == 1:
                    self.Disp_Total_tunes.config(text = "        Stn:")
                elif self.cutdown == 4:
                    self.Disp_Total_tunes.config(text = "    Stn:")
                else:   
                    self.L3.config(text = "Stn:")
            self.Name = self.Radio_Stns[self.Radio]
            if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg") or os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                self.imgxon = 0
            if self.imgxon == 1:
                self.imgx.after(100, self.imgx.destroy())
                self.imgxon = 0
                if cutdown == 1:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 4:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 5:
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
                    
            elif self.imgxon == 0 and (self.cutdown == 1 or self.cutdown == 4 or self.cutdown == 5):
                    if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg"):
                        self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".jpg")
                        if self.cutdown == 1:
                            self.load = self.load.resize((100, 100), Image.LANCZOS)
                        elif self.cutdown == 4:
                            self.load = self.load.resize((130, 130), Image.LANCZOS)
                        elif self.cutdown == 5:
                            self.load = self.load.resize((170, 170), Image.LANCZOS)
                        self.render2 = ImageTk.PhotoImage(self.load)
                        if self.imgxon == 0:
                            self.imgx = tk.Label(self.Frame10, image = self.render2)
                            self.imgx.grid(row = 1, column = 1, columnspan = 3, rowspan = 3, pady = 0)
                            self.imgxon = 1
                            if self.cutdown == 1 or self.cutdown == 4:
                                self.Disp_plist_name.after(100, self.Disp_plist_name.destroy())
                            self.Disp_artist_name.after(100, self.Disp_artist_name.destroy())
                            self.Disp_album_name.after(100, self.Disp_album_name.destroy())
                        self.imgx.config(image = self.render2)
                    elif os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                        self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".png")
                        if self.cutdown == 1:
                            self.load = self.load.resize((100, 100), Image.LANCZOS)
                        elif self.cutdown == 4:
                            self.load = self.load.resize((130, 130), Image.LANCZOS)
                        elif self.cutdown == 5:
                            self.load = self.load.resize((170, 170), Image.LANCZOS)
                        self.render2 = ImageTk.PhotoImage(self.load)
                        if self.imgxon == 0:
                            self.imgx = tk.Label(self.Frame10, image = self.render2)
                            self.imgx.grid(row = 1, column = 1, columnspan = 3, rowspan = 3, pady = 0)
                            self.imgxon = 1
                            if self.cutdown == 1 or self.cutdown == 4:
                                self.Disp_plist_name.after(100, self.Disp_plist_name.destroy())
                            self.Disp_artist_name.after(100, self.Disp_artist_name.destroy())
                            self.Disp_album_name.after(100, self.Disp_album_name.destroy())
                        self.imgx.config(image = self.render2)
            if( self.cutdown != 7 and self.cutdown != 8) and self.imgxon == 0:
                self.Disp_artist_name.config(text = self.Name)
            elif self.imgxon == 0:
                self.Disp_artist_name.set(self.Name)
            if self.cutdown != 4 and self.cutdown !=5 and self.cutdown !=1:
                if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg"):
                    self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".jpg")
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS)
                    self.render2 = ImageTk.PhotoImage(self.load)
                    self.img.config(image = self.render2)
                elif os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                    self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".png")
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS)
                    self.render2 = ImageTk.PhotoImage(self.load)
                    self.img.config(image = self.render2)
                elif os.path.exists(self.radio_jpg):
                    self.load = Image.open(self.radio_jpg)
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS)
                    self.render3 = ImageTk.PhotoImage(self.load)
                    self.img.config(image = self.render3)
            track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            # check RAM space and set self.max_record
            st = os.statvfs("/run/shm/")
            self.freeram1 = (st.f_bavail * st.f_frsize)/1100000
            self.timer7 = time.monotonic()
            free2 = int((self.freeram1 - self.ram_min)/10) * 10
            self.max_record = min(free2,991)
            self.ramtest = 1
            self.Check_Record()
            if len(track) == 0  and self.Radio_Stns[self.Radio + 2]  > 0:
                if self.rotary_pos== 0:
                    messagebox.showinfo("WARNING!","Check Recordable entry set correctly for this stream")

    def prevAZ(self):
        if (self.Radio_RON == 1 or self.album_start == 1 or self.stopstart == 1):
            self.PopupInfo()
            if self.rotary_pos == 1:
                self.Button_Next_AZ.config(bg = "yellow")
            #else:
            #    self.Button_Next_AZ.config(bg = "orange")
        elif self.album_start == 0 and self.stopstart == 0 and len(self.tunes) > 1 and self.Radio_ON == 0:
            stop = 0
            if self.wheel_opt == 0 or self.wheel_opt == 3 or self.rot_mode == 2:
                while (self.tunes[self.track_no].split('^')[0][0]) == self.artist_name[0] and stop == 0:
                    self.track_no -=1
                    if self.track_no < 0:
                        self.track_no = len(self.tunes) - 1
                        stop = 1
            elif self.wheel_opt == 1:
                while (self.tunes[self.track_no].split('^')[1][0]) == self.album_name[0] and stop == 0:
                    self.track_no -=1
                    if self.track_no < 0:
                        self.track_no = len(self.tunes) - 1
                        stop = 1
            elif self.wheel_opt == 2:
                while (self.tunes[self.track_no].split('^')[2][3]) == self.track_name[3] and stop == 0:
                    self.track_no -=1
                    if self.track_no < 0:
                        self.track_no = len(self.tunes) - 1
                        stop = 1
            elif self.wheel_opt == 4:
                while (self.tunes[self.track_no].split('^')[0][0][0:1]) == self.artist_name[0][0:1] and stop == 0:
                    self.track_no -=1
                    if self.track_no < 0:
                        self.track_no = len(self.tunes) - 1
                        stop = 1
            self.Time_Left_Play()
        elif self.album_start == 0 and self.stopstart == 0 and self.Radio_ON == 1 and self.rot_mode == 1:
             # Prev A-Z Radio Station
            self.copy = 0
            self.Disp_track_name.config(text = "")
            if cutdown == 1:
                self.Disp_track_len.config(text =int(len(self.Radio_Stns)/3))
                self.L4.config(text="of")
            if self.Radio_Stns[self.Radio + 2] == 0:
                self.q.kill()
            else:
                self.q.kill()
                self.r.kill()
            if self.NewRadio == -1:
                stop = 0
                while self.Name[0:1] == self.Radio_Stns[self.Radio][0:1] and stop == 0:
                    self.Radio -= 3
                    if self.Radio < 0:
                        self.Radio = len(self.Radio_Stns) - 3
                        stop = 1
            else:
                self.Radio = self.NewRadio
                self.NewRadio = -1
            if cutdown == 1:
                self.Disp_played.config(text = int((self.Radio)/3)+1)
            if self.Radio_Stns[self.Radio + 2] == 0:
                self.q = subprocess.Popen(["mplayer", "-nocache", self.Radio_Stns[self.Radio + 1]] , shell=False)
            else:
                self.r = subprocess.Popen(["streamripper", self.Radio_Stns[self.Radio + 1],"-r","--xs_offset=-9000","-z","-l", "99999","-d", "/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings","-a",self.Radio_Stns[self.Radio]], shell=False)
                time.sleep(1)
                self.q = subprocess.Popen(["mplayer", "-nocache", "http://localhost:8000"] , shell=False)
                track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
                if len(track) == 0:
                    time.sleep(2)
            if self.Radio_Stns[self.Radio + 2]  > 0 and self.record == 1:
                self.Button_Pause.config(fg = "black", bg = "light blue", text = "RECORD")
                if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and  self.cutdown != 6 and self.touchscreen == 1:
                    self.L8.config(text = ".mp3")
            else:
                self.Button_Pause.config(fg = "black", bg = "light grey", text = "Pause")
                if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and  self.cutdown != 6 and self.touchscreen == 1:
                    self.L8.config(text = "")
            if self.cutdown == 1 or self.cutdown == 4 or self.cutdown == 5:
                self.Disp_track_len.config(text = int(len(self.Radio_Stns)/3))
                self.Disp_played.config(text = int((self.Radio)/3)+1)
                self.L4.config(text="of")
                if self.cutdown == 1:
                    self.Disp_Total_tunes.config(text = "        Stn:")
                if self.cutdown == 1:
                    self.Disp_Total_tunes.config(text = "        Stn:")
                elif self.cutdown == 4:
                    self.Disp_Total_tunes.config(text = "    Stn:")
                else:   
                    self.L3.config(text = "Stn:")
            self.Name = self.Radio_Stns[self.Radio]
            if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg") or os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                self.imgxon = 0
            if self.imgxon == 1:
                self.imgx.after(100, self.imgx.destroy())
                self.imgxon = 0
                if cutdown == 1:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 4:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 5:
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
                    
            elif self.imgxon == 0 and (self.cutdown == 1 or self.cutdown == 4 or self.cutdown == 5):
                    if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg"):
                        self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".jpg")
                        if self.cutdown == 1:
                            self.load = self.load.resize((100, 100), Image.LANCZOS)
                        elif self.cutdown == 4:
                            self.load = self.load.resize((130, 130), Image.LANCZOS)
                        elif self.cutdown == 5:
                            self.load = self.load.resize((170, 170), Image.LANCZOS)
                        self.render2 = ImageTk.PhotoImage(self.load)
                        if self.imgxon == 0:
                            self.imgx = tk.Label(self.Frame10, image = self.render2)
                            self.imgx.grid(row = 1, column = 1, columnspan = 3, rowspan = 3, pady = 0)
                            self.imgxon = 1
                            if self.cutdown == 1 or self.cutdown == 4:
                                self.Disp_plist_name.after(100, self.Disp_plist_name.destroy())
                            self.Disp_artist_name.after(100, self.Disp_artist_name.destroy())
                            self.Disp_album_name.after(100, self.Disp_album_name.destroy())
                        self.imgx.config(image = self.render2)
                    elif os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                        self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".png")
                        if self.cutdown == 1:
                            self.load = self.load.resize((100, 100), Image.LANCZOS)
                        elif self.cutdown == 4:
                            self.load = self.load.resize((130, 130), Image.LANCZOS)
                        elif self.cutdown == 5:
                            self.load = self.load.resize((170, 170), Image.LANCZOS)
                        self.render2 = ImageTk.PhotoImage(self.load)
                        if self.imgxon == 0:
                            self.imgx = tk.Label(self.Frame10, image = self.render2)
                            self.imgx.grid(row = 1, column = 1, columnspan = 3, rowspan = 3, pady = 0)
                            self.imgxon = 1
                            if self.cutdown == 1 or self.cutdown == 4:
                                self.Disp_plist_name.after(100, self.Disp_plist_name.destroy())
                            self.Disp_artist_name.after(100, self.Disp_artist_name.destroy())
                            self.Disp_album_name.after(100, self.Disp_album_name.destroy())
                        self.imgx.config(image = self.render2)
            if( self.cutdown != 7 and self.cutdown != 8) and self.imgxon == 0:
                self.Disp_artist_name.config(text = self.Name)
            elif self.imgxon == 0:
                self.Disp_artist_name.set(self.Name)
            if self.cutdown != 4 and self.cutdown !=5 and self.cutdown !=1:
                if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg"):
                    self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".jpg")
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS)
                    self.render2 = ImageTk.PhotoImage(self.load)
                    self.img.config(image = self.render2)
                elif os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                    self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".png")
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS)
                    self.render2 = ImageTk.PhotoImage(self.load)
                    self.img.config(image = self.render2)
                elif os.path.exists(self.radio_jpg):
                    self.load = Image.open(self.radio_jpg)
                    if self.cutdown != 2:
                        if self.cutdown == 8:
                            self.load = self.load.resize((320,320), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((218, 218), Image.LANCZOS)
                    else:
                        self.load = self.load.resize((150, 150), Image.LANCZOS)
                    self.render3 = ImageTk.PhotoImage(self.load)
                    self.img.config(image = self.render3)
            track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            # check RAM space and set self.max_record
            st = os.statvfs("/run/shm/")
            self.freeram1 = (st.f_bavail * st.f_frsize)/1100000
            self.timer7 = time.monotonic()
            free2 = int((self.freeram1 - self.ram_min)/10) * 10
            self.max_record = min(free2,991)
            self.ramtest = 1
            self.Check_Record()
            if len(track) == 0  and self.Radio_Stns[self.Radio + 2]  > 0:
                if self.rotary_pos== 0:
                    messagebox.showinfo("WARNING!","Check Recordable entry set correctly for this stream")

    def RnextAZ(self):
        if self.album_start == 0 and self.stopstart == 0 and len(self.tunes) > 1:
            stop = 0
            while (self.tunes[self.track_no].split('^')[0][0][0:1]) == self.artist_name[0][0:1] and stop == 0:
                self.track_no -=1
                if self.track_no < 1:
                     self.track_no = 0
                     stop = 1
        self.Time_Left_Play()
      
    def RELOAD_List(self):
        if self.trace > 0:
            print ("RELOAD_List")
        # skip forward (next track if .txt file available, eg radio recording)
        if os.path.exists(self.track2) and self.paused == 0 and (self.album_start == 1 or self.stopstart == 1) and self.Radio_ON == 0:
           names = []
           with open(self.track2, "r") as file:
               line = file.readline()
               while line:
                   names.append(line.strip())
                   line = file.readline()
           x = 0
           stop = 0
           while x < len(names) and stop == 0:
               dtime = names[x][0:6]
               dname = names[x][7:]
               pstime = int(dtime[0:3]) * 60 + int(dtime[4:6])
               if (self.p_minutes * 60) + self.p_seconds < pstime and dtime != "000:00":
                   #print("skip to ",pstime,self.start,self.total,self.played)
                   player.time_pos = pstime
                   self.start -= pstime - self.played
                   self.total -= pstime - self.played
                   stop = 1
               x +=1
            
        # skip forward (1/10 of track)
        elif self.paused == 0 and (self.album_start == 1 or self.stopstart == 1) and self.Radio_ON == 0:
                   if self.play == 1 and self.version == 2 and self.paused == 0:
                       self.skip = int(self.track_len/10)
                       if self.skip + self.played < self.track_len  - self.skip:
                           self.start -= self.skip
                           self.total -= self.skip
                           if self.sleep_time_min > self.skip and self.shutdown == 1 and self.album_start == 1:
                               self.sleep_time_min += self.skip
                           if self.BT == 0:
                               player.time_pos = self.played + self.skip
            
        # RELOAD tracks   
        if self.paused == 0 and self.album_start == 0 and self.stopstart == 0 and self.Radio_ON == 0:
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3:
                self.Disp_Name_m3u.config(background="light gray", foreground="black")
            if self.cutdown != 7 and self.cutdown != 8:
                self.Disp_artist_name.config(text =" ")
                self.Disp_album_name.config(text =" ")
                self.Disp_track_name.config(text =" ")
            else:
                self.Disp_artist_name.set(" ")
                self.Disp_album_name.set(" ")
                self.Disp_track_name.set(" ")
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3:
                self.Disp_Drive.config(text =" ")
            self.Disp_track_no.config(text =" ")
            self.Disp_Total_tunes.config(text =" ")
            self.Disp_played.config(text =" ")
            self.Disp_track_len.config(text =" ")
            self.Button_Shuffle.config(bg = "light blue",fg = "black",text = "Shuffle")
            self.shuffle_on = 0
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3:
                self.Disp_Total_Plist.config(text=" ")
            if self.play == 2:
                self.play = 0
            if self.play > 0:
                self.play = 0
                self.Button_Start.config(bg = "green",fg = "black",text = "PLAY Playlist")
                if self.version == 1:
                    self.p.kill()
                else:
                    player.stop()
            if os.path.exists(self.m3u_dir + self.m3u_def + ".m3u"):
                os.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.sorted == 0
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3:
                self.Button_AZ_artists.config(bg = "light blue",fg = "black",text = "A-Z Sort")
            self.Tracks = []
            # search for MP3 files
            self.Tracks = glob.glob(self.mp3_search)
            # search for wav files
            self.wavs = glob.glob(self.wav_search)
            if len (self.wavs) > 0 :
                for j in range(0,len(self.wavs)):
                    self.Tracks.append(self.wavs[j])
            # search for flac files
            self.Flacs = glob.glob(self.flac_search)
            if len (self.Flacs) > 0 :
                for j in range(0,len(self.Flacs)):
                    self.Tracks.append(self.Flacs[j])
            # search for dsf files
            self.dsfs = glob.glob(self.dsf_search)
            if len (self.dsfs) > 0 :
                for j in range(0,len(self.dsfs)):
                    self.Tracks.append(self.dsfs[j])
            # search for M4A files
            self.m4as = glob.glob(self.m4a_search)
            if len (self.m4as) > 0 :
                for j in range(0,len(self.m4as)):
                    self.Tracks.append(self.m4as[j])
            # search for more flac files
            self.Flacs2 = glob.glob(self.flac2_search)
            if len (self.Flacs2) > 0 :
                for j in range(0,len(self.Flacs2)):
                    self.Tracks.append(self.Flacs2[j])
            # search for more wav files
            self.wav2 = glob.glob(self.wav2_search)
            if len (self.wav2) > 0 :
                for j in range(0,len(self.wav2)):
                    self.Tracks.append(self.wav2[j])
            # search for more MP3 files
            self.MP3_2 = glob.glob(self.mp32_search)
            if len (self.MP3_2) > 0 :
                for j in range(0,len(self.MP3_2)):
                    self.Tracks.append(self.MP3_2[j])
            # search for even more MP3 files
            self.MP3_3 = glob.glob(self.mp33_search)
            if len (self.MP3_3) > 0 :
                for j in range(0,len(self.MP3_3)):
                    self.Tracks.append(self.MP3_3[j])
            # search for more flac files
            self.Flacs3 = glob.glob(self.flac3_search)
            if len (self.Flacs3) > 0 :
                for j in range(0,len(self.Flacs3)):
                    self.Tracks.append(self.Flacs3[j])
            # search for more wav files
            self.wav3 = glob.glob(self.wav3_search)
            if len (self.wav3) > 0 :
                for j in range(0,len(self.wav3)):
                    self.Tracks.append(self.wav3[j])
            #search for more flac files
            self.Flacs3 = glob.glob(self.flac3_search)
            if len (self.Flacs3) > 0 :
                for j in range(0,len(self.Flacs3)):
                    self.Tracks.append(self.Flacs3[j])
            # search for more MP3 files under .../Music
            self.MP3sd = glob.glob(self.mp3sd_search)
            if len (self.MP3sd) > 0 :
                for j in range(0,len(self.MP3sd)):
                    self.Tracks.append(self.MP3sd[j])
            # search for more dsf files
            self.dsf_2 = glob.glob(self.dsf2_search)
            if len (self.dsf_2) > 0 :
                for j in range(0,len(self.dsf_2)):
                    self.Tracks.append(self.dsf_2[j])
            # search for more dsf files
            self.dsf_3 = glob.glob(self.dsf3_search)
            if len (self.dsf_3) > 0 :
                for j in range(0,len(self.dsf_3)):
                    self.Tracks.append(self.dsf_3[j])
            # search for more m4a files
            self.m4a_2 = glob.glob(self.m4a2_search)
            if len (self.m4a_2) > 0 :
                for j in range(0,len(self.m4a_2)):
                    self.Tracks.append(self.m4a_2[j])
            # search for more m4a files
            self.m4a_3 = glob.glob(self.m4a3_search)
            if len (self.m4a_3) > 0 :
                for j in range(0,len(self.m4a_3)):
                    self.Tracks.append(self.m4a_3[j])
            if len (self.Tracks) > 0 :
                with open(self.m3u_dir + self.m3u_def + ".m3u", 'w') as f:
                    for item in self.Tracks:
                        f.write("%s\n" % item)
             
            if len (self.Tracks) > 0 :
                self.counter5 = 0
                self.tunes = []
                self.Button_Reload.config(bg = "red")
                self.paused = 1
                if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2:
                    self.L9.config(text= " L :")
                self.RELOAD1_List()
               
            else:
                self.Disp_artist_name.config(text =" NO TRACKS FOUND !")
                if self.rotary_pos== 0:
                    messagebox.showinfo("WARNING!","No Tracks found!")

    def RELOAD1_List(self):
         counter2 = self.Tracks[self.counter5].count('/')
         if counter2 == 6:
             self.genre_name = "None"
             z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = self.Tracks[self.counter5].split('/')
             self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)
         elif counter2 == 5:
             self.genre_name = "None"
             self.drive_name1,self.drive_name2,self.drive_name,self.artist_name3,self.album_name3,self.track_name  = self.Tracks[self.counter5].split('/')
             if self.album_name3.count(" - ") == 1:
                 self.artist_name,self.album_name = self.album_name3.split(" - ")
                 self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.artist_name3 + "*^" + self.drive_name2 + "^" + self.drive_name + "^" + self.genre_name)
         elif counter2 == 7:
             z,self.drive_name1,self.drive_name2,self.drive_name,self.genre_name,self.artist_name,self.album_name,self.track_name  = self.Tracks[self.counter5].split('/')
             self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)
         self.counter5 +=1
         if self.cutdown != 1 and self.cutdown != 5 and self.cutdown != 4 and self.cutdown != 6 and self.model != 0:
             self.s.configure("LabeledProgressbar", text="{0} %      ".format(int((self.counter5/len(self.Tracks)*100))), background='red')
             self.progress['value']=(self.counter5/len(self.Tracks)* 100)
         self.Disp_Total_tunes.config(text =str(self.counter5))
         if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3:
             self.Disp_Drive.config(text = "/" + self.drive_name1 + "/" +  self.drive_name2 + "/" +  self.drive_name )
         if self.counter5 < len(self.Tracks) and len(self.Tracks) > 0:
             self.after(1,self.RELOAD1_List)
         else:
             if self.trace > 0:
                 print ("RELOAD1",len(self.tunes))
             self.RELOAD2_List()

    def RELOAD2_List(self):
        self.counter5 = 0
        self.Button_Reload.config(fg = "black", bg = "light blue")
        if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2:
            self.L9.config(text= " ")
        if self.cutdown != 1 and self.cutdown != 5 and self.cutdown != 6  and self.cutdown != 4 and self.model != 0:
            self.s.configure("LabeledProgressbar", text="0 %      ", background='red')
            self.progress['value']= 0
        self.track_no = 0
        self.Disp_Total_tunes.config(text =len(self.tunes))
        self.m3us = glob.glob(self.m3u_dir + "*.m3u")
        self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")
        if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3:
            self.Disp_Name_m3u.delete('1.0','20.0')
        self.que_dir   = self.m3u_dir + self.m3u_def + ".m3u"
        if self.cutdown != 5 and self.cutdown != 6 :
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
        if self.cutdown != 7 and self.cutdown != 8:
            self.Disp_artist_name.config(fg = "black")
        self.paused = 0
        self.tunes.sort()
        if self.play == 0:
            self.reload = 1
            if self.cutdown >= 7:
                if self.trace > 0:
                    print ("RELOAD2",len(self.tunes))
                self.plist_callback()
            self.Time_Left_Play()
        if self.rotary_pos == 1:
            self.rot_mode = 0
            self.rot_pos = 3
            self.rot_posp = 3
            self.Button_Start.config(bg = "yellow",fg = "black")
        

    def Repeat(self):
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir) and self.Radio_ON == 0:
            if self.play == 2:
                self.play = 0
            self.repeat_count +=1
            if self.repeat_count == 1:
                self.repeat_track = 1
                self.repeat = 0
                self.Button_repeat.config(bg = "green",fg = "black",text = "Repeat Track")
            elif self.repeat_count == 2:
                self.repeat_track = 0
                self.repeat = 1
                self.Button_repeat.config(bg = "green",fg = "black",text = "Repeat P-List")
            else:
                self.repeat_count = 0
                self.repeat = 0
                self.repeat_track = 0
                self.Button_repeat.config(bg = "light blue",fg = "black",text = "Repeat")
            if self.play == 1:
                self.Start_Play()
            else:
                self.Show_Track()
        if self.paused == 0 and self.album_start == 1 and self.repeat_album == 0:
            self.repeat_album = 1
            self.repeat = 0
            self.repeat_track = 0
            self.Button_repeat.config(bg = "green",fg = "black",text = "Repeat Album")
        elif self.paused == 0 and self.album_start == 1 and self.repeat_album == 1:
            self.repeat_album = 0
            self.repeat = 0
            self.repeat_track = 0
            self.Button_repeat.config(bg = "light blue",fg = "black",text = "Repeat Album")
        if self.rotary_pos == 1:
            self.Button_repeat.config(bg = "yellow")
            

    def Shuffle_Tracks(self):
        # clear ram
        if self.Radio_ON == 1 and self.Radio_RON == 0:
            rems = glob.glob("/run/shm/music/*/*/*/*/*.mp3")
            for x in range(0,len(rems)):
                os.remove(rems[x])
            rems = glob.glob("/run/shm/music/*/*/*.mp3")
            for x in range(0,len(rems)):
                stop = 0
                k = 0
                while stop == 0 and k < len(self.tunes) - 1:
                    data = rems[x].split('/',7)
                    data2 = data[4] + "^" + data[5] + "^" + data[6]+"^"+data[3]+"^"+data[1]+"^"+data[2]
                    if data2 == self.tunes[k]:
                        self.tunes.remove(data2)
                        stop = 1
                    k +=1
                os.remove(rems[x])
            rems = glob.glob("/run/shm/music/*/*/*.cue")
            for x in range(0,len(rems)):
                os.remove(rems[x])
            rems = glob.glob("/run/shm/music/*/*/*.txt")
            for x in range(0,len(rems)):
                os.remove(rems[x])
        # shuffle
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir) and self.Radio_ON == 0:
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2 or self.cutdown == 3:
                self.Disp_Name_m3u.config(background="light gray", foreground="black")
            if self.play == 2:
                self.play = 0
            if self.shuffle_on == 0:
                self.shuffle_on = 1
                shuffle(self.tunes)
                with open('Lasttrack3.txt', 'w') as f:
                    f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
                if self.rotary_pos == 1:
                    self.Button_Shuffle.config(bg = "yellow",fg = "black",text = "Shuffled")
                else:
                    self.Button_Shuffle.config(bg = "orange",fg = "black",text = "Shuffled")
                if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and self.cutdown != 6 :
                    self.Button_AZ_artists.config(bg = "light blue", fg = "black", text = "A-Z Sort")
                if self.cutdown >= 7:
                    self.Disp_artist_name.set(self.artist_name)
                    self.ac = 1
                    self.plist_callback2()
                    self.Disp_album_name.set(self.album_name)
                    self.Disp_track_name.set(self.track_name)
            else:
                self.shuffle_on = 0
                with open('Lasttrack3.txt', 'w') as f:
                    f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
                self.tunes.sort()
                tpath = self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2
                stop = 0
                k = 0
                while stop == 0 and k < len(self.tunes) - 1:
                    if tpath == self.tunes[k]:
                        stop = 1
                        self.track_no = k
                    k +=1
                if self.cutdown != 5 and self.cutdown != 6 and self.imgxon == 0 :
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                self.Disp_Total_tunes.config(text =len(self.tunes))
                if self.rotary_pos== 0:
                    self.Button_Shuffle.config(bg = "light blue",fg = "black",text = "Shuffle")
                else:
                    self.Button_Shuffle.config(bg = "yellow",fg = "black",text = "Shuffle")
                if self.cutdown >= 7:
                    self.Disp_artist_name.set(self.artist_name)
                    self.ac = 0
                    self.plist_callback2()
                    self.Disp_album_name.set(self.album_name)
                    self.Disp_track_name.set(self.track_name)
            if self.play == 1:
                if self.version == 1:
                    self.p.kill()
                else:
                    player.stop()
                self.start = 0
                self.Start_Play()
            else:
                self.Show_Track()
        if self.paused == 0 and self.album_start == 1 and len(self.tunes) > 1:
            if self.shuffle_on == 0 and self.track_no < self.tcount:
                self.shuffle_on = 1
                self.tunes[self.track_no + 1:self.tcount] = random.sample(self.tunes[self.track_no + 1:self.tcount], (self.tcount - (self.track_no + 1)))
                self.Button_Shuffle.config(bg = "yellow",fg = "black",text = "Shuffled")
                if self.cutdown >= 7:
                    self.Disp_artist_name.set(self.artist_name)
                    self.ac = 1
                    self.plist_callback()
                    self.Disp_album_name.set(self.album_name)
                    self.Disp_track_name.set(self.track_name)
                else:
                    self.Show_Track()
            else:
                self.shuffle_on = 0
                self.tunes[self.track_no + 1:self.tcount]=sorted(self.tunes[self.track_no + 1:self.tcount])
                if self.rotary_pos== 0:
                    self.Button_Shuffle.config(bg = "light blue",fg = "black",text = "Shuffle")
                else:
                    self.Button_Shuffle.config(bg = "yellow",fg = "black",text = "Shuffle")
                if self.cutdown >= 7:
                    self.Disp_artist_name.set(self.artist_name)
                    self.plist_callback()
                    self.Disp_album_name.set(self.album_name)
                    self.Disp_track_name.set(self.track_name)
                else:
                    self.Show_Track()

    def AZ_Tracks(self):
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir) and self.Radio_ON == 0:
            self.Disp_Name_m3u.config(background="light gray", foreground="black")
            self.Button_Shuffle.config(bg = "light blue",fg = "black",text = "Shuffle")
            self.shuffle_on = 0
            if self.play == 2:
                self.play = 0
            if self.play == 1:
               self.play = 0
               self.Button_Start.config(bg = "green",fg = "black",text = "PLAY Playlist")
               self.Button_TAlbum.config(fg = "black",bg = "blue")
               if self.version == 1:
                   self.p.kill()
               else:
                   player.stop()
            if self.sort_no < 3:
               self.sort_no +=1  
               if self.sort_no == 1:
                   self.Button_AZ_artists.config(bg = "green",fg = "black",text = "A-Z Artists ON")
                   self.tunes.sort()
               if self.sort_no == 2:
                   self.Button_AZ_artists.config(bg = "green",fg = "black",text = "A-Z Album ON")
                   self.tunes2 = []
                   for counter in range (0,len(self.tunes)):
                       self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[counter].split('^')
                       self.tunes2.append(self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.artist_name + "^" + self.genre_name)
                   self.tunes2.sort()
                   self.tunes = []
                   for counter in range (0,len(self.tunes2)):
                       self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.artist_name,self.genre_name  = self.tunes2[counter].split('^')
                       self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)
               if self.sort_no == 3:
                   self.Button_AZ_artists.config(bg = "green",fg = "black",text = "A-Z Tracks ON")
                   num_list = ["0","1","2","3","4","5","6","7","8","9"]
                   self.tunes2 = []
                   L = 2
                   for counter in range (0,len(self.tunes)):
                       self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[counter].split('^')
                       if self.track_name[0:1] in num_list and self.track_name[1:2] in num_list and (self.track_name[2:3] == " " or self.track_name[2:3] == "-" or self.track_name[2:3] == "_"):
                           L = 3
                           if self.track_name[3:4] == " " or self.track_name[3:4] == "-" or self.track_name[3:4] == "(":
                               L = 4
                           if self.track_name[4:5] == " ":
                               L = 5
                           self.track_number = self.track_name[0:L]
                           self.track_name2 = self.track_name[L:]
                       elif self.track_name[0:1] in num_list and self.track_name[1:2] == "-" and self.track_name[2:3] in num_list and self.track_name[3:4] in num_list:
                           L = 5
                           self.track_number = self.track_name[0:L]
                           self.track_name2 = self.track_name[L:]
                       else:
                           self.track_name2 = self.track_name
                           self.track_number = ""
                       self.tunes2.append(self.track_name2 + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.artist_name + "^" + self.album_name + "^" + self.track_number + "^" + self.genre_name)
                   self.tunes2.sort()
                   self.tunes = []
                   for counter in range (0,len(self.tunes2)):
                       self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.artist_name,self.album_name,self.track_number,self.genre_name  = self.tunes2[counter].split('^')
                       self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_number + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)
               self.track_no = 0
            else:
               self.sort_no = 0
               Tracks = []
               with open(self.que_dir,"r") as textobj:
                  line = textobj.readline()
                  while line:
                     Tracks.append(line.strip())
                     line = textobj.readline()
               self.tunes = []
               for counter in range (0,len(Tracks)):
                   counter2 = Tracks[counter].count('/')
                   if counter2 == 6:
                       z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                       self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)###
                   if counter2 == 7:
                       z,self.drive_name1,self.drive_name2,self.drive_name,self.genre_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                       self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)
                   if counter2 == 5:
                       self.drive_name1,self.drive_name2,self.drive_name,self.artist_name3,self.album_name3,self.track_name  = Tracks[counter].split('/')
                       if self.album_name3.count(" - ") == 1:
                           self.artist_name,self.album_name = self.album_name3.split(" - ")
                           self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.artist_name3 + "^" + self.drive_name2 + "^" + self.drive_name + "^" + self.genre_name)
               self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
               self.Disp_Total_tunes.config(text =len(self.tunes))
               self.Button_AZ_artists.config(bg = "light blue",fg = "black",text = "A-Z Sort")
               self.track_no = 0
            self.Disp_Total_Plist.config(text = "       " )
            self.Time_Left_Play()
        if self.rotary_pos == 1 and self.rot_pos == 15:
            self.Button_AZ_artists.config(bg = "yellow")
            
    def Track_m3u(self):
        if (os.path.exists(self.que_dir) and self.cutdown != 4 and self.Radio_ON == 0) or (os.path.exists(self.que_dir) and self.cutdown == 4 and self.album_start == 0 and self.stopstart == 0 and self.Radio_ON == 0):
            if self.cutdown >= 7:
                self.artist_name = self.Disp_artist_name.get()
                self.album_name = self.Disp_album_name.get()
                self.track_name = self.Disp_track_name.get()
            Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
            if len(Name) == 0 or Name == "Name ?":
                now = datetime.datetime.now()
                Name = now.strftime("%y%m%d%H%M%S")
                self.Disp_Name_m3u.delete('1.0','20.0')
                self.Disp_Name_m3u.insert(INSERT,Name)
            with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                if self.genre_name == "None":
                    f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" + self.track_name + "\n")
                else:
                    f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.genre_name + "/" + self.artist_name + "/" + self.album_name + "/" + self.track_name + "\n")
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")

    def FAV_List(self):
        if os.path.exists(self.que_dir) and self.Radio_ON == 0:
            if self.cutdown >= 7:
                self.artist_name = self.Disp_artist_name.get()
                self.album_name = self.Disp_album_name.get()
                self.track_name = self.Disp_track_name.get()
            Name = "FAVourites"
            self.Disp_Name_m3u.config(background="light gray", foreground="black")
            self.Disp_Name_m3u.delete('1.0','20.0')
            with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                if self.genre_name == "None":
                    f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" + self.track_name + "\n" )
                else:
                    f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.genre_name + "/" + self.artist_name + "/" + self.album_name + "/" + self.track_name + "\n")
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")

    def Artist_m3u(self):
        if (os.path.exists(self.que_dir) and self.cutdown != 4 and self.Radio_ON == 0) or (os.path.exists(self.que_dir) and self.cutdown == 4 and self.album_start == 0 and self.stopstart == 0 and self.Radio_ON == 0):
            if self.cutdown >= 7:
                self.artist_name = self.Disp_artist_name.get()
            self.Disp_Name_m3u.config(background="light gray", foreground="black")
            Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
            if len(Name) == 0 or Name == "Name ?":
                Name = self.artist_name
                self.Disp_Name_m3u.delete('1.0','20.0')
                self.Disp_Name_m3u.insert(INSERT,Name)
            if not os.path.exists(self.m3u_dir + Name + ".m3u"):
                artist = []
                for counter in range (0,len(self.tunes)):
                    if (self.tunes[counter].split('^')[0]) == self.artist_name:
                        artist.append(self.tunes[counter])
                artist.sort()
                for counter in range(0,len(artist)):
                    self.artist_name,self.album_name2,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = artist[counter].split('^')
                    
                    with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                        if self.genre_name == "None":
                            f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name2 + "/" + self.track_name + "\n")
                        else:
                            f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.genre_name + "/" + self.artist_name + "/" + self.album_name2 + "/" + self.track_name + "\n")
                self.m3us = glob.glob(self.m3u_dir + "*.m3u")
                self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
                self.m3us.sort()
                self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")


    def Album_m3u(self):
        if (os.path.exists(self.que_dir) and self.cutdown != 4 and self.Radio_ON == 0) or (os.path.exists(self.que_dir) and self.cutdown == 4 and self.album_start == 0 and self.stopstart == 0 and self.Radio_ON == 0):
            self.Disp_Name_m3u.config(background="light gray", foreground="black")
            if self.cutdown >= 7:
                self.artist_name = self.Disp_artist_name.get()
                self.album_name = self.Disp_album_name.get()
            Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
            if len(Name) == 0 or Name == "Name ?":
                now = datetime.datetime.now()
                Name = now.strftime("%y%m%d%H%M%S")
                self.Disp_Name_m3u.delete('1.0','20.0')
                self.Disp_Name_m3u.insert(INSERT,Name)
            album = []
            for counter in range (0,len(self.tunes)):
                if (self.tunes[counter].split('^')[1][0:-1]) == self.album_name[0:-1] and (self.tunes[counter].split('^')[0]) == self.artist_name:
                    album.append(self.tunes[counter])
            album.sort()
            for counter in range(0,len(album)):
                self.artist_name,self.album_name2,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = album[counter].split('^')
                with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                    if self.genre_name == "None":
                        f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name2 + "/" + self.track_name + "\n")
                    else:
                        f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.genre_name + "/" + self.artist_name + "/" + self.album_name2 + "/" + self.track_name + "\n")
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")


    def PList_m3u(self):
        if self.que_dir != self.m3u_dir + self.m3u_def + ".m3u" and os.path.exists(self.que_dir):
            if  (self.cutdown != 4 and self.Radio_ON == 0) or (self.cutdown == 4 and self.album_start == 0 and self.stopstart == 0 and self.Radio_ON == 0):
                self.Disp_Name_m3u.config(background="light gray", foreground="black")
                Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
                if len(Name) == 0 or Name == "Name ?":
                    now = datetime.datetime.now()
                    Name = now.strftime("%y%m%d%H%M%S")
                    self.Disp_Name_m3u.delete('1.0','20.0')
                    self.Disp_Name_m3u.insert(INSERT,Name)
                with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                    for counter in range (0,len(self.tunes)):
                        self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = self.tunes[counter].split('^')
                        if self.genre_name == "None":
                            f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" + self.track_name + "\n")
                        else:
                            f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.genre_name + "/" + self.artist_name + "/" + self.album_name + "/" + self.track_name + "\n")
                self.m3us = glob.glob(self.m3u_dir + "*.m3u")
                self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
                self.m3us.sort()
                self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")

    def sleep(self):
        if self.album_start == 1 and self.sleep_time > 0 and self.album_sleep == 0:
            self.album_sleep = 1
            self.sleep_time = 0
            self.record_sleep = 0
        if self.album_start == 0 or self.album_sleep == 1:
            self.shutdown = 1
            if self.sleep_time == 0:
                self.Check_Sleep()
            self.begin = time.monotonic()
            self.sleep_time = int(self.sleep_time + 15.99)
            if self.sleep_time > self.max_sleep:
                self.sleep_time = 0
                self.album_sleep = 0
            self.sleep_time_min = self.sleep_time * 60
        elif self.shutdown == 0:
            self.shutdown = 1
            self.record_sleep = 0
            if self.sleep_time == 0:
                self.Check_Sleep()
            self.begin = time.monotonic()
            self.sleep_time_min = self.tplaylist + 60 
            self.sleep_time = int(self.sleep_time_min / 60)
        else:
            self.shutdown = 0
            self.sleep_time = 0
            self.sleep_time_min = 0
            self.album_sleep = 0
        if self.Radio_ON == 1 and self.Radio_RON == 1 and self.shutdown == 1 and self.record_sleep == 0:
            self.sleep_time_min = (self.record_current *60) + 120
            self.sleep_time = int(self.sleep_time_min / 60)
            self.record_sleep = 1
        elif self.Radio_ON == 1 and self.Radio_RON == 1 and self.shutdown == 1 and self.record_sleep == 1:
            self.shutdown = 0
            self.sleep_time = 0
            self.sleep_time_min = 0
            self.album_sleep = 0
            self.record_sleep = 0
            
        if self.sleep_time == 0:
            if self.rotary_pos== 0:
                self.Button_Sleep.config(bg = "light blue", text = "SLEEP")
            elif self.rotary_pos == 1 and self.rot_pos == 10:
                self.Button_Sleep.config(bg = "yellow", text = "SLEEP")
        elif self.sleep_time > 0:
            if self.rotary_pos== 0:
                self.Button_Sleep.config(fg = "black", bg = "orange", text = str(self.sleep_time)  + " mins")
            elif self.rotary_pos == 1 and self.rot_pos == 10:
                self.Button_Sleep.config(fg = "black", bg = "yellow", text = str(self.sleep_time)  + " mins")
            
    def sleep_off(self):
        if self.cutdown != 1  and self.cutdown != 5 and self.cutdown != 6:
            self.Disp_Name_m3u.config(background="light gray", foreground="black")
            self.Disp_Name_m3u.delete('1.0','20.0')
        if self.shutdown == 1 or self.sleep_time > 0:
            self.shutdown = 0
            self.sleep_time = 0
            self.sleep_time_min = 0
            self.album_sleep = 0
            self.Button_Sleep.config(bg = "light blue", text = "SLEEP")
 
    def Check_Sleep(self):
        if self.trace > 0:
            print ("Check Sleep")
        if self.sleep_time > 0:
            if self.album_start == 1 and self.album_sleep == 0:
                self.sleep_current = int(self.tplaylist/60)  + 1
            else:            
                self.sleep_current = int((self.sleep_time_min - (time.monotonic() - self.begin))/60)
            if self.sleep_current > 0:
                if self.rotary_pos == 1 and self.rot_pos == 10:
                    self.Button_Sleep.config(fg = "black", bg = "yellow", text = str(self.sleep_current + 1)  + " mins")
                else:
                    self.Button_Sleep.config(fg = "black", bg = "orange", text = str(self.sleep_current + 1)  + " mins")
            else:
                self.Button_Sleep.config(fg = "yellow", bg = "red", text = str(int((self.sleep_time_min - (time.monotonic() - self.begin)))) + " s")
            if self.sleep_current < 1:
                self.Button_Sleep.config(bg = "red")
        if (time.monotonic() - self.begin > self.sleep_time_min) and self.sleep_time > 0 and self.shutdown == 1 and self.Radio_RON == 0 and self.usave == 1:
            os.system("sudo shutdown -h now")
        if (time.monotonic() - self.begin > self.sleep_time_min) and self.sleep_time > 0 and self.shutdown == 1 and self.Radio_RON == 0:
            if self.R_Stopped == 0:
                os.system("sudo shutdown -h now")
            else:
                self.shutdown = 0
                self.sleep_time = 0
                self.sleep_time_min = 0
                self.album_sleep = 0
                self.Button_Sleep.config(bg = "light blue", text = "SLEEP", fg = "black")
                self.Radio_ON = 1
                self.RadioX()
        self.after(1000, self.Check_Sleep)

    def DelPL_m3u(self):
        if self.cutdown != 1 and self.cutdown != 5 and self.cutdown != 6 and self.Radio_ON == 0:
            self.Disp_Name_m3u.config(background="light gray", foreground="black")
        if os.path.exists(self.que_dir) and self.paused == 0 and self.album_start == 0 and self.Radio_ON == 0:
            Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
            if self.muted == 1 and Name == "":
                Name = self.que_dir[len(self.m3u_dir):-4]
            if len(Name) > 0 and Name != self.m3u_def:
                if Name == "FAV":
                    Name = "FAVourites"
                if os.path.exists(self.m3u_dir + Name + ".m3u") and Name != self.m3u_def:
                    os.remove(self.m3u_dir + Name + ".m3u")
                    self.m3us = glob.glob(self.m3u_dir + "*.m3u")
                    self.m3us.sort()
                    self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")
                    self.Disp_Name_m3u.delete('1.0','20.0')
                    self.m3u_no = 0
                    self.m3us = glob.glob(self.m3u_dir + "*.m3u")
                    self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
                    self.m3us.sort()
                    self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")
                    self.wheel_opt = 3
                    self.Button_Next_PList.config(fg = "red")
                    self.Button_Next_Artist.config(fg = "black")
                    self.Button_Next_Album.config(fg = "black")
                    self.Button_Next_Track.config(fg = "black")
                    if self.BT == 0:
                        self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                    self.Button_Start.config(bg = "green",fg = "black",text = "PLAY Playlist")
                    self.play = 0
                    self.que_dir = self.m3us[self.m3u_no]
                    Tracks = []
                    with open(self.que_dir,"r") as textobj:
                        line = textobj.readline()
                        while line:
                            Tracks.append(line.strip())
                            line = textobj.readline()
                    self.tunes = []
                    for counter in range (0,len(Tracks)):
                        counter2 = Tracks[counter].count('/')
                        if counter2 == 6:
                            self.genre_name = "None"
                            z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                            self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)
                        if counter2 == 7:
                            z,self.drive_name1,self.drive_name2,self.drive_name,self.genre_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                            self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)
                        if counter2 == 5:
                            self.genre_name = "None"
                            self.drive_name1,self.drive_name2,self.drive_name,self.artist_name3,self.album_name3,self.track_name  = Tracks[counter].split('/')
                            if self.album_name3.count(" - ") == 1:
                                self.artist_name,self.album_name = self.album_name3.split(" - ")
                                self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.artist_name3 + "^" + self.drive_name2 + "^" + self.drive_name + "^" + self.genre_name)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_Total_tunes.config(text =len(self.tunes))
                    self.track_no = 0
                    self.shuffle_on = 0
                    self.Button_Shuffle.config(bg = "light blue",fg = "black",text = "Shuffle")
                    self.sorted = 0
                    self.Button_AZ_artists.config(bg = "light blue",fg = "black",text = "A-Z Sort")
                    self.Disp_Name_m3u.config(background="light gray", foreground="black")
                    self.Time_Left_Play()

            else:
                self.Disp_Name_m3u.config(background="light gray", foreground="black")

    def exit(self):
        if self.play == 1 and self.Radio_ON == 0:
            if self.version == 1:
                self.p.kill()
            else:
                player.stop()
        if self.Radio_ON == 1:
            self.q.kill()
        self.play = 0
        self.master.destroy()
        if self.HP4_backlight == 1 or self.LCD_backlight == 1:
            self.LCD_pwm.close()
            os.system("raspi-gpio set " + str(self.LCD_LED_pin) + " op")
            os.system("raspi-gpio set " + str(self.LCD_LED_pin) + " dh")
        sys.exit()

    def Search(self):
        self.Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
        if self.paused == 0 and self.album_start == 0 and len(self.Name) > 0 and self.Radio_ON == 0:
          search = []
          for counter in range (0,len(self.tunes)):
                self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name= self.tunes[counter].split('^')
                if self.Name in self.track_name:
                    search.append(self.tunes[counter])
          if len(search) > 0:
            search.sort()
            for counter in range(0,len(search)):
                self.artist_name,self.album_name2,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.genre_name  = search[counter].split('^')
                with open(self.m3u_dir + self.Name + ".m3u", 'a') as f:
                    if self.genre_name == "None":
                        f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name2 + "/" + self.track_name + "\n")
                    else:
                        f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.genre_name  + "/" + self.artist_name + "/" + self.album_name2 + "/" + self.track_name + "\n")
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")
            self.wheel_opt = 3
            self.Button_Next_PList.config(fg = "red")
            self.Button_Next_Artist.config(fg = "black")
            self.Button_Next_Album.config(fg = "black")
            self.Button_Next_Track.config(fg = "black")
            if self.play == 1:
                if self.version == 1:
                    self.p.kill()
                else:
                    player.stop()
                    self.paused = 0
                    if self.BT == 0:
                        self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                self.Button_Start.config(bg = "green",fg = "black",text = "PLAY Playlist")
            self.play = 0
            for x in range(0,len(self.m3us)):
                 if self.m3us[x] == self.m3u_dir + self.Name + ".m3u":
                     self.m3u_no = x
            self.que_dir = self.m3us[self.m3u_no]
            Tracks = []
            with open(self.que_dir,"r") as textobj:
               line = textobj.readline()
               while line:
                  Tracks.append(line.strip())
                  line = textobj.readline()
            self.tunes = []
            for counter in range (0,len(Tracks)):
                counter2 = Tracks[counter].count('/')
                if counter2 == 6:
                    self.genre_name == "None"
                    z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                    self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2+ "^" + self.genre_name)
                if counter2 == 7:
                    z,self.drive_name1,self.drive_name2,self.drive_name,self.genre_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                    self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.genre_name)
                if counter2 == 5:
                    self.genre_name == "None"
                    self.drive_name1,self.drive_name2,self.drive_name,self.artist_name3,self.album_name3,self.track_name  = Tracks[counter].split('/')
                    if self.album_name3.count(" - ") == 1:
                        self.artist_name,self.album_name = self.album_name3.split(" - ")
                        self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.artist_name3 + "^" + self.drive_name2 + "^" + self.drive_name+ "^" + self.genre_name)
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.track_no = 0
            self.shuffle_on = 0
            self.Button_Shuffle.config(bg = "light blue",fg = "black",text = "Shuffle")
            self.sorted = 0
            self.Button_AZ_artists.config(bg = "light blue",fg = "black",text = "A-Z Sort")
            self.Disp_Name_m3u.config(background="light gray", foreground="black")
            self.Disp_Name_m3u.delete('1.0','20.0')
            self.Time_Left_Play()


    def isConnected(self):
        try:
            sock = socket.create_connection(("www.google.com", 80))
            if sock is not None:
                sock.close
            self.StillConnected()
            return True
        except OSError:
            if self.rotary_pos== 0:
                messagebox.showinfo("WARNING!","No Internet found!")
        return False

    def StillConnected(self):
        try:
            if self.trace > 0:
                print ("Still Connected")
            sock = socket.create_connection(("www.google.com", 80))
            if sock is not None:
                sock.close
            if self.Radio_ON == 1:
                self.after(600000, self.StillConnected)
            return True
        except OSError:
            if self.trace > 0:
                print ("Connect ERROR")
            if self.Radio_ON == 1:
                if self.Radio_Stns[self.Radio + 2] == 0:
                    self.q.kill()
                else:
                    self.q.kill()
                    self.r.kill()
                if self.Radio_RON == 1:
                    self.record = 1
                    self.Copy_Record()
                    self.Radio_RON = 0
                self.RadioX()
        return False
            
    def RadioX(self):
        if self.wheel_opt == 2 and self.sleep_time > 0 and self.Radio_ON == 0:
            self.exit()
        self.f_volume = self.volume
        if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 2:
            self.Button_volume.config(text = self.volume)
        else:
            self.Button_Vol_UP.config(text = "Vol >   " + str(self.volume))
        self.muted = 0
        self.m.setvolume(self.volume)
        os.system("amixer -D pulse sset Master " + str(self.volume) + "%")
        if (self.cutdown == 6 or self.cutdown == 5) and (self.stopstart == 1 or self.album_start == 1):
            self.Gapless()
        if (self.cutdown == 6 or self.cutdown == 4 or self.cutdown == 5) and self.paused == 0 and (self.album_start == 1 or self.stopstart == 1) and self.Radio_ON == 0:
            if self.cutdown == 6 or self.cutdown == 4 or self.cutdown == 5:
                if self.play == 2:
                    self.play = 0
                self.repeat_count +=1
                if self.repeat_count == 1:
                    self.repeat_track = 1
                    self.repeat = 0
                    self.Button_Radio.config(bg = "green", fg = "black", text = "Repeat Track")
                elif self.repeat_count == 2:
                    self.repeat_track = 0
                    self.repeat = 1
                    self.Button_Radio.config(bg = "green",fg = "black",text = "Repeat P-List")
                else:
                    self.repeat_count = 0
                    self.repeat = 0
                    self.repeat_track = 0
                    self.Button_Radio.config(bg = "light blue",fg = "black",text = "Repeat")
                if self.play == 1:
                    self.Start_Play()
                else:
                    self.Show_Track()
            if self.paused == 0 and self.album_start == 1 and self.repeat_album == 0:
                self.repeat_album = 1
                self.repeat = 0
                self.repeat_track = 0
                self.Button_Radio.config(bg = "green",fg = "black",text = "Repeat Album")
            elif self.paused == 0 and self.album_start == 1 and self.repeat_album == 1:
                self.repeat_album = 0
                self.repeat = 0
                self.repeat_track = 0
                self.Button_Radio.config(bg = "light blue",fg = "black",text = "Repeat Album")
            if self.rotary_pos == 1:
                self.Button_Radio.config(bg = "yellow")
        # STOP RECORD BUTTON
        elif self.Radio_ON == 1 and self.Radio_RON == 1 and self.record == 1:
            if self.trace > 0:
                print ("Stop Record")
            self.Radio_RON    = 0
            self.auto_record  = 0
            self.auto_radio   = 1
            self.auto_rec_set = 0
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            self.L4.config(text = "")
            self.Disp_track_len.config(text ="     ")
            self.Disp_played.config(text ="     ")
            self.Disp_track_no.config(text = "")
            self.Button_Reload.config( bg = "light gray", fg = "black")
            if self.imgxon == 1:
                self.imgx.after(100, self.imgx.destroy())
                self.imgxon = 0
                if cutdown == 1:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 4:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 5:
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
            if self.cutdown == 6:
                self.L1.config(text = "RAM: ")
                self.Disp_track_name1.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name2.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name3.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name4.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name5.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name6.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name7.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name8.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name9.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
            if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and  self.cutdown != 6:
                self.Disp_Total_Plist.config(text = "")
                if self.touchscreen == 1:
                    self.L8.config(text = "")
                if self.cutdown != 3 and self.cutdown != 2:
                    self.L3.config(text = "")
                    self.L1.config(text = "RAM: ")
                self.Button_Radio.config(bg = "yellow",fg = "black", text = "STOP Radio")
            else:
                self.Button_Radio.config(bg = "yellow",fg = "black", text = "STOP")
            if self.Radio_Stns[self.Radio + 2]  > 0:
                self.Button_Pause.config(fg = "black", bg = "light blue", text = "RECORD")
            else:
                self.Button_Pause.config(fg = "black", bg = "light grey", text = "RECORD")
            if self.cutdown != 1:
                self.Button_Radio.config(bg = "yellow",fg = "black", text = "STOP Radio")
            if self.cutdown != 1  and self.cutdown != 5 and self.cutdown != 6 and self.model != 0:
                if self.cutdown != 3:
                    self.L9.config(text= "   ")
                self.s.configure("LabeledProgressbar", text="0 %      ", background='red')
                self.progress['value'] = 0
            if self.cutdown == 5 or self.cutdown == 4 or self.cutdown == 2 or self.cutdown >= 7:
                self.Button_Next_AZ.config(fg = "black", bg = "light blue", text = "NextAZ")
            self.Copy_Record()
        # STOP RADIO BUTTON
        elif self.Radio_ON == 1 and self.stopstart == 0 and self.album_start == 0:
            if self.trace > 0:
                print ("Stop Radio")
            self.Radio_ON    = 0
            self.auto_radio  = 0
            self.auto_record = 0
            with open('Lasttrack3.txt', 'w') as f:
                f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
            if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5 and self.cutdown != 6 :
                if self.touchscreen == 1:
                    self.L8.config(text = ".m3u")
                    self.Button_DELETE_m3u.config(fg= "black")
                self.Disp_Name_m3u.delete('1.0','20.0')
                self.Disp_Total_Plist.config(text = "")
                if self.cutdown != 2:
                    self.L5.config(text="Drive :")
                self.L6.config(text="Playlist :")
            if self.cutdown == 5 or self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 6:
                self.L1.config(text="Track:")
                self.L3.config(text="Played:")
                if self.cutdown == 5 or self.cutdown >= 7:
                    self.Button_Next_AZ.config(fg = "black", bg = "light blue", text = "NextAZ")
            if self.cutdown >= 7 or self.cutdown == 0 or self.cutdown == 2:
                self.Button_Bluetooth.config(bg = 'light blue')
            self.Button_Radio.config(bg = "light blue",fg = "black", text = "Radio")
            if self.Radio_Stns[self.Radio + 2] == 0:
                self.q.kill()
            else:
                self.q.kill()
                self.r.kill()
            self.play = 0
            self.total_record = 0
            self.L2.config(text="of")
            self.L4.config(text="/")
            if self.imgxon == 1:
                self.imgx.after(100, self.imgx.destroy())
                self.imgxon = 0
                if cutdown == 1:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 4:
                    self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                    self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                elif cutdown == 5:
                    self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                    self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                    self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                    self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
            if self.cutdown != 5 and self.cutdown != 6 :
                self.Button_Next_Artist.config(text="Artist >")
                self.Button_Prev_Artist.config(text="< Artist")
                if self.cutdown != 1:
                    if self.touchscreen == 1:
                        self.Button_PList_m3u.config(bg  = "light green", fg = "black")
                        self.Button_Track_m3u.config(bg  = "light green", fg = "black")
                        self.Button_Album_m3u.config(bg  = "light green", fg = "black")
                        self.Button_Artist_m3u.config(bg = "light green", fg = "black")
                self.Button_Start.config(bg = "green",fg = "black",text = "PLAY Playlist")
                self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            else:
                self.Button_Next_Artist.config(text="Artist >")
                if self.rotary_pos== 0:
                    self.Button_Prev_Artist.config(text="< Artist")
                else:
                    self.rot_pos = 3
                    self.rot_posp = 3
                    self.Button_Start.config(bg = "yellow",text="PLAY Playlist")
                    self.Button_Prev_Artist.config(text="< Artist")
            self.Button_Shuffle.config(bg  = "light blue", fg = "black", text = "Shuffle")
            if (self.cutdown == 0 or self.cutdown >= 7) and self.touchscreen == 1:
                self.Button_Search_to_m3u.config(bg = "light green", fg = "black", text = "Search to .m3u")
            if self.cutdown != 4 and self.cutdown != 5 and self.cutdown != 1 and  self.cutdown != 6 and self.touchscreen == 1:
                self.Button_Add_to_FAV.config(bg = "light green", fg = "black",text = "Add track to FAV .m3u  ")
                self.Button_PList_m3u.config(bg  = "light green", fg = "black",text = "ADD P-List to .m3u")
            self.Button_Reload.config(text = "RELOAD",bg  = "light blue", fg = "black")
            if self.cutdown != 5 and self.cutdown != 6 :
                self.Button_Prev_PList.config(fg = "black")
            self.Button_Start.config(bg  = "green", fg = "black")
            if self.rotary_pos== 0:
                self.Button_Prev_Artist.config(bg = "light blue", fg = "black")
            else:
                self.rot_pos = 3
                self.rot_posp = 3
                self.Button_Start.config(bg = "yellow",text="PLAY Playlist")
                self.Button_Prev_Artist.config(text="< Artist")
            self.Button_Prev_Album.config(bg = "light blue", fg = "black")
            self.Button_Prev_Track.config(bg = "light blue", fg = "black")
            self.Button_Next_Artist.config(bg = "light blue", fg = "black")
            self.Button_Next_Album.config(bg = "light blue", fg = "black")
            self.Button_Next_Track.config(bg = "light blue", fg = "black")
            if self.cutdown != 5 and self.cutdown != 6 :
                self.Button_Prev_PList.config(fg = "black", bg = "light blue")
                self.Button_Next_PList.config(fg = "black", bg = "light blue")
            if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3 or self.cutdown == 2:
                self.Button_Next_AZ.config(text = "NextAZ", bg = "light blue", fg = "black")
            if self.cutdown == 6:
                self.Button_Next_AZ.config(text = "Info", bg = "light blue", fg = "black")
            self.Button_Reload.config(bg = "light blue", fg = "black")
            self.Button_Next_AZ.config(bg = "light blue", fg = "black")
            if self.shuffle_on == 0:
                self.Button_Shuffle.config(fg = "black",bg = "light blue")
            else:
                self.Button_Shuffle.config(fg = "black",bg = "green")
            if self.cutdown != 1 and self.cutdown != 4 and self.cutdown != 5 and  self.cutdown != 6:
                 self.Button_AZ_artists.config(fg = "black",bg = "light blue")
                 self.Button_repeat.config(fg = "black",bg = "light blue", text = "Repeat")
            if self.cutdown == 6:
                self.Button_Pause.config(fg = "black",bg = "light blue", text = "NextAZ")
            else:
                self.Button_Pause.config(fg = "black",bg = "light blue", text = "Pause")
            if self.cutdown != 1 and self.cutdown != 5 and  self.cutdown != 6:
                self.Button_Gapless.config(fg = "black",bg = "light blue")
            self.Button_TAlbum.config(fg = "black",bg = "blue")
            self.Disp_track_no.config(text = str(self.track_no + 1))
            if self.cutdown == 6:
                self.Disp_track_name1.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name2.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name3.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name4.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name5.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name6.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name7.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name8.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
                self.Disp_track_name9.config(fg = "black",bg = "light grey",text = " ", borderwidth=2)
            self.version = 2
            time.sleep(2)
            if self.cutdown >= 7:
                self.shuffle_on = 0
                self.Disp_artist_name.set(self.artist_name)
                self.ac = 1
                if len(self.tunes) > 0:
                    self.plist_callback()
                self.Disp_album_name.set(self.album_name)
                self.Disp_track_name.set(self.track_name)
            self.reload = 1
            self.Show_Track()
        # START RADIO BUTTON
        elif self.paused == 0 and self.album_start == 0 and self.stopstart == 0 and self.Radio_ON == 0 and self.bt_on == 0:
            if self.trace > 0:
                print ("Start Radio")
            out = self.isConnected()
            if out == True:
                self.Radio_ON = 1
                if self.cutdown >= 7:
                    self.Disp_artist_name.set("")
                    self.Disp_album_name.set("")
                    self.Disp_track_name.set("")
                    self.Disp_artist_name["values"] = []
                    self.Disp_album_name["values"]  = []
                    self.Disp_track_name["values"]  = []
                    self.plist_callback()
                self.play      = 1
                self.version   = 1
                self.R_Stopped = 0
                self.rec_begin = time.monotonic()
                self.Name = self.Radio_Stns[self.Radio]
                if self.Radio_Stns[self.Radio + 2]  > 0 and self.record == 1:
                    self.Disp_played.config(text ="000:00")
                    if self.cutdown != 1 and self.cutdown != 4 and self.cutdown != 5 and self.cutdown != 6  and self.cutdown != 3:
                        self.Button_Pause.config(fg = "black", bg = "light blue", text = "RECORD")
                        if self.touchscreen == 1:
                            self.L8.config(text = ".mp3")
                        self.L6.config(text="")
                else:
                    if self.cutdown != 1 and self.cutdown != 4 and self.cutdown != 5 and self.cutdown != 6 and self.touchscreen == 1:
                        self.L8.config(text = "")
                    self.Button_Pause.config(fg = "black", bg = "light blue", text = "Pause")
                    
                if self.cutdown != 1 and self.cutdown != 4:
                    if self.cutdown != 3 and self.cutdown != 2:
                        self.L1.config(text="")
                        self.L3.config(text="")
                    if self.cutdown != 2 and self.cutdown != 5 and self.cutdown != 6 :
                        self.L5.config(text="")
                    if self.cutdown != 5 and self.cutdown != 6 :
                        self.L6.config(text="")
                        if self.touchscreen == 1:
                            self.Button_DELETE_m3u.config(fg= "white")
                        if self.cutdown != 2 and self.cutdown != 3 and self.touchscreen == 1:
                            self.Button_Search_to_m3u.config(fg = "black", bg = "light grey", text = "Search to .m3u")
                if self.cutdown != 1:
                    self.Button_Radio.config(bg = "yellow",fg = "black", text = "STOP Radio")
                else:
                    self.Button_Radio.config(bg = "yellow",fg = "black", text = "STOP")
                self.L2.config(text="")
                self.L4.config(text="")
                if self.cutdown >= 7 or self.cutdown == 0 or self.cutdown == 2:
                    self.Button_Bluetooth.config(bg = 'light gray')
                if self.cutdown == 6:
                    if len(self.Radio_Stns) > 0:
                        self.Disp_track_name1.config(fg = "black",bg = "white",text = self.Radio_Stns[0], borderwidth=2, relief="groove")
                    else:
                        self.Disp_track_name1.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if len(self.Radio_Stns) > 3:
                        self.Disp_track_name2.config(fg = "black",bg = "white",text = self.Radio_Stns[3], borderwidth=2, relief="groove")
                    else:
                        self.Disp_track_name2.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if len(self.Radio_Stns) > 6:
                        self.Disp_track_name3.config(fg = "black",bg = "white",text = self.Radio_Stns[6], borderwidth=2, relief="groove")
                    else:
                        self.Disp_track_name3.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if len(self.Radio_Stns) > 9:
                        self.Disp_track_name4.config(fg = "black",bg = "white",text = self.Radio_Stns[9], borderwidth=2, relief="groove")
                    else:
                        self.Disp_track_name4.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if len(self.Radio_Stns) > 12:
                        self.Disp_track_name5.config(fg = "black",bg = "white",text = self.Radio_Stns[12], borderwidth=2, relief="groove")
                    else:
                        self.Disp_track_name5.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if len(self.Radio_Stns) > 15:
                        self.Disp_track_name6.config(fg = "black",bg = "white",text = self.Radio_Stns[15], borderwidth=2, relief="groove")
                    else:
                        self.Disp_track_name6.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if len(self.Radio_Stns) > 18:
                        self.Disp_track_name7.config(fg = "black",bg = "white",text = self.Radio_Stns[18], borderwidth=2, relief="groove")
                    else:
                        self.Disp_track_name7.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if len(self.Radio_Stns) > 21:
                        self.Disp_track_name8.config(fg = "black",bg = "white",text = self.Radio_Stns[21], borderwidth=2, relief="groove")
                    else:
                        self.Disp_track_name8.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
                    if len(self.Radio_Stns) > 24:
                        self.Disp_track_name9.config(fg = "black",bg = "white",text = self.Radio_Stns[24], borderwidth=2, relief="groove")
                    else:
                        self.Disp_track_name9.config(fg = "black",bg = "#ddd",text = " ", borderwidth=0)
 
                if self.cutdown != 5 and self.cutdown != 6 :
                    if self.cutdown != 1 and self.touchscreen == 1:
                        self.Disp_Name_m3u.delete('1.0','20.0')
                        self.Button_Track_m3u.config(bg  = "light grey", fg = "black")
                        self.Button_Artist_m3u.config(bg  = "light grey", fg = "black")
                        self.Button_Album_m3u.config(bg  = "light grey", fg = "black")
                    if self.cutdown != 1:
                        self.Button_Gapless.config(bg  = "light grey", fg = "black")
                    self.Button_Prev_Artist.config(bg  = "light grey", fg = "black")
                    self.Button_Next_Artist.config(bg  = "light grey", fg = "black")
                    self.Button_Prev_Artist.config(text = " < Station", fg = "black", bg = "light blue")
                    self.Button_Next_Artist.config(text = " Station >", fg = "black", bg = "light blue")
                    if self.cutdown != 7 and self.cutdown != 8:
                        self.Disp_artist_name.config(text = self.Name)
                    else:
                        self.Disp_artist_name.set(self.Name)
                    self.Disp_plist_name.config(text = "")
                    self.Button_Prev_PList.config(fg = "black", bg = "light gray")
                    self.Button_Next_PList.config(fg = "black", bg = "light gray")
                else:
                    self.Button_Prev_Artist.config(text = " < Station", fg = "black")
                    self.Button_Next_Artist.config(text = " Station >", fg = "black")
                    self.Disp_artist_name.config(text = self.Name)
                    if self.cutdown != 5 and self.cutdown != 6 :
                        self.Button_Prev_PList.config(fg = "black", bg = "light gray")
                        self.Button_Next_PList.config(fg = "black", bg = "light gray")
                self.Button_Start.config(bg  = "light grey", fg = "black")
                self.Button_Prev_Album.config(bg  = "light grey", fg = "black")
                self.Button_Next_Album.config(bg  = "light grey", fg = "black")
                self.Button_Prev_Track.config(bg  = "light grey", fg = "black")
                self.Button_Next_Track.config(bg = "light grey", fg = "black")
                if self.cutdown == 5 or self.cutdown >= 7:
                    self.Button_Next_AZ.config(bg = "light blue", fg = "black", text = "Info")
                else:
                    self.Button_Next_AZ.config(bg = "light grey", fg = "black")
                self.Button_Shuffle.config(bg = "light gray", fg = "black")
                if (self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 3 or self.cutdown == 2) and self.touchscreen == 1:
                    self.Button_Add_to_FAV.config(bg = "light grey", fg = "black",text = "Add track to FAV .m3u  ")
                if self.cutdown != 5 and self.cutdown != 1 and self.cutdown != 6 and self.touchscreen == 1 :
                    self.Button_PList_m3u.config(bg  = "light grey", fg = "black")
                if self.cutdown != 4 and self.cutdown !=5 and self.cutdown !=1:
                    if self.cutdown != 6:
                        if self.touchscreen == 1:
                           self.Button_Album_m3u.config(bg = "light grey", fg = "black")
                        self.Button_AZ_artists.config(bg  = "light grey", fg = "black")
                        self.Button_repeat.config(bg  = "light grey", fg = "black")
                        self.Disp_Total_Plist.config(text = "")
                    if self.cutdown == 0 or self.cutdown == 3 or self.cutdown >= 7:
                        self.Disp_Drive.config(text = "")
                    if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg"):
                        self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".jpg")
                        if self.cutdown != 2:
                            if self.cutdown == 8:
                                self.load = self.load.resize((320,320), Image.LANCZOS)
                            else:
                                self.load = self.load.resize((218, 218), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((150, 150), Image.LANCZOS)
                        self.render2 = ImageTk.PhotoImage(self.load)
                        self.img.config(image = self.render2)
                    elif os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                        self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".png")
                        if self.cutdown != 2:
                            if self.cutdown == 8:
                                self.load = self.load.resize((320,320), Image.LANCZOS)
                            else:
                                self.load = self.load.resize((218, 218), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((150, 150), Image.LANCZOS)
                        self.render2 = ImageTk.PhotoImage(self.load)
                        self.img.config(image = self.render2)
                    elif os.path.exists(self.radio_jpg):
                        self.load = Image.open(self.radio_jpg)
                        if self.cutdown != 2:
                            if self.cutdown == 8:
                                self.load = self.load.resize((320,320), Image.LANCZOS)
                            else:
                                self.load = self.load.resize((218, 218), Image.LANCZOS)
                        else:
                            self.load = self.load.resize((150, 150), Image.LANCZOS)
                        self.render3 = ImageTk.PhotoImage(self.load)
                        self.img.config(image = self.render3)
                       
                self.Button_TAlbum.config(bg  = "light grey", fg = "black")
                if self.Radio_Stns[self.Radio + 2]  > 0 and self.record == 1:
                    self.Button_Pause.config(bg  = "light blue", fg = "black", text = "RECORD")
                else:
                    self.Button_Pause.config(fg = "black", bg = "light grey", text = "Pause")
                self.Button_Reload.config(bg  = "light grey", fg = "black")
                self.Disp_album_name.config(text ="")
                self.Disp_track_name.config(text ="")
                self.Disp_track_no.config(text = "")
                self.Disp_Total_tunes.config(text = "")
                self.Disp_played.config(text = "")
                self.Disp_track_len.config(text = "")
                self.Radio_ON    = 1
                if self.cutdown == 1 or self.cutdown == 4 or self.cutdown == 5:
                    self.Disp_track_len.config(text = int(len(self.Radio_Stns)/3))
                    self.Disp_played.config(text = int((self.Radio)/3)+1)
                    self.L4.config(text="of")
                    if self.cutdown == 1:
                        self.Disp_Total_tunes.config(text = "        Stn:")
                    elif self.cutdown == 4:
                        self.Disp_Total_tunes.config(text = "    Stn:")
                    else:   
                        self.L3.config(text = "Stn:")
                    if os.path.exists(self.h_user + "/Documents/" + self.Name + ".jpg"):
                        self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".jpg")
                        if self.cutdown == 1:
                           self.load = self.load.resize((100, 100), Image.LANCZOS)
                        elif self.cutdown == 4:
                           self.load = self.load.resize((130, 130), Image.LANCZOS)
                        else:
                           self.load = self.load.resize((170, 170), Image.LANCZOS)
                        self.render2 = ImageTk.PhotoImage(self.load)
                        if self.imgxon == 0:
                            self.imgx = tk.Label(self.Frame10, image = self.render2)
                            self.imgx.grid(row = 1, column = 1, columnspan = 3, rowspan = 3, pady = 0)
                            self.imgxon = 1
                            if self.cutdown == 1 or self.cutdown == 4:
                                self.Disp_plist_name.after(100, self.Disp_plist_name.destroy())
                            self.Disp_artist_name.after(100, self.Disp_artist_name.destroy())
                            self.Disp_album_name.after(100, self.Disp_album_name.destroy())
                        self.imgx.config(image = self.render2)
                    elif os.path.exists(self.h_user + "/Documents/" + self.Name + ".png"):
                        self.load = Image.open(self.h_user + "/Documents/" + self.Name + ".png")
                        if self.cutdown == 1:
                           self.load = self.load.resize((100, 100), Image.LANCZOS)
                        elif self.cutdown == 4:
                           self.load = self.load.resize((130, 130), Image.LANCZOS)
                        else:
                           self.load = self.load.resize((170, 170), Image.LANCZOS)
                        self.render2 = ImageTk.PhotoImage(self.load)
                        if self.imgxon == 0:
                            self.imgx = tk.Label(self.Frame10, image = self.render2)
                            self.imgx.grid(row = 1, column = 1, columnspan = 3, rowspan = 3, pady = 0)
                            self.imgxon = 1
                            if self.cutdown == 1 or self.cutdown == 4:
                                self.Disp_plist_name.after(100, self.Disp_plist_name.destroy())
                            self.Disp_artist_name.after(100, self.Disp_artist_name.destroy())
                            self.Disp_album_name.after(100, self.Disp_album_name.destroy())
                        self.imgx.config(image = self.render2)

                self.copy = 0
                self.auto_radio  = 1
                with open('Lasttrack3.txt', 'w') as f:
                    f.write(str(self.track_no) + "\n" + str(self.auto_play) + "\n" + str(self.Radio) + "\n" + str(self.volume) + "\n" + str(self.auto_radio) + "\n" + str(self.auto_record) + "\n" + str(self.auto_rec_time) + "\n" + str(self.shuffle_on) + "\n" + str(self.auto_album) + "\n")
                if self.cutdown == 0 or self.cutdown >= 7 or self.cutdown == 5 or self.cutdown == 6:
                    self.L1.config(text = "RAM: ")
                out = self.isConnected()
                rems = glob.glob("/run/shm/music/*/*/*/*/*.mp3")
                for x in range(0,len(rems)):
                    os.remove(rems[x])
                rems = glob.glob("/run/shm/music/*/*/*.cue")
                for x in range(0,len(rems)):
                    os.remove(rems[x])
                self.playlist ="-nocache"
                if ".pls" in self.Radio_Stns[self.Radio + 1]  or ".m3u"  in self.Radio_Stns[self.Radio + 1]  :
                    self.playlist = "-playlist"
                    self.Radio_Stns[self.Radio + 2] = 0
                if self.Radio_Stns[self.Radio + 2] == 0:
                    self.q = subprocess.Popen(["mplayer",self.playlist, self.Radio_Stns[self.Radio + 1]] , shell=False)
                else:
                    self.r = subprocess.Popen(["streamripper",self.Radio_Stns[self.Radio + 1],"-r","--xs_offset=-9000","-z","-l","99999","-d","/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings","-a",self.Name], shell=False)
                    time.sleep(1)
                    self.q = subprocess.Popen(["mplayer","-nocache","http://localhost:8000"] , shell=False)
                    track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
                    if len(track) == 0:
                       time.sleep(2)
                track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
                if len(track) == 0  and self.Radio_Stns[self.Radio + 2]  > 0:
                    if self.rotary_pos== 0:
                        messagebox.showinfo("WARNING!","Check Recordable entry set correctly for this stream")
                # check RAM space and set self.max_record
                st = os.statvfs("/run/shm/")
                self.freeram1 = (st.f_bavail * st.f_frsize)/1100000
                self.timer7 = time.monotonic()
                free2 = int((self.freeram1 - self.ram_min)/10) * 10
                self.max_record = min(free2,991)
                self.ramtest = 1
                
                self.Check_Record()

    def Check_Record(self):
        if self.trace > 2:
            print ("Check Record")
        # check RAM space
        st = os.statvfs("/run/shm/")
        freeram = (st.f_bavail * st.f_frsize)/1100000
        if self.Radio_RON == 1 and self.record == 1:
            self.rplayed = time.monotonic() - self.rec_begin
            self.r_minutes = int(self.rplayed // 60)
            self.r_seconds = int (self.rplayed - (self.r_minutes * 60))
            if self.r_seconds != self.roldsecs:
                self.Disp_played.config(text ="%03d:%02d" % (self.r_minutes, self.r_seconds % 60),fg = "red")
                self.roldsecs = self.r_seconds
            rec_stat = 0
            rec_stat = (os.stat("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/" + self.Name + ".mp3").st_size)/1000000
            self.record_current = int((self.record_time_min - (time.monotonic() - self.rec_begin))/60)
            if self.record_current > 0:
                if self.rot_pos == 9:
                    self.Button_Pause.config(fg = "black", bg = "yellow", text = str(self.record_current + 1)  + " mins")
                else:
                    self.Button_Pause.config(fg = "black", bg = "orange", text = str(self.record_current + 1)  + " mins")
            else:
                self.Button_Pause.config(fg = "black", bg = "orange", text = str(int((self.record_time_min - (time.monotonic() - self.rec_begin)))) + " s")
            if self.cutdown != 1 and self.cutdown != 5 and self.cutdown != 6 and self.model != 0:
                if self.cutdown != 3:
                    self.L9.config(text= " R :")
                self.s.configure("LabeledProgressbar", text="{0} %      ".format(int((self.rplayed/self.record_time_min)*100)), background='red')
                self.progress['value'] = (self.rplayed/self.record_time_min)*100
        self.Get_track(1)
        # Clear RAM if RAM space less than limit, or time exceeds 9900 seconds
        if self.Radio_ON == 1 and self.Radio_RON == 0 and (time.monotonic() - self.rec_begin > 9900 or freeram < self.ram_min):
            self.rec_begin = time.monotonic()
            if self.Radio_Stns[self.Radio + 2] == 0:
                self.q.kill()
            else:
                self.q.kill()
                self.r.kill()
            time.sleep(1)
            self.rems2 = glob.glob("/run/shm/music/*/*/*/*/*.mp3")
            for x in range(0,len(self.rems2)):
                os.remove(self.rems2[x])
            self.rems2 = glob.glob("/run/shm/music/*/*/*.mp3")
            for x in range(0,len(self.rems2)):
                os.remove(self.rems2[x])
            self.rems3 = glob.glob("/run/shm/music/*/*/*.cue")
            for x in range(0,len(self.rems3)):
                os.remove(self.rems3[x])
            if self.Radio_Stns[self.Radio + 2] == 0:
                self.q = subprocess.Popen(["mplayer", "-nocache", self.Radio_Stns[self.Radio + 1]] , shell=False)
            else:
                self.r = subprocess.Popen(["streamripper",self.Radio_Stns[self.Radio + 1],"-r","--xs_offset=-9000","-z","-l","99999","-d","/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings","-a",self.Name], shell=False)
                time.sleep(1)
                self.q = subprocess.Popen(["mplayer","-nocache","http://localhost:8000"] , shell=False)
                track = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/incomplete/*.mp3")
                if len(track) == 0:
                   time.sleep(2)
        # stop recording if record time exceeded or RAM space less than limit (wait for end of track if track names available in stream)
        now = datetime.datetime.now()
        if (self.Radio_RON == 1 and now > self.stop_record and self.record == 1 and self.oldtrack != self.track_nameX[self.counter]) or (self.Radio_RON == 1 and freeram < self.ram_min):
            if self.trace > 0:
                print ("Stopped Recording")
            self.R_Stopped    = 1
            self.Radio_RON    = 0
            self.auto_rec_set = 0
            if self.cutdown != 1  and self.cutdown != 5 and self.cutdown != 6 and self.model != 0:
                self.L9.config(text= "   ")
                self.s.configure("LabeledProgressbar", text="0 %      ", background='red')
                self.progress['value'] = 0
            self.Copy_Record()
        if self.track_nameX[self.counter][0:3] != " - ":
            self.oldtrack = self.track_nameX[self.counter]
        if self.Radio_ON == 1:
            self.Disp_track_no.config(text = str(int(freeram)))
            self.after(1000, self.Check_Record)

    def Copy_Record(self):
        #==Copy Long Tracks to USB=====================================================================================
        if self.trace > 0:
            print ("Copy Long",self.copy)
        if self.copy == 0 and self.usave == 1:
          USB_Files = []
          USB_Files = (os.listdir(self.m_user + ""))
          if len(USB_Files) > 0:
            st1 = os.statvfs(self.m_user + "/" + USB_Files[0])
            free1 = (st1.f_bavail * st1.f_frsize)/1100000
            free = free1
            if len(USB_Files) > 1:
                st2 = os.statvfs(self.m_user + "/" + USB_Files[1])
                free2 = (st2.f_bavail * st2.f_frsize)/1100000
                if free2 > free1:
                    free = free2
                    del USB_Files[0]
                    if len(USB_Files) > 1:
                        st3 = os.statvfs(self.m_user + "/" + USB_Files[1])
                        free3 = (st3.f_bavail * st3.f_frsize)/1100000
                        if free3 > free:
                            free = free3
                            del USB_Files[0]
            stn1 = self.m_user + "/" + USB_Files[0] + "/" + self.Radio_Stns[self.Radio]
            stn2 = self.m_user + "/" + USB_Files[0] + "/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/"
            if not os.path.exists(stn1):
                os.system ("mkdir " + "'" + stn1 + "'")
                time.sleep(1)
            if not os.path.exists(stn2):
                os.system ("mkdir " + "'" + stn2 + "'")
                time.sleep(1)
            vpath = self.Radio_Stns[self.Radio] + "^Radio_Recordings^" + self.Name + ".mp3^" + USB_Files[0] + "^media^" + os.getlogin() + "^" + self.genre_name 
            if os.path.exists(self.m_user + "/" + USB_Files[0] + "/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/"):
                if not os.path.exists(self.m_user + "/" + USB_Files[0] + "/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/" + self.Name + ".mp3"):
                    shutil.copy("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/" + self.Name + ".mp3", self.m_user + "/" + USB_Files[0] + "/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/" + self.Name + ".mp3")
                    self.tunes.append(vpath)
                    upath = self.m_user + "/" + USB_Files[0] + "/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/" + self.Name + ".mp3"
                    with open(self.m3u_dir + self.m3u_def + ".m3u", 'a') as f:
                        f.write(upath + "\n")
                    self.tunes.sort()
                    self.tunes.append(vpath)
                if os.path.exists("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/" + self.Name + ".txt"):
                    if not os.path.exists(self.m_user + "/" + USB_Files[0] + "/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/" + self.Name + ".txt"):
                        shutil.copy("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/" + self.Name + ".txt", self.m_user + "/" + USB_Files[0] + "/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/" + self.Name + ".txt")
                time.sleep(1)
        # ==============================================================================================================
        if self.trace > 0:
            print ("Copy Record")
        self.total_record = 0
        rems = glob.glob("/run/shm/music/*/*/*/*/*.mp3")
        for x in range(0,len(rems)):
            if self.usave == 1:
                shutil.copy(rems[x],self.h_user + "/Music/")
            os.remove(rems[x])
        rems = glob.glob("/run/shm/music/*/*/*.cue")
        for x in range(0,len(rems)):
            os.remove(rems[x])
        if self.trace > 0:
            print ("Copy Record - add to Tunes")
        tpath = self.Radio_Stns[self.Radio] + "^Radio_Recordings^" + self.Name + ".mp3^music^run^shm^None"
        self.tunes.append(tpath)
        self.tunes.sort()
        if self.trace > 0:
            print ("Copy Record - find track_no")
        stop = 0
        k = 0
        while stop == 0 and k < len(self.tunes):
            if tpath == self.tunes[k]:
                stop = 1
                self.track_no = k
            k +=1
        if self.trace > 0:
            print ("Copy Record - clear display " + str(self.track_no))
        if self.imgxon == 1:
            self.imgx.after(100, self.imgx.destroy())
            self.imgxon = 0
            if cutdown == 1:
                self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=20,bg='white',   anchor="w", borderwidth=2, relief="groove")
                self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                self.Disp_album_name = tk.Label(self.Frame10, height=1, width=20,bg='white', anchor="w", borderwidth=2, relief="groove")
                self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
            elif cutdown == 4:
                self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=30,bg='white',   anchor="w", borderwidth=2, relief="groove")
                self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 3)
                self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                self.Disp_album_name = tk.Label(self.Frame10, height=2, width=30,bg='white', anchor="w", borderwidth=2, relief="groove")
                self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
            elif cutdown == 5:
                self.Disp_artist_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 3)
                self.Disp_album_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                self.Disp_album_name.grid(row = 3, column = 1, columnspan = 3)
                self.Disp_track_name = tk.Label(self.Frame10, height=2, width=25,bg='white',font = self.helv01, anchor="w", borderwidth=2, relief="groove")
                self.Disp_track_name.grid(row = 4, column = 1, columnspan = 3)
        if self.cutdown != 7 and self.cutdown != 8:
            self.Disp_album_name.config(text ="")
            self.Disp_track_name.config(text ="")
        else:
            self.Disp_album_name.set("")
            self.Disp_track_name.set("")
        if self.cutdown != 1 and self.cutdown != 5 and self.cutdown != 6:
            self.Disp_Name_m3u.delete('1.0','20.0')
        if self.trace > 0:
            print ("EXIT Copy Record - " + str(self.track_no))
        self.RadioX()

    def Get_track(self,x):
        #get track name, if available.
        if self.trace > 2:
            print ("Get Track")
        # determine max recording time based on stream rate
        if time.monotonic() - self.timer7 >= 30 and self.ramtest == 1 and self.Radio_RON == 1:
            self.ramtest = 0
            st = os.statvfs("/run/shm/")
            self.freeram2 = (st.f_bavail * st.f_frsize)/1100000
            self.max_record = int(int((self.freeram1 - self.ram_min) / ((self.freeram1 - self.freeram2) * 2)) * 1.9)
            self.max_record = min(self.max_record,990)
            if self.record_time > self.max_record and self.max_record > 0:
                self.record_time = self.max_record
                self.total_record = self.max_record * 60
                self.record_time_min = self.record_time * 60
                t_minutes = int(self.total_record // 60)
                t_seconds = int (self.total_record - (t_minutes * 60))
                self.Disp_track_len.config(text ="%03d:%02d" % (t_minutes, t_seconds % 60))
                self.record_current = int((self.total_record - (time.monotonic() - self.rec_begin))/60)
                self.Button_Pause.config(fg = "yellow", bg = "red", text = str(self.stop_record)[11:16])
                now = datetime.datetime.now()
                self.stop_record = now + timedelta(minutes=self.record_time)
                if (self.cutdown >= 7 or self.cutdown == 0) and self.synced == 1:
                    self.L6.config(text = "(" + str(self.stop_record)[11:16] + ")")
            
        # backlight off
        if time.monotonic() - self.light_on > self.light and (self.HP4_backlight == 1 or self.LCD_backlight == 1 or self.Pi7_backlight == 1):
            if self.HP4_backlight == 1 or self.LCD_backlight == 1:
                self.LCD_pwm.value = self.dim
            if self.Pi7_backlight == 1:
                os.system("rpi-backlight -b 0")
            
        self.Radio_Stns2 = self.Radio_Stns[self.Radio]
        track = sorted(glob.glob("/run/shm/music/" + self.Radio_Stns2 + "/Radio_Recordings/*/incomplete/*.mp3"),key = os.path.getmtime, reverse=True)
        if self.trace > 2:
            print ("Get Track",track[0])
        self.counter = 0
        self.track_nameX = [" - .mp3"]
        self.tname = re.sub("[^a-zA-Z0-9- &!()',.]+", '',self.tname)
        if self.tname == "":
            self.tname= "Unknown"
        if self.Radio_ON == 1 and self.Radio_Stns[self.Radio + 2]  > 0:
            if self.cutdown >= 7:
                self.Disp_track_name.set(self.tname)
                if self.imgxon == 0:
                    self.Disp_album_name.set("Radio")
            else:
                self.Disp_track_name.config(text = self.tname)
                if self.imgxon == 0:
                    self.Disp_album_name.config(text = "Radio")
        elif self.Radio_ON == 1:
            self.tname = "Unknown" 
            self.copy = 0
            if self.cutdown >= 7:
                self.Disp_track_name.set(self.tname)
            else:
                self.Disp_track_name.config(text = self.tname)
        if len(track) > 0 and self.Radio_ON == 1:
            self.counter = track[0].count('/')
            self.track_nameX = track[0].split("/",self.counter)
            if self.track_nameX[self.counter][0:3] != " - ":
                self.tname = self.track_nameX[self.counter][:-4]
                vv = 0
                if self.oldtrack2 != self.tname and self.trace == 2:
                    print("1",self.tname)
                    self.oldtrack2 = self.tname
                    vv = 1
                self.tname = re.sub("[^a-zA-Z0-9- &!()',.]+", '',self.tname)
                if self.tname == "":
                    self.tname= "Unknown"
                if vv == 1 and self.trace == 2:
                    print("2",self.tname)
                if self.cutdown >= 7:
                    self.Disp_track_name.set(self.tname)
                else:
                    self.Disp_track_name.config(text = self.tname)
                if self.tname != self.old_tname and self.Radio_RON == 1:
                    with open("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/" + self.Name + ".txt", "a") as f:
                        f.write("%03d:%02d" % (self.r_minutes, self.r_seconds % 60) + " " + self.tname + "\n")
                    self.old_tname = self.tname
            elif self.track_nameX[self.counter][0:3] == " - " and self.track_nameX[self.counter] != " - .mp3":
                self.tname = self.track_nameX[self.counter][:-4]
                self.tname = re.sub("[^a-zA-Z0-9- &!()',.]+", '',self.tname)
                if self.tname == "":
                    self.tname= "Unknown"
                if self.cutdown >= 7:
                    self.Disp_track_name.set(self.tname[3:])
                else:
                    self.Disp_track_name.config(text = self.tname[3:])
                if self.tname != self.old_tname and self.Radio_RON == 1:
                    with open("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/" + self.Name + ".txt", "a") as f:
                        f.write("%03d:%02d" % (self.r_minutes, self.r_seconds % 60) + " " + self.tname[3:] + "\n")
                    self.old_tname = self.tname
            else:
                self.tname = "Unknown"
                if self.cutdown >= 7:
                    self.Disp_track_name.set(self.tname)
                else:
                    self.Disp_track_name.config(text = self.tname)
        elif self.Radio_RON == 1 :
            if self.rotary_pos == 0:
                messagebox.showinfo("WARNING!","NOT RECORDING" + "\n" + "Check Recordable")
                self.Button_Pause.config(fg = "black",bg = "light blue",text = "RECORD")
            else:
                print("WARNING!","NOT RECORDING - Check Recordable")
                print("x",self.rot_pos)
                if self.rot_pos == 9:
                    self.Button_Pause.config(fg = "black",bg = "yellow",text = "RECORD")
                else:
                    self.Button_Pause.config(fg = "black",bg = "light blue",text = "RECORD")
            self.rems = glob.glob("/run/shm/music/*/*/*.mp3")
            for x in range(0,len(self.rems)):
                os.remove(self.rems[x])
            self.rems2 = glob.glob("/run/shm/music/*/*/*/*/*.mp3")
            for x in range(0,len(self.rems2)):
                os.remove(self.rems2[x])
            self.rems3 = glob.glob("/run/shm/music/*/*/*.cue")
            for x in range(0,len(self.rems3)):
                os.remove(self.rems3[x])
            if self.Radio_ON == 1 and self.Radio_RON == 1 and self.record == 1:
                self.Radio_RON = 0
                self.L4.config(text = "")
                self.Disp_track_len.config(text ="     ")
                self.Disp_played.config(text ="     ")
                self.Disp_track_no.config(text = "")
                if self.cutdown != 1 and self.cutdown != 4 and  self.cutdown != 5:
                    if self.touchscreen == 1:
                        self.L8.config(text = "")
                    if self.cutdown != 3 and self.cutdown != 2:
                        self.L3.config(text = "")
                        self.L1.config(text = "")
                    self.Button_Radio.config(bg = "orange",fg = "black", text = "STOP Radio")
                else:
                    self.Button_Radio.config(bg = "orange",fg = "black", text = "STOP")
                if self.cutdown != 1:
                    self.Button_Radio.config(bg = "orange",fg = "black", text = "STOP Radio")
                if self.imgxon == 0:
                    self.Disp_album_name.config(text = "")
                if self.cutdown >= 7:
                    self.Disp_track_name.set("")
                else:
                    self.Disp_track_name.config(text = "")

        #==Copy Individual Tracks to USB===========================================================================
        rems = glob.glob("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/*/*.mp3" )
        USB_Files = []
        USB_Files = (os.listdir(self.m_user + ""))
        if len(rems) > 0 and len(USB_Files) > 0 and self.Radio_RON == 1 and self.usave == 1 and self.Radio_Stns[self.Radio + 2] > 1:
            self.copy = 1
            USB_Files = []
            USB_Files = (os.listdir(self.m_user + ""))
            if self.trace > 0:
                print("usbs",USB_Files)
            st1 = os.statvfs(self.m_user + "/" + USB_Files[0])
            free = (st1.f_bavail * st1.f_frsize)/1100000
            try:
                if len(USB_Files) > 1:
                    st2 = os.statvfs(self.m_user + "/" + USB_Files[1])
                    free2 = (st2.f_bavail * st2.f_frsize)/1100000
                    if free2 > free:
                        free = free2
                        del USB_Files[0]
                        if len(USB_Files) > 1:
                            st3 = os.statvfs(self.m_user + "/" + USB_Files[1])
                            free3 = (st3.f_bavail * st3.f_frsize)/1100000
                            if free3 > free:
                                free = free3
                                del USB_Files[0]
            except:
                pass
            if self.cutdown == 0 or self.cutdown == 3 or self.cutdown >= 7:
                self.Disp_Drive.config(text = USB_Files[0])
            if self.cutdown == 6:
                self.Disp_Total_tunes.config(text = "USB: " + str(int(free)))
            if self.cutdown != 4 and self.cutdown != 5 and self.cutdown != 6 and self.cutdown != 1:
                self.Disp_Total_Plist.config(text = str(int(free)) + "MB")
            if self.trace > 0:
                print ("Copy Indies")
            for v in range(0,len(rems)):
                count = rems[v].count('/')
                data = rems[v].split('/',count)
                trame = data[count]
                if self.trace > 0:
                    print(trame)
                if trame[0:10] != 'Commercial' and trame[0:6] != ' - AD ' and trame[0:8] != ' - STOP ' and trame[0:9] != ' - START ':
                    if self.Radio_Stns[self.Radio + 2] == 2 or self.Radio_Stns[self.Radio + 2] == 3:
                        count2 = trame.count(' - ')
                        names = trame.split(' - ',count2)
                    elif self.Radio_Stns[self.Radio + 2] == 4:
                        count2 = trame.count(' by ')
                        names = trame.split(' by ',count2)
                        
                    if self.Radio_Stns[self.Radio + 2] == 2 :
                        artist = names[0]
                        track  = names[count2]
                        mp = track[-4:]
                        track = track[:-4]
                    elif self.Radio_Stns[self.Radio + 2] == 3 or self.Radio_Stns[self.Radio + 2] == 4:
                        artist = names[count2][:-4]
                        track  = names[0]
                        mp = names[count2][-4:]
                    artist = re.sub("[^a-zA-Z0-9- &!()',.]+", '',artist)
                    if artist == "":
                        artist = "Unknown"
                    track = re.sub("[^a-zA-Z0-9- &!()',.]+", '',track)
                    if track == "" or track == "-" or track == " - ":
                        now = datetime.datetime.now()
                        track = now.strftime("%y%m%d_%H%M%S")
                    track += mp
                    if self.trace > 0:
                        print(track,mp)
                    stn1 = self.m_user + "/" + USB_Files[0] + "/" + artist
                    stn2 = self.m_user + "/" + USB_Files[0] + "/" + artist + "/Radio_Recordings/"
                    if track != ".mp3" and artist !="":
                        if not os.path.exists(stn1):
                            os.system ("mkdir " + "'" + stn1 + "'")
                            time.sleep(1)
                        if not os.path.exists(stn2):
                            os.system ("mkdir " + "'" + stn2 + "'")
                            time.sleep(1)
                        vpath = artist + "^Radio_Recordings^" + track + "^" + USB_Files[0] + "^media^" + os.getlogin( ) + "^" + self.genre_name
                        if os.path.exists(self.m_user + "/" + USB_Files[0] + "/" + artist + "/Radio_Recordings/"):
                            if self.trace > 0:
                                print("Copy Indies 1")
                                print(rems[v], self.m_user + "/" + USB_Files[0] + "/" + artist + "/Radio_Recordings/")
                            if not os.path.exists(self.m_user + "/" + USB_Files[0] + "/" + artist + "/Radio_Recordings/" + track):
                                if self.trace > 0:
                                    print("Copy Indies 2",rems[v], self.m_user + "/" + USB_Files[0] + "/" + artist + "/Radio_Recordings/" + track)
                                    print(rems[v], self.m_user + "/" + USB_Files[0] + "/" + artist + "/Radio_Recordings/" + track)
                                shutil.copy(rems[v], self.m_user + "/" + USB_Files[0] + "/" + artist + "/Radio_Recordings/" + track)
                                self.tunes.append(vpath)
                                upath = self.m_user + "/" + USB_Files[0] + "/" + artist + "/Radio_Recordings/" + track
                                with open(self.m3u_dir + self.m3u_def + ".m3u", 'a') as f:
                                    f.write(upath + "\n")
                                with open("/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings/" + self.Name + ".txt", "a") as f:
                                    f.write("000:00 " + artist + "/Radio_Recordings/" + track + "\n")
                                self.tunes.sort()
                                time.sleep(1)
                                tcount = len(glob.glob(self.m_user + "/" + USB_Files[0] + "/" + artist + "/Radio_Recordings/*.mp3"))
                                try: 
                                    tags = ID3(self.m_user + "/" + USB_Files[0] + "/" + artist + "/Radio_Recordings/" + track)
                                except ID3NoHeaderError:
                                    tags = ID3()
                                tags["TIT2"] = TIT2(encoding=1, text=track[:-4])
                                tags["TALB"] = TALB(encoding=1, text=u'Radio_Recordings')
                                tags["TPE2"] = TPE2(encoding=1, text=artist)
                                tags["TPE1"] = TPE1(encoding=1, text=artist)
                                now = datetime.datetime.now()
                                Year = now.strftime("%Y")
                                tags["TDRC"] = TDRC(encoding=1, text=Year)
                                tags["TENC"] = TDRC(encoding=1, text="")
                                tags["TRCK"] = TRCK(encoding=1, text=str(tcount))
                                tags["TXXX:Encoded by"] = TXXX(encoding=0, text="")
                                tags.save(self.m_user + "/" + USB_Files[0] + "/" + artist + "/Radio_Recordings/" + track)
                                


        # ======================================================================================================================
        rems = glob.glob("/run/shm/music/*/*/*/*.mp3")
        for x in range(0,len(rems)):
            os.remove(rems[x])

    def PopupInfo(self):
        # show info.txt
        if self.Radio_ON == 0 or self.Radio_RON == 1:
            ipath = ""
            if self.Radio_RON == 1:
                ipath = "/run/shm/music/" + self.Radio_Stns[self.Radio] + "/Radio_Recordings"
            elif len(self.tunes) > 0:
                ipath = "/" + self.drive_name1 + "/" + self.drive_name2 + "/"
                if self.drive_name[-1] == "*":
                    ipath = ipath + self.drive_name[:-1] + "/" + self.artist_name + " - " + self.album_name
                else:
                    ipath = ipath + self.drive_name + "/" + self.artist_name + "/" + self.album_name
            ipath = ipath + "/"
            infofile = ""
            filename = "info.txt"
            # Look for info.txt
            if os.path.exists(ipath + filename):
                infofile = filename
            else:
                # Look for other txt files
                txts = glob.glob(ipath + "/*.txt")
                txts.sort(reverse=True)
                for txt in txts:
                    filename = os.path.split(txt)[1]
                    if "fing" in filename or "md5" in filename or "ffp" in filename or self.track_name in filename:
                        infofile = txts[0]
                    elif "album" in filename:
                        infofile = "album.txt"
                    else:
                        infofile = filename
                        break
            if infofile == '':
                m3us = glob.glob(ipath + "/*.m3u")
                if len(m3us) > 0:
                    for txt in m3us:
                        filename = os.path.split(txt)[1]
                        infofile = m3us[0]
                
            if infofile != '':
                popup = Tk()
                if (self.cutdown > 4 and self.cutdown < 8) or self.cutdown == 0:
                    popup.geometry("700x400")
                    STxtBox = ScrolledText(popup, height=700, width=400)
                elif self.cutdown == 4:
                    popup.geometry("480x320")
                    STxtBox = ScrolledText(popup, height=480, width=320)
                elif self.cutdown == 3:
                    popup.geometry("480x800")
                    STxtBox = ScrolledText(popup, height=480, width=800)
                elif self.cutdown == 2:
                    popup.geometry("640x480")
                    STxtBox = ScrolledText(popup, height=640, width=480)
                elif self.cutdown == 1:
                    popup.geometry("320x240")
                    STxtBox = ScrolledText(popup, height=320, width=240)
                elif self.cutdown == 8 :
                    popup.geometry("800x700")
                    STxtBox = ScrolledText(popup, height=800, width=700)
                STxtBox.pack(expand = 0,fill = BOTH)
                popup.title(infofile)
                with open(ipath + filename, "r", encoding="Latin-1") as f:
                    for line in f:
                        STxtBox.insert(END, line)
                f.close()
                popup.after(10000, popup.destroy)
                    
    def Shutdown(self):
        if (self.shuffle_on == 1 and self.sleep_time > 0 and self.play == 0) or self.Shutdown_exit == 0:
            if self.rotary_pos == 1 or self.rotary_vol == 1:
                os.system("sudo shutdown -h now")
            self.exit()
            
def main():
    global cutdown,fullscreen,scr_width,scr_height
    print ("Loading...")
    root = Tk()
    root.title("Pi MP3 Player v" + str(version))
    if cutdown == 1:
        root.geometry("320x240")
    elif cutdown == 2:
        root.geometry("656x416")
    elif cutdown == 3:
        root.geometry("480x800")
    elif cutdown == 4:
        root.geometry("480x320")
    elif cutdown == 5:
        root.geometry("800x480")
    elif cutdown == 8:
        root.geometry("1280x720")
    else:
        root.geometry("800x480")
    if root.winfo_screenwidth() == 320 and root.winfo_screenheight() == 240:
        root.geometry("320x240")
        cutdown = 1
    elif root.winfo_screenwidth() == 480 and root.winfo_screenheight() == 320:
        root.geometry("480x320")
        cutdown = 4
    elif root.winfo_screenwidth() == 656 and root.winfo_screenheight() == 416:
        root.geometry("656x416")
        cutdown = 2
    elif root.winfo_screenwidth() == 640 and root.winfo_screenheight() == 480:
        root.geometry("640x480")
        cutdown = 2
    if fullscreen == 1:
        root.wm_attributes('-fullscreen','true')
    scr_width  = root.winfo_screenwidth()
    scr_height = root.winfo_screenheight()
    ex = MP3Player()
    root.mainloop() 

if __name__ == '__main__':
    main() 
