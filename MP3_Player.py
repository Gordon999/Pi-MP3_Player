#!/usr/bin/env python3
import tkinter as tk
from tkinter import *
import os, sys
import time
import subprocess
import signal
from random import shuffle
import glob
from mutagen.mp3 import MP3
import alsaaudio

class Player(Frame):
    
    def __init__(self):
        super().__init__() 
        self.initUI()
        
    def initUI(self): 
        global p,E1,E2,E3,E4,E5,E6,E7,E8,E9,E10,playing,que_dir,track_no,sleep,begin,sleep_min,tunes,volume
        que_dir = "/home/pi/Queue.txt"
        playing = 0
        track_no = 0
        sleep = 0
        sleep_min = 0
        volume = 85
        m = alsaaudio.Mixer('PCM')
        m.setvolume(volume)
        begin = time.time()
        B1 =  tk.Button(self.master, text = "Start Play", bg = "green",fg = "white",width = 7, height = 2,font = 20, command = self.Start_Play).grid(row = 0, column = 0, padx = 30,pady = 12)
        B2 =  tk.Button(self.master, text = "Stop  Play", bg = "red",width = 7, height = 2,command = self.Stop_Play).grid(row = 0, column = 1,padx = 30)
        B3 =  tk.Button(self.master, text = " < Vol ", bg = "yellow",width = 7, height = 2,command = self.Volume_DN).grid(row = 0, column = 4,padx = 30)
        B4 =  tk.Button(self.master, text = "Vol >", bg = "yellow",width = 7, height = 2,command = self.Volume_UP).grid(row = 0, column = 5,padx = 30)
        B5 =  tk.Button(self.master, text = "< Artist", bg = "light blue",width = 7, height = 2,command = self.Prev_Artist).grid(row = 2, column = 0,padx = 30)
        B6 =  tk.Button(self.master, text = "Artist >", bg = "light blue",width = 7, height = 2,command = self.Next_Artist).grid(row = 2, column = 5,padx = 30)
        B7 =  tk.Button(self.master, text = "< Album", bg = "light blue",width = 7, height = 2,command = self.Prev_Album).grid(row = 3, column = 0,padx = 30)
        B8 =  tk.Button(self.master, text = "Album>", bg = "light blue",width = 7, height = 2,command = self.Next_Album).grid(row = 3, column = 5,padx = 30)
        B9 =  tk.Button(self.master, text = "< Track", bg = "light blue",width = 7, height = 2,command = self.Prev_Track).grid(row = 4, column = 0,padx = 30)
        B10 = tk.Button(self.master, text = "Track >", bg = "light blue",width = 7, height = 2,command = self.Next_Track).grid(row = 4, column = 5,padx = 30)
        B11 = tk.Button(self.master, text = "New Track List",width = 9, height = 2, command = self.New_Track_List).grid(row = 6, column = 5,padx = 30, pady = 40)
        B12 = tk.Button(self.master, text = "Shuffle Tracks", fg = "blue",width = 9, height = 2,command = self.Shuffle_Tracks).grid(row = 7, column = 3,padx = 30)
        B13 = tk.Button(self.master, text = "A-Z Artists", fg = "blue",width = 9, height = 2,command = self.Restore_Tracks).grid(row = 7, column = 4,padx = 30)
        B14 = tk.Button(self.master, text = "QUIT", bg = "light green",width = 7, height = 2,command=self.exit).grid(row = 8, column = 0,padx = 30)
        B15 = tk.Button(self.master, text = "SLEEP", bg = "light blue",width = 7, height = 2,command = self.Sleep).grid(row = 8, column = 1,padx = 30)
        B16 = tk.Button(self.master, text = "Shutdown", bg = "gray",width = 7, height = 2,command = self.Shutdown).grid(row = 8, column = 5,padx = 30)
    
        L1 = tk.Label(self.master, text="Track : " , font = 10)
        L1.place(x=138, y=232)
        L2 = tk.Label(self.master, text="of" , font = 10)
        L2.place(x=271, y=232)
        L3 = tk.Label(self.master, text="Played :" , font = 10)
        L3.place(x=400, y=232)
        L4 = tk.Label(self.master,text=" of " , font = 10)
        L4.place(x=525, y=232)
        L5 = tk.Label(self.master, text="Drive :" , font = 10)
        L5.place(x=60, y=295)
        L6 = tk.Label(self.master, text="mins" , font = 10)
        L6.place(x=345, y=412)

        E1 = tk.Text(self.master, height=1, width=3, font = 40, padx = 10, pady = 10)
        E1.place(x=595, y=16)
        E1.insert(INSERT,volume)
        E2 = tk.Text(self.master, height=1, width=50, font = 40, padx = 10, pady = 10)
        E2.place(x=130, y=79)
        E3 = tk.Text(self.master, height=1, width=50, font = 40, padx = 10, pady = 10)
        E3.place(x=130, y=126)
        E4 = tk.Text(self.master, height=1, width=50, font = 40, padx = 10, pady = 10)
        E4.place(x=130, y=174)
        E5 = tk.Text(self.master, height=1, width=6, font = 40)
        E5.place(x=200, y=232)
        E6 = tk.Text(self.master, height=1, width=6, font = 40)
        E6.place(x=300, y=232)
        E7 = tk.Text(self.master, height=1, width=5, font = 40)
        E7.place(x=470, y=232)
        E8 = tk.Text(self.master, height=1, width=5, font = 40)
        E8.place(x=560, y=232)
        E9 = tk.Text(self.master, height=1, width=20)
        E9.place(x=130, y=295)
        E10 = tk.Text(self.master, height=1, width=4, font = 40, padx = 5, pady = 10)
        E10.place(x=278, y=398)
        E10.insert(INSERT,"OFF")
        
        
        time.sleep(2)
        if not os.path.exists(que_dir):
            self.New_Track_List()
        else:
            tunes = []        
            with open(que_dir,"r") as textobj:
               line = textobj.readline()
               while line:
                  tunes.append(line.strip())
                  line = textobj.readline()
            tunes.sort()
            E6.insert(INSERT,len(tunes))
            self.Show_Track()

    def Show_Track(self):
        global artist_name,tunes,album_name,drive_name,track_no
        if len(tunes) > 0:
            E5.delete('1.0','6.0')
            E5.insert(INSERT,track_no+1)
            artist_name = (tunes[track_no].split('^')[0])
            album_name  = (tunes[track_no].split('^')[1])
            track_name  = (tunes[track_no].split('^')[2])
            drive_name  = (tunes[track_no].split('^')[3])
            track = "/media/pi/" + drive_name + "/" + artist_name + "/" + album_name + "/"  + track_name
            E2.delete('1.0','50.0')
            E3.delete('1.0','50.0')
            E4.delete('1.0','50.0')
            E7.delete('1.0','6.0')
            E8.delete('1.0','6.0')
            E9.delete('1.0','20.0')
            E2.insert(INSERT,artist_name)
            E3.insert(INSERT,album_name)
            E4.insert(INSERT,track_name)
            E9.config(fg = 'black')
            E9.insert(INSERT,drive_name)
            if os.path.exists(track):
                audio = MP3(track)
                track_len = audio.info.length
                minutes = int(track_len // 60)
                seconds = int (track_len - (minutes * 60))
                E8.insert(INSERT,"%02d:%02d" % (minutes, seconds % 60))
            else:
                E9.config(fg = 'red')
                E9.insert(INSERT,"-MISSING")

    
    def Start_Play(self):
        global p,playing,start,track,track_len,track_mins,track_secs,tunes,artist_name,track_no,album_name,drive_name,begin
        if len(tunes) > 0 and playing == 0:
            E5.delete('1.0','6.0')
            E5.insert(INSERT,track_no+1)
            artist_name = (tunes[track_no].split('^')[0])
            album_name  = (tunes[track_no].split('^')[1])
            track_name  = (tunes[track_no].split('^')[2])
            drive_name  = (tunes[track_no].split('^')[3])
            track = "/media/pi/" + drive_name + "/" + artist_name + "/" + album_name + "/"  + track_name
            rpistr = "mplayer " + '"' + track + '"'
            E2.delete('1.0','50.0')
            E3.delete('1.0','50.0')
            E4.delete('1.0','50.0')
            E7.delete('1.0','6.0')
            E8.delete('1.0','6.0')
            E9.delete('1.0','20.0')
            E2.insert(INSERT,artist_name)
            E3.insert(INSERT,album_name)
            E4.insert(INSERT,track_name)
            E9.config(fg = 'black')
            E9.insert(INSERT,drive_name)
            if os.path.exists(track):
                rpistr = "mplayer " + '"' + track + '"'
                audio = MP3(track)
                track_len = audio.info.length
                minutes = int(track_len // 60)
                seconds = int (track_len - (minutes * 60))
                E8.insert(INSERT,"%02d:%02d" % (minutes, seconds % 60))
                p = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid)
                playing = 1
                track_no +=1
                if track_no > len(tunes) - 1:
                    track_no = 0
                start = time.time()
                time.sleep(2)
                self.playing()
            else:
                E9.config(fg = 'red')
                E9.insert(INSERT,"-MISSING")
                stop = 0
                while (tunes[track_no].split('^')[3]) == drive_name and stop == 0:
                    track_no +=1
                    if track_no > len(tunes) - 1:
                        track_no = 0
                        stop = 1
                if playing == 0:
                    self.Show_Track()
                else:
                    self.Start_Play()

    def Next_Artist(self):
        global tunes,track_no,artist_name,playing
        stop = 0
        if len(tunes) > 0:
            while (tunes[track_no].split('^')[0]) == artist_name and stop == 0:
                track_no +=1
                if track_no > len(tunes) - 1:
                    track_no = 0
                    stop = 1
            if playing == 0:
               self.Show_Track()
            else:
               os.killpg(p.pid, signal.SIGTERM)
               self.Start_Play()

    def Prev_Artist(self):
        global tunes,track_no,artist_name,playing
        stop = 0
        if len(tunes) > 0:
            while (tunes[track_no].split('^')[0]) == artist_name and stop == 0:
                track_no -=1
                if track_no < 0:
                    track_no = len(tunes)-1
                    stop = 1
            if playing == 0:
               self.Show_Track()
            else:
               os.killpg(p.pid, signal.SIGTERM)
               self.Start_Play()

    def Next_Album(self):
        global tunes,track_no,album_name,playing
        stop = 0
        if len(tunes) > 0:
            while (tunes[track_no].split('^')[1]) == album_name and stop == 0:
                track_no +=1
                if track_no > len(tunes) - 1:
                    track_no = 0
                    stop = 1
            if playing == 0:
               self.Show_Track()
            else:
               os.killpg(p.pid, signal.SIGTERM)
               self.Start_Play()

    def Prev_Album(self):
        global tunes,track_no,album_name,playing
        stop = 0
        if len(tunes) > 0:
            while (tunes[track_no].split('^')[1]) == album_name and stop == 0:
                track_no -=1
                if track_no < 0:
                    track_no = len(tunes)-1
                    stop = 1
            if playing == 0:
               self.Show_Track()
            else:
               os.killpg(p.pid, signal.SIGTERM)
               self.Start_Play()
         
    def playing(self):
        global playing,p,track_no,sleep,begin,sleep_min,track
        if sleep > 0:
           E10.delete('1.0','3.0')
           E10.insert(INSERT,int((sleep_min - (time.time() - begin))/60))
        if (time.time() - begin > sleep_min) and sleep > 0:
            print ("Shutting Down")
            os.system("sudo shutdown -h now")
        if os.path.exists(track):
            poll = p.poll()
            if poll != None and playing == 1:
                playing = 0
                self.Start_Play()
            if playing == 1:
                E7.delete('1.0','6.0')
                played = time.time() - start
                p_minutes = int(played // 60)
                p_seconds = int (played - (p_minutes * 60))
                E7.insert(INSERT,"%02d:%02d" % (p_minutes, p_seconds % 60))
                self.after(1000, self.playing)
        else:
            self.Start_Play()

    def Stop_Play(self):
        global playing, track_no
        if playing == 1:
           playing = 0
           os.killpg(p.pid, signal.SIGTERM)
           E2.delete('1.0','50.0')
           E3.delete('1.0','50.0')
           E4.delete('1.0','50.0')
           E7.delete('1.0','6.0')
           E8.delete('1.0','6.0')
           E9.delete('1.0','20.0')
           track_no -=1
        self.Show_Track()

    def Next_Track(self):
        global playing,track_no
        if playing == 1:
           os.killpg(p.pid, signal.SIGTERM)
           self.Start_Play()
        else:
           track_no +=1
           if track_no > len(tunes) -1:
              track_no = 0
           self.Show_Track()
           
    def Prev_Track(self):
        global playing,track_no
        if playing == 1:
           os.killpg(p.pid, signal.SIGTERM)
           track_no -=2
           if track_no < 0:
               track_no = len(tunes) -1
           self.Start_Play()
        else:
           track_no -=1
           if track_no < 0:
               track_no = len(tunes) -1
           self.Show_Track()

    def Shuffle_Tracks(self):
        global tunes,track_no,playing
        shuffle(tunes)
        if playing == 1:
           playing = 0
           os.killpg(p.pid, signal.SIGTERM)
        track_no = 0
        if playing == 0:
            self.Show_Track()
                
    def New_Track_List(self):
        global tunes,playing,que_dir,track_no
        if playing == 1:
           playing = 0
           os.killpg(p.pid, signal.SIGTERM)
        if os.path.exists(que_dir):
            os.remove(que_dir)
        Tracks = glob.glob("/media/pi/*/*/*/*.mp3")
        tunes = []
        if len (Tracks) > 0 :
            for counter in range (0,len(Tracks)):
                drive_name  = (Tracks[counter].split('/')[3])
                artist_name = (Tracks[counter].split('/')[4])
                album_name  = (Tracks[counter].split('/')[5])
                track_name  = (Tracks[counter].split('/')[6])
                with open(que_dir,"a") as f:
                    f.write(artist_name + "^" + album_name + "^" + track_name + "^" + drive_name + "\n")
       
            with open(que_dir,"r") as textobj:
               line = textobj.readline()
               while line:
                  tunes.append(line.strip())
                  line = textobj.readline()
            tunes.sort()
            track_no = 0
        else:
            E2.delete('1.0','50.0')
            E2.insert(INSERT," NO TRACKS FOUND !")
        E6.delete('1.0','7.0')
        E6.insert(INSERT,len(tunes))
        if playing == 0:
            self.Show_Track()
            
    def Restore_Tracks(self):
        global que_dir,tunes,playing,track_no
        if playing == 1:
           playing = 0
           os.killpg(p.pid, signal.SIGTERM)
        tunes = []
        if os.path.exists(que_dir):
            with open(que_dir,"r") as textobj:
               line = textobj.readline()
               while line:
                  tunes.append(line.strip())
                  line = textobj.readline()
            tunes.sort()
            track_no = 0
            if playing == 0:
                self.Show_Track()
              
    def Shutdown(self):
        os.system("sudo shutdown -h now")

    def Sleep(self):
        global sleep, sleep_min,begin
        begin = time.time()
        sleep +=15
        sleep = (int(sleep/15) * 15)
        if sleep > 120:
            sleep = 0
        sleep_min = sleep * 60
        E10.delete('1.0','6.0')
        if sleep == 0:
            E10.insert(INSERT,"OFF")
        else:
            E10.insert(INSERT,sleep)
    def exit(self):
        global playing
        if playing == 1:
           os.killpg(p.pid, signal.SIGTERM)
        playing = 0
        self.master.destroy()

    def Volume_UP(self):
        global volume
        m = alsaaudio.Mixer('PCM')
        volume +=2
        if volume > 100:
            volume = 100
        m.setvolume(volume)
        E1.delete('1.0','3.0')
        E1.insert(INSERT,volume)

    def Volume_DN(self):
        global volume
        m = alsaaudio.Mixer('PCM')
        volume -=2
        if volume < 0:
            volume = 0
        m.setvolume(volume)
        E1.delete('1.0','3.0')
        E1.insert(INSERT,volume)

def main(): 
    root = Tk()
    root.title("MP3 Player") 
    ex = Player()
    root.geometry("800x480")
    root.mainloop() 

if __name__ == '__main__':
    main() 
