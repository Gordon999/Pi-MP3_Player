#!/usr/bin/env python3
import tkinter as tk
from tkinter import *
import os, sys
import time
import datetime
import subprocess
import signal
from random import shuffle
import glob
from mutagen.mp3 import MP3
import alsaaudio
from PIL import ImageTk, Image
import RPi.GPIO as GPIO
from mplayer import Player
Player.introspect()
player = Player()

# Pi_MP3_Player v10.0

class MP3Player(Frame):
    
    def __init__(self):
        super().__init__() 
        self.initUI()
        
    def initUI(self):
        
        self.tunes_dir  = "/media/pi/"          # where mp3s are stored under
        self.mp3_search = "*/*/*/*.mp3"         # search criteria for mp3s
        self.m3u_def    = "ALLTracks"           # name of default .m3u
        self.m3u_dir    = "/home/pi/Documents/" # where .m3us are stored
        self.mp3_jpg    = "mp3.jpg"             # logo (used if no album jpg image)
        self.Disp_max_time  = 120               # in minutes
        self.volume         = 80                # range 0 - 100
        self.gapless_time   = 2                 # in seconds
        self.voldn          = 36                # external volume down gpio input
        self.volup          = 40                # external volume up gpio input
        self.stop_start     = 38                # external start / stop play gpio input
        
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.voldn,GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.stop_start,GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.volup,GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.que_dir   = self.m3u_dir + self.m3u_def + ".m3u"
        self.repeat         = 0
        self.play           = 0
        self.track_no       = 0
        self.sleep_time     = 0
        self.sleep_time_min = 0
        self.mute           = 0
        self.shuffle_on     = 0
        self.sorted         = 0
        self.begin = time.time()
        self.m3u_no         = 0
        self.stopstart      = 0
        self.paused         = 0
        self.gapless        = 0
        self.count1         = 0
        self.count2         = 0
        self.version        = 2
        self.album_time     = 0
        self.album_start    = 0
        self.shutdown       = 0
        self.album_track    = 0
        m = alsaaudio.Mixer('PCM')
        m.setvolume(self.volume)

        self.Check_switches()
        
        self.Button_Start = tk.Button(self.master, text = "START", bg = "green",fg = "white",width = 7, height = 2,font = 20, command = self.Play, wraplength=80, justify=CENTER)
        self.Button_Start.grid(row = 0, column = 0, padx = 24,pady = 12)
        self.Button_Pause = tk.Button(self.master, text = "Pause", width = 7, height = 2,command=self.Pause, wraplength=80, justify=CENTER)
        self.Button_Pause.place(x = 140, y = 14)
        self.Button_Pstart = tk.Button(self.master, text = "Gapless OFF", fg = "white", width = 7, height = 2,command=self.Gapless, wraplength=80, justify=CENTER)
        self.Button_Pstart.place(x = 352, y = 14)
        self.Button_TAlbum = tk.Button(self.master, text = "Play Album", fg = "blue", width = 7, height = 2,command=self.Play_Album, wraplength=80, justify=CENTER)
        self.Button_TAlbum.place(x = 457, y = 14)
        self.Button_Stop =  tk.Button(self.master, text = "STOP",fg = "white",width = 7, height = 2,font = 20,command = self.Stop_Play)
        self.Button_Stop.grid(row = 0, column = 1, padx = 2)
        self.Button_Shuffle = tk.Button(self.master, text = "Shuffle OFF", bg = "light blue", fg = "blue",width = 7, height = 2,command = self.Shuffle_Tracks)
        self.Button_Shuffle.grid(row = 6, column = 3, padx = 15)
        self.Button_AZ_artists = tk.Button(self.master, text = "A-Z Artists OFF",bg = "light blue", fg = "blue",width = 7, height = 2,command = self.AZ_Tracks, wraplength=80, justify=CENTER)
        self.Button_AZ_artists.grid(row = 6, column = 4)
        self.Button_Sleep = tk.Button(self.master, text = "SLEEP", bg = "light blue",width = 7, height = 2,command = self.sleep,repeatdelay=1000, repeatinterval=500)
        self.Button_Sleep.grid(row = 8, column = 1, padx = 100, pady = 0)
        self.Button_Track_m3u = tk.Button(self.master, text = "ADD track   to .m3u", bg = "light green",width = 7, height = 2,command = self.Track_m3u, wraplength=80, justify=CENTER)
        self.Button_Track_m3u.grid(row = 7, column = 1, padx = 0, pady = 10)
        self.Button_Artist_m3u = tk.Button(self.master, text = "ADD artist   to .m3u", bg = "light green",width = 7, height = 2,command = self.Artist_m3u, wraplength=80, justify=CENTER)
        self.Button_Artist_m3u.grid(row = 7, column = 3, padx = 0, pady = 10)
        self.Button_Album_m3u = tk.Button(self.master, text = "ADD album   to .m3u", bg = "light green",width = 7, height = 2,command = self.Album_m3u, wraplength=80, justify=CENTER)
        self.Button_Album_m3u.grid(row = 7, column = 2, padx = 0, pady = 10)
        self.Button_PList_m3u = tk.Button(self.master, text = "ADD P-list   to .m3u", bg = "light green",width = 7, height = 2,command = self.PList_m3u, wraplength=80, justify=CENTER)
        self.Button_PList_m3u.grid(row = 7, column = 4, padx = 0, pady = 10)
        self.Button_DELETE_m3u = tk.Button(self.master, text = "DEL .m3u", bg = "#191",width = 7, height = 1,command = self.DelPL_m3u)
        self.Button_DELETE_m3u.grid(row = 8, column = 2, padx = 0, pady = 10)
        self.Button_repeat = tk.Button(self.master, text = "Repeat OFF", bg = "light blue",fg = "blue",width = 7, height = 2,command = self.Repeat)
        self.Button_repeat.grid(row = 6, column = 2, padx = 10)
        self.Button_volume = tk.Button(self.master, text = self.volume, bg = "white",fg = "blue",width = 2, height = 2,command = self.Mute)
        if self.master.winfo_screenwidth() == 800 and self.master.winfo_screenheight() == 480:
            self.Button_volume.place(x = 631, y = 14)
        else:
            self.Button_volume.place(x = 651, y = 14)
        B1 =  tk.Button(self.master, text = " < Vol ",    bg = "yellow",width = 7, height = 2,command = self.volume_DN).grid(row = 0, column = 3,padx = 0)
        B2 =  tk.Button(self.master, text = "Vol >",      bg = "yellow",width = 7, height = 2,command = self.volume_UP).grid(row = 0, column = 4,padx = 25)
        B3 =  tk.Button(self.master, text = "< P-list",   bg = "light blue",width = 7, height = 1,command = self.Prev_m3u,repeatdelay=1000, repeatinterval=500).grid(row = 1, column = 0,padx = 0)
        B4 =  tk.Button(self.master, text = "P-list >",   bg = "light blue",width = 7, height = 1,command = self.Next_m3u,repeatdelay=1000, repeatinterval=500).grid(row = 1, column = 4,padx = 10)
        B5 =  tk.Button(self.master, text = "< Artist",   bg = "light blue",width = 7, height = 2,command = self.Prev_Artist,repeatdelay=1000, repeatinterval=500).grid(row = 2, column = 0,padx = 0)
        B6 =  tk.Button(self.master, text = "Artist >",   bg = "light blue",width = 7, height = 2,command = self.Next_Artist,repeatdelay=1000, repeatinterval=500).grid(row = 2, column = 4,padx = 10)
        B7 =  tk.Button(self.master, text = "< Album",    bg = "light blue",width = 7, height = 2,command = self.Prev_Album,repeatdelay=1000, repeatinterval=500).grid(row = 3, column = 0,padx = 0)
        B8 =  tk.Button(self.master, text = "Album >",     bg = "light blue",width = 7, height = 2,command = self.Next_Album,repeatdelay=1000, repeatinterval=500).grid(row = 3, column = 4,padx = 10)
        B9 =  tk.Button(self.master, text = "< Track",    bg = "light blue",width = 7, height = 2,command = self.Prev_Track,repeatdelay=1000, repeatinterval=500).grid(row = 4, column = 0,padx = 0)
        B10 = tk.Button(self.master, text = "Track >",    bg = "light blue",width = 7, height = 2,command = self.Next_Track,repeatdelay=1000, repeatinterval=500).grid(row = 4, column = 4,padx = 10)
        B11 = tk.Button(self.master, text = " RELOAD " + self.m3u_def ,width = 7, height = 2, bg = "#c5c",command = self.RELOAD_List, wraplength=80, justify=CENTER).grid(row = 6, column = 1,padx = 0)
        B12 = tk.Button(self.master, text = "QUIT",       width = 7, height = 2,command=self.exit).grid(row = 8, column = 3)
        B13 = tk.Button(self.master, text = "Next A-Z",   width = 7, height = 1,bg = "light blue",command=self.nextAZ,repeatdelay=250, repeatinterval=500).grid(row = 5, column = 4, pady = 13)
        B14 = tk.Button(self.master, text = "Shutdown",   bg = "gray",width = 7, height = 2,command = self.Shutdown).grid(row = 8, column = 4)
    
        L1 = tk.Label(self.master, text="Track : " )
        L1.place(x=243, y=252)
        L2 = tk.Label(self.master, text="of" )
        L2.place(x=360, y=252)
        L3 = tk.Label(self.master, text="Played :" )
        L3.place(x=450, y=252)
        L4 = tk.Label(self.master,text=" of " )
        L4.place(x=566, y=252)
        L5 = tk.Label(self.master, text="Drive :" )
        L5.place(x=243, y=280)
        L6 = tk.Label(self.master, text="Playlist:" )
        L6.place(x=530, y=280)
        L7 = tk.Label(self.master, text="mins" )
        L7.place(x=398, y=455)
        L8 = tk.Label(self.master, text=".m3u" )
        L8.place(x=400, y=397)
        
        self.Disp_plist_name = tk.Label(self.master, height=1, width=57,bg='white',   anchor="w", borderwidth=2, relief="groove")
        self.Disp_plist_name.place(x=130, y=79)
        self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
        self.Disp_artist_name = tk.Label(self.master, height=1, width=50,bg='white', font = 40, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
        self.Disp_artist_name.place(x=130, y=109)
        self.Disp_album_name = tk.Label(self.master, height=1, width=50,bg='white',font = 40, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
        self.Disp_album_name.place(x=130, y=156)
        self.Disp_track_name = tk.Label(self.master, height=1, width=50,bg='white',font = 40, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
        self.Disp_track_name.place(x=130, y=204)
        self.Disp_track_no = tk.Label(self.master, height=1, width=5,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_track_no.place(x=295, y=252)
        self.Disp_Total_tunes = tk.Label(self.master, height=1, width=5,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_Total_tunes.place(x=385, y=252)
        self.Disp_played = tk.Label(self.master, height=1, width=5,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_played.place(x=509, y=252)
        self.Disp_track_len = tk.Label(self.master, height=1, width=5,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_track_len.place(x=598, y=252)
        self.Disp_Drive = tk.Label(self.master, height=1, width=20,bg= 'white', anchor="w", borderwidth=2, relief="groove")
        self.Disp_Drive.place(x=295, y=278)
        self.Disp_Name_m3u = tk.Text(self.master,height = 1, width=12,bg= 'white', borderwidth=2, relief="groove")
        self.Disp_Name_m3u.place(x=336, y=377)
        self.Disp_sleep = tk.Label(self.master, height=1,bg='white',width = 4, font = 40, padx = 5, pady = 10, borderwidth=2, relief="groove")
        self.Disp_sleep.place(x=340, y=429)
        self.Disp_sleep.config(text='OFF')
        self.Disp_Total_Plist = tk.Label(self.master, height=1, width=6,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_Total_Plist.place(x=588, y=278)
        
        if os.path.exists(self.mp3_jpg):
            self.load = Image.open(self.mp3_jpg)
            self.render = ImageTk.PhotoImage(self.load)
            self.img = tk.Label(self.master, image = self.render)
            self.img.place(x=1,y=255)

        if not os.path.exists(self.que_dir):
            self.RELOAD_List()
        else:
            Tracks = []
            with open(self.que_dir,"r") as textobj:
               line = textobj.readline()
               while line:
                  Tracks.append(line.strip())
                  line = textobj.readline()
            self.tunes = []
            for counter in range (0,len(Tracks)):
                self.drive_name  = (Tracks[counter].split('/')[3])
                self.artist_name = (Tracks[counter].split('/')[4])
                self.album_name  = (Tracks[counter].split('/')[5])
                self.track_name  = (Tracks[counter].split('/')[6])
                self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name)
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.total = 0
            self.Time_Left_Play()

    def Show_Track(self):
        if len(self.tunes) > 0:
            self.Disp_track_no.config(text =self.track_no+1)
            self.artist_name = (self.tunes[self.track_no].split('^')[0])
            self.album_name  = (self.tunes[self.track_no].split('^')[1])
            self.track_name  = (self.tunes[self.track_no].split('^')[2])
            self.drive_name  = (self.tunes[self.track_no].split('^')[3])
            self.track = os.path.join(self.tunes_dir,self.drive_name, self.artist_name, self.album_name, self.track_name)
            self.Disp_artist_name.config(text =self.artist_name)
            self.Disp_album_name.config(text =self.album_name)
            self.Disp_track_name.config(text =self.track_name[:-4])
            self.Disp_played.config(text ="")
            self.Disp_Drive.config(fg = 'black')
            self.Disp_Drive.config(text = self.drive_name)
            path = self.tunes_dir + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
            pictures = glob.glob(path)
            if len(pictures) > 0:
                self.image = pictures[0]
                self.load = Image.open(self.image)
                self.render = ImageTk.PhotoImage(self.load)
                self.img.config(image = self.render)
            elif os.path.exists(self.mp3_jpg):
                self.load = Image.open(self.mp3_jpg)
                self.render = ImageTk.PhotoImage(self.load)
                self.img.config(image = self.render)
            if os.path.exists(self.track):
                audio = MP3(self.track)
                self.track_len = audio.info.length
                minutes = int(self.track_len // 60)
                seconds = int (self.track_len - (minutes * 60))
                self.Disp_track_len.config(text ="%02d:%02d" % (minutes, seconds % 60))
                self.Show_Album_Pic()
            else:
                self.Disp_Drive.config(fg = 'red')
                self.Disp_Drive.config(text = self.drive_name + "-MISSING")
            self.Check_Sleep()
            
    def Play(self):
        if  self.album_start == 0:
            self.stopstart = 1
            self.play = 0
            self.start2 = time.time()
            self.Start_Play()

    def Start_Play(self):
        if len(self.tunes) > 0 and self.play == 0 and self.paused == 0:
            self.Disp_track_no.config(text =self.track_no+1)
            self.artist_name = (self.tunes[self.track_no].split('^')[0])
            self.album_name  = (self.tunes[self.track_no].split('^')[1])
            self.track_name  = (self.tunes[self.track_no].split('^')[2])
            self.drive_name  = (self.tunes[self.track_no].split('^')[3])
            self.track = os.path.join(self.tunes_dir,self.drive_name, self.artist_name, self.album_name, self.track_name)
            self.Disp_artist_name.config(text =self.artist_name)
            self.Disp_album_name.config(text =self.album_name)
            self.Disp_track_name.config(text =self.track_name[:-4])
            self.Disp_Drive.config(fg = 'black')
            self.Disp_Drive.config(text =self.drive_name)
            self.Disp_Name_m3u.delete('1.0','20.0')
            if os.path.exists(self.track):
                if self.version == 2:
                    player.loadfile(self.track)
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
                    self.Button_Start.config(bg = "light gray",fg = "red",text = "Playing Album...")
                else:
                    self.Button_Start.config(bg = "light gray",fg = "red",text = "Playing...")
                self.Button_Stop.config(bg = "red")
                self.Start_Play2()
            else:
                self.Disp_Drive.config(fg = 'red')
                self.Disp_Drive.config(text = self.drive_name + "-MISSING")
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
                self.artist_name1 = (self.tunes[counter].split('^')[0])
                self.album_name1  = (self.tunes[counter].split('^')[1])
                self.track_name1  = (self.tunes[counter].split('^')[2])
                self.drive_name1  = (self.tunes[counter].split('^')[3])
                counter +=1
                self.track = os.path.join(self.tunes_dir,self.drive_name1, self.artist_name1, self.album_name1, self.track_name1)
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
                stop = 1
            while stop == 0 and (self.tunes[counter].split('^')[1]) == self.album_name :
                self.artist_name1 = (self.tunes[counter].split('^')[0])
                self.album_name1  = (self.tunes[counter].split('^')[1])
                self.track_name1  = (self.tunes[counter].split('^')[2])
                self.drive_name1  = (self.tunes[counter].split('^')[3])
                self.track = os.path.join(self.tunes_dir,self.drive_name1, self.artist_name1, self.album_name1, self.track_name1)
                if os.path.exists(self.track):
                    audio = MP3(self.track)
                    self.album_time += audio.info.length
                counter +=1
                if counter > len(self.tunes) - 1:
                    counter -=1
                    stop = 1
            self.Disp_track_no.config (text = self.album_track)
            if self.album_track == 1:
                self.Disp_Total_tunes.config(text = counter - self.track_no + stop)
            self.total = self.album_time
        self.start2 = time.time()
        path = self.tunes_dir + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
        pictures = glob.glob(path)
        if len(pictures) > 0:
            self.image = pictures[0]
            self.load = Image.open(self.image)
            self.render = ImageTk.PhotoImage(self.load)
            self.img.config(image = self.render)
        elif os.path.exists(self.mp3_jpg):
            self.load = Image.open(self.mp3_jpg)
            self.render = ImageTk.PhotoImage(self.load)
            self.img.config(image = self.render)
        self.playing()

    def playing(self):
        if len(self.album_name)> 60:
            self.count1 +=1
            if self.count1 > 60:
                self.count1 = 0
            if self.count1 > len(self.album_name) - 60:
                self.count1 = 0
                self.Disp_album_name.config(text =self.album_name)
            if self.count1 > 5:
               self.Disp_album_name.config(text =self.album_name[self.count1 - 5:])
        if len(self.track_name)> 60:
            self.count2 +=1
            if self.count2 > 60:
                self.count2 = 0
            if self.count2 > len(self.track_name) - 60:
                self.count2 = 0
                self.Disp_track_name.config(text =self.track_name[:-4])
            if self.count2 > 5:
                self.Disp_track_name.config(text =self.track_name[self.count2 - 5:-4])
                
        if self.minutes == 0 and ((self.gapless == 0 and self.seconds == 0) or (self.gapless == self.gapless_time and self.seconds <= self.gapless_time)) and self.album_start == 1:
            self.play = 2
            self.album_start = 0
            self.album_time = 0 
            self.Button_Start.config(bg = "green",fg = "white",text = "START")
            self.Button_Stop.config(bg = "light gray")
            self.Button_TAlbum.config(bg = "light gray", fg = "blue", text = "Play Album")
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.track_no -=1
            self.Disp_track_no.config(text =self.track_no+1)
            self.Time_Left_Play()
            
        if os.path.exists(self.track):
            if time.time() - self.start > self.track_len - self.gapless and self.play == 1 and self.paused == 0:
                self.play = 0
                self.track_no +=1
                if self.track_no > len(self.tunes) - 1 and self.repeat == 0:
                    self.play = 2
                    self.Button_Start.config(bg = "green",fg = "white",text = "START")
                    self.Button_Stop.config(bg = "light gray")
                    self.track_no -=1
                    self.Time_Left_Play()
                if self.track_no > len(self.tunes) - 1 and self.repeat == 1:
                    self.track_no = 0
                self.Start_Play()
            if self.play == 1 :
                if self.paused == 0:
                    self.played = time.time() - self.start
                p_minutes = int(self.played // 60)
                p_seconds = int (self.played - (p_minutes * 60))
                self.Disp_played.config(text ="%02d:%02d" % (p_minutes, p_seconds % 60))
                self.after(1000, self.playing)
            if self.play == 1 and self.paused == 0:
                tplayed = self.total + self.track_len
                if self.stop == 0:
                    tplayed = (self.total + self.track_len - (time.time() - self.start2))
                self.minutes = int(tplayed// 60)
                self.seconds = int (tplayed - (self.minutes * 60))
                if self.minutes < 0 or self.seconds < 0:
                    self.Disp_Total_Plist.config(text = " 00:00 " )
                elif self.stop == 0:
                    self.Disp_Total_Plist.config(text ="%02d:%02d" % (self.minutes, self.seconds % 60))
                else:
                    self.Disp_Total_Plist.config(text = ">" + str(self.Disp_max_time) + ":0" )
        elif self.play == 1:
            self.Start_Play()

    def Pause(self):
        if self.version == 1 and self.play == 1:
            os.killpg(self.p.pid, signal.SIGTERM)
            self.play = 0
            self.version = 2
            if self.album_start  == 1:
                self.album_track -=1
            self.Start_Play()
        if self.version == 1 and self.play == 0:
            self.version = 2
            self.gapless = 0
            self.Button_Pstart.config(fg = "white",bg = "light gray", text ="Gapless OFF")
            self.Button_Pause.config(fg = "black",bg = "light gray", text ="Pause")
            self.paused = 0
        if self.paused == 0 and self.stopstart == 1:
            self.paused = 1
            self.gapless = 0
            self.Button_Pstart.config(fg = "white",bg = "light gray", text ="Gapless OFF")
            self.time1 = time.time()
            self.Button_Pause.config(fg = "black",bg = "orange", text ="UNPAUSE")
            player.pause()
        elif self.paused == 1 and self.stopstart == 1:
            self.paused = 0
            self.time2 = time.time()
            self.start = self.start + (self.time2 - self.time1)
            self.start2 = self.start2 + (self.time2 - self.time1)
            self.Button_Pause.config(fg = "black",bg = "light gray", text ="Pause")
            player.pause()

    def Gapless(self):
        if self.version == 2 and self.play == 1 and self.paused == 0 and self.album_start == 0:
            player.stop()
            self.play = 0
            self.version = 1
            self.Start_Play()
        if self.gapless == 0 and self.paused == 0 and self.album_start == 0:
            self.gapless = self.gapless_time
            self.paused = 0
            self.version = 1
            self.Button_Pause.config(fg = "white",bg = "light gray", text ="Pause")
            self.Button_Pstart.config(fg = "black",bg = "orange", text ="Gapless ON")
        elif self.gapless == self.gapless_time and self.paused == 0:
            self.gapless = 0
            self.Button_Pstart.config(fg = "black",bg = "light gray", text ="Gapless OFF")
        elif self.gapless == 0 and self.paused == 0 and self.version == 1:
            self.gapless = self.gapless_time
            self.Button_Pause.config(fg = "white",bg = "light gray", text ="Pause")
            self.Button_Pstart.config(fg = "black",bg = "orange", text ="Gapless ON")

    def Play_Album(self):
        if self.paused == 0 and len(self.tunes) > 0:
            if self.shuffle_on == 1 and len(self.tunes) > 2:
                self.Button_Shuffle.config(bg = "light blue",fg = "blue",text = "Shuffle OFF")
                self.shuffle_on = 0
                self.tunes.sort()
                stop = 0
                counter = 0
                while stop == 0:
                    self.artist_name2  = (self.tunes[counter].split('^')[0])
                    self.album_name2   = (self.tunes[counter].split('^')[1])
                    if self.artist_name == self.artist_name2 and self.album_name == self.album_name2:
                        stop = 1
                    counter +=1
                self.track_no = counter
            if self.album_start > 0 and self.shutdown == 0:
                self.shutdown = 1
                self.begin = time.time()
                self.sleep_time_min = self.album_time + self.track_len  + 60
                self.sleep_time = int(self.sleep_time_min / 60)
                self.Button_Sleep.config(bg = "orange")
                self.Disp_sleep.config(text =self.sleep_time)
                self.Button_TAlbum.config(fg = "black", bg = "orange", text = "Cancel SLEEP")
            elif self.album_start > 0 and self.shutdown == 1:
                self.shutdown = 0
                self.begin = time.time()
                self.sleep_time_min = 0
                self.sleep_time = 0
                self.Button_Sleep.config(bg = "light blue")
                self.Disp_sleep.config(text = "OFF")
                self.Button_TAlbum.config(fg = "red",bg = "light grey", text = "Play Album & SLEEP")
            else:
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
                self.Button_TAlbum.config(fg = "red", text = "Play Album & SLEEP")
                self.album_track = 0
                if self.album_start == 0:
                    self.album_start = 1
                    self.stopstart = 1
                self.Start_Play()

    def Stop_Play(self):
        self.stopstart = 0
        self.shutdown = 0
        if self.paused == 1:
           self.Button_Pause.config(fg = "black",bg = "light gray", text ="Pause")
           player.pause()
           time.sleep(.25)
        if self.album_start > 0:
            self.album_start = 0
            self.album_time = 0
            self.sleep_time_min = 0
            self.sleep_time = 0
            self.Button_Sleep.config(bg = "light blue")
            self.Button_TAlbum.config(bg = "light gray", fg = "blue", text = "Play Album")
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.Disp_sleep.config(text ="OFF")
        if self.play == 1:
            self.play = 0
            if self.version == 1:
                os.killpg(self.p.pid, signal.SIGTERM)
            else:
                player.stop()
                self.paused = 0
                self.Button_Pause.config(fg = "black",bg = "light gray", text ="Pause")
            self.Button_Start.config(bg = "green",fg = "white",text = "START")
            self.Button_Stop.config(bg = "light gray")
        self.Disp_Name_m3u.delete('1.0','20.0')
        self.Time_Left_Play()

    def Check_switches(self):
        if GPIO.input(self.volup)== 0:
            m = alsaaudio.Mixer('PCM')
            self.volume +=2
            if self.volume > 100:
                self.volume = 100
            m.setvolume(self.volume)
            self.Button_volume.config(text =self.volume)
        elif GPIO.input(self.voldn)== 0:
            m = alsaaudio.Mixer('PCM')
            self.volume -=2
            if self.volume  < 0:
                self.volume = 0
            m.setvolume(self.volume)
            self.Button_volume.config(text =self.volume)
        elif GPIO.input(self.stop_start) == 0:
            if self.album_start > 0:
                self.album_start = 0
                self.album_time = 0
                self.sleep_time_min = 0
                self.sleep_time = 0
                self.Button_Sleep.config(bg = "light blue")
                self.Button_TAlbum.config(bg = "light gray", fg = "blue", text = "Play Album")
                self.Disp_Total_tunes.config(text =len(self.tunes))
                self.Disp_sleep.config(text ="OFF")
            if self.stopstart == 1:
                self.stopstart = 0
                if self.play == 1:
                    self.play = 0
                    if self.version == 1:
                        os.killpg(self.p.pid, signal.SIGTERM)
                    else:
                        player.stop()
                    self.Button_Start.config(bg = "green",fg = "white",text = "START")
                    self.Button_Stop.config(bg = "light gray")
                    self.Disp_played.config(text = "     ")
            else:
                self.stopstart = 1
                self.play = 0
                self.start2 = time.time()
                self.Start_Play()
                
        self.after(1000, self.Check_switches)
 
    def volume_DN(self):
        m = alsaaudio.Mixer('PCM')
        self.volume -=2
        if self.volume < 0:
            self.volume = 0
        m.setvolume(self.volume)
        self.Button_volume.config(text =self.volume)

    def volume_UP(self):
        m = alsaaudio.Mixer('PCM')
        self.volume +=2
        if self.volume > 100:
            self.volume = 100
        m.setvolume(self.volume)
        self.Button_volume.config(text =self.volume)

    def Mute(self):
        m = alsaaudio.Mixer('PCM')
        if self.mute == 0:
            self.mute = 1
            volume = 0
        else:
            self.mute = 0
            volume = self.volume
        m.setvolume(volume)
        self.Button_volume.config(text = volume)

    def Prev_m3u(self):
        if self.paused == 0 and self.album_start == 0:
            if self.play == 1:
                if self.version == 1:
                    os.killpg(self.p.pid, signal.SIGTERM)
                else:
                    player.stop()
                    self.paused = 0
                    self.Button_Pause.config(fg = "black",bg = "light gray", text ="Pause")
                self.Button_Start.config(bg = "green",fg = "white",text = "START")
                self.Button_Stop.config(bg = "light gray")
            self.play = 0
            self.m3u_no -=1
            if self.m3u_no < 0:
                self.m3u_no = 0
            self.que_dir = self.m3us[self.m3u_no]
            if self.que_dir == self.m3u_dir + self.m3u_def + ".m3u" and self.m3u_no != 0:
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
                self.drive_name  = (Tracks[counter].split('/')[3])
                self.artist_name = (Tracks[counter].split('/')[4])
                self.album_name  = (Tracks[counter].split('/')[5])
                self.track_name  = (Tracks[counter].split('/')[6])
                self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name)
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.total = 0
            self.track_no = 0
            self.shuffle_on = 0
            self.Button_Shuffle.config(bg = "light blue",fg = "blue",text = "Shuffle OFF")
            self.sorted = 0
            self.Button_AZ_artists.config(bg = "light blue",fg = "blue",text = "A-Z Artists OFF")
            self.Time_Left_Play()

    def Next_m3u(self):
        if self.paused == 0 and self.album_start == 0:
            if self.play == 1:
                if self.version == 1:
                    os.killpg(self.p.pid, signal.SIGTERM)
                else:
                    player.stop()
                    self.paused = 0
                    self.Button_Pause.config(fg = "black",bg = "light gray", text ="Pause")
                self.Button_Start.config(bg = "green",fg = "white",text = "START")
                self.Button_Stop.config(bg = "light gray")
            self.play = 0
            self.m3u_no +=1
            if self.m3u_no > len(self.m3us)-1:
                self.m3u_no = 0
            self.que_dir = self.m3us[self.m3u_no]
            if self.que_dir == self.m3u_dir + self.m3u_def + ".m3u" and self.m3u_no != 0:
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
                self.drive_name  = (Tracks[counter].split('/')[3])
                self.artist_name = (Tracks[counter].split('/')[4])
                self.album_name  = (Tracks[counter].split('/')[5])
                self.track_name  = (Tracks[counter].split('/')[6])
                self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name)
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.track_no = 0
            self.shuffle_on = 0
            self.Button_Shuffle.config(bg = "light blue",fg = "blue",text = "Shuffle OFF")
            self.sorted = 0
            self.Button_AZ_artists.config(bg = "light blue",fg = "blue",text = "A-Z Artists OFF")
            self.Time_Left_Play()

    def Prev_Artist(self):
        if self.paused == 0 and self.album_start == 0:
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
        if self.paused == 0 and self.album_start == 0:
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
        if self.paused == 0 and self.album_start == 0:
            if self.play == 2:
                self.play = 0
            if self.version == 2:
                self.paused = 0
                self.Button_Pause.config(fg = "black",bg = "light gray", text ="Pause")
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
        if self.paused == 0 and self.album_start == 0:
            if self.play == 2:
                self.play = 0
            if self.version == 2:
                self.paused = 0
                self.Button_Pause.config(fg = "black",bg = "light gray", text ="Pause")
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
        if self.paused == 0 and self.album_start == 0:
            if self.play == 2:
                self.play = 0
            if self.version == 2:
                self.Button_Pause.config(fg = "black",bg = "light gray", text ="Pause")
            if self.play == 1:
               if self.version == 1:
                   os.killpg(self.p.pid, signal.SIGTERM)
               else:
                   player.stop()
               self.start = 0
               self.track_no -=2
               if self.track_no < -1:
                  self.track_no = -1
               self.count1 = 0
               self.count2 = 0
               self.Time_Left_Play()
            else:
               self.track_no -=1
               if self.track_no < 0:
                   self.track_no = 0
               self.count1 = 0
               self.count2 = 0
               self.Time_Left_Play()

    def Next_Track(self):
        if self.paused == 0 and self.album_start == 0:
            if self.play == 2:
                self.play = 0
            if self.version == 2:
                self.Button_Pause.config(fg = "black",bg = "light gray", text ="Pause")
            if self.play == 1:
                if self.version == 1:
                    os.killpg(self.p.pid, signal.SIGTERM)
                else:
                    player.stop()
                self.start = 0
                self.count1 = 0
                self.count2 = 0
                self.Time_Left_Play()
            else:
                self.track_no +=1
                if self.track_no > len(self.tunes) -1:
                    self.track_no = len(self.tunes) -1
                self.count1 = 0
                self.count2 = 0
                self.Time_Left_Play()

    def Show_Album_Pic(self):
        path = self.tunes_dir + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
        pictures = glob.glob(path)
        if len(pictures) > 0:
            self.image = pictures[0]
            self.load = Image.open(self.image)
            self.render = ImageTk.PhotoImage(self.load)
            self.img.config(image = self.render)
        elif os.path.exists(self.mp3_jpg):
            self.load = Image.open(self.mp3_jpg)
            self.render = ImageTk.PhotoImage(self.load)
            self.img.config(image = self.render)

    def Time_Left_Play(self):
         self.start2 = time.time()
         self.total = 0
         stop = 0
         counter = self.track_no 
         if self.play == 1:
             counter +=1
         if self.play == 2:
             counter = 0
             self.track_no = 0
         self.minutes = 0
         while counter < len(self.tunes) and stop == 0:
             self.artist_name = (self.tunes[counter].split('^')[0])
             self.album_name  = (self.tunes[counter].split('^')[1])
             self.track_name  = (self.tunes[counter].split('^')[2])
             self.drive_name  = (self.tunes[counter].split('^')[3])
             counter +=1
             self.track = os.path.join(self.tunes_dir,self.drive_name, self.artist_name, self.album_name, self.track_name)
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
             self.Disp_Total_Plist.config(text = ">" + str(self.Disp_max_time) + ":0" )
         if self.play == 1:
            self.Start_Play()
         else:
            self.Show_Track()

    def nextAZ(self):
        if self.album_start == 0:
            if self.play == 2:
                self.play = 0
            stop = 0
            if len(self.tunes) > 0:
                while (self.tunes[self.track_no].split('^')[0][0]) == self.artist_name[0] and stop == 0:
                    self.track_no +=1
                    if self.track_no > len(self.tunes) - 1:
                        self.track_no = 0
                        stop = 1
            self.Time_Left_Play()

    def RELOAD_List(self):
        if self.paused == 0 and self.album_start == 0:
            if self.play == 2:
                self.play = 0
            if self.play > 0:
                self.play = 0
                self.Button_Start.config(bg = "green",fg = "white",text = "START")
                self.Button_Stop.config(bg = "light gray")
                if self.version == 1:
                    os.killpg(self.p.pid, signal.SIGTERM)
                else:
                    player.stop()
            if os.path.exists(self.m3u_dir + self.m3u_def + ".m3u"):
                os.remove(self.m3u_dir + self.m3u_def + ".m3u")
            self.Disp_artist_name.config(text ="")
            self.Disp_album_name.config(text ="")
            self.Disp_track_name.config(text ="")
            self.Disp_Drive.config(text ="")
            self.Disp_track_no.config(text ="")
            self.Disp_Total_tunes.config(text ="")
            self.Disp_played.config(text ="")
            self.Disp_track_len.config(text ="")
            self.sorted == 0
            self.Button_AZ_artists.config(bg = "light blue",fg = "blue",text = "A-Z Artists OFF")
            Tracks = glob.glob(self.tunes_dir + self.mp3_search)
            self.tunes = []
            if len (Tracks) > 0 :
                with open(self.m3u_dir + self.m3u_def + ".m3u", 'w') as f:
                    for item in Tracks:
                        f.write("%s\n" % item)
                for counter in range (0,len(Tracks)):
                    self.drive_name  = (Tracks[counter].split('/')[3])
                    self.artist_name = (Tracks[counter].split('/')[4])
                    self.album_name  = (Tracks[counter].split('/')[5])
                    self.track_name  = (Tracks[counter].split('/')[6])
                    self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name)
                self.track_no = 0
                self.Disp_plist_name.config(text=self.que_dir)
            else:
                self.Disp_artist_name.config(text =" NO TRACKS FOUND !")
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")
            self.Disp_Name_m3u.delete('1.0','20.0')
            self.que_dir   = self.m3u_dir + self.m3u_def + ".m3u"
            self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
            if self.play == 0:
                self.Time_Left_Play()

    def Repeat(self):
        if self.paused == 0 and self.album_start == 0:
            if self.play == 2:
                self.play = 0
            if self.repeat == 0:
                self.repeat = 1
                self.Button_repeat.config(bg = "green",fg = "white",text = "Repeat ON")
            else:
                self.repeat = 0
                self.Button_repeat.config(bg = "light blue",fg = "blue",text = "Repeat OFF")
            if self.play == 1:
                self.Start_Play()
            else:
                self.Show_Track()

    def Shuffle_Tracks(self):
        if self.paused == 0 and self.album_start == 0:
            if self.play == 2:
                self.play = 0
            if self.shuffle_on == 0:
                self.shuffle_on = 1
                shuffle(self.tunes)
                self.Button_Shuffle.config(bg = "green",fg = "white",text = "Shuffle ON")
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
                    self.drive_name  = (Tracks[counter].split('/')[3])
                    self.artist_name = (Tracks[counter].split('/')[4])
                    self.album_name  = (Tracks[counter].split('/')[5])
                    self.track_name  = (Tracks[counter].split('/')[6])
                    self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name)
                self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
                self.Disp_Total_tunes.config(text =len(self.tunes))
                self.Button_Shuffle.config(bg = "light blue",fg = "blue",text = "Shuffle OFF")
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

    def AZ_Tracks(self):
        if self.paused == 0 and self.album_start == 0:
            if self.play == 2:
                self.play = 0
            if self.play == 1:
               self.play = 0
               self.Button_Start.config(bg = "green",fg = "white",text = "START")
               self.Button_Stop.config(bg = "light gray")
               if self.version == 1:
                   os.killpg(self.p.pid, signal.SIGTERM)
               else:
                   player.stop()
            if self.sorted == 0:
               self.sorted = 1
               self.Button_AZ_artists.config(bg = "green",fg = "white",text = "A-Z Artists ON")
               self.tunes.sort()
               self.track_no = 0
            else:
               self.sorted = 0
               Tracks = []
               with open(self.que_dir,"r") as textobj:
                  line = textobj.readline()
                  while line:
                     Tracks.append(line.strip())
                     line = textobj.readline()
               self.tunes = []
               for counter in range (0,len(Tracks)):
                   self.drive_name  = (Tracks[counter].split('/')[3])
                   self.artist_name = (Tracks[counter].split('/')[4])
                   self.album_name  = (Tracks[counter].split('/')[5])
                   self.track_name  = (Tracks[counter].split('/')[6])
                   self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name)
               self.Disp_plist_name.config(text=" " + self.que_dir[len(self.m3u_dir):])
               self.Disp_Total_tunes.config(text =len(self.tunes))
               self.Button_AZ_artists.config(bg = "light blue",fg = "blue",text = "A-Z Artists OFF")
               self.track_no = 0
            self.Disp_Total_Plist.config(text = "       " )
            self.Time_Left_Play()

    def Track_m3u(self):
        Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
        if len(Name) == 0:
            now = datetime.datetime.now()
            Name = now.strftime("%y%m%d%H%M%S")
            self.Disp_Name_m3u.insert(INSERT,Name)
        with open(self.m3u_dir + Name + ".m3u", 'a') as f:
            f.write(self.tunes_dir + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" + self.track_name + "\n")
        self.m3us = glob.glob(self.m3u_dir + "*.m3u")
        self.m3us.sort()
        self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")

    def Artist_m3u(self):
        Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
        if len(Name) == 0:
            now = datetime.datetime.now()
            Name = now.strftime("%y%m%d%H%M%S") 
            self.Disp_Name_m3u.insert(INSERT,Name)
        artist = []
        for counter in range (0,len(self.tunes)):
            if (self.tunes[counter].split('^')[0]) == self.artist_name:
                artist.append(self.tunes[counter])
        artist.sort()
        for counter in range(0,len(artist)):
            self.artist_name  = (artist[counter].split('^')[0])
            self.album_name2  = (artist[counter].split('^')[1])
            self.track_name   = (artist[counter].split('^')[2])
            self.drive_name   = (artist[counter].split('^')[3])
            with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                f.write(self.tunes_dir + self.drive_name + "/" + self.artist_name + "/" + self.album_name2 + "/" + self.track_name + "\n")
        self.m3us = glob.glob(self.m3u_dir + "*.m3u")
        self.m3us.sort()
        self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")

    def Album_m3u(self):
        Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
        if len(Name) == 0:
            now = datetime.datetime.now()
            Name = now.strftime("%y%m%d%H%M%S")
            self.Disp_Name_m3u.insert(INSERT,Name)
        album = []
        for counter in range (0,len(self.tunes)):
            if (self.tunes[counter].split('^')[1]) == self.album_name and (self.tunes[counter].split('^')[0]) == self.artist_name:
                album.append(self.tunes[counter])
        album.sort()
        for counter in range(0,len(album)):
            self.artist_name  = (album[counter].split('^')[0])
            self.album_name2  = (album[counter].split('^')[1])
            self.track_name   = (album[counter].split('^')[2])
            self.drive_name   = (album[counter].split('^')[3])
            with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                f.write(self.tunes_dir + self.drive_name + "/" + self.artist_name + "/" + self.album_name2 + "/" + self.track_name + "\n")
        self.m3us = glob.glob(self.m3u_dir + "*.m3u")
        self.m3us.sort()
        self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")

    def PList_m3u(self):
        if self.que_dir != self.m3u_dir + self.m3u_def + ".m3u":
            Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
            if len(Name) == 0:
                now = datetime.datetime.now()
                Name = now.strftime("%y%m%d%H%M%S")
                self.Disp_Name_m3u.insert(INSERT,Name)
                
            with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                for counter in range (0,len(self.tunes)):
                    self.artist_name = (self.tunes[counter].split('^')[0])
                    self.album_name  = (self.tunes[counter].split('^')[1])
                    self.track_name  = (self.tunes[counter].split('^')[2])
                    self.drive_name  = (self.tunes[counter].split('^')[3])
                    f.write(self.tunes_dir + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" + self.track_name + "\n")
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.sort()
            self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")

    def sleep(self):
        self.shutdown = 1
        self.begin = time.time()
        self.sleep_time = int(self.sleep_time + 15.99)
        if self.sleep_time > self.Disp_max_time:
            self.sleep_time = 0
        self.sleep_time_min = self.sleep_time * 60
        if self.sleep_time == 0:
            self.Button_Sleep.config(bg = "light blue")
            self.Disp_sleep.config(text ="OFF")
        else:
            self.Button_Sleep.config(bg = "orange")
            self.Disp_sleep.config(text =self.sleep_time)

    def Check_Sleep(self):
        if self.sleep_time > 0:
            self.sleep_current = int((self.sleep_time_min - (time.time() - self.begin))/60)
            self.Disp_sleep.config(text = self.sleep_current)
            if self.sleep_current < 1:
                self.Button_Sleep.config(bg = "red")
        if (time.time() - self.begin > self.sleep_time_min) and self.sleep_time > 0 and self.shutdown == 1:
            os.system("sudo shutdown -h now")
        self.after(10000, self.Check_Sleep)

    def DelPL_m3u(self):
        Name = str(self.Disp_Name_m3u.get('1.0','20.0')).strip()
        if len(Name) > 0 and Name != self.m3u_def:
            if os.path.exists(self.m3u_dir + Name + ".m3u"):
                os.remove(self.m3u_dir + Name + ".m3u")
                self.m3us = glob.glob(self.m3u_dir + "*.m3u")
                self.m3us.sort()
                self.m3us.insert(0,self.m3u_dir + self.m3u_def + ".m3u")
                self.Disp_Name_m3u.delete('1.0','20.0')
                self.m3u_no = -1
                self.Next_m3u()

    def exit(self):
        if self.play == 1:
            self.Button_Start.config(bg = "green")
            self.Button_Stop.config(bg = "light gray")
            if self.version == 1:
               os.killpg(self.p.pid, signal.SIGTERM)
            else:
               player.stop()
        self.play = 0
        self.master.destroy()

    def Shutdown(self):
        os.system("sudo shutdown -h now")
            
def main(): 
    root = Tk()
    root.title("MP3 Player")
    if root.winfo_screenwidth() == 800 and root.winfo_screenheight() == 480:
        root.wm_attributes('-fullscreen','true')
    ex = MP3Player()
    root.geometry("800x480")
    root.mainloop() 

if __name__ == '__main__':
    main() 
