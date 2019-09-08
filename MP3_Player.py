#!/usr/bin/env python3
import tkinter as tk
from tkinter import *
import os, sys
import time
import datetime
import subprocess
import signal
import random
import glob
from mutagen.mp3 import MP3
import alsaaudio
from PIL import ImageTk, Image

# Pi_MP3_Player v8

class Player(Frame):
    
    def __init__(self):
        super().__init__() 
        self.initUI()
        
    def initUI(self): 
        self.m3u_dir = "/home/pi/Documents/"
        self.que_dir = self.m3u_dir + "ALLTracks.m3u"
        self.repeat = 0
        self.play = 0
        self.track_no = 0
        self.sleep_time = 0
        self.sleep_time_min = 0
        self.volume = 86
        self.shuffle_on = 0
        self.sorted = 0
        self.begin = time.time()
        self.m3u_no = 0
        m = alsaaudio.Mixer('PCM')
        m.setvolume(self.volume)
        self.Button_Start = tk.Button(self.master, text = "Start Play", bg = "green",fg = "white",width = 7, height = 2,font = 20, command = self.Play)
        self.Button_Start.grid(row = 0, column = 0, padx = 24,pady = 12)
        self.Button_Stop =  tk.Button(self.master, text = "Stop  Play",fg = "white",width = 7, height = 2,command = self.Stop_Play)
        self.Button_Stop.grid(row = 0, column = 1, padx = 2)
        B1 =  tk.Button(self.master, text = " < Vol ",    bg = "yellow",width = 7, height = 2,command = self.volume_DN).grid(row = 0, column = 2,padx = 0)
        B2 =  tk.Button(self.master, text = "Vol >",      bg = "yellow",width = 7, height = 2,command = self.volume_UP).grid(row = 0, column = 4,padx = 25)
        B3 =  tk.Button(self.master, text = "< P-list",   bg = "light blue",width = 7, height = 1,command = self.Prev_m3u).grid(row = 1, column = 0,padx = 0)
        B4 =  tk.Button(self.master, text = "P-list >",   bg = "light blue",width = 7, height = 1,command = self.Next_m3u).grid(row = 1, column = 4,padx = 10)
        B5 =  tk.Button(self.master, text = "< Artist",   bg = "light blue",width = 7, height = 2,command = self.Prev_Artist).grid(row = 2, column = 0,padx = 0)
        B6 =  tk.Button(self.master, text = "Artist >",   bg = "light blue",width = 7, height = 2,command = self.Next_Artist).grid(row = 2, column = 4,padx = 10)
        B7 =  tk.Button(self.master, text = "< Album",    bg = "light blue",width = 7, height = 2,command = self.Prev_Album).grid(row = 3, column = 0,padx = 0)
        B8 =  tk.Button(self.master, text = "Album>",     bg = "light blue",width = 7, height = 2,command = self.Next_Album).grid(row = 3, column = 4,padx = 10)
        B9 =  tk.Button(self.master, text = "< Track",    bg = "light blue",width = 7, height = 2,command = self.Prev_Track).grid(row = 4, column = 0,padx = 0)
        B10 = tk.Button(self.master, text = "Track >",    bg = "light blue",width = 7, height = 2,command = self.Next_Track).grid(row = 4, column = 4,padx = 10)
        B11 = tk.Button(self.master, text = " RELOAD ALLTracks",width = 7, height = 2, bg = "#c5c",command = self.New_Track_List, wraplength=80, justify=LEFT).grid(row = 6, column = 1,padx = 0,)
        self.Button_Shuffle = tk.Button(self.master, text = "Shuffle OFF", bg = "light blue",width = 7, height = 2,command = self.Shuffle_Tracks)
        self.Button_Shuffle.grid(row = 6, column = 4)
        B12 = tk.Button(self.master, text = "A-Z Artists", fg = "blue",width = 9, height = 1,command = self.Restore_Tracks).grid(row = 6, column = 2,padx = 15)
        B13 = tk.Button(self.master, text = "QUIT", width = 7, height = 2,command=self.exit).grid(row = 8, column = 3)
        B14 = tk.Button(self.master, text = "QUIT", width = 7, height = 2,command=self.exit).grid(row = 5, column = 0, pady = 5)
        self.Button_Sleep = tk.Button(self.master, text = "SLEEP", bg = "light blue",width = 7, height = 2,command = self.sleep)
        self.Button_Sleep.grid(row = 8, column = 1, padx = 100, pady = 0)
        self.Button_Track_m3u = tk.Button(self.master, text = "ADD track   to .m3u", bg = "light green",width = 7, height = 2,command = self.Track_m3u, wraplength=80, justify=LEFT)
        self.Button_Track_m3u.grid(row = 7, column = 1, padx = 0, pady = 10)
        self.Button_Track_m3u = tk.Button(self.master, text = "ADD album   to .m3u", bg = "light green",width = 7, height = 2,command = self.Album_m3u, wraplength=80, justify=LEFT)
        self.Button_Track_m3u.grid(row = 7, column = 3, padx = 0, pady = 10)
        self.Button_Track_m3u = tk.Button(self.master, text = "ADD P-list   to .m3u", bg = "light green",width = 7, height = 2,command = self.PList_m3u, wraplength=80, justify=LEFT)
        self.Button_Track_m3u.grid(row = 7, column = 4, padx = 0, pady = 10)
        self.Button_Track_m3u = tk.Button(self.master, text = "DEL .m3u", bg = "#191",width = 7, height = 1,command = self.DelPL_m3u)
        self.Button_Track_m3u.grid(row = 8, column = 2, padx = 0, pady = 10)
        self.Button_repeat = tk.Button(self.master, text = "Repeat OFF", bg = "light blue",width = 7, height = 2,command = self.Repeat)
        self.Button_repeat.grid(row = 6, column = 3, padx = 0,)
        B15 = tk.Button(self.master, text = "Shutdown",   bg = "gray",width = 7, height = 2,command = self.Shutdown).grid(row = 8, column = 4)
    
        L1 = tk.Label(self.master, text="Track : " )
        L1.place(x=273, y=252)
        L2 = tk.Label(self.master, text="of" )
        L2.place(x=406, y=252)
        L3 = tk.Label(self.master, text="Played :" )
        L3.place(x=535, y=252)
        L4 = tk.Label(self.master,text=" of " )
        L4.place(x=660, y=252)
        L5 = tk.Label(self.master, text="Drive :" )
        L5.place(x=273, y=278)
        L6 = tk.Label(self.master, text="mins" )
        L6.place(x=398, y=455)
        L7 = tk.Label(self.master, text=".m3u" )
        L7.place(x=497, y=380)
        
        self.Disp_volume = tk.Label(self.master, height=1, width=3,bg='white',font = 40, padx = 10, pady = 10, borderwidth=2, relief="groove")
        self.Disp_volume.place(x=570, y=17)
        self.Disp_volume.config(text=self.volume)
        self.Disp_plist_name = tk.Label(self.master, height=1, width=57,bg='white',   anchor="w", borderwidth=2, relief="groove")
        self.Disp_plist_name.place(x=130, y=79)
        self.Disp_plist_name.config(text=self.que_dir)
        self.Disp_artist_name = tk.Label(self.master, height=1, width=50,bg='white', font = 40, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
        self.Disp_artist_name.place(x=130, y=109)
        self.Disp_album_name = tk.Label(self.master, height=1, width=50,bg='white',font = 40, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
        self.Disp_album_name.place(x=130, y=156)
        self.Disp_track_name = tk.Label(self.master, height=1, width=50,bg='white',font = 40, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
        self.Disp_track_name.place(x=130, y=204)
        self.Disp_track_no = tk.Label(self.master, height=1, width=6,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_track_no.place(x=335, y=252)
        self.Disp_Total_tunes = tk.Label(self.master, height=1, width=6,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_Total_tunes.place(x=435, y=252)
        self.Disp_Played = tk.Label(self.master, height=1, width=5,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_Played.place(x=605, y=252)
        self.Disp_track_len = tk.Label(self.master, height=1, width=5,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_track_len.place(x=695, y=252)
        self.Disp_Drive = tk.Label(self.master, height=1, width=20,bg= 'white', anchor="w", borderwidth=2, relief="groove")
        self.Disp_Drive.place(x=335, y=278)
        self.Disp_Track_m3u = tk.Text(self.master, height=1, width=18,bg= 'white', borderwidth=2, relief="groove")
        self.Disp_Track_m3u.place(x=348, y=375)
        self.Disp_sleep = tk.Label(self.master, height=1,bg='white',width = 4, font = 40, padx = 5, pady = 10, borderwidth=2, relief="groove")
        self.Disp_sleep.place(x=340, y=429)
        self.Disp_sleep.config(text='OFF')
        if os.path.exists("mp3.jpg"):
            self.load = Image.open("mp3.jpg")
            self.render = ImageTk.PhotoImage(self.load)
            self.img = tk.Label(self.master, image = self.render)
            self.img.place(x=1,y=255)
                    
        time.sleep(2)
        if not os.path.exists(self.que_dir):
            self.New_Track_List()
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
            self.m3us.insert(0,self.m3u_dir + "ALLTracks.m3u")
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.Show_Track()
            
    def Play(self):
        self.play = 0
        self.Start_Play()
        
    def Show_Track(self):
        if len(self.tunes) > 0:
            self.Disp_track_no.config(text =self.track_no+1)
            self.artist_name = (self.tunes[self.track_no].split('^')[0])
            self.album_name  = (self.tunes[self.track_no].split('^')[1])
            self.track_name  = (self.tunes[self.track_no].split('^')[2])
            self.drive_name  = (self.tunes[self.track_no].split('^')[3])
            self.track = os.path.join('/media/pi/',self.drive_name, self.artist_name, self.album_name, self.track_name)
            self.Disp_artist_name.config(text =self.artist_name)
            self.Disp_album_name.config(text =self.album_name)
            self.Disp_track_name.config(text =self.track_name)
            self.Disp_Played.config(text ="")
            self.Disp_Drive.config(fg = 'black')
            self.Disp_Drive.config(text =self.drive_name)
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

    def Show_Album_Pic(self):
        path = "/media/pi/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
        pictures = glob.glob(path)
        if len(pictures) > 0:
            self.image = pictures[0]
            self.load = Image.open(self.image)
            self.render = ImageTk.PhotoImage(self.load)
            self.img.config(image = self.render)
        elif os.path.exists("mp3.jpg"):
            self.load = Image.open("mp3.jpg")
            self.render = ImageTk.PhotoImage(self.load)
            self.img.config(image = self.render)
    
    def Start_Play(self):
        if len(self.tunes) > 0 and self.play == 0:
            self.Disp_track_no.config(text =self.track_no+1)
            self.artist_name = (self.tunes[self.track_no].split('^')[0])
            self.album_name  = (self.tunes[self.track_no].split('^')[1])
            self.track_name  = (self.tunes[self.track_no].split('^')[2])
            self.drive_name  = (self.tunes[self.track_no].split('^')[3])
            self.track = os.path.join('/media/pi/',self.drive_name, self.artist_name, self.album_name, self.track_name)
            rpistr = "mplayer " + '"' + self.track + '"'
            self.Disp_artist_name.config(text =self.artist_name)
            self.Disp_album_name.config(text =self.album_name)
            self.Disp_track_name.config(text =self.track_name)
            self.Disp_Drive.config(fg = 'black')
            self.Disp_Drive.config(text =self.drive_name)
            self.Disp_Track_m3u.delete('1.0','20.0')
            if os.path.exists(self.track):
                rpistr = "mplayer " + '"' + self.track + '"'
                audio = MP3(self.track)
                self.track_len = audio.info.length
                minutes = int(self.track_len // 60)
                seconds = int (self.track_len - (minutes * 60))
                self.Disp_track_len.config(text ="%02d:%02d" % (minutes, seconds % 60))
                self.p = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid)
                self.play = 1
                self.start = time.time()
                self.Button_Start.config(bg = "light gray",fg = "red",text = "Playing...")
                self.Button_Stop.config(bg = "red")
                path = "/media/pi/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" +  "*.jpg"
                pictures = glob.glob(path)
                if len(pictures) > 0:
                    self.image = pictures[0]
                    self.load = Image.open(self.image)
                    self.render = ImageTk.PhotoImage(self.load)
                    self.img.config(image = self.render)
                elif os.path.exists("mp3.jpg"):
                    self.load = Image.open("mp3.jpg")
                    self.render = ImageTk.PhotoImage(self.load)
                    self.img.config(image = self.render)
                time.sleep(2)
                self.playing()
            else:
                self.Disp_Drive.config(fg = 'red')
                self.Disp_Drive.config(text = self.drive_name + "-MISSING")
                stop = 0
                while (self.tunes[self.track_no].split('^')[3]) == self.drive_name and stop == 0:
                    self.track_no +=1
                    if self.track_no > len(self.tunes) - 1:
                        self.track_no = 0
                        stop = 1
                if self.play == 0:
                    self.Show_Track()
                else:
                    self.Start_Play()

    def playing(self):
        if self.sleep_time > 0:
           self.Disp_sleep.config(text =int((self.sleep_time_min - (time.time() - self.begin))/60))
           if int((self.sleep_time_min - (time.time() - self.begin))/60) < 1:
               self.Button_Sleep.config(bg = "red")
           
        if (time.time() - self.begin > self.sleep_time_min) and self.sleep_time > 0:
            os.system("sudo shutdown -h now")
            
        if os.path.exists(self.track):
            poll = self.p.poll()
            if poll != None and self.play == 1:
                self.play = 0
                if self.shuffle_on == 0:
                    self.track_no +=1
                else:
                    self.track_no = random.randint(1,len(self.tunes))
                if self.track_no > len(self.tunes) - 1 and self.repeat == 0:
                    self.play = 2
                    self.Button_Start.config(bg = "green",fg = "white",text = "Start Play")
                    self.Button_Stop.config(bg = "light gray")
                    self.track_no -=1
                    self.Show_Track()
                if self.track_no > len(self.tunes) - 1 and self.repeat == 1:
                    self.track_no = 0
                self.Start_Play()
            if self.play == 1:
                self.Button_Start.config(bg = "light gray",fg = "red",text = "Playing...")
                played = time.time() - self.start
                p_minutes = int(played // 60)
                p_seconds = int (played - (p_minutes * 60))
                self.Disp_Played.config(text ="%02d:%02d" % (p_minutes, p_seconds % 60))
                self.after(1000, self.playing)
        elif self.play == 1:
            self.Start_Play()

    def Next_Artist(self):
        stop = 0
        if len(self.tunes) > 0:
            while (self.tunes[self.track_no].split('^')[0]) == self.artist_name and stop == 0:
                self.track_no +=1
                if self.track_no > len(self.tunes) - 1:
                    self.track_no = 0
                    stop = 1
            if self.play == 0:
               self.Show_Track()
            else:
               os.killpg(self.p.pid, signal.SIGTERM)
               self.Start_Play()

    def Prev_Artist(self):
        stop = 0
        if len(self.tunes) > 0:
            while (self.tunes[self.track_no].split('^')[0]) == self.artist_name and stop == 0:
                self.track_no -=1
                if self.track_no < 0:
                    self.track_no = len(self.tunes)-1
                    stop = 1
            new_artist_name = self.tunes[self.track_no].split('^')[0]
            stop = 0
            while (self.tunes[self.track_no].split('^')[0]) == new_artist_name and stop == 0:
                self.track_no -=1
                if self.track_no < 0:
                    self.track_no = len(self.tunes)-1
                    stop = 1
            self.track_no +=1
            if self.track_no > len(self.tunes) - 1:
               self.track_no = 0
            if self.play == 0:
               self.Show_Track()
            else:
               os.killpg(self.p.pid, signal.SIGTERM)
               self.Button_Start.config(bg = "green")
               self.Button_Stop.config(bg = "light gray")
               self.Start_Play()

    def Next_Album(self):
        stop = 0
        if len(self.tunes) > 0:
            while (self.tunes[self.track_no].split('^')[1]) == self.album_name and stop == 0:
                self.track_no +=1
                if self.track_no > len(self.tunes) - 1:
                    self.track_no = 0
                    stop = 1
            if self.play == 0:
               self.Show_Track()
            else:
               os.killpg(self.p.pid, signal.SIGTERM)
               self.Start_Play()

    def Prev_Album(self):
        stop = 0
        if len(self.tunes) > 0:
            while (self.tunes[self.track_no].split('^')[1]) == self.album_name and stop == 0:
                self.track_no -=1
                if self.track_no < 0:
                    self.track_no = len(self.tunes)-1
                    stop = 1
            new_album_name = self.tunes[self.track_no].split('^')[1]
            stop = 0
            while (self.tunes[self.track_no].split('^')[1]) == new_album_name and stop == 0:
                self.track_no -=1
                if self.track_no < 0:
                    self.track_no = len(self.tunes)-1
                    stop = 1
            self.track_no +=1
            if self.track_no > len(self.tunes) - 1:
               self.track_no = 0
            if self.play == 0:
               self.Show_Track()
            else:
               os.killpg(self.p.pid, signal.SIGTERM)
               self.Start_Play()
         
    def Stop_Play(self):
        if self.play == 1:
           self.play = 0
           os.killpg(self.p.pid, signal.SIGTERM)
           self.track_no -=1
           self.Button_Start.config(bg = "green",fg = "white",text = "Start Play")
           self.Button_Stop.config(bg = "light gray")
        self.Disp_Track_m3u.delete('1.0','20.0')
        self.Show_Track()

    def Next_Track(self):
        if self.play == 1:
           os.killpg(self.p.pid, signal.SIGTERM)
           self.Start_Play()
        else:
           self.track_no +=1
           if self.track_no > len(self.tunes) -1:
              self.track_no = 0
           self.Show_Track()
           
    def Prev_Track(self):
        if self.play == 1:
           os.killpg(self.p.pid, signal.SIGTERM)
           self.track_no -=2
           if self.track_no < 0:
               self.track_no = len(self.tunes) -1
           self.Start_Play()
        else:
           self.track_no -=1
           if self.track_no < 0:
               self.track_no = len(self.tunes) -1
           self.Show_Track()

    def Next_m3u(self):
        if self.play == 1:
           os.killpg(self.p.pid, signal.SIGTERM)
        self.m3u_no +=1
        if self.m3u_no > len(self.m3us)-1:
            self.m3u_no = 0
        self.que_dir = self.m3us[self.m3u_no]
        if self.que_dir == self.m3u_dir + "ALLTracks.m3u" and self.m3u_no != 0:
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
        self.Disp_plist_name.config(text=self.que_dir)
        self.Disp_Total_tunes.config(text =len(self.tunes))
        self.track_no = 0
        self.Show_Track()
        
    def Prev_m3u(self):
        if self.play == 1:
           os.killpg(self.p.pid, signal.SIGTERM)
        self.m3u_no -=1
        if self.m3u_no < 0:
            self.m3u_no = 0
        self.que_dir = self.m3us[self.m3u_no]
        if self.que_dir == self.m3u_dir + "ALLTracks.m3u" and self.m3u_no != 0:
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
        self.Disp_plist_name.config(text=self.que_dir)
        self.Disp_Total_tunes.config(text =len(self.tunes))
        self.track_no = 0
        self.Show_Track()

    def DelPL_m3u(self):
        Name = str(self.Disp_Track_m3u.get('1.0','20.0')).strip()
        if len(Name) > 0 and Name != "ALLTracks":
            if os.path.exists(self.m3u_dir + Name + ".m3u"):
                os.remove(self.m3u_dir + Name + ".m3u")
                self.m3us = glob.glob(self.m3u_dir + "*.m3u")
                self.m3us.insert(0,self.m3u_dir + "ALLTracks.m3u")
        
    def Track_m3u(self):
        Name = str(self.Disp_Track_m3u.get('1.0','20.0')).strip()
        if len(Name) == 0:
            now = datetime.datetime.now()
            Name = now.strftime("%y%m%d%H%M%S")
            self.Disp_Track_m3u.insert(INSERT,Name)
        with open(self.m3u_dir + Name + ".m3u", 'a') as f:
            f.write("/media/pi/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" + self.track_name + "\n")
        self.m3us = glob.glob(self.m3u_dir + "*.m3u")
        self.m3us.insert(0,self.m3u_dir + "ALLTracks.m3u")
        
    def PList_m3u(self):
        if self.que_dir != self.m3u_dir + "ALLTracks.m3u":
            Name = str(self.Disp_Track_m3u.get('1.0','20.0')).strip()
            if len(Name) == 0:
                now = datetime.datetime.now()
                Name = now.strftime("%y%m%d%H%M%S")
                self.Disp_Track_m3u.insert(INSERT,Name)
                
            with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                for counter in range (0,len(self.tunes)):
                    self.artist_name = (self.tunes[counter].split('^')[0])
                    self.album_name  = (self.tunes[counter].split('^')[1])
                    self.track_name  = (self.tunes[counter].split('^')[2])
                    self.drive_name  = (self.tunes[counter].split('^')[3])
                    f.write("/media/pi/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/" + self.track_name + "\n")
            self.m3us = glob.glob(self.m3u_dir + "*.m3u")
            self.m3us.insert(0,self.m3u_dir + "ALLTracks.m3u")
        
    def Album_m3u(self):
        Name = str(self.Disp_Track_m3u.get('1.0','20.0')).strip()
        if len(Name) == 0:
            now = datetime.datetime.now()
            Name = now.strftime("%y%m%d%H%M%S")
            self.Disp_Track_m3u.insert(INSERT,Name)
        stop = 0
        while (self.tunes[self.track_no].split('^')[1]) == self.album_name and stop == 0:
            self.track_no -=1
            if self.track_no < 0:
                self.track_no = len(self.tunes)-1
                stop = 1
        self.track_no +=1
        if self.track_no > len(self.tunes) - 1:
           self.track_no = 0
        stop = 0
        while (self.tunes[self.track_no].split('^')[1]) == self.album_name and stop == 0:
            self.artist_name = (self.tunes[self.track_no].split('^')[0])
            self.album_name2  = (self.tunes[self.track_no].split('^')[1])
            self.track_name  = (self.tunes[self.track_no].split('^')[2])
            self.drive_name  = (self.tunes[self.track_no].split('^')[3])
            with open(self.m3u_dir + Name + ".m3u", 'a') as f:
                f.write("/media/pi/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name2 + "/" + self.track_name + "\n")
            self.track_no +=1
            if self.track_no > len(self.tunes) - 1:
               self.track_no = 0
               stop = 1
   
        self.m3us = glob.glob(self.m3u_dir + "*.m3u")
        self.m3us.insert(0,self.m3u_dir + "ALLTracks.m3u")
        
    def Shuffle_Tracks(self):
        if self.shuffle_on == 0:
            self.shuffle_on = 1
            self.Button_Shuffle.config(bg = "green",fg = "white",text = "Shuffle ON")
        else:
            self.shuffle_on = 0
            self.Button_Shuffle.config(bg = "light blue",fg = "blue",text = "Shuffle OFF")
        if self.play == 0:
            self.Show_Track()
        else:
            os.killpg(self.p.pid, signal.SIGTERM)
            self.Start_Play()

    def Repeat(self):
        if self.repeat == 0:
            self.repeat = 1
            self.Button_repeat.config(bg = "green",fg = "white",text = "Repeat ON")
        else:
            self.repeat = 0
            self.Button_repeat.config(bg = "light blue",fg = "blue",text = "Repeat OFF")
        if self.play == 0:
            self.Show_Track()
        else:
            os.killpg(self.p.pid, signal.SIGTERM)
            self.Start_Play()
            

    def Restore_Tracks(self):
        if self.play == 1:
           self.play = 0
           self.Button_Start.config(bg = "green",fg = "white",text = "Start Play")
           self.Button_Stop.config(bg = "light gray")
           os.killpg(self.p.pid, signal.SIGTERM)
        if self.sorted == 0:
           self.sorted = 1
           self.tunes.sort()
           self.track_no = 0
        else:
            stop = 0
            if len(self.tunes) > 0:
                while (self.tunes[self.track_no].split('^')[0][0]) == self.artist_name[0] and stop == 0:
                    self.track_no +=1
                    if self.track_no > len(self.tunes) - 1:
                        self.track_no = 0
                        stop = 1
        self.Show_Track()
                
    def New_Track_List(self):
        if self.play == 1:
           self.play = 0
           self.Button_Start.config(bg = "green",fg = "white",text = "Start Play")
           self.Button_Stop.config(bg = "light gray")
           os.killpg(self.p.pid, signal.SIGTERM)
        if os.path.exists(self.m3u_dir + "ALLTracks.m3u"):
            os.remove(self.m3u_dir + "ALLTracks.m3u")
        self.Disp_artist_name.config(text ="")
        self.Disp_album_name.config(text ="")
        self.Disp_track_name.config(text ="")
        self.Disp_Drive.config(text ="")
        self.Disp_track_no.config(text ="")
        self.Disp_Total_tunes.config(text ="")
        self.Disp_Played.config(text ="")
        self.Disp_track_len.config(text ="")
        self.sorted == 0
        Tracks = glob.glob("/media/pi/*/*/*/*.mp3")
        self.tunes = []
        if len (Tracks) > 0 :
            with open(self.m3u_dir + "ALLTracks.m3u", 'w') as f:
                for item in Tracks:
                    f.write("%s\n" % item)
            for counter in range (0,len(Tracks)):
                self.drive_name  = (Tracks[counter].split('/')[3])
                self.artist_name = (Tracks[counter].split('/')[4])
                self.album_name  = (Tracks[counter].split('/')[5])
                self.track_name  = (Tracks[counter].split('/')[6])
                self.tunes.append(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name)
            self.tunes.sort()
            self.track_no = 0
            self.Disp_plist_name.config(text=self.que_dir)
        else:
            self.Disp_artist_name.config(text =" NO TRACKS FOUND !")
        self.Disp_Total_tunes.config(text =len(self.tunes))
        self.m3us = glob.glob(self.m3u_dir + "*.m3u")
        self.m3us.insert(0,self.m3u_dir + "ALLTracks.m3u")
        self.Disp_plist_name.config(text = self.m3u_dir + "ALLTracks.m3u")
        self.Disp_Track_m3u.delete('1.0','20.0')
        if self.play == 0:
            self.Show_Track()
             
    def Shutdown(self):
        os.system("sudo shutdown -h now")

    def sleep(self):
        self.begin = time.time()
        if self.play == 0:
           self.sleep_time +=15.9
        else:
           self.sleep_time = int((self.sleep_time_min - (time.time() - self.begin))/60) + 16
        self.sleep_time = (int(self.sleep_time/15) * 15.2) 
        if self.sleep_time > 120:
            self.sleep_time = 0
        self.sleep_time_min = self.sleep_time * 60
        if self.sleep_time == 0:
            self.Button_Sleep.config(bg = "light blue")
            self.Disp_sleep.config(text ="OFF")
        else:
            self.Button_Sleep.config(bg = "orange")
            self.Disp_sleep.config(text =self.sleep_time)
        time.sleep(1)
            
    def exit(self):
        if self.play == 1:
           self.Button_Start.config(bg = "green")
           self.Button_Stop.config(bg = "light gray")
           os.killpg(self.p.pid, signal.SIGTERM)
        self.play = 0
        self.master.destroy()

    def volume_UP(self):
        m = alsaaudio.Mixer('PCM')
        self.volume +=2
        if self.volume > 100:
            self.volume = 100
        m.setvolume(self.volume)
        self.Disp_volume.config(text =self.volume)

    def volume_DN(self):
        m = alsaaudio.Mixer('PCM')
        self.volume -=2
        if self.volume < 0:
            self.volume = 0
        m.setvolume(self.volume)
        self.Disp_volume.config(text =self.volume)

def main(): 
    root = Tk()
    root.title("MP3 Player")
    root.wm_attributes('-type', 'splash')
    ex = Player()
    root.geometry("800x480")
    root.mainloop() 

if __name__ == '__main__':
    main() 
