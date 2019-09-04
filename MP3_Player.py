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

# Pi_MP3_Player v4.0

class Player(Frame):
    
    def __init__(self):
        super().__init__() 
        self.initUI()
        
    def initUI(self): 
        self.que_dir = "/home/pi/Queue.txt"
        self.play = 0
        self.track_no = 0
        self.sleep_time = 0
        self.sleep_time_min = 0
        self.volume = 86
        self.shuffled = 0
        self.begin = time.time()
        m = alsaaudio.Mixer('PCM')
        m.setvolume(self.volume)
        self.B1 = tk.Button(self.master, text = "Start Play", bg = "green",fg = "white",width = 7, height = 2,font = 20, command = self.Start_Play)
        self.B1.grid(row = 0, column = 0, pady = 12)
        self.B2 =  tk.Button(self.master, text = "Stop  Play",width = 7, height = 2,command = self.Stop_Play)
        self.B2.grid(row = 0, column = 1,padx = 40)
        B3 =  tk.Button(self.master, text = " < Vol ",    bg = "yellow",width = 7, height = 2,command = self.volume_DN).grid(row = 0, column = 4,padx = 30)
        B4 =  tk.Button(self.master, text = "Vol >",      bg = "yellow",width = 7, height = 2,command = self.volume_UP).grid(row = 0, column = 5,padx = 30)
        B5 =  tk.Button(self.master, text = "< Artist",   bg = "light blue",width = 7, height = 2,command = self.Prev_Artist).grid(row = 2, column = 0,padx = 30)
        B6 =  tk.Button(self.master, text = "Artist >",   bg = "light blue",width = 7, height = 2,command = self.Next_Artist).grid(row = 2, column = 5,padx = 30)
        B7 =  tk.Button(self.master, text = "< Album",    bg = "light blue",width = 7, height = 2,command = self.Prev_Album).grid(row = 3, column = 0,padx = 30)
        B8 =  tk.Button(self.master, text = "Album>",     bg = "light blue",width = 7, height = 2,command = self.Next_Album).grid(row = 3, column = 5,padx = 30)
        B9 =  tk.Button(self.master, text = "< Track",    bg = "light blue",width = 7, height = 2,command = self.Prev_Track).grid(row = 4, column = 0,padx = 30)
        B10 = tk.Button(self.master, text = "Track >",    bg = "light blue",width = 7, height = 2,command = self.Next_Track).grid(row = 4, column = 5,padx = 30)
        B11 = tk.Button(self.master, text = "New Track List",width = 9, height = 2, command = self.New_Track_List).grid(row = 6, column = 5,padx = 30, pady = 40)
        B12 = tk.Button(self.master, text = "Shuffle Tracks", fg = "blue",width = 9, height = 2,command = self.Shuffle_Tracks).grid(row = 7, column = 3,padx = 30)
        B13 = tk.Button(self.master, text = "A-Z Artists", fg = "blue",width = 9, height = 2,command = self.Restore_Tracks).grid(row = 7, column = 4,padx = 30)
        B14 = tk.Button(self.master, text = "QUIT",       bg = "light green",width = 7, height = 2,command=self.exit).grid(row = 8, column = 0,padx = 30)
        B15 = tk.Button(self.master, text = "SLEEP",      bg = "light blue",width = 7, height = 2,command = self.sleep).grid(row = 8, column = 1,padx = 30)
        B16 = tk.Button(self.master, text = "Shutdown",   bg = "gray",width = 7, height = 2,command = self.Shutdown).grid(row = 8, column = 5,padx = 30)
    
        L1 = tk.Label(self.master, text="Track : " , font = 10)
        L1.place(x=138, y=232)
        L2 = tk.Label(self.master, text="of" , font = 10)
        L2.place(x=271, y=232)
        L3 = tk.Label(self.master, text="Played :" , font = 10)
        L3.place(x=400, y=232)
        L4 = tk.Label(self.master,text=" of " , font = 10)
        L4.place(x=525, y=232)
        L5 = tk.Label(self.master, text="Drive :" , font = 10)
        L5.place(x=140, y=275)
        L6 = tk.Label(self.master, text="mins" , font = 10)
        L6.place(x=345, y=412)

        self.Disp_volume = tk.Label(self.master, height=1, width=3,bg='white',font = 40, padx = 10, pady = 10, borderwidth=2, relief="groove")
        self.Disp_volume.place(x=600, y=17)
        self.Disp_volume.config(text=self.volume)
        self.Disp_artist_name = tk.Label(self.master, height=1, width=50,bg='white', font = 40, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
        self.Disp_artist_name.place(x=130, y=79)
        self.Disp_album_name = tk.Label(self.master, height=1, width=50,bg='white',font = 40, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
        self.Disp_album_name.place(x=130, y=126)
        self.Disp_track_name = tk.Label(self.master, height=1, width=50,bg='white',font = 40, padx = 10, pady = 10, anchor="w", borderwidth=2, relief="groove")
        self.Disp_track_name.place(x=130, y=174)
        self.Disp_track_no = tk.Label(self.master, height=1, width=6,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_track_no.place(x=200, y=232)
        self.Disp_Total_tunes = tk.Label(self.master, height=1, width=6,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_Total_tunes.place(x=300, y=232)
        self.Disp_Played = tk.Label(self.master, height=1, width=5,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_Played.place(x=470, y=232)
        self.Disp_track_len = tk.Label(self.master, height=1, width=5,bg='white',font = 40, borderwidth=2, relief="groove")
        self.Disp_track_len.place(x=560, y=232)
        self.Disp_Drive = tk.Label(self.master, height=1, width=20,bg= 'white', anchor="w", borderwidth=2, relief="groove")
        self.Disp_Drive.place(x=200, y=275)
        self.Disp_sleep = tk.Label(self.master, height=1,bg='white',width = 4, font = 40, padx = 5, pady = 10, borderwidth=2, relief="groove")
        self.Disp_sleep.place(x=278, y=400)
        self.Disp_sleep.config(text='OFF')
       
        time.sleep(2)
        if not os.path.exists(self.que_dir):
            self.New_Track_List()
        else:
            self.tunes = []        
            with open(self.que_dir,"r") as textobj:
               line = textobj.readline()
               while line:
                  self.tunes.append(line.strip())
                  line = textobj.readline()
            self.tunes.sort()
            self.Disp_Total_tunes.config(text =len(self.tunes))
            self.Show_Track()

    def Show_Track(self):
        if len(self.tunes) > 0:
            self.Disp_track_no.config(text =self.track_no+1)
            self.artist_name = (self.tunes[self.track_no].split('^')[0])
            self.album_name  = (self.tunes[self.track_no].split('^')[1])
            self.track_name  = (self.tunes[self.track_no].split('^')[2])
            self.drive_name  = (self.tunes[self.track_no].split('^')[3])
            self.track = "/media/pi/" + self.drive_name + "/" + self.artist_name + "/" + self.album_name + "/"  + self.track_name
            self.Disp_artist_name.config(text =self.artist_name)
            self.Disp_album_name.config(text =self.album_name)
            self.Disp_track_name.config(text =self.track_name)
            self.Disp_Drive.config(fg = 'black')
            self.Disp_Drive.config(text =self.drive_name)
            if os.path.exists(self.track):
                audio = MP3(self.track)
                self.track_len = audio.info.length
                minutes = int(self.track_len // 60)
                seconds = int (self.track_len - (minutes * 60))
                self.Disp_track_len.config(text ="%02d:%02d" % (minutes, seconds % 60))
            else:
                self.Disp_Drive.config(fg = 'red')
                self.Disp_Drive.config(text = self.drive_name + "-MISSING")
    
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
            if os.path.exists(self.track):
                rpistr = "mplayer " + '"' + self.track + '"'
                audio = MP3(self.track)
                self.track_len = audio.info.length
                minutes = int(self.track_len // 60)
                seconds = int (self.track_len - (minutes * 60))
                self.Disp_track_len.config(text ="%02d:%02d" % (minutes, seconds % 60))
                self.p = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid)
                self.play = 1
                self.track_no +=1
                if self.track_no > len(self.tunes) - 1:
                    self.track_no = 0
                self.start = time.time()
                self.B1.config(bg = "light gray")
                self.B2.config(bg = "red")
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
               self.B1.config(bg = "green")
               self.B2.config(bg = "light gray")
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
         
    def playing(self):
        if self.sleep_time > 0:
           self.Disp_sleep.config(text =int((self.sleep_time_min - (time.time() - self.begin))/60))
        if (time.time() - self.begin > self.sleep_time_min) and self.sleep_time > 0:
            print ("Shutting Down")
            os.system("sudo shutdown -h now")
        if os.path.exists(self.track):
            poll = self.p.poll()
            if poll != None and self.play == 1:
                self.play = 0
                self.Start_Play()
            if self.play == 1:
                played = time.time() - self.start
                p_minutes = int(played // 60)
                p_seconds = int (played - (p_minutes * 60))
                self.Disp_Played.config(text ="%02d:%02d" % (p_minutes, p_seconds % 60))
                self.after(1000, self.playing)
        else:
            self.Start_Play()

    def Stop_Play(self):
        if self.play == 1:
           self.play = 0
           os.killpg(self.p.pid, signal.SIGTERM)
           self.track_no -=1
           self.B1.config(bg = "green")
           self.B2.config(bg = "light gray")
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

    def Shuffle_Tracks(self):
        self.shuffled = 1
        shuffle(self.tunes)
        if self.play == 1:
           self.play = 0
           self.B1.config(bg = "green")
           self.B2.config(bg = "light gray")
           os.killpg(self.p.pid, signal.SIGTERM)
        self.track_no = 0
        self.Show_Track()

    def Restore_Tracks(self):
        if self.play == 1:
           self.play = 0
           self.B1.config(bg = "green")
           self.B2.config(bg = "light gray")
           os.killpg(self.p.pid, signal.SIGTERM)
        if self.shuffled == 1:
           self.shuffled = 0
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
           self.B1.config(bg = "green")
           self.B2.config(bg = "light gray")
           os.killpg(self.p.pid, signal.SIGTERM)
        if os.path.exists(self.que_dir):
            os.remove(self.que_dir)
        self.Disp_artist_name.config(text ="")
        self.Disp_album_name.config(text ="")
        self.Disp_track_name.config(text ="")
        self.Disp_Drive.config(text ="")
        self.Disp_track_no.config(text ="")
        self.Disp_Total_tunes.config(text ="")
        self.Disp_Played.config(text ="")
        self.Disp_track_len.config(text ="")
        Tracks = glob.glob("/media/pi/*/*/*/*.mp3")
        self.tunes = []
        if len (Tracks) > 0 :
            for counter in range (0,len(Tracks)):
                self.drive_name  = (Tracks[counter].split('/')[3])
                self.artist_name = (Tracks[counter].split('/')[4])
                self.album_name  = (Tracks[counter].split('/')[5])
                self.track_name  = (Tracks[counter].split('/')[6])
                with open(self.que_dir,"a") as f:
                    f.write(self.artist_name + "^" + self.album_name + "^" + self.track_name + "^" + self.drive_name + "\n")
            with open(self.que_dir,"r") as textobj:
               line = textobj.readline()
               while line:
                  self.tunes.append(line.strip())
                  line = textobj.readline()
            self.tunes.sort()
            self.track_no = 0
        else:
            self.Disp_artist_name.config(text =" NO TRACKS FOUND !")
        self.Disp_Total_tunes.config(text =len(self.tunes))
        if self.play == 0:
            self.Show_Track()
             
    def Shutdown(self):
        os.system("sudo shutdown -h now")

    def sleep(self):
        self.begin = time.time()
        if self.play == 0:
           self.sleep_time +=15
        else:
           self.sleep_time = int((self.sleep_time_min - (time.time() - self.begin))/60) + 16
        self.sleep_time = (int(self.sleep_time/15) * 15)
        if self.sleep_time > 120:
            self.sleep_time = 0
        self.sleep_time_min = self.sleep_time * 60
        if self.sleep_time == 0:
            self.Disp_sleep.config(text ="OFF")
        else:
            self.Disp_sleep.config(text =self.sleep_time)
            
    def exit(self):
        if self.play == 1:
           self.B1.config(bg = "green")
           self.B2.config(bg = "light gray")
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
    ex = Player()
    root.geometry("800x480")
    root.mainloop() 

if __name__ == '__main__':
    main() 
