#!/usr/bin/env python
"""
GpsTrackPRocessing.py -- Convert NMEA GPS data to my evil purposes and do
subsequent processing.
Usage:
    $ ./GpsTrackProcessing.py

    Script will prompt for input file. File should be in raw NMEA GPS
    data format.

There are 19 interpreted sentences in NMEA data.  Of these, we are currently
only interested in the GPGGA GPS fix data and the GPRMC:
   $GPBOD - Bearing, origin to destination
   $GPBWC - Bearing and distance to waypoint, great circle
   $GPGGA - Global Positioning System Fix Data
   $GPGLL - Geographic position, latitude / longitude
   $GPGSA - GPS DOP and active satellites
   $GPGSV - GPS Satellites in view
   $GPHDT - Heading, True
   $GPR00 - List of waypoints in currently active route
   $GPRMA - Recommended minimum specific Loran-C data
   $GPRMB - Recommended minimum navigation info
   $GPRMC - Recommended minimum specific GPS/Transit data
   $GPRTE - Routes
   $GPTRF - Transit Fix Data
   $GPSTN - Multiple Data ID
   $GPVBW - Dual Ground / Water Speed
   $GPVTG - Track made good and ground speed
   $GPWPL - Waypoint location
   $GPXTE - Cross-track error, Measured
   $GPZDA - Date & Time
   http://aprs.gids.nl/nmea
"""
import sys
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import ParseNmea
import GpsTrackStats

def FindStartEndIndex(gpsData, stats):
    """
    Pick off the first N points then use a graphical method to find the
    actual start point. Return the index of this point
    """
    print ("Starting procedure to find start or end event")
    numberOfPoints = len(gpsData)
    offsetPoints = 0
    startIndex = 0
    keepGoing = True
    while keepGoing:
        print( "Find the start or end index:")
        print( "   Enter the number of points to use (max = %d) [%d]" % (len(gpsData) , numberOfPoints))
        theInput = input()
        if(len(theInput)>0):
            numberOfPoints = int(theInput)
            if numberOfPoints > len(gpsData):
                numberOfPoints = len(gpsData)

        print ("   Enter offset points to skip [%d]" % offsetPoints)
        theInput = input()
        if(len(theInput)>0):
            offsetPoints = int(theInput)

        print( "   Enter guess of index of the start point [%d]" % startIndex)
        theInput = input()
        if(len(theInput)>0):
            startIndex = int(theInput)

        [lats, longs] = stats.ExtractLatsAndLongs(gpsData, numberOfPoints)
        lats_offset = lats[offsetPoints:]
        longs_offset = longs[offsetPoints:]
        #plt.scatter(longs_offset, lats_offset, s = 5, c='r')
        plt.plot(longs_offset, lats_offset, 'r-o')
        plt.scatter(longs[startIndex], lats[startIndex], s = 20, c='g')
        plt.annotate(s="Start/End Point",
            xy=(longs[startIndex], lats[startIndex]),
            xytext=(-50,-30),
            textcoords='offset points',
            arrowprops=dict(facecolor='white', shrink=0.05))

        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('POSITION (in Decimal Degrees)')

    	#lay the image under the graph
    	#read a png file to map on
        # im = plt.imread('Image/JogStartSat.png')
        #adjust these values based on your location and map, lat and long are in decimal degrees
        # TRX = -77.102308          #top right longitude (orig -77.084388)
        # TRY = 38.839869            #top right latitude (orig 38.843056)
        # BLX = -77.104708          #bottom left longitude (orig -77.105987)
        # BLY = 38.838114             #bottom left latitude

        im = plt.imread('Image/JogStartMall.png')
        #adjust these values based on your location and map, lat and long are in decimal degrees
        TRX = -77.02749          #top right longitude (orig -77.084388)
        TRY = 38.88953            #top right latitude (orig 38.843056)
        BLX = -77.02957          #bottom left longitude (orig -77.105987)
        BLY = 38.88773             #bottom left latitude

        plt.imshow(im,extent=[BLX, TRX, BLY, TRY])
        plt.show()
        print( "Hit q to finish, anything else to try again")
        theInput = input()
        if theInput == 'q':
            keepGoing = False
    return startIndex

def PlotAnnotatedTrack(gpsData, annotation, IsCommute, stats):
    """
    Plot the track with split statistics labeled.
    """
    [lats, longs] = stats.ExtractLatsAndLongs(gpsData, len(gpsData))

    plt.plot(longs, lats, 'r-o')

    for item in annotation:
        msg = "%.2f, %s" % (item[1], item[2])
        plt.annotate(s=msg,
            xy=(longs[item[0]], lats[item[0]]),
            xytext=(20,10),
            textcoords='offset points',
            arrowprops=dict(facecolor='black', shrink=0.05))

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('POSITION (in Decimal Degrees)')

	#lay the image under the graph
	#read a png file to map on
    if IsCommute:
        im = plt.imread('Image/Comute1.png')
        TRX = -76.922429          #top right longitude (orig -77.084388)
        TRY = 38.905379            #top right latitude (orig 38.843056)
        BLX = -77.210489          #bottom left longitude (orig -77.105987)
        BLY = 38.761480             #bottom left latitude
    else:
        # im = plt.imread('Image/Jog1.png')
        # TRX = -77.084556          #top right longitude (orig -77.084388)
        # TRY = 38.843009            #top right latitude (orig 38.843056)
        # BLX = -77.105911          #bottom left longitude (orig -77.105987)
        # BLY = 38.829715             #bottom left latitude
        im = plt.imread('Image/MallJog.png')
        TRX = -77.00392          #top right longitude (orig -77.084388)
        TRY = 38.9005            #top right latitude (orig 38.843056)
        BLX = -77.0725          #bottom left longitude (orig -77.105987)
        BLY = 38.8717             #bottom left latitude
    #adjust these values based on your location and map, lat and long are in decimal degrees
    plt.imshow(im,extent=[BLX, TRX, BLY, TRY])

def BoundingBoxContainsCommute(bbox):
    """
    Check to see if the bounding box contains any of the standard
    routes
    """
    meanLat = bbox[0]
    meanLong = bbox[1]
    deltaLat = bbox[2]
    deltaLong = bbox[3]

    # Beltway Route
    Lat1a = -77.07626
    Long1b = 38.81345
    Lat1b = -77.095808967241382
    Long1b = 38.817804860344829

    #Quaker Lane Route
    Lat2a = -77.06596           # To Work
    Long2a = 38.81875
    Lat2b = -77.058113224299063 # Back Home
    Long2b = 38.813570009345796

    #Through Town Route
    Lat3 = -77.047123420689658
    Long3 = 38.847879744827587
    return True


def IsCommuteTrack(bbox, avgMph):
    """
    Check if this is most likely a commute track
    """
    if (avgMph < 10.0):
        return False
    else:
        print ("Avg MPH is %.1f, too fast for jog" % avgMph)
    if BoundingBoxContainsCommute(bbox):
        return True
    else:
        return False

def main():
    # construct the file parser
    parser = ParseNmea.ParseNmea()

    # construct the stats calculator
    stats = GpsTrackStats.GpsTrackStats()

    # select an input file
    #root = tk.Tk()
    #root.withdraw()
    inputFile = filedialog.askopenfilename(filetypes=[("text files", "*.TXT")])

    parser.ParseGpsNmeaFile(inputFile)
    # If the gpsData is length zero the file was not in the
    # GPGGA, GPRMC pair format. Try the just GPRMC format
    if len(parser.gpsData) == 0:
        parser.ParseGpsNmeaGprmcFile(sys.argv[1])
        if len(parser.gpsData) == 0:
            print("Error parsing data. Fix input file?")
            exit

    # make a local copy of the GPS data
    gpsData = parser.gpsData

    # done with the parser so nuke it (not required)
    del parser

    stats.ReportTimingStats(gpsData)
    bbox = stats.CalcBoundingBox(gpsData)
    print( "Bounding Box %.5f +/- %.6f, %.5f +/- %.6f" % \
        (bbox[0],bbox[2],bbox[1], bbox[3]))
    avgMph = stats.ExtractAvgMph(gpsData)
    if IsCommuteTrack(bbox, avgMph): # Too fast for a Jog1
        print( "Do Commute Logic") # Do Commute Version of things
        delta = stats.ReportTimingStats(gpsData)
        annotation = stats.CalculateTrackStatistics(gpsData, delta, 1609.34)
        PlotAnnotatedTrack(gpsData, annotation, True, stats)
    else:
        print( "Do Jogging logic")
        print( "Find Start/Stop Offsets? [y/n]")
        theInput = input()
        if theInput == 'y':
            startIndex = FindStartEndIndex(gpsData, stats)
            endIndex = FindStartEndIndex(gpsData, stats)
        else:
            print( "Enter start index")
            theInput = input()
            startIndex = int(theInput)
            print( "Enter stop index")
            theInput = input()
            endIndex = int(theInput)
        gpsData = gpsData[startIndex:endIndex]
        print( "Using Start Index of %d" % startIndex)
        print( "Using End Index of %d" % endIndex)
        delta = stats.ReportTimingStats(gpsData)
        annotation = stats.CalculateTrackStatistics(gpsData, delta, 402.336) # 1/4 mile distance
        PlotAnnotatedTrack(gpsData, annotation, False, stats)
    plt.plot(bbox[1], bbox[0], 'bo', markersize=15, label="Average Position")
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) != 1:
        print( __doc__)
        sys.exit()
    main()
