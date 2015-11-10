#!/usr/bin/env python
"""
ProcessGpsNmea.py -- Convert NMEA GPS data to csv and do subsequent processing.
Usage:
    $ ./ProcessGpsNmea.py input-file.txt
    where:
        input-file.txt is the raw NMEA GPS data

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
import datetime
import matplotlib.pyplot as plt
import numpy
import ParseNmea


def ExtractTimeString(csvLine):
    """
    Extract the date and time from the csv formated line of GPS data
    Fields are:
    0: Timestamp (HHmmss.mmm)
    1: latitude
    2: longitude
    3: altitude
    4: distance (m)
    5: number of satellites
    6: gps quality
    7: speed (knots)
    8: course
    9: datestamp (DDMMYY)
    """
    splitLine = csvLine.split(',')
    #time = splitLine[0][:6]
    time = splitLine[0][:2] + ":" + \
        splitLine[0][2:4] + ":" + \
        splitLine[0][4:6] + " " + \
        splitLine[9][2:4] + "/" + \
        splitLine[9][:2] + "/" + \
        splitLine[9][4:]
    return time

def ExtractDateTime(csvLine):
    """
    Extract the date and time and stick them in a Python datetime object
    """
    try:
        splitLine = csvLine.split(',')
        year = int("20" + splitLine[9][4:])
        month = int(splitLine[9][2:4])
        day = int(splitLine[9][:2])
        hour = int(splitLine[0][:2])
        minute = int(splitLine[0][2:4])
        second = int(splitLine[0][4:6])
        aDateTime = datetime.datetime(year, month, day, hour, minute, second)
    except:
        print( "Error parsing csvLine for datetime")
        print( csvLine)
        print("Element 9 = %s" % splitLine[9])
        print( "Element 0 = %s" % splitLine[0])
        aDateTime = "ERROR"
    return aDateTime

def ReportTimingStats(gpsData):
    print( "gpsData has length %d" % len(gpsData))
    print( "Start Time %s" % ExtractTimeString(gpsData[0]))
    startDateTime = ExtractDateTime(gpsData[0])
    print( "End Time   %s" % ExtractTimeString(gpsData[len(gpsData)-1]))
    endDateTime = ExtractDateTime(gpsData[len(gpsData)-1])
    deltaTime = endDateTime - startDateTime
    print( "Delta = ", deltaTime)
    return deltaTime

def CalcBoundingBox(gpsData):
    print ("Calculating bounding box")
    [latitude, longitude] = ExtractLatsAndLongs(gpsData, len(gpsData))
    lats = numpy.array(latitude)
    longs = numpy.array(longitude)
    maxLat = lats.max()
    minLat = lats.min()
    maxLong = longs.max()
    minLong = longs.min()
    avgLat = lats.mean()
    avgLong = longs.mean()
    return [avgLat, avgLong, maxLat - minLat, maxLong - minLong]

def ExtractLatsAndLongs(gpsData, numberOfPoints):
    """
    Pull off the first numberOfPoints of lat and long from gpsData
    Fields are:
    0: Timestamp (HHmmss.mmm)
    1: latitude
    2: longitude
    """
    print( "Extracting Lat/Long from data")
    lats = []
    longs = []
    for i in range(numberOfPoints):
        splitLine = gpsData[i].split(',')
        lats.append(float(splitLine[1]))
        longs.append(float(splitLine[2]))
    return [lats, longs]

def FindStartEndIndex(gpsData):
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

        [lats, longs] = ExtractLatsAndLongs(gpsData, numberOfPoints)
        lats_offset = lats[offsetPoints:]
        longs_offset = longs[offsetPoints:]
        #plt.scatter(longs_offset, lats_offset, s = 5, c='r')
        plt.plot(longs_offset, lats_offset, 'r-o')
        plt.scatter(longs[startIndex], lats[startIndex], s = 20, c='g')
        plt.annotate(s="Start/End Point",
            xy=(longs[startIndex], lats[startIndex]),
            xytext=(-50,-30),
            textcoords='offset points',
            arrowprops=dict(facecolor='black', shrink=0.05))

        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('POSITION (in Decimal Degrees)')

    	#lay the image under the graph
    	#read a png file to map on
        im = plt.imread('JogStartSat.png')
        #adjust these values based on your location and map, lat and long are in decimal degrees
        TRX = -77.102308          #top right longitude (orig -77.084388)
        TRY = 38.839869            #top right latitude (orig 38.843056)
        BLX = -77.104708          #bottom left longitude (orig -77.105987)
        BLY = 38.838114             #bottom left latitude

        #im = plt.imread('JogStartMall.png')
        #adjust these values based on your location and map, lat and long are in decimal degrees
        #TRX = -77.02749          #top right longitude (orig -77.084388)
        #TRY = 38.88953            #top right latitude (orig 38.843056)
        #BLX = -77.02957          #bottom left longitude (orig -77.105987)
        #BLY = 38.88773             #bottom left latitude

        # map version
        #TRX = -77.101736          #top right longitude (orig -77.084388)
        #TRY = 38.839353            #top right latitude (orig 38.843056)
        #BLX = -77.104546          #bottom left longitude (orig -77.105987)
        #BLY = 38.838198             #bottom left latitude

        plt.imshow(im,extent=[BLX, TRX, BLY, TRY])
        plt.show()
        print( "Hit q to finish, anything else to try again")
        theInput = input()
        if theInput == 'q':
            keepGoing = False
    return startIndex

def ExtractDistanceAndSpeed(gpsData):
    """
    Pluck off the distances and speeds
    4: distance (m)
    x: speed (knots)
    """
    distance = []
    speedKnts = []
    speedMps = []
    speedMpsCalc = []
    speedMph = []
    timeStamp = []
    lastTime = 0

    for i in range(len(gpsData)):
        splitLine = gpsData[i].split(',')
        distance.append(float(splitLine[4]))
        speedKnts.append(float(splitLine[7]))
        speedMps.append(float(splitLine[7])*0.514444) # Knots to m/s
        speedMph.append(float(splitLine[7])*1.15078) # Knots to mph
        theTime = ExtractDateTime(gpsData[i])
        timeStamp.append(theTime)
        if i == 0:
            speedMpsCalc.append(0)
        else:
            speedMpsCalc.append(distance[i]/(theTime-lastTime).seconds)
        lastTime = theTime
    return [numpy.array(distance), \
            numpy.array(speedKnts), \
            numpy.array(speedMps), \
            numpy.array(speedMpsCalc), \
            numpy.array(speedMph), timeStamp]

def ExtractAvgMph(gpsData):
    """
    Calc avg MPH
    """
    speedMph = []
    for i in range(len(gpsData)):
        splitLine = gpsData[i].split(',')
        speedMph.append(float(splitLine[7])*1.15078) # Knots to mph
    return numpy.array(speedMph).mean()

def CalcSplitIndices(distance, splitDistance):
    sum = 0.0
    splitIndex = [0] # split indices
    nextSplit = splitDistance # 402.336 # meters
    index = 0
    for segment in distance:
        sum += segment
        if(sum > nextSplit):
            splitIndex.append(index)
            nextSplit += splitDistance
        index += 1
    #for i in range(len(qmi)-1):
    #    print distance[:qmi[i+1]].sum()*0.000621371 # meter to miles
    return splitIndex

def ReportSplits(distance, time, splitDistance):
    print ("Split Times:")
    qmi = CalcSplitIndices(distance, splitDistance) #402.336
    annotation = []
    for i in range(len(qmi)-1):
        cumDist = distance[:qmi[i+1]].sum()*0.000621371 # meter to miles
        segmentDistance = distance[qmi[i]:qmi[i+1]].sum()*0.000621371
        t1 = time[qmi[i]]
        t2 = time[qmi[i+1]]
        delta = t2-t1
        pace = CalcMinPerMile(delta, segmentDistance)
        annotation.append([qmi[i+1],cumDist, pace])
        print( "%.3f, %.3f, %.1f, %s" % (cumDist, segmentDistance, delta.seconds, pace))
    cumDist = distance.sum()*0.000621371 # meter to miles
    segmentDistance = distance[qmi[-1]:].sum()*0.000621371
    t1 = time[qmi[-1]]
    t2 = time[-1]
    delta = t2-t1
    pace = CalcMinPerMile(delta, segmentDistance)
    annotation.append([len(distance)-1,cumDist, pace])
    print( "%.3f, %.3f, %.1f, %s" % (cumDist, segmentDistance, delta.seconds, pace))
    return annotation

def CalcMinPerMile(timePeriod, miles):
    vanityFactor = 1.0 # Set this to fudge your time on the plots for demos :)
    minutesPerMile = ((timePeriod.seconds / miles)/60.0) * vanityFactor
    fractMinPerMile = minutesPerMile - int(minutesPerMile)
    result = "%02d:%04.1f" % (int(minutesPerMile), fractMinPerMile*60.0)
    return result

def CalcSpeedMetrics(gpsData, delta):
    [distance, knots, mps, MpsCalc, mph, time] = ExtractDistanceAndSpeed(gpsData)
    print ("Max speeds:")
    print ("  knots: %.3f" % knots.max())
    print ("  m/s  : %.3f" % mps.max())
    print ("  m/s c: %.3f" % MpsCalc.max())
    print ("  mph  : %.3f" % mph.max())
    print( "Average speeds:")
    print( "  knots: %.3f" % knots.mean())
    print( "  m/s  : %.3f" % mps.mean())
    print( "  m/s c: %.3f" % MpsCalc.mean())
    print( "  mph  : %.3f" % mph.mean())
    print( "Total distance:")
    print( "  km   : %.3f" % (distance.sum()/1000.))
    miles = distance.sum() * 0.000621371 # meter to miles
    print( "  miles : %.3f" % (miles))
    print( "Average pace:")
    result = CalcMinPerMile(delta, miles)
    print( "  " + result)
    return [distance, time]

def CalculateTrackStatistics(gpsData, delta, splitDistance):
    """
    Report on the statistics of this gpsTrack
    Total distance
    Average speed
    Max speed
    1/4 mile splits
    """
    [distance,time] = CalcSpeedMetrics(gpsData, delta)
    annotation = ReportSplits(distance,time, splitDistance)
    return annotation

def PlotAnnotatedTrack(gpsData, annotation, IsCommute):
    """
    Plot the track with split statistics labeled.
    """
    [lats, longs] = ExtractLatsAndLongs(gpsData, len(gpsData))

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
        im = plt.imread('Comute1.png')
        TRX = -76.922429          #top right longitude (orig -77.084388)
        TRY = 38.905379            #top right latitude (orig 38.843056)
        BLX = -77.210489          #bottom left longitude (orig -77.105987)
        BLY = 38.761480             #bottom left latitude
    else:
        im = plt.imread('Jog1.png')
        TRX = -77.084556          #top right longitude (orig -77.084388)
        TRY = 38.843009            #top right latitude (orig 38.843056)
        BLX = -77.105911          #bottom left longitude (orig -77.105987)
        BLY = 38.829715             #bottom left latitude
        #im = plt.imread('MallJog.png')
        #TRX = -77.00392          #top right longitude (orig -77.084388)
        #TRY = 38.9005            #top right latitude (orig 38.843056)
        #BLX = -77.0725          #bottom left longitude (orig -77.105987)
        #BLY = 38.8717             #bottom left latitude
    #adjust these values based on your location and map, lat and long are in decimal degrees
    implot = plt.imshow(im,extent=[BLX, TRX, BLY, TRY])

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
    parser = ParseNmea.ParseNmea()
    
    parser.ParseGpsNmeaFile(sys.argv[1])
    if len(parser.gpsData) == 0:
        parser.ParseGpsNmeaGprmcFile(sys.argv[1])
        
    gpsData = parser.gpsData

    ReportTimingStats(gpsData)
    bbox = CalcBoundingBox(gpsData)
    print( "Bounding Box %.5f +/- %.6f, %.5f +/- %.6f" % \
        (bbox[0],bbox[2],bbox[1], bbox[3]))
    avgMph = ExtractAvgMph(gpsData)
    if IsCommuteTrack(bbox, avgMph): # Too fast for a Jog1
        print( "Do Commute Logic") # Do Commute Version of things
        delta = ReportTimingStats(gpsData)
        annotation = CalculateTrackStatistics(gpsData, delta, 1609.34)
        PlotAnnotatedTrack(gpsData, annotation, True)
    else:
        print( "Do Jogging logic")
        print( "Find Start/Stop Offsets? [y/n]")
        theInput = input()
        if theInput == 'y':
            startIndex = FindStartEndIndex(gpsData)
            endIndex = FindStartEndIndex(gpsData)
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
        delta = ReportTimingStats(gpsData)
        annotation = CalculateTrackStatistics(gpsData, delta, 402.336) # 1/4 mile distance
        PlotAnnotatedTrack(gpsData, annotation, False)
    plt.plot(bbox[1], bbox[0], 'bo', markersize=15, label="Average Position")
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print( __doc__)
        sys.exit()
    main()
