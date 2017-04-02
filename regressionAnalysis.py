import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.patches as patches
import datetime as dt
import csv
import sys
import time
from matplotlib.backends.backend_pdf import PdfPages

def analyseData(activitiesList,maxDate,minDate):
    
    dayLengthHours = 24
    nightStartTimeHours = 23
    nightDurationHours = 8
    daytimeStartTimeHours = (nightStartTimeHours + nightDurationHours) % dayLengthHours

    # Creates array of twentyFourHourPeriods
    twentyFourHourPeriods = []
    startingPoint = minDate.begins + dt.timedelta(hours=daytimeStartTimeHours)
    endingPoint = maxDate.ends + dt.timedelta(hours=daytimeStartTimeHours)
    delta = endingPoint - startingPoint

    for i in range(delta.days + 1):
        day = timePeriod("24hours",startingPoint+dt.timedelta(days=i),startingPoint+dt.timedelta(days=i+1))
        twentyFourHourPeriods.append(day)

    # Creates array of all night periods
    nights = []
    startOfFirstNight = minDate.begins + dt.timedelta(hours=nightStartTimeHours) - dt.timedelta(days=1)
    for i in range(delta.days + 1):
        night = timePeriod("night",startOfFirstNight+dt.timedelta(days=i,hours=nightStartTimeHours+1),startOfFirstNight+dt.timedelta(days=i,hours=nightStartTimeHours+1+nightDurationHours))
        nights.append(night)

    # Adds nights to twentyFourHourPeriods
    for night in nights:
        for period in twentyFourHourPeriods:
            if night.begins >= period.begins and night.begins < period.ends:
                period.subperiods["night"] = night
    
    # Adds days to twentyFourHourPeriods
    for period in twentyFourHourPeriods:
        dawn = period.begins
        dusk = period.subperiods["night"].begins
        day = timePeriod("day",dawn,dusk)
        period.subperiods["day"] = day

    # Test print
    for period in twentyFourHourPeriods:
        print period
        #for subperiod in period.subperiods:
        #    print str(subperiod)
        print period.subperiods["day"]
        print period.subperiods["night"]
        print ""

    # Creates a dictionary of dataItem objects, with start date keys of the form "2019-01-27" and timePeriod values
    dataItemsDict = {}
    for period in twentyFourHourPeriods:
        item = dataItem("dataItem",period)
        dataItemsDict[item.startDate] = item

    print dataItemsDict

    # Creates a dictionary of activity objects, with start date keys and of the form "2019-01-27" and values containing lists of activityInstance values
    activityInstancesDict = {}
    for activity in activitiesList:
        activitiesStartingOnDate = []
        if len(activityInstancesDict[activity.startDate]) == 0:
            activityInstancesDict[activity.startDate] = [activity]
        else:
            activityInstancesDict[activity.startDate].append(activity)
    print activityInstancesDict

    addActivitiesToTwentyFourHourPeriods(dataItemsDict,twentyFourHourPeriodDict)

def addActivitiesToTwentyFourHourPeriods(activitiesDict,twentyFourHourPeriodDict):
    activitiesSpillingIntoNextDay = {}
    for key in twentyFourHourPeriodDict:
        for activityList in activitiesDict[key]:
        if len(activitiesDict[key]) > 0:
            for activity in activityList:
                if activity.begins >= twentyFourHourPeriodDict[key].begins and activity.ends <= twentyFourHourPeriodDict[key]:
                    twentyFourHourPeriodDict[key].activities.append(activity)

class dataItem(object):
    def __init__(self,name,twentyFourHourPeriod):
        self.name = name
        self.twentyFourHourPeriod = twentyFourHourPeriod
        startDate = self.twentyFourHourPeriod.begins
        self.startDate = startDate.strftime("%Y-%m-%d")
        self.activities = []
        self.subperiods = []
        self.nightSleepPeriods = []
        self.daySleepPeriods = []
        self.day = twentyFourHourPeriod.subperiods["day"]
        self.night = twentyFourHourPeriod.subperiods["night"]
        self.slept24HoursSeconds = 1.0
        self.sleptNightSeconds = 1.0
        self.sleptDaySeconds = 1.0
        self.avgNightSleepSeconds = 1.0
        self.avgDaySleepSeconds = 1.0
        self.goodNightsSleepScore = 1.0
        print (self)
    def __str__(self):
        return "name:"+str(self.name)+"; startDate:"+str(self.startDate)+"; activities:"+str(self.activities)+"; subperiods"+str(self.subperiods)+"; day:"+str(self.day)+"; night:"+str(self.night)+"; slept24HoursSeconds:"+str(self.slept24HoursSeconds)+"; sleptNightSeconds:"+str(self.sleptNightSeconds)+"; sleptDaySeconds:"+str(self.sleptDaySeconds)+"; avgNightSleepSeconds:"+str(self.avgNightSleepSeconds)+"; avgDaySleepSeconds:"+str(self.avgDaySleepSeconds)+"; goodNightsSleepScore:"+str(self.goodNightsSleepScore)

class timePeriod(object):
    def __init__(self,name,begins,ends):
        self.name = name
        self.begins = begins
        self.ends = ends
        self.activitiesAndTimePercentages = {}
        self.subperiods = {}
        self.seconds = (self.ends - self.begins).total_seconds()
        startDate = self.begins
        self.startDate = startDate.strftime("%Y-%m-%d")
    def __str__(self):
        return "timePeriod name:"+str(self.name)+"; startDate:"+str(self.startDate)+" starts:"+str(self.begins)+"; ends:"+str(self.ends)+"; seconds;"+str(self.seconds)

class activityInstance(object):
    def __init__(self,item):
        startDate = item[0]
        startTime = item[1]
        endTime = item[2]
        self.name = item[3]
        self.begins = dt.datetime.strptime(str(startDate)+" "+str(startTime), "%d/%m/%y %H:%M:%S")
        self.ends = dt.datetime.strptime(str(startDate)+" "+str(endTime), "%d/%m/%y %H:%M:%S")
        if self.ends < self.begins:
            self.ends += dt.timedelta(days=1)
        self.seconds = (self.ends - self.begins).total_seconds()
        startDate = self.begins
        self.startDate = startDate.strftime("%Y-%m-%d")
    def __str__(self):
        return "name:"+str(self.name)+"; startDate:"+str(self.startDate)+" start:"+str(self.begins)+"; end:"+str(self.ends)+"; seconds:"+str(self.seconds)

#        self.startDate = item[0]
#        self.formatDate(self.startDate)
#        self.startTime = item[1]
#        self.endTime = item[2]
#        self.name = item[3]
#        self.getStart()
#        print str(self)
#    def getStart(self):
#        self.startDatetime = time.strptime(str(self.startDay)+" "+str(self.startMonth)+" "+str(self.startYear), "%d %m %y")
#    # Extracts date information variables
#    def formatDate(self,unformattedDate):
#        date = dt.datetime.strptime(unformattedDate,"%d/%m/%y")
#        self.startDay = int(date.strftime("%d"))
#        self.startMonth = int(date.strftime("%m"))
#        self.startYear = int(date.strftime("%Y"))
#    def __str__(self):
#        return "activity name:"+self.name+"; startDate:"+self.startDate+"; startTime:"+self.startTime+"; endTime:"+self.endTime+"; datetime:"+str(self.startDatetime)

# Read data from csv file
def readDataFromFile(dataFile,activityName):
    f = open(dataFile,'rt')
    listOfInputLists = []
    try:
        reader = csv.reader(f)
        for row in reader:
            row.append(activityName)
            listOfInputLists.append(row)
    finally:
        f.close()
    return listOfInputLists

## Class to store time and date data read from file
#class activityInstance(object):
#    def __init__(self,listOfInputLists):
#        self.day = 0
#        self.month = 0
#        self.year = 0
#        self.formatDate(listOfInputLists[0])
#        self.startTime = self.formatTime(listOfInputLists[1])
#        self.stopTime = self.formatTime(listOfInputLists[2])
#        self.activityIndex = int(listOfInputLists[3])
#
#    # Extracts date information variables
#    def formatDate(self,unformattedDate):
#        date = dt.datetime.strptime(unformattedDate,"%d/%m/%y")
#        self.day = int(date.strftime("%d"))
#        self.month = int(date.strftime("%m"))
#        self.year = int(date.strftime("%Y"))
#
#    # Formats time as a decimal fraction of day, for use in graph
#    def formatTime(self,unformattedTime):
#        timeSinceMidnight = dt.datetime.strptime(unformattedTime,'%H:%M:%S')
#        midnight = dt.datetime(1900,1,1)
#        minutesSinceMidnight = ((timeSinceMidnight - midnight).total_seconds() / 60.0)
#        fractionOfDay = minutesSinceMidnight / MINUTES_IN_DAY
#        return fractionOfDay

# Formats data read from file as a list of eventInstance objects
def formatDataForAnalysis(listOfInputLists):
    activities = []
    for i in range(len(listOfInputLists)):
        for j in range(1,len(listOfInputLists[i])):
            nextActivityInstance = activityInstance(listOfInputLists[i][j])
            print "nextActivityInstance = "+str(nextActivityInstance)
            activities.append(nextActivityInstance)
    return activities

# Extracts earliest (min) and latest (max) dates from data, for use in setting graph limits
def getMaxAndMinDates(analysisDataList):
    earliestDate = analysisDataList[0]
    latestDate = analysisDataList[0]
    for item in analysisDataList:
        if item.begins < earliestDate.begins:
            earliestDate = item
        if item.ends > latestDate.ends:
            latestDate = item
    print "earliestDate = "+str(earliestDate)
    print "latestDate = "+str(latestDate)
    return latestDate, earliestDate
        
#    dateTimeList = []
#    for item in plotDataList:
#        nextDate = dt.datetime(item.year,item.month,item.day)
#        dateTimeList.append(nextDate)
#    maxDate = max(dateTimeList)
#    minDate = min(dateTimeList)
#    # Ensure minimun of three days displayed 
#    if not maxDate > minDate + dt.timedelta(days=1):
#        maxDate = minDate + dt.timedelta(days=2)
#    return maxDate, minDate

def go():
    dataFiles = ['sleepDataStartingMarch22.csv']#,'feedingDataStartingMarch22.csv']
    activityTypes = ['sleeping','feeding']
    listOfInputLists = []
    for i in range(len(dataFiles)):
        nextList = readDataFromFile(dataFiles[i],activityTypes[i])
        listOfInputLists.append(nextList)
    activitiesList = formatDataForAnalysis(listOfInputLists)
    maxDate, minDate = getMaxAndMinDates(activitiesList)

    analyseData(activitiesList,maxDate,minDate)

go()
