#!/usr/bin/env python3
import tkinter as tk
from tkinter import *
from tkinter import ttk
import os, sys
import time
import datetime
import subprocess
import signal
import random
from random import shuffle
import glob
from mutagen.mp3 import MP3
import alsaaudio
import math
from PIL import ImageTk, Image
import RPi.GPIO as GPIO
from mplayer import Player
Player.introspect()
player = Player()

# Pi_MP3_Player v15.03

class MP3Player(Frame):
    
    def __init__(self):
        super().__init__() 
        self.initUI()
        
    def initUI(self):
        self.master.bind("<Button-1>", self.Wheel_Opt_Button)
        self.mp3_search = "/*/*/*/*/*/*.mp3"    # search criteria for mp3s (/*/*/USBDrive Name/Artist Name/Album Name/Tracks.mp3)
        self.m3u_def    = "ALLTracks"           # name of default .m3u. Limit to 9 characters.
        self.m3u_dir    = "/home/pi/Documents/" # where .m3us are stored
        self.mp3_jpg    = "mp3.jpg"             # logo including the 'wheel', when inactive
        self.mp3c_jpg   = "mp3c.jpg"            # blue logo including the 'wheel, when active'
        self.Disp_max_time  = 120               # in minutes. Limits time taken to determine playlist length.
        self.volume         = 65                # range 0 - 100
        self.gapless_time   = 2                 # in seconds. Defines length of track overlap.
        self.voldn          = 36                # external volume down gpio input
        self.volup          = 40                # external volume up gpio input
        self.stop_start     = 38                # external start / stop play gpio input
        self.repeat         = 0
        self.play           = 0
        self.track_no       = 0
        self.sleep_time     = 0
        self.sleep_time_min = 0
        self.mute           = 0
        self.shuffle_on     = 0
        self.sorted         = 0
        self.begin          = time.time()
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
        self.BT             = 0

        # check for audio mixers
        print (alsaaudio.mixers())
        for mixername in alsaaudio.mixers():
            if str(mixername) == "PCM" or str(mixername) == "Master":
                self.m = alsaaudio.Mixer(mixername)
            else:
                self.m = alsaaudio.Mixer(alsaaudio.mixers()[0])
                self.version = 1
                self.BT      = 1
                self.gapless = 1
        self.m.setvolume(self.volume)
        self.test            = 0
        self.counter5        = 0
        
        # check for HyperPixel4 LCD and if so disable GPIO.
        if os.path.exists ('/sys/devices/platform/i2c@0'): 
            self.gpio_enable = 0
        else:
            self.gpio_enable = 1
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BOARD)
            GPIO.setwarnings(False)
            GPIO.setup(self.voldn,GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.stop_start,GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.volup,GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # setup GUI
        self.Frame10 = tk.Frame(width=800, height=480)
        self.Frame10.grid_propagate(0)
        self.Frame10.grid(row=0, column=0)
        
        self.Button_Start = tk.Button(self.Frame10, text = "PLAY Playlist", bg = "green",fg = "white",width = 7, height = 2,font = 18, command = self.Play, wraplength=80, justify=CENTER)
        self.Button_Start.grid(row = 0, column = 0, padx = 10,pady = 0)
        if self.BT == 0:
            self.Button_Pause = tk.Button(self.Frame10, text = "Pause",bg = "light blue", width = 7, height = 2,command=self.Pause, wraplength=80, justify=CENTER)
            self.Button_Pause.grid(row = 0, column = 1, padx = 0,pady = 0)
        self.Button_Stop =  tk.Button(self.Frame10, text = "STOP",fg = "white",width = 7, height = 2,font = 20,command = self.Stop_Play)
        self.Button_Stop.grid(row = 0, column = 2)
        if self.BT == 0:
            self.Button_Pstart = tk.Button(self.Frame10, text = "Gapless OFF", fg = "white", width = 7, height = 2,command=self.Gapless, wraplength=80, justify=CENTER)
            self.Button_Pstart.grid(row = 0, column = 3,pady = 0)
        self.Button_TAlbum = tk.Button(self.Frame10, text = "Play Album", bg = "light blue",fg = "blue", width = 7, height = 2,command=self.Play_Album, wraplength=80, justify=CENTER)
        self.Button_TAlbum.grid(row = 0, column = 4,pady = 0)
        B1 =  tk.Button(self.Frame10, text = " < Vol ",    bg = "yellow",width = 7, height = 2,command = self.volume_DN)
        B1.grid(row = 0, column = 5)
        self.Button_volume = tk.Button(self.Frame10, text = self.volume, bg = "white",fg = "blue",width = 1, height = 2,command = self.Mute)
        self.Button_volume.grid(row = 0, column = 6,pady = 2)
        B2 =  tk.Button(self.Frame10, text = "Vol >",      bg = "yellow",width = 7, height = 2,command = self.volume_UP)
        B2.grid(row = 0, column = 7)
        self.B3 =  tk.Button(self.Frame10, text = "< P-list",   bg = "light blue",width = 7, height = 1,command = self.Prev_m3u,repeatdelay=1000, repeatinterval=500)
        self.B3.grid(row = 1, column = 0)
        self.B4 =  tk.Button(self.Frame10, text = "P-list >",   bg = "light blue",width = 7, height = 1,command = self.Next_m3u,repeatdelay=1000, repeatinterval=500)
        self.B4.grid(row = 1, column = 7)
        self.B5 =  tk.Button(self.Frame10, text = "< Artist",   bg = "light blue",fg = "red",width = 7, height = 2,command = self.Prev_Artist,repeatdelay=1000, repeatinterval=500)
        self.B5.grid(row = 2, column = 0)
        self.B6 =  tk.Button(self.Frame10, text = "Artist >",   bg = "light blue",width = 7, height = 2,command = self.Next_Artist,repeatdelay=1000, repeatinterval=500)
        self.B6.grid(row = 2, column = 7)
        self.B7 =  tk.Button(self.Frame10, text = "< Album",    bg = "light blue",width = 7, height = 2,command = self.Prev_Album,repeatdelay=1000, repeatinterval=500)
        self.B7.grid(row = 3, column = 0)
        self.B8 =  tk.Button(self.Frame10, text = "Album >",     bg = "light blue",width = 7, height = 2,command = self.Next_Album,repeatdelay=1000, repeatinterval=500)
        self.B8.grid(row = 3, column = 7)
        self.B9 =  tk.Button(self.Frame10, text = "< Track",    bg = "light blue",width = 7, height = 2,command = self.Prev_Track,repeatdelay=1000, repeatinterval=500)
        self.B9.grid(row = 4, column = 0)
        self.B10 = tk.Button(self.Frame10, text = "Track >",    bg = "light blue",width = 7, height = 2,command = self.Next_Track,repeatdelay=1000, repeatinterval=500)
        self.B10.grid(row =4, column = 7)
        self.B13 = tk.Button(self.Frame10, text = "Next A-Z",   width = 7, height = 1,bg = "light blue",command=self.nextAZ,repeatdelay=250, repeatinterval=500)
        self.B13.grid(row = 5, column = 7, pady = 1)
        self.load = Image.open(self.mp3c_jpg)
        self.renderc = ImageTk.PhotoImage(self.load)
        self.img = tk.Label(self.Frame10, image = self.renderc)
        self.img.grid(row = 5, column = 0, columnspan = 2, rowspan = 5, pady = 2)
        self.B11 = tk.Button(self.Frame10, text = " RELOAD " + self.m3u_def ,width = 7, height = 2, bg = "#c5c",command = self.RELOAD_List, wraplength=80, justify=CENTER)
        self.B11.grid(row = 7, column = 2,padx = 10, pady = 0)
        B12 = tk.Button(self.Frame10, text = "QUIT",bg = "light blue",  width = 7, height = 2,command=self.exit).grid(row = 9, column = 5, columnspan = 2)
        B14 = tk.Button(self.Frame10, text = "Shutdown",   bg = "gray",width = 7, height = 2,command = self.Shutdown).grid(row = 9, column = 7, padx = 10)
        self.B15 = tk.Button(self.Frame10, text = "Add track to FAV .m3u  " ,width = 7, height = 2, bg = "light green",command = self.FAV_List, wraplength=80, justify=CENTER)
        self.B15.grid(row = 7, column = 3)
        self.Button_Shuffle = tk.Button(self.Frame10, text = "Shuffle P-LIST OFF", bg = "light blue", fg = "blue",width = 7, height = 2,command = self.Shuffle_Tracks, wraplength=80, justify=CENTER)
        self.Button_Shuffle.grid(row = 7, column = 5, columnspan = 2)
        self.Button_AZ_artists = tk.Button(self.Frame10, text = "A-Z Sort OFF",bg = "light blue", fg = "blue",width = 7, height = 2,command = self.AZ_Tracks, wraplength=80, justify=CENTER)
        self.Button_AZ_artists.grid(row = 7, column = 7)
        self.Button_Sleep = tk.Button(self.Frame10, text = "SLEEP", bg = "light blue",width = 7, height = 2,command = self.sleep,repeatdelay=1000, repeatinterval=500)
        self.Button_Sleep.grid(row = 9, column = 2, padx = 0)
        self.Button_Track_m3u = tk.Button(self.Frame10, text = "ADD track   to .m3u", bg = "light green",width = 7, height = 2,command = self.Track_m3u, wraplength=80, justify=CENTER)
        self.Button_Track_m3u.grid(row = 8, column = 2)
        self.Button_Artist_m3u = tk.Button(self.Frame10, text = "ADD artist   to .m3u", bg = "light green",width = 7, height = 2,command = self.Artist_m3u, wraplength=80, justify=CENTER)
        self.Button_Artist_m3u.grid(row = 8, column = 5, columnspan = 2)
        self.Button_Album_m3u = tk.Button(self.Frame10, text = "ADD album   to .m3u", bg = "light green",width = 7, height = 2,command = self.Album_m3u, wraplength=80, justify=CENTER)
        self.Button_Album_m3u.grid(row = 8, column = 4)
        self.Button_PList_m3u = tk.Button(self.Frame10, text = "ADD P-list   to .m3u", bg = "light green",width = 7, height = 2,command = self.PList_m3u, wraplength=80, justify=CENTER)
        self.Button_PList_m3u.grid(row = 8, column = 7)
        self.Button_DELETE_m3u = tk.Button(self.Frame10, text = "DEL .m3u", bg = "#191",width = 7, height = 1,command = self.DelPL_m3u)
        self.Button_DELETE_m3u.grid(row = 9, column = 4, padx = 10)
        self.Button_repeat = tk.Button(self.Frame10, text = "Repeat OFF", bg = "light blue",fg = "blue",width = 7, height = 2,command = self.Repeat, wraplength=80, justify=CENTER)
        self.Button_repeat.grid(row = 7, column = 4)
        self.Disp_sleep = tk.Button(self.Frame10, text = "OFF", bg = "white",fg = "blue",width = 2, height = 2,command = self.sleep_off)
        self.Disp_sleep.grid(row = 9, column = 3, sticky = W)
    
        L1 = tk.Label(self.Frame10, text="Track:")
        L1.grid(row = 5, column = 2, sticky = W)
        L2 = tk.Label(self.Frame10, text="of")
        L2.grid(row = 5, column = 3, sticky = W, padx = 16)
        L3 = tk.Label(self.Frame10, text="Played:")
        L3.grid(row = 6, column = 2, sticky = W)
        L4 = tk.Label(self.Frame10,text="of")
        L4.grid(row = 6, column = 3, sticky = W, padx = 16)
        L5 = tk.Label(self.Frame10, text="Drive :")
        L5.grid(row = 5, column = 4, sticky = W,padx = 17)
        self.L6 = tk.Label(self.Frame10, text="Playlist :")
        self.L6.grid(row = 6, column = 4, sticky = E)
        L7 = tk.Label(self.Frame10, text="mins")
        L7.grid(row = 9, column = 3, sticky = E, padx = 15) 
        L8 = tk.Label(self.Frame10, text=".m3u")
        L8.grid(row = 8, column = 3, sticky = S)
        self.L9 = tk.Label(self.Frame10, text=" ")
        self.L9.grid(row = 6, column = 6, sticky = E)
        
        self.Disp_plist_name = tk.Label(self.Frame10, height=1, width=57,bg='white',   anchor="w", borderwidth=2, relief="groove")
        self.Disp_plist_name.grid(row = 1, column = 1, columnspan = 6)
        self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
        self.Disp_artist_name = tk.Label(self.Frame10, height=1, width=50,bg='white', font = 40, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
        self.Disp_artist_name.grid(row = 2, column = 1,columnspan = 6)
        self.Disp_album_name = tk.Label(self.Frame10, height=1, width=50,bg='white',font = 40, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
        self.Disp_album_name.grid(row = 3, column = 1, columnspan = 6)
        self.Disp_track_name = tk.Label(self.Frame10, height=1, width=50,bg='white',font = 40, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
        self.Disp_track_name.grid(row = 4, column = 1, columnspan = 6)
        self.Disp_track_no = tk.Label(self.Frame10, height=1, width=5,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_track_no.grid(row = 5, column = 2, sticky = E)
        self.Disp_Total_tunes = tk.Label(self.Frame10, height=1, width=5,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_Total_tunes.grid(row = 5, column = 3, sticky = E)
        self.Disp_played = tk.Label(self.Frame10, height=1, width=5,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_played.grid(row = 6, column = 2, sticky = E)
        self.Disp_track_len = tk.Label(self.Frame10, height=1, width=5,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_track_len.grid(row = 6, column = 3, sticky = E)
        self.Disp_Drive = tk.Label(self.Frame10, height=1, width=17,bg= 'white', anchor="w", borderwidth=2, relief="groove")
        self.Disp_Drive.grid(row = 5, column = 4, columnspan = 3, sticky = E, padx = 15)
        self.Disp_Name_m3u = tk.Text(self.Frame10,height = 1, width=12,bg= 'white', borderwidth=2, relief="groove")
        self.Disp_Name_m3u.grid(row = 8, column = 3, sticky = N, pady = 10)
        self.Disp_Total_Plist = tk.Label(self.Frame10, height=1, width=7,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_Total_Plist.grid(row = 6, column = 5, columnspan = 2, sticky = W)

        self.s = ttk.Style()
        self.s.theme_use('default')
        self.s.layout("LabeledProgressbar",[('LabeledProgressbar.trough',
           {'children': [('LabeledProgressbar.pbar',{'side': 'left', 'sticky': 'ns'}),("LabeledProgressbar.label",{"sticky": ""})],'sticky': 'nswe'})])
        self.s.configure("LabeledProgressbar", text="0 %      ", background='red')
        self.progress=ttk.Progressbar(self.Frame10,style="LabeledProgressbar",orient=HORIZONTAL,length=90,mode='determinate')
        self.progress.grid(row = 6, column = 7)
        
        if os.path.exists(self.mp3_jpg):
            self.load = Image.open(self.mp3_jpg)
            self.render = ImageTk.PhotoImage(self.load)
        self.Check_switches()
        
        # check default .m3u exists, if not then make it
        if not os.path.exists(self.que_dir):
            self.RELOAD_List()
        else:
            # if it does exist then load default .m3u
            Tracks = []
            with open(self.que_dir,"r") as textobj:
               line = textobj.readline()
               while line:
                  Tracks.append(line.strip())
                  line = textobj.readline()
            self.tunes = []
            for counter in range (0,len(Tracks)):
                z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2)

            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.total = 0
            self.Time_Left_Play()

    def Show_Track(self):
        if len(self.tunes) > 0:
            self.Disp_track_no.config(text =self.track_no+1)
            self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2  = self.tunes[self.track_no].split('^')
            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name, self.artist_name, self.album_name, self.track_name)
            self.Disp_artist_name.config(text =self.artist_name)
            self.Disp_album_name.config(text =self.album_name)
            self.Disp_track_name.config(text =self.track_name[:-4])
            self.Disp_played.config(text ="")
            self.Disp_Drive.config(fg = 'black')
            self.Disp_Drive.config(text = "/" + self.drive_name1 + "/" + self.drive_name2  + "/" + self.drive_name)
            self.render2 = ""
            path = "/" + self.drive_name1 + "/" +self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
            pictures = glob.glob(path)
            if len(pictures) > 0: # and self.wheel == 0:
                if len(pictures) > 1:
                    r = random.randrange(len(pictures))
                    self.image = pictures[r]
                else:
                    self.image = pictures[0]
                self.load = Image.open(self.image)
                self.load = self.load.resize((218, 218), Image.ANTIALIAS) 
                self.render2 = ImageTk.PhotoImage(self.load)
                self.img.config(image = self.render2)
            elif self.stopstart == 0:
                self.img.config(image = self.renderc)
            else:
                self.img.config(image = self.render)
            if os.path.exists(self.track):
                audio = MP3(self.track)
                self.track_len = audio.info.length
                minutes = int(self.track_len // 60)
                seconds = int (self.track_len - (minutes * 60))
                self.Disp_track_len.config(text ="%02d:%02d" % (minutes, seconds % 60))
            else:
                self.Disp_Drive.config(fg = 'red')
                if self.m3u_no != 0:
                    self.Disp_Drive.config(text = "MISSING")
            self.Check_Sleep()
            
    def Play(self):
        # check for audio mixers
        print (alsaaudio.mixers())
        for mixername in alsaaudio.mixers():
            if str(mixername) == "PCM" or str(mixername) == "Master":
                self.m = alsaaudio.Mixer(mixername)
            else:
                self.m = alsaaudio.Mixer(alsaaudio.mixers()[0])
                self.version = 1
                self.BT      = 1
                self.gapless = 1
        self.m.setvolume(self.volume)
        if  self.album_start == 0:
            self.stopstart = 1
            self.play = 0
            self.start2 = time.time()
            self.wheel = 0
            if self.BT == 0:
                player.time_pos
            self.Start_Play()

    def Wheel_Opt_Button(self,u):
        if os.path.exists(self.mp3_jpg):
            if self.gapless == 0 and self.paused == 0:
                self.img.config(image = self.renderc)
            else:
                self.img.config(image = self.render)
            self.timer4 = time.time()
        x = self.master.winfo_pointerx()
        y = self.master.winfo_pointery()
        abs_x = self.master.winfo_pointerx() - self.master.winfo_rootx()
        abs_y = self.master.winfo_pointery() - self.master.winfo_rooty()
        x2 = abs_x - 114
        y2 = abs_y - 370
        if math.sqrt((x2*x2)+ (y2*y2)) < 30 and self.stopstart == 0:
            self.wheel_opt +=1
            if self.wheel_opt > 3:
                self.wheel_opt = 0
            self.B3.config(fg = "black")
            self.B5.config(fg = "black")
            self.B7.config(fg = "black")
            self.B9.config(fg = "black")
            if self.wheel_opt == 0:
                self.B5.config(fg = "red")
            if self.wheel_opt == 1:
                self.B7.config(fg = "red")
            if self.wheel_opt == 2:
                self.B9.config(fg = "red")
            if self.wheel_opt == 3:
                self.B3.config(fg = "red")
        elif math.sqrt((x2*x2)+ (y2*y2)) < 30:
            self.Mute()

    def Start_Play(self):
        if self.album_start == 0:
            self.B3.config(fg = "black")
            self.B5.config(fg = "black")
            self.B7.config(fg = "black")
            self.B9.config(fg = "black")
        
        if len(self.tunes) > 0 and self.play == 0 and self.paused == 0:
            self.Disp_track_no.config(text =self.track_no+1)
            self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2  = self.tunes[self.track_no].split('^')
            self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name, self.artist_name, self.album_name, self.track_name)
            self.Disp_artist_name.config(text =self.artist_name)
            self.Disp_album_name.config(text =self.album_name)
            self.Disp_track_name.config(text =self.track_name[:-4])
            self.Disp_Drive.config(fg = 'black')
            self.Disp_Drive.config(text = "/" + self.drive_name1 + "/" + self.drive_name2  + "/" + self.drive_name)
            self.Disp_Name_m3u.config(background="white", foreground="black")
            self.Disp_Name_m3u.delete('1.0','20.0')
            if os.path.exists(self.track):
                if self.version == 2:
                    player.loadfile(self.track)
                    player.time_pos = 0
                else:
                    rpistr = "mplayer " + '"' + self.track + '"'
                    self.p = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid)
                       
                audio = MP3(self.track)
                self.track_len = audio.info.length
                minutes = int(self.track_len // 60)
                seconds = int (self.track_len - (minutes * 60))
                self.Disp_track_len.config(text ="%02d:%02d" % (minutes, seconds % 60))
                self.play = 1
                self.start = time.time()
                if self.album_start == 1:
                    self.Button_Start.config(bg = "light gray",fg = "blue",text = "Playing Album...")
                else:
                    self.Button_Start.config(bg = "light gray",fg = "red",text = "Playing Playlist...")
                self.Button_Stop.config(bg = "red")
                self.Start_Play2()
            else:
                self.Disp_Drive.config(fg = 'red')
                self.Disp_Drive.config(text = "MISSING")
                stop = 0
                while (self.tunes[self.track_no].split('^')[3]) == self.drive_name and stop == 0:
                    self.track_no +=1
                    if self.track_no > len(self.tunes) - 1:
                        self.track_no = 0
                        stop = 1
                if self.play == 1:
                    self.Start_Play()
                else:
                    self.Show_Track()
        elif self.album_start == 1:
            self.Start_Play2()
            
    def Start_Play2(self):
        self.stop = 0
        if self.album_start == 0:
            self.total = 0
            self.count1 = 0
            self.count2 = 0
            counter = self.track_no + 1
            self.minutes = 0
            while counter < len(self.tunes) and self.stop == 0:
                self.artist_name1,self.album_name1,self.track_name1,self.drive_name10,self.drive_name11,self.drive_name21  = self.tunes[counter].split('^')
                counter +=1
                self.track = os.path.join("/" + self.drive_name11,self.drive_name21,self.drive_name10, self.artist_name1, self.album_name1, self.track_name1)
                if os.path.exists(self.track):
                    audio = MP3(self.track)
                    self.total += audio.info.length
                    if self.total > self.Disp_max_time * 60:
                        self.stop = 1
        else:
            stop = 0
            self.album_time = 0
            self.album_track += 1
            counter = self.track_no + 1
            if counter > len(self.tunes) - 1:
                stop = 2
            while stop == 0 and (self.tunes[counter].split('^')[1]) == self.album_name :
                self.artist_name1,self.album_name1,self.track_name1,self.drive_name10,self.drive_name11,self.drive_name21  = self.tunes[counter].split('^')
                self.track = os.path.join("/" + self.drive_name11,self.drive_name21,self.drive_name10, self.artist_name1, self.album_name1, self.track_name1)
                if os.path.exists(self.track):
                    audio = MP3(self.track)
                    self.album_time += audio.info.length
                counter +=1
                if counter > len(self.tunes) - 1:
                    counter -=1
                    stop = 2
            if stop == 2:
                counter -=1
            self.Disp_track_no.config (text = self.album_track)
            if self.album_track == 1 and len(self.tunes) > 1:
                self.countex = counter - self.track_no + stop
                self.Disp_Total_tunes.config(text = counter - self.track_no + stop)
            self.total = self.album_time
        self.start2 = time.time()
        self.render2 = ""
        path = "/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
        pictures = glob.glob(path)
        self.render2 = ""
        if len(pictures) > 0:
            if len(pictures) > 1:
               r = random.randrange(len(pictures))
               self.image = pictures[r]
            else:
               self.image = pictures[0]
            self.load = Image.open(self.image)
            self.load = self.load.resize((218, 218), Image.ANTIALIAS) 
            self.render2 = ImageTk.PhotoImage(self.load)
            self.img.config(image = self.render2)
        elif self.gapless == 0:
            self.img.config(image = self.renderc)
        else:
            self.img.config(image = self.render)
        self.playing()

    def playing(self):
        # scroll album name
        if len(self.album_name) > 60:
            self.count1 +=1
            if self.count1 > 60:
                self.count1 = 0
            if self.count1 > len(self.album_name) - 50:
                self.count1 = 0
                self.Disp_album_name.config(text =self.album_name)
            if self.count1 > 5:
               self.Disp_album_name.config(text =self.album_name[self.count1 - 5:])
               time.sleep(0.25)
        # scroll track name
        if len(self.track_name) > 60:
            self.count2 +=1
            if self.count2 > 60:
                self.count2 = 0
            if self.count2 > len(self.track_name) - 50:
                self.count2 = 0
                self.Disp_track_name.config(text =self.track_name[:-4])
            if self.count2 > 5:
                self.Disp_track_name.config(text =self.track_name[self.count2 - 5:-4])
                time.sleep(0.25)
        # end of album (no repeat)
        if self.minutes == 0 and ((self.gapless == 0 and self.seconds == 0 and self.BT == 0) or (self.gapless == 1 and self.seconds == (2 * self.BT) and self.BT == 1) or (self.gapless == self.gapless_time and self.seconds <= self.gapless_time)) and self.album_start == 1 and self.repeat_album == 0:
            self.play = 2
            self.stopstart = 0
            self.plist_trig = 0
            self.album_trig = 0
            self.L9.config(text= "   ")
            self.s.configure("LabeledProgressbar", text="0 %      ", background='red')
            self.progress['value'] = 0
            self.B3.config(bg = "light blue", fg = "black")
            self.B4.config(bg = "light blue", fg = "black")
            self.B5.config(bg = "light blue", fg = "red")
            self.B6.config(bg = "light blue", fg = "black")
            self.B7.config(bg = "light blue", fg = "black")
            self.B8.config(bg = "light blue", fg = "black")
            self.B9.config(bg = "light blue", fg = "black")
            self.B10.config(bg = "light blue", fg = "black")
            self.B11.config(bg = "#c5c", fg = "black")
            self.B13.config(bg = "light blue", fg = "black")
            self.Button_Shuffle.config(fg = "blue",bg = "light blue")
            self.Button_AZ_artists.config(fg = "blue",bg = "light blue")
            self.Button_repeat.config(fg = "blue",bg = "light blue", text = "Repeat OFF")
            self.Button_TAlbum.config(fg = "blue",bg = "light blue")
            self.L6.config(text= "Playlist :")
            self.wheel_opt = 0
            self.album_start = 0
            self.album_time = 0 
            self.Button_Start.config(bg = "green",fg = "white",text = "PLAY Playlist")
            self.Button_Stop.config(bg = "light gray")
            self.Button_TAlbum.config(bg = "light gray", fg = "blue", text = "Play Album")
            self.Button_Shuffle.config(bg = "light blue",fg = "blue",text = "Shuffle P-LIST OFF")
            if self.shuffle_on == 1:
                self.shuffle_on = 0
                self.tunes[self.track_no - self.album_track + 1:self.tcount]=sorted(self.tunes[self.track_no  - self.album_track + 1:self.tcount])
            self.Disp_Total_tunes.config(text = len(self.tunes))
            self.Disp_track_no.config(text = self.track_no + 1)
            self.Time_Left_Play()
        # end of album (repeat)
        if self.minutes == 0 and ((self.gapless == 0 and self.seconds == 0 and self.BT == 0) or (self.gapless == 1 and self.seconds == (2 * self.BT) and self.BT == 1) or (self.gapless == self.gapless_time and self.seconds <= self.gapless_time)) and self.album_start == 1 and self.repeat_album == 1:
            self.play = 0
            self.minutes = 1
            self.album_start = 0
            self.album_trig = 0
            self.L9.config(text= "   ")
            self.Play_Album()
        # end of track   
        if os.path.exists(self.track):
            if time.time() - self.start > (self.track_len - self.gapless) - self.BT and self.play == 1 and self.paused == 0:
                self.play = 0
                self.s.configure("LabeledProgressbar", text="0 %      ", background='red')
                self.progress['value'] = 0
                if self.repeat_track == 0:
                    self.track_no +=1
                if self.BT == 1:
                    os.killpg(self.p.pid, signal.SIGTERM)
                    time.sleep(2)
                # stop if playlist last track and repeat OFF
                if self.track_no > len(self.tunes) - 1 and self.repeat == 0 and self.repeat_album == 0:
                    self.play = 2
                    self.stopstart = 0
                    self.Button_Start.config(bg = "green",fg = "white",text = "PLAY Playlist")
                    self.Button_Stop.config(bg = "light gray")
                    self.track_no -=1
                    self.Time_Left_Play()
                # repeat if playlist last track and repeat ON
                if self.track_no > len(self.tunes) - 1 and self.repeat == 1:
                    self.track_no = 0
                self.Start_Play()
                
            # display bar charts
            if self.play == 1 :
                if self.paused == 0:
                    self.played = time.time() - self.start
                p_minutes = int(self.played // 60)
                p_seconds = int (self.played - (p_minutes * 60))
                if self.total > self.Disp_max_time * 60:
                    if self.album_start == 0:
                        self.L9.config(text= " T :")
                        self.s.configure("LabeledProgressbar", text="{0} %      ".format(int((self.played/self.track_len)*100)), background='blue')
                        self.progress['value'] = (self.played/self.track_len)*100
                self.Disp_played.config(text ="%02d:%02d" % (p_minutes, p_seconds % 60))
                self.Disp_played.config(fg = "red")
                self.after(100, self.playing)
            if self.play == 1 and self.paused == 0:
                self.tplaylist = self.total + self.track_len
                if self.stop == 0:
                    self.tplaylist = (self.total + self.track_len - (time.time() - self.start2))
                self.minutes = int(self.tplaylist// 60)
                self.seconds = int (self.tplaylist - (self.minutes * 60))
                if self.album_start == 1:
                    if self.album_track == 1 and self.album_trig == 0:
                        self.album_length = self.total + self.track_len
                        self.album_trig = 1
                    self.L9.config(text= " A :")
                    self.s.configure("LabeledProgressbar", text="{0} %      ".format(100-int((self.tplaylist/(self.album_length))*100)), background='green')
                    self.progress['value'] = 100 - (self.tplaylist/(self.album_length))*100
                else:
                    if self.total < self.Disp_max_time * 60:
                        if self.plist_trig == 0:
                            self.plist_length = self.total + self.track_len
                            self.plist_trig = 1
                        self.L9.config(text= " P :")
                        self.s.configure("LabeledProgressbar", text="{0} %      ".format(100-int((self.tplaylist/(self.plist_length))*100)), background='green')
                        self.progress['value'] = 100 - (self.tplaylist/(self.plist_length))*100
                if self.minutes < 0 or self.seconds < 0:
                    self.Disp_Total_Plist.config(text = " 00:00 " )
                elif self.stop == 0 or self.stop == 2:
                    self.Disp_Total_Plist.config(text ="%02d:%02d" % (self.minutes, self.seconds % 60))
                else:
                    self.Disp_Total_Plist.config(text = ">" + str(self.Disp_max_time) + ":00" )
        elif self.play == 1:
            self.Start_Play()

    def Pause(self):
        if self.BT == 0:
            if self.version == 1 and self.play == 1 and self.counter5 == 0:
                os.killpg(self.p.pid, signal.SIGTERM)
                self.play = 0
                self.version = 2
                if self.album_start  == 1:
                    self.album_track -=1
                self.Start_Play()
            if self.version == 1 and self.play == 0 and self.counter5 == 0:
                self.version = 2
                self.gapless = 0
                self.Button_Pstart.config(fg = "white",bg = "light gray", text ="Gapless OFF")
                self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                self.paused = 0
            if self.paused == 0 and self.stopstart == 1:
                self.paused = 1
                self.gapless = 0
                self.Button_Pstart.config(fg = "white",bg = "light gray", text ="Gapless OFF")
                self.time1 = time.time()
                self.Button_Pause.config(fg = "black",bg = "orange", text ="UNPAUSE")
                self.img.config(image = self.render)
                player.pause()
            elif self.paused == 1 and self.stopstart == 1 and self.counter5 == 0:
                self.paused = 0
                self.time2 = time.time()
                self.start = self.start + (self.time2 - self.time1)
                self.start2 = self.start2 + (self.time2 - self.time1)
                self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                self.img.config(image = self.renderc)
                player.pause()

    def Gapless(self):
        if self.BT == 0:
            if self.version == 2 and self.play == 1 and self.paused == 0 and self.album_start == 0:
                player.stop()
                self.play = 0
                self.version = 1
                self.Start_Play()
            if self.gapless == 0 and self.paused == 0 and self.album_start == 0:
                self.gapless = self.gapless_time
                self.paused = 0
                self.version = 1
                self.Button_Pstart.config(fg = "black",bg = "orange", text ="Gapless ON")
                self.img.config(image = self.render)
            elif self.gapless == self.gapless_time and self.paused == 0:
                self.gapless = 0
                self.Button_Pstart.config(fg = "black",bg = "light gray", text ="Gapless OFF")
                self.img.config(image = self.render)
            elif self.gapless == 0 and self.paused == 0 and self.version == 1:
                self.gapless = self.gapless_time
                self.Button_Pstart.config(fg = "black",bg = "orange", text ="Gapless ON")
                self.img.config(image = self.render)

    def Play_Album(self):
        if self.paused == 0 and len(self.tunes) > 0 and self.album_start == 0:
            self.album_length  = 0
            self.plist_length  = 0
            self.album_trig    = 0
            self.plist_trig    = 0
            self.B3.config(bg  = "light grey", fg = "white")
            self.B4.config(bg  = "light grey", fg = "white")
            self.B5.config(bg  = "light grey", fg = "white")
            self.B6.config(bg  = "light grey", fg = "white")
            self.B7.config(bg  = "light grey", fg = "white")
            self.B8.config(bg  = "light grey", fg = "white")
            self.B9.config(bg  = "light blue", fg = "black")
            self.B11.config(bg = "light grey", fg = "white")
            self.B13.config(bg = "light grey", fg = "white")
            self.L6.config(text= "Album :")
            self.Button_Shuffle.config(fg = "white",bg = "light grey", text = "Shuffle P-LIST OFF")
            self.Button_AZ_artists.config(fg = "white",bg = "light grey")
            self.Button_TAlbum.config(fg = "white",bg = "light grey")
            self.Button_repeat.config(bg = "light blue",fg = "blue",text = "Repeat Album OFF")
            self.Button_Shuffle.config(bg = "light blue",fg = "blue",text = "Shuffle Album OFF")
            self.repeat_count = 0
            self.repeat = 0
            self.repeat_track = 0
            if len(self.tunes) > 2:
                self.shuffle_on = 0
                self.Disp_Name_m3u.config(background="white", foreground="black")
                self.Disp_Name_m3u.delete('1.0','20.0')
                self.sort_no = 0
                self.tunes.sort()
                stop = 0
                counter = 0
                while stop == 0:
                    self.artist_name2  = (self.tunes[counter].split('^')[0])
                    self.album_name2   = (self.tunes[counter].split('^')[1])
                    if self.artist_name == self.artist_name2 and self.album_name == self.album_name2:
                        stop = 1
                    counter +=1
                self.track_no = counter - 1
            if len(self.tunes) > 0:
                stop = 0
                if self.track_no == 0:
                    stop = 1
                while stop == 0:
                    self.artist_name2  = (self.tunes[self.track_no].split('^')[0])
                    self.album_name2   = (self.tunes[self.track_no].split('^')[1])
                    if self.artist_name != self.artist_name2 or self.album_name != self.album_name2:
                        self.track_no +=2
                        stop = 1
                    self.track_no -=1
                    if self.track_no < 0:
                       stop = 1
                       self.track_no +=1
                if len(self.tunes) > 1:
                    stop = 0
                    self.tcount = self.track_no
                    while stop == 0:
                        self.artist_name2  = (self.tunes[self.tcount].split('^')[0])
                        self.album_name2   = (self.tunes[self.tcount].split('^')[1])
                        if self.artist_name != self.artist_name2 or self.album_name != self.album_name2:
                            self.tcount -=2
                            stop = 1
                        self.tcount +=1
                        if self.tcount >= len(self.tunes):
                            stop = 1
                else:
                    self.tcount = self.track_no
                self.album_track = 0
                self.album_start = 1
                self.album_trig = 0
                self.stopstart = 1
                self.play = 0
                self.Start_Play()

    def Stop_Play(self):
        self.Disp_Name_m3u.config(background="white", foreground="black")
        self.Disp_Name_m3u.delete('1.0','20.0')
        self.L9.config(text= "   ")
        self.s.configure("LabeledProgressbar", text="0 %      ", background='red')
        self.progress['value'] = 0
        self.stopstart = 0
        self.wheel = 0
        self.shutdown = 0
        self.plist_trig = 0
        self.album_trig = 0
        self.album_length   = 0
        self.plist_length   = 0
        self.B3.config(bg = "light blue", fg = "black")
        self.B4.config(bg = "light blue", fg = "black")
        self.B5.config(bg = "light blue", fg = "black")
        self.B6.config(bg = "light blue", fg = "black")
        self.B7.config(bg = "light blue", fg = "black")
        self.B8.config(bg = "light blue", fg = "black")
        self.B9.config(bg = "light blue", fg = "black")
        if self.wheel_opt == 0:
            self.B5.config(fg = "red")
        if self.wheel_opt == 1:
            self.B7.config(fg = "red")
        if self.wheel_opt == 2:
            self.B9.config(fg = "red")
        if self.wheel_opt == 3:
            self.B3.config(fg = "red")
        self.B10.config(bg = "light blue", fg = "black")
        self.B11.config(bg = "#c5c", fg = "black")
        self.B13.config(bg = "light blue", fg = "black")
        self.Button_Shuffle.config(fg = "blue",bg = "light blue")
        self.Button_AZ_artists.config(fg = "blue",bg = "light blue")
        self.Button_repeat.config(fg = "blue",bg = "light blue", text = "Repeat OFF")
        self.Button_TAlbum.config(fg = "blue",bg = "light blue")
        self.L6.config(text= "Playlist :")
        if self.album_start == 1 and self.shuffle_on == 1:
            self.shuffle_on = 0
            self.tunes[self.track_no - self.album_track + 1:self.tcount]=sorted(self.tunes[self.track_no  - self.album_track + 1:self.tcount])
        self.Button_Shuffle.config(bg = "light blue",fg = "blue",text = "Shuffle P-LIST OFF")
        if self.BT == 0:
            player.time_pos = 0
        if self.paused == 1:
           if self.BT == 0:
               self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
               player.pause()
               time.sleep(.25)
        if self.album_start > 0:
            self.album_start = 0
            self.album_track = 0
            self.album_time = 0
            self.sleep_time_min = 0
            self.sleep_time = 0
            self.Button_Sleep.config(bg = "light blue")
            self.Button_TAlbum.config(bg = "light blue", fg = "blue", text = "Play Album")
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.Disp_sleep.config(text ="OFF")
        if self.play == 1:
            self.Button_volume.config(fg = "blue")
            self.wheel_opt = 0
            self.B5.config(fg = "red")
            self.B7.config(bg = "light blue", fg = "black")
            self.B3.config(bg = "light blue", fg = "black")
            self.B9.config(bg = "light blue", fg = "black")
            self.play = 0
            if self.version == 1:
                os.killpg(self.p.pid, signal.SIGTERM)
            else:
                player.stop()
                self.paused = 0
                if self.BT == 0:
                    self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
            self.Button_Start.config(bg = "green",fg = "white",text = "PLAY Playlist")
            self.Button_Stop.config(bg = "light gray")
        self.Disp_Name_m3u.delete('1.0','20.0')
        self.Time_Left_Play()

    def Check_switches(self):
        if self.gpio_enable == 1:
            if GPIO.input(self.volup)== 0:
                self.volume_UP()
            elif GPIO.input(self.voldn)== 0:
                self.volume_DN()
            elif GPIO.input(self.stop_start) == 0:
                if self.stopstart == 1:
                    self.Stop_Play()
                else:
                    self.Play()
        if time.time() - self.timer4 > 2 and self.drive_name != "":
           if self.render2 != "":
               self.img.config(image = self.render2)
        if self.album_start == 0 or self.stopstart == 1:
            x = self.master.winfo_pointerx()
            y = self.master.winfo_pointery()
            abs_x = self.master.winfo_pointerx() - self.master.winfo_rootx()
            abs_y = self.master.winfo_pointery() - self.master.winfo_rooty()
            x2 = abs_x - 114
            y2 = abs_y - 370
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
            if math.sqrt((x2*x2)+ (y2*y2)) > 40 and math.sqrt((x2*x2)+ (y2*y2)) < 100 :
                if os.path.exists(self.mp3_jpg):
                    if self.gapless == 0 and self.paused == 0:
                        self.img.config(image = self.renderc)
                    else:
                        self.img.config(image = self.render)
                    self.timer4 = time.time()
                self.wheel = 1
                if self.old_t > 22 and self.t < 2:
                    self.old_t = 0
                elif self.old_t < 4 and self.t > 20:
                    self.old_t = 24
                if self.t > self.old_t:
                    self.old_t = self.t
                    if self.wheel_opt == 0 and self.stopstart == 0:
                        self.Next_Artist()
                    elif self.wheel_opt == 1 and self.stopstart == 0:
                        self.Next_Album()
                    elif self.wheel_opt == 2 and self.stopstart == 0:
                        self.Next_Track()
                    elif self.wheel_opt == 3 and self.stopstart == 0:
                        self.Next_m3u()
                    elif self.play == 1 and self.version == 2 and self.paused == 0:
                        self.skip = 10
                        if self.skip + self.played < self.track_len  - self.skip:
                            self.start -= self.skip
                            self.total -= self.skip
                            if self.sleep_time_min > self.skip and self.shutdown == 1 and self.album_start == 1:
                                self.sleep_time_min -= self.skip
                            if self.BT == 0:
                                player.time_pos = self.skip + self.played
                elif self.t < self.old_t:
                   self.old_t = self.t
                   if self.wheel_opt == 0 and self.stopstart == 0:
                       self.Prev_Artist()
                   elif self.wheel_opt == 1 and self.stopstart == 0:
                        self.Prev_Album()
                   elif self.wheel_opt == 2 and self.stopstart == 0:
                        self.Prev_Track()
                   elif self.wheel_opt == 3 and self.stopstart == 0:
                        self.Prev_m3u()
                   elif self.play == 1 and self.version == 2 and self.paused == 0:
                       self.skip = 10
                       if self.played - self.skip >= self.skip:
                          self.start += self.skip
                          self.total += self.skip
                          if self.sleep_time_min > self.skip and self.shutdown == 1 and self.album_start == 1:
                              self.sleep_time_min += self.skip
                          if self.BT == 0:
                              player.time_pos = self.played - self.skip
                self.old_t = self.t
        self.after(200, self.Check_switches)
 
    def volume_DN(self):
        self.volume -=2
        if self.volume < 0:
            self.volume = 0
        self.m.setvolume(self.volume)
        self.Button_volume.config(text =self.volume)

    def volume_UP(self):
        self.volume +=2
        if self.volume > 100:
            self.volume = 100
        self.m.setvolume(self.volume)
        self.Button_volume.config(text =self.volume)

    def Mute(self):
        if self.mute == 0:
            self.mute = 1
            volume = 0
        else:
            self.mute = 0
            volume = self.volume
        self.m.setvolume(volume)
        self.Button_volume.config(text = volume)

    def Prev_m3u(self):
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir):
            self.wheel_opt = 3
            self.B3.config(fg = "red")
            self.B5.config(fg = "black")
            self.B7.config(fg = "black")
            self.B9.config(fg = "black")
            self.Disp_Name_m3u.config(background="white", foreground="black")
            if self.play == 1:
                if self.version == 1:
                    os.killpg(self.p.pid, signal.SIGTERM)
                else:
                    player.stop()
                    self.paused = 0
                    if self.BT == 0:
                        self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                self.Button_Start.config(bg = "green",fg = "white",text = "PLAY Playlist")
                self.Button_Stop.config(bg = "light gray")
            self.play = 0
            self.m3u_no -=1
            if self.m3u_no < 0:
                self.m3u_no = 0
            self.que_dir = self.m3us[self.m3u_no]
            Tracks = []
            with open(self.que_dir,"r") as textobj:
                line = textobj.readline()
                while line:
                    Tracks.append(line.strip())
                    line = textobj.readline()
            self.tunes = []
            for counter in range (0,len(Tracks)):
                z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2)
             
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.total = 0
            self.track_no = 0
            self.shuffle_on = 0
            self.Button_Shuffle.config(bg = "light blue",fg = "blue",text = "Shuffle P-LIST OFF")
            self.sorted = 0
            self.Button_AZ_artists.config(bg = "light blue",fg = "blue",text = "A-Z Sort OFF")
            self.Time_Left_Play()

    def Next_m3u(self):
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir):
            self.wheel_opt = 3
            self.B3.config(fg = "red")
            self.B5.config(fg = "black")
            self.B7.config(fg = "black")
            self.B9.config(fg = "black")
            self.Disp_Name_m3u.config(background="white", foreground="black")
            if self.play == 1:
                if self.version == 1:
                    os.killpg(self.p.pid, signal.SIGTERM)
                else:
                    player.stop()
                    self.paused = 0
                    if self.BT == 0:
                        self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                self.Button_Start.config(bg = "green",fg = "white",text = "PLAY Playlist")
                self.Button_Stop.config(bg = "light gray")
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
            for counter in range (0,len(Tracks)):
                z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2)

            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.track_no = 0
            self.shuffle_on = 0
            self.Button_Shuffle.config(bg = "light blue",fg = "blue",text = "Shuffle P-LIST OFF")
            self.sorted = 0
            self.Button_AZ_artists.config(bg = "light blue",fg = "blue",text = "A-Z Sort OFF")
            self.Time_Left_Play()

    def Prev_Artist(self):
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir):
            self.wheel_opt = 0
            self.B5.config(fg = "red")
            self.B3.config(fg = "black")
            self.B7.config(fg = "black")
            self.B9.config(fg = "black")
            self.Disp_Name_m3u.config(background="white", foreground="black")
            if self.play == 2:
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
                        os.killpg(self.p.pid, signal.SIGTERM)
                    else:
                        player.stop()
                    self.start = 0
                self.count1 = 0
                self.count2 = 0
                self.Time_Left_Play()

    def Next_Artist(self):
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir):
            self.wheel_opt = 0
            self.B5.config(fg = "red")
            self.B3.config(fg = "black")
            self.B7.config(fg = "black")
            self.B9.config(fg = "black")
            self.Disp_Name_m3u.config(background="white", foreground="black")
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
                        os.killpg(self.p.pid, signal.SIGTERM)
                    else:
                        player.stop()
                    self.start = 0
                self.count1 = 0
                self.count2 = 0
                self.Time_Left_Play()

    def Prev_Album(self):
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir):
            self.wheel_opt = 1
            self.B7.config(fg = "red")
            self.B5.config(fg = "black")
            self.B3.config(fg = "black")
            self.B9.config(fg = "black")
            self.Disp_Name_m3u.config(background="white", foreground="black")
            if self.play == 2:
                self.play = 0
            if self.version == 2:
                self.paused = 0
                if self.BT == 0:
                    self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
            stop = 0
            if len(self.tunes) > 0:
                while (self.tunes[self.track_no].split('^')[1]) == self.album_name and stop == 0:
                    self.track_no -=1
                    if self.track_no < 0:
                        self.track_no = 0 
                        stop = 1
                new_album_name = self.tunes[self.track_no].split('^')[1]
                stop = 0
                while (self.tunes[self.track_no].split('^')[1]) == new_album_name and stop == 0:
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
                         os.killpg(self.p.pid, signal.SIGTERM)
                    else:
                         player.stop()
                    self.start = 0
                self.count1 = 0
                self.count2 = 0
                self.Time_Left_Play()

    def Next_Album(self):
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir):
            self.wheel_opt = 1
            self.B7.config(fg = "red")
            self.B5.config(fg = "black")
            self.B3.config(fg = "black")
            self.B9.config(fg = "black")
            self.Disp_Name_m3u.config(background="white", foreground="black")
            if self.play == 2:
                self.play = 0
            if self.version == 2:
                self.paused = 0
                self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
            stop = 0
            if len(self.tunes) > 0:
                while (self.tunes[self.track_no].split('^')[1]) == self.album_name and stop == 0:
                    self.track_no +=1
                    if self.track_no > len(self.tunes) - 1:
                        self.track_no = 0
                        stop = 1
                if self.play == 1:
                    if self.track_no != 0:
                        self.track_no -=1
                    if self.version == 1:
                        os.killpg(self.p.pid, signal.SIGTERM)
                    else:
                        player.stop()
                    self.start = 0
                self.count1 = 0
                self.count2 = 0
                self.Time_Left_Play()

    def Prev_Track(self):
        if self.album_track != 1 and os.path.exists(self.que_dir):
            self.Disp_Name_m3u.config(background="white", foreground="black")
            if self.paused == 0:
                if self.album_start == 0:
                    self.wheel_opt = 2
                    self.B9.config(fg = "red")
                    self.B5.config(fg = "black")
                    self.B7.config(fg = "black")
                    self.B3.config(fg = "black")
                if self.play == 2:
                    self.play = 0
                if self.version == 2:
                    self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                if self.play == 1:
                   if self.version == 1:
                       os.killpg(self.p.pid, signal.SIGTERM)
                   else:
                       player.stop()
                   self.start = 0
                   self.track_no -=2
                   if self.track_no < -1:
                       self.track_no = -1
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
                        self.track_no = 0
                    self.count1 = 0
                    self.count2 = 0
                    self.Time_Left_Play()

    def Next_Track(self):
        if (self.album_start == 0 and os.path.exists(self.que_dir)) or (self.album_start == 1 and self.track_no != self.tcount and os.path.exists(self.que_dir)):
            self.Disp_Name_m3u.config(background="white", foreground="black")
            if self.paused == 0:
                if self.album_start == 0:
                    self.wheel_opt = 2
                    self.B9.config(fg = "red")
                    self.B5.config(fg = "black")
                    self.B7.config(fg = "black")
                    self.B3.config(fg = "black")
                if self.play == 2:
                    self.play = 0
                if self.version == 2:
                    self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                if self.play == 1 :
                    if self.version == 1:
                        os.killpg(self.p.pid, signal.SIGTERM)
                    else:
                        player.stop()
                    self.start = 0
                    if self.album_start == 0:
                        self.count1 = 0
                        self.count2 = 0
                    if self.album_start == 0:
                        self.Time_Left_Play()
                    else:
                        self.Play()
                else:
                    self.track_no +=1
                    if self.track_no > len(self.tunes) -1:
                        self.track_no = len(self.tunes) -1
                    self.count1 = 0
                    self.count2 = 0
                    self.Time_Left_Play()

    def Time_Left_Play(self):
         self.start2 = time.time()
         self.total = 0
         stop = 0
         counter = self.track_no 
         if self.play == 1:
             counter +=1
         if self.play == 2:
             counter = 0
         self.minutes = 0
         while counter < len(self.tunes) and stop == 0:
             self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2  = self.tunes[counter].split('^')
             counter +=1
             self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name, self.artist_name, self.album_name, self.track_name)
             if os.path.exists(self.track):
                 audio = MP3(self.track)
                 self.total += audio.info.length
                 if self.total > self.Disp_max_time * 60:
                    stop = 1
         self.minutes = int(self.total // 60)
         self.seconds = int (self.total - (self.minutes * 60))
         if stop == 0:
             self.Disp_Total_Plist.config(text ="%02d:%02d" % (self.minutes, self.seconds % 60))
         else:
             self.Disp_Total_Plist.config(text = ">" + str(self.Disp_max_time) + ":00" )
         if self.play == 1:
            self.Start_Play()
         else:
            self.stopstart = 0
            self.Show_Track()

    def nextAZ(self):
        if self.album_start == 0 and os.path.exists(self.que_dir):
            self.Disp_Name_m3u.config(background="white", foreground="black")
            if self.play == 2:
                self.play = 0
            stop = 0
            if len(self.tunes) > 0:
                if self.wheel_opt == 0 or self.wheel_opt == 3:
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
            self.Time_Left_Play()

      
    def RELOAD_List(self):
        if self.paused == 0 and self.album_start == 0:
            self.Disp_Name_m3u.config(background="white", foreground="black")
            self.timer = time.time()
            self.Disp_artist_name.config(text =" ")
            self.Disp_album_name.config(text =" ")
            self.Disp_track_name.config(text =" ")
            self.Disp_Drive.config(text =" ")
            self.Disp_track_no.config(text =" ")
            self.Disp_Total_tunes.config(text =" ")
            self.Disp_played.config(text =" ")
            self.Disp_track_len.config(text =" ")
            self.Disp_Total_Plist.config(text=" ")
            if self.play == 2:
                self.play = 0
            if self.play > 0:
                self.play = 0
                self.Button_Start.config(bg = "green",fg = "white",text = "PLAY Playlist")
                self.Button_Stop.config(bg = "light gray")
                if self.version == 1:
                    os.killpg(self.p.pid, signal.SIGTERM)
                else:
                    player.stop()
            if os.path.exists(self.m3u_dir + self.m3u_def + ".m3u"):
                os.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.sorted == 0
            self.Button_AZ_artists.config(bg = "light blue",fg = "blue",text = "A-Z Artists OFF")
            self.Tracks = glob.glob(self.mp3_search)
            if len (self.Tracks) > 0 :
                with open(self.m3u_dir + self.m3u_def + ".m3u", 'w') as f:
                    for item in self.Tracks:
                        f.write("%s\n" % item)
            if len (self.Tracks) > 0 :
                self.counter5 = 0
                self.tunes = []
                self.B11.config(bg = "red")
                self.paused = 1
                self.L9.config(text= " L :")
                self.RELOAD1_List()
               
            else:
                self.Disp_artist_name.config(text =" NO TRACKS FOUND !")
            
    def RELOAD1_List(self):       
         z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = self.Tracks[self.counter5].split('/')
         self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2)
         self.counter5 +=1
         self.s.configure("LabeledProgressbar", text="{0} %      ".format(int((self.counter5/len(self.Tracks)*100))), background='red')
         self.progress['value']=(self.counter5/len(self.Tracks)* 100)
         self.Disp_Total_tunes.config(text =str(self.counter5))
         self.Disp_Drive.config(text = "/" + self.drive_name1 + "/" +  self.drive_name2 + "/" +  self.drive_name )
         if self.counter5 < len(self.Tracks) and len(self.Tracks) > 0:
             self.after(1,self.RELOAD1_List)
         else:    
             self.RELOAD2_List()

    def RELOAD2_List(self):
        self.counter5 = 0
        self.B11.config(bg = "#c5c")
        self.L9.config(text= " ")
        self.s.configure("LabeledProgressbar", text="0 %      ", background='red')
        self.progress['value']= 0
        self.track_no = 0
        self.Disp_Total_tunes.config(text =len(self.tunes))
        self.m3us = glob.glob(self.m3u_dir + "*.m3u")
        self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")
        self.Disp_Name_m3u.delete('1.0','20.0')
        self.que_dir   = self.m3u_dir + self.m3u_def + ".m3u"
        self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
        self.Disp_artist_name.config(fg = "black")
        self.paused = 0
        if self.play == 0:
            self.Time_Left_Play()

    def Repeat(self):
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir):
            if self.play == 2:
                self.play = 0
            self.repeat_count +=1
            if self.repeat_count == 1:
                self.repeat_track = 1
                self.repeat = 0
                self.Button_repeat.config(bg = "green",fg = "white",text = "Repeat Track ON")
            elif self.repeat_count == 2:
                self.repeat_track = 0
                self.repeat = 1
                self.Button_repeat.config(bg = "green",fg = "white",text = "Repeat P-List ON")
            else:
                self.repeat_count = 0
                self.repeat = 0
                self.repeat_track = 0
                self.Button_repeat.config(bg = "light blue",fg = "blue",text = "Repeat OFF")
            if self.play == 1:
                self.Start_Play()
            else:
                self.Show_Track()
        if self.paused == 0 and self.album_start == 1 and self.repeat_album == 0:
            self.repeat_album = 1
            self.repeat = 0
            self.repeat_track = 0
            self.Button_repeat.config(bg = "green",fg = "white",text = "Repeat Album ON")
        elif self.paused == 0 and self.album_start == 1 and self.repeat_album == 1:
            self.repeat_album = 0
            self.repeat = 0
            self.repeat_track = 0
            self.Button_repeat.config(bg = "light blue",fg = "blue",text = "Repeat Album OFF")

    def Shuffle_Tracks(self):
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir):
            self.Disp_Name_m3u.config(background="white", foreground="black")
            if self.play == 2:
                self.play = 0
            if self.shuffle_on == 0:
                self.shuffle_on = 1
                shuffle(self.tunes)
                self.Button_Shuffle.config(bg = "green",fg = "white",text = "Shuffle P-LIST ON")
            else:
                self.shuffle_on = 0
                Tracks = []
                with open(self.que_dir,"r") as textobj:
                   line = textobj.readline()
                   while line:
                      Tracks.append(line.strip())
                      line = textobj.readline()
                self.tunes = []
                for counter in range (0,len(Tracks)):
                    z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                    self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2)
                self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                self.Disp_Total_tunes.config(text =len(self.tunes))
                self.Button_Shuffle.config(bg = "light blue",fg = "blue",text = "Shuffle P-LIST OFF")
                self.track_no = 0
            if self.play == 1:
                if self.version == 1:
                    os.killpg(self.p.pid, signal.SIGTERM)
                else:
                    player.stop()
                self.start = 0
                self.Start_Play()
            else:
                self.Show_Track()
        if self.paused == 0 and self.album_start == 1 and len(self.tunes) > 1:
            if self.shuffle_on == 0:
                self.shuffle_on = 1
                self.tunes[self.track_no  - self.album_track + 1:self.tcount] = random.sample(self.tunes[self.track_no  - self.album_track + 1:self.tcount], (self.tcount - (self.track_no  - self.album_track + 1)))
                self.Button_Shuffle.config(bg = "green",fg = "white",text = "Shuffle Album ON")
            else:
                self.shuffle_on = 0
                self.tunes[self.track_no - self.album_track + 1:self.tcount]=sorted(self.tunes[self.track_no  - self.album_track + 1:self.tcount])
                self.Button_Shuffle.config(bg = "light blue",fg = "blue",text = "Shuffle Album OFF")

    def AZ_Tracks(self):
        if self.paused == 0 and self.album_start == 0 and os.path.exists(self.que_dir):
            self.Disp_Name_m3u.config(background="white", foreground="black")
            if self.play == 2:
                self.play = 0
            if self.play == 1:
               self.play = 0
               self.Button_Start.config(bg = "green",fg = "white",text = "PLAY Playlist")
               self.Button_Stop.config(bg = "light gray")
               if self.version == 1:
                   os.killpg(self.p.pid, signal.SIGTERM)
               else:
                   player.stop()
            if self.sort_no < 3:
               self.sort_no +=1  
               if self.sort_no == 1:
                   self.Button_AZ_artists.config(bg = "green",fg = "white",text = "A-Z Artists ON")
                   self.tunes.sort()
               if self.sort_no == 2:
                   self.Button_AZ_artists.config(bg = "green",fg = "white",text = "A-Z Albums ON")
                   self.tunes2 = []
                   for counter in range (0,len(self.tunes)):
                       self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2  = self.tunes[counter].split('^')
                       self.track = os.path.join("/" + self.drive_name1,self.drive_name2,self.drive_name, self.artist_name, self.album_name, self.track_name)
                       self.tunes2.append(self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.artist_name)
                   self.tunes2.sort()
                   self.tunes = []
                   for counter in range (0,len(self.tunes2)):
                       self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.artist_name  = self.tunes2[counter].split('^')
                       self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2)
               if self.sort_no == 3:
                   self.Button_AZ_artists.config(bg = "green",fg = "white",text = "A-Z Tracks ON")
                   num_list = ["0","1","2","3","4","5","6","7","8","9"]
                   self.tunes2 = []
                   L = 2
                   for counter in range (0,len(self.tunes)):
                       self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2  = self.tunes[counter].split('^')
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
                       self.tunes2.append(self.track_name2 + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2 + "^" + self.artist_name + "^" + self.album_name + "^" + self.track_number)
                   self.tunes2.sort()
                   self.tunes = []
                   for counter in range (0,len(self.tunes2)):
                       self.track_name,self.drive_name,self.drive_name1,self.drive_name2,self.artist_name,self.album_name,self.track_number  = self.tunes2[counter].split('^')
                       self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_number + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2)
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
                   z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                   self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2)
               self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
               self.Disp_Total_tunes.config(text =len(self.tunes))
               self.Button_AZ_artists.config(bg = "light blue",fg = "blue",text = "A-Z Sort OFF")
               self.track_no = 0
            self.Disp_Total_Plist.config(text = "       " )
            self.Time_Left_Play()

    def Track_m3u(self):
        if os.path.exists(self.que_dir):
            Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
            if len(Name) == 0 or Name == "Name ?":
                now = datetime.datetime.now()
                Name = now.strftime("%y%m%d%H%M%S")
                self.Disp_Name_m3u.delete('1.0','20.0')
                self.Disp_Name_m3u.insert(INSERT,Name)
            with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" + self.track_name + "\n")
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")

    def FAV_List(self):
        if os.path.exists(self.que_dir):
            Name = "FAVourites"
            self.Disp_Name_m3u.config(background="white", foreground="black")
            self.Disp_Name_m3u.delete('1.0','20.0')
            with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" + self.track_name + "\n")
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")

    def Artist_m3u(self):
        if os.path.exists(self.que_dir):
            self.Disp_Name_m3u.config(background="white", foreground="black")
            Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
            if len(Name) == 0 or Name == "Name ?":
                now = datetime.datetime.now()
                Name = now.strftime("%y%m%d%H%M%S")
                self.Disp_Name_m3u.delete('1.0','20.0')
                self.Disp_Name_m3u.insert(INSERT,Name)
            artist = []
            for counter in range (0,len(self.tunes)):
                if (self.tunes[counter].split('^')[0]) == self.artist_name:
                    artist.append(self.tunes[counter])
            artist.sort()
            for counter in range(0,len(artist)):
                self.artist_name,self.album_name2,self.track_name,self.drive_name,self.drive_name1,self.drive_name2  = artist[counter].split('^')
                with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                    f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name2 + "/" + self.track_name + "\n")
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")

    def Album_m3u(self):
        if os.path.exists(self.que_dir):
            self.Disp_Name_m3u.config(background="white", foreground="black")
            Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
            if len(Name) == 0 or Name == "Name ?":
                now = datetime.datetime.now()
                Name = now.strftime("%y%m%d%H%M%S")
                self.Disp_Name_m3u.delete('1.0','20.0')
                self.Disp_Name_m3u.insert(INSERT,Name)
            album = []
            for counter in range (0,len(self.tunes)):
                if (self.tunes[counter].split('^')[1]) == self.album_name and (self.tunes[counter].split('^')[0]) == self.artist_name:
                    album.append(self.tunes[counter])
            album.sort()
            for counter in range(0,len(album)):
                self.artist_name,self.album_name2,self.track_name,self.drive_name,self.drive_name1,self.drive_name2  = album[counter].split('^')
                with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                    f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name2 + "/" + self.track_name + "\n")
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")

    def PList_m3u(self):
        
        if self.que_dir != self.m3u_dir + self.m3u_def + ".m3u" and os.path.exists(self.que_dir):
            self.Disp_Name_m3u.config(background="white", foreground="black")
            Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
            if len(Name) == 0 or Name == "Name ?":
                now = datetime.datetime.now()
                Name = now.strftime("%y%m%d%H%M%S")
                self.Disp_Name_m3u.delete('1.0','20.0')
                self.Disp_Name_m3u.insert(INSERT,Name)
            with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                for counter in range (0,len(self.tunes)):
                    self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2  = self.tunes[counter].split('^')
                    f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" + self.track_name + "\n")
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")

    def sleep(self):
        if self.album_start == 0:
            self.shutdown = 1
            self.begin = time.time()
            self.sleep_time = int(self.sleep_time + 15.99)
            if self.sleep_time > 999:
                self.sleep_time = 0
            self.sleep_time_min = self.sleep_time * 60
        elif self.shutdown == 0:
            self.shutdown = 1
            self.begin = time.time()
            self.begin = time.time()
            self.sleep_time_min = self.tplaylist + 60 
            self.sleep_time = int(self.sleep_time_min / 60)
        else:
            self.shutdown = 0
            self.sleep_time = 0
            self.sleep_time_min = 0
        if self.sleep_time == 0:
            self.Button_Sleep.config(bg = "light blue")
            self.Disp_sleep.config(text ="OFF")
        else:
            self.Button_Sleep.config(bg = "orange")
            self.Disp_sleep.config(text =self.sleep_time)
            
    def sleep_off(self):
        if self.shutdown == 1 or self.sleep_time > 0:
            self.shutdown = 0
            self.sleep_time = 0
            self.sleep_time_min = 0
            self.Button_Sleep.config(bg = "light blue")
            self.Disp_sleep.config(text ="OFF")
 
    def Check_Sleep(self):
        if self.sleep_time > 0:
            if self.album_start == 1:
                self.sleep_current = int(self.tplaylist/60)  + 1
            else:            
                self.sleep_current = int((self.sleep_time_min - (time.time() - self.begin))/60)
            self.Disp_sleep.config(text = self.sleep_current)
            if self.sleep_current < 1:
                self.Button_Sleep.config(bg = "red")
        if (time.time() - self.begin > self.sleep_time_min) and self.sleep_time > 0 and self.shutdown == 1:
            os.system("sudo shutdown -h now")
        self.after(10000, self.Check_Sleep)

    def DelPL_m3u(self):
        if os.path.exists(self.que_dir) and self.paused == 0 and self.album_start == 0:
            Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
            if len(Name) > 0 and Name != self.m3u_def:
                if Name == "FAV":
                    Name = "FAVourites"
                if os.path.exists(self.m3u_dir + Name + ".m3u"):
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
                    self.B3.config(fg = "red")
                    self.B5.config(fg = "black")
                    self.B7.config(fg = "black")
                    self.B9.config(fg = "black")
                    if self.BT == 0:
                        self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                    self.Button_Start.config(bg = "green",fg = "white",text = "PLAY Playlist")
                    self.Button_Stop.config(bg = "light gray")
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
                        z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                        self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2)
                    self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                    self.Disp_Total_tunes.config(text =len(self.tunes))
                    self.track_no = 0
                    self.shuffle_on = 0
                    self.Button_Shuffle.config(bg = "light blue",fg = "blue",text = "Shuffle P-LIST OFF")
                    self.sorted = 0
                    self.Button_AZ_artists.config(bg = "light blue",fg = "blue",text = "A-Z Sort OFF")
                    self.Disp_Name_m3u.config(background="white", foreground="black")
                    self.Time_Left_Play()
                elif Name != " Name ?":
                    self.Search()
            else:
                self.Disp_Name_m3u.config(background="yellow", foreground="red")
                self.Disp_Name_m3u.insert(END,' Name ?')

    def exit(self):
        if self.play == 1:
            if self.version == 1:
                os.killpg(self.p.pid, signal.SIGTERM)
            else:
                player.stop()
        self.play = 0
        self.master.destroy()

    def Search(self):
        Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
        if self.paused == 0 and self.album_start == 0 and len(Name) > 0:
          search = []
          for counter in range (0,len(self.tunes)):
                self.artist_name,self.album_name,self.track_name,self.drive_name,self.drive_name1,self.drive_name2  = self.tunes[counter].split('^')
                if Name in self.track_name:
                    search.append(self.tunes[counter])
          if len(search) > 0:
            search.sort()
            for counter in range(0,len(search)):
                self.artist_name,self.album_name2,self.track_name,self.drive_name,self.drive_name1,self.drive_name2  = search[counter].split('^')
                with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                    f.write("/" + self.drive_name1 + "/" + self.drive_name2 + "/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name2 + "/" + self.track_name + "\n")
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")

            self.wheel_opt = 3
            self.B3.config(fg = "red")
            self.B5.config(fg = "black")
            self.B7.config(fg = "black")
            self.B9.config(fg = "black")
            if self.play == 1:
                if self.version == 1:
                    os.killpg(self.p.pid, signal.SIGTERM)
                else:
                    player.stop()
                    self.paused = 0
                    if self.BT == 0:
                        self.Button_Pause.config(fg = "black",bg = "light blue", text ="Pause")
                self.Button_Start.config(bg = "green",fg = "white",text = "PLAY Playlist")
                self.Button_Stop.config(bg = "light gray")
            self.play = 0
            for x in range(0,len(self.m3us)):
                 if self.m3us[x] == self.m3u_dir + Name + ".m3u":
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
                z,self.drive_name1,self.drive_name2,self.drive_name,self.artist_name,self.album_name,self.track_name  = Tracks[counter].split('/')
                self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "^" + self.drive_name1 + "^" + self.drive_name2)

            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.track_no = 0
            self.shuffle_on = 0
            self.Button_Shuffle.config(bg = "light blue",fg = "blue",text = "Shuffle P-LIST OFF")
            self.sorted = 0
            self.Button_AZ_artists.config(bg = "light blue",fg = "blue",text = "A-Z Sort OFF")
            self.Disp_Name_m3u.config(background="white", foreground="black")
            self.Disp_Name_m3u.delete('1.0','20.0')
            self.Time_Left_Play()

    def Shutdown(self):
        os.system("sudo shutdown -h now")
            
def main():
    print ("Loading...")
    root = Tk()
    root.title("Pi MP3 Player")
    #if root.winfo_screenwidth() == 800 and root.winfo_screenheight() == 480:
    #    root.wm_attributes('-fullscreen','true')
    ex = MP3Player()
    root.geometry("800x450")
    root.mainloop() 

if __name__ == '__main__':
    main() 
