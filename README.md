# GpsTrackTools
A collection of Python code for processing NMEA GPS tracks.

After I found my FitBit busted up and lying in the gutter, I had a new mission.
Make my own fitness tracker. I'm a big fan of the Adafruit company for DIY
electronics. So I bought a bunch of parts from them and made a Arduino based GPS
logger. I had intended to use it for keeping track of my jogging stats. But then
I ran into some mission creep. I started just taking the logger with me
everywhere. The tracker dumps NMEA sentences to an SD card. I then used these
bits of Python code to crunch the track info into something I found meaningful.
If  you find anything useful, feel free to clone it fork it or whatever floats
your boat.

Thanks go to several other internet warriors who posted their efforts so I
didn't have to start from zero. Becky Lewis who blogs at blog.scaryclam.co.uk
created a fine NMEA processing package for python (pynmea). Thanks Becky. Thanks
and apparently a beer go to A.Weiss at SparkFun Electronics. I used his
matplotlib framework to plot my GPS tracks on map images. Thanks A. I owe you a
beer.

S. Trickey 11/2015
