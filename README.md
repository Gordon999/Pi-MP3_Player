# Pi-MP3_Player
Pi-MP3_Player

Designed to be used with a Pi and the Pi 7" Touchscreen LCD. Playing tracks from USB sticks under /media/pi/

Tested on Pi 2 v1.1 and Pi 4, using Buster.

## LCD Screenshot

![screenshot](lcd.jpg)

I use the analog audio output on the 3.5" 4way socket. Bluetooth may work BUT I found it kept dropping out.

The default playlist is stored in  /home/pi/Documents/ALLTracks.m3u with the following format...

/media/pi/JUKEBOX/Roxy Music/For Your Pleasure/01 Do The Strand.mp3

/media/pi/JUKEBOX/Roxy Music/For Your Pleasure/02 Beauty Queen.mp3

in this case JUKEBOX is the name of the USB stick. 

You can put other .m3u files in the /home/pi/Documents/ directory and they can be accessed using the P-List buttons.
Remember to include the full path to the tracks.

On the USB sticks the format must be /Artist Name/Album Name/Track Name 
so in File Manager you will see the Tracks under /media/pi/JUKEBOX/Roxy Music/For Your Pleasure/

If you don't have a /home/pi/Documents/ALLTracks.m3u file when you start the script it will generate one from the tracks it finds on the USB stick(s).

Clicking on RELOAD ALLTracks will make a new playlist from the USB stick(s).

You can Play or Stop Tracks (remember to Stop BEFORE closing the script or click QUIT or SHUTDOWN ), Shuffle ON/OFF, Repeat ON/OFF, Chnage to A-Z Artist track order, switch to next / previous Artist, Album or Track.
Clicking A-Z Artists track after the initial sort will step through the artists from A to Z, showing the first one for each letter. To select others with the same starting letter use NEXT ARTIST.

You can also generate .m3u files. Choose the album or track from ALLTracks.m3u, enter a name for the .m3u list (if you don't it will make a name based on date & time), then press either ADD track to .m3u or ADD album to .m3u. ADD P-LIst to .m3u will allow you to make larger .m3us from other m3us. You can now access the new playlist with the P-list buttons.

You can also set a SLEEP period and the pi will shutdown after that, or SHUTDOWN will shutdown immediately.

You can add images of the album covers in the album directories, name ending in .jpg MAX sixe 218 x 218

You'll need to run...

sudo apt-get install python3-alsaaudio

sudo apt-get install mplayer

sudo pip3 install mutagen

To get the script to run at boot, assuming you are booting to the GUI

add the following line to /etc/xdg/lxsession/LXDE-pi/autostart

@/usr/bin/python3 /home/pi/MP3_player.py 

(NOTE: assuming you saved the script as MP3_player.py in /home/pi/)
