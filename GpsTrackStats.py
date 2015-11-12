# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 22:57:00 2015

@author: Steve
"""

import datetime
import numpy

class GpsTrackStats:
    """
    A class to calculate statistics on GPS Tracks. The format for the 
    csv track data is:
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
    
    def ExtractTimeString(self, csvLine):
        """
        Extract the date and time from the csv formated line of GPS data
        Relevant fields are:
        0: Timestamp (HHmmss.mmm)
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
        
    def ExtractDateTime(self, csvLine):
        """
        Extract the date and time from a CSV input line and 
        stick them in a Python datetime object
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
        
    def ReportTimingStats(self, gpsData):
        """
        Report timing information about a list of CSV lines of GPS data points
        """
        print( "gpsData has length %d" % len(gpsData))
        print( "Start Time %s" % self.ExtractTimeString(gpsData[0]))
        startDateTime = self.ExtractDateTime(gpsData[0])
        print( "End Time   %s" % self.ExtractTimeString(gpsData[len(gpsData)-1]))
        endDateTime = self.ExtractDateTime(gpsData[len(gpsData)-1])
        deltaTime = endDateTime - startDateTime
        print( "Delta = ", deltaTime)
        return deltaTime

    def ExtractDistanceAndSpeed(self, gpsData):
        """
        Pluck off the distances and speeds
        4: distance (m)
        7: speed (knots)
        Put in a numpy array to facilitate some math operations
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
            theTime = self.ExtractDateTime(gpsData[i])
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

    def ExtractAvgMph(self, gpsData):
        """
        Calc avg MPH
        """
        speedMph = []
        for i in range(len(gpsData)):
            splitLine = gpsData[i].split(',')
            speedMph.append(float(splitLine[7])*1.15078) # Knots to mph
        return numpy.array(speedMph).mean()
    
    def CalcSplitIndices(self, distance, splitDistance):
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
    
    def ReportSplits(self, distance, time, splitDistance):
        print ("Split Times:")
        qmi = self.CalcSplitIndices(distance, splitDistance) #402.336
        annotation = []
        for i in range(len(qmi)-1):
            cumDist = distance[:qmi[i+1]].sum()*0.000621371 # meter to miles
            segmentDistance = distance[qmi[i]:qmi[i+1]].sum()*0.000621371
            t1 = time[qmi[i]]
            t2 = time[qmi[i+1]]
            delta = t2-t1
            pace = self.CalcMinPerMile(delta, segmentDistance)
            annotation.append([qmi[i+1],cumDist, pace])
            print( "%.3f, %.3f, %.1f, %s" % (cumDist, segmentDistance, delta.seconds, pace))
        cumDist = distance.sum()*0.000621371 # meter to miles
        segmentDistance = distance[qmi[-1]:].sum()*0.000621371
        t1 = time[qmi[-1]]
        t2 = time[-1]
        delta = t2-t1
        pace = self.CalcMinPerMile(delta, segmentDistance)
        annotation.append([len(distance)-1,cumDist, pace])
        print( "%.3f, %.3f, %.1f, %s" % (cumDist, segmentDistance, delta.seconds, pace))
        return annotation
    
    def CalcMinPerMile(self, timePeriod, miles):
        vanityFactor = 1.0 # Set this to fudge your time on the plots for demos :)
        minutesPerMile = ((timePeriod.seconds / miles)/60.0) * vanityFactor
        fractMinPerMile = minutesPerMile - int(minutesPerMile)
        result = "%02d:%04.1f" % (int(minutesPerMile), fractMinPerMile*60.0)
        return result
    
    def CalcSpeedMetrics(self, gpsData, delta):
        [distance, knots, mps, MpsCalc, mph, time] = self.ExtractDistanceAndSpeed(gpsData)
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
        result = self.CalcMinPerMile(delta, miles)
        print( "  " + result)
        return [distance, time]
    
    def CalculateTrackStatistics(self, gpsData, delta, splitDistance):
        """
        Report on the statistics of this gpsTrack
        Total distance
        Average speed
        Max speed
        1/4 mile splits
        """
        [distance,time] = self.CalcSpeedMetrics(gpsData, delta)
        annotation = self.ReportSplits(distance,time, splitDistance)
        return annotation
        
    def CalcBoundingBox(self, gpsData):
        print ("Calculating bounding box")
        [latitude, longitude] = self.ExtractLatsAndLongs(gpsData, len(gpsData))
        lats = numpy.array(latitude)
        longs = numpy.array(longitude)
        maxLat = lats.max()
        minLat = lats.min()
        maxLong = longs.max()
        minLong = longs.min()
        avgLat = lats.mean()
        avgLong = longs.mean()
        return [avgLat, avgLong, maxLat - minLat, maxLong - minLong]
    
    def ExtractLatsAndLongs(self, gpsData, numberOfPoints):
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