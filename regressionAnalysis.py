import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.patches as patches
import datetime as dt
import csv
import sys
import time
import copy
from matplotlib.backends.backend_pdf import PdfPages

def analyseData(activitiesList,maxDate,minDate):
    
    dayLengthHours = 24
    nightStartTimeHours = 22
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

    # Creates a dictionary of dataItem objects, with start date keys of the form "2019-01-27" and timePeriod values
    dataItemsDict = {}
    for period in twentyFourHourPeriods:
        item = dataItem("dataItem",period)
        dataItemsDict[item.startDate] = item


    # Creates a dictionary of activity objects, with start date keys and of the form "2019-01-27" and values containing lists of activityInstance values
    activityInstancesDict = {}
    for activity in activitiesList:
        activitiesStartingOnDate = []
        key = activity.startDate
        if key not in activityInstancesDict:
            activityInstancesDict[key] = [activity]
        else:
            activityInstancesDict[key].append(activity)

    dataItemsDict = addActivitiesToDataItems(dataItemsDict,activitiesList)

    dataItemsDict = calculateAnalysisDataValues(dataItemsDict)


    dataItemsDict = setHoursSleptDayAndNight(dataItemsDict)

    testPrintSpecificItemKey(dataItemsDict,"2017-03-13")
    testPrintSpecificItemKey(dataItemsDict,"2017-03-14")

def convertSecondsToHMS(secs):
    return dt.timedelta(seconds=secs)

def setHoursSleptDayAndNight(dataItemsDict):
    for key in dataItemsDict:
        item = dataItemsDict[key]
        totalSecsSleptNight = 0.0
        for activity in item.nightActivities:
            totalSecsSleptNight += activity.getSeconds()
        item.sleptNightSeconds = totalSecsSleptNight
        totalSecsSleptDay = 0.0
        for activity in item.dayActivities:
            totalSecsSleptDay += activity.getSeconds()
        item.totalSecsSleptDay = totalSecsSleptDay
    return dataItemsDict

def testPrintSpecificItemKey(dataItemsDict,key):
    print dataItemsDict[key].starts
    print dataItemsDict[key].ends
    print "nightfall = "+str(dataItemsDict[key].nightfall)
    print "sleptNightSeconds = "+str(dataItemsDict[key].sleptNightSeconds)
    print "slept night H:M:S = "+str(dt.timedelta(seconds=dataItemsDict[key].sleptNightSeconds))
    print "sleptDaySeconds = "+str(dataItemsDict[key].sleptDaySeconds)
    print "slept day H:M:S = "+str(dt.timedelta(seconds=dataItemsDict[key].sleptDaySeconds))
    print "nightActivities"
    for item in dataItemsDict[key].nightActivities:
        print item
    print "dayActivities"
    for item in dataItemsDict[key].dayActivities:
        print item
    print ""

def testPrintDataItems(dataItemsDict):
    for key in dataItemsDict:
        print dataItemsDict[key].starts
        print dataItemsDict[key].ends
        print "nightfall = "+str(item.nightfall)
        print "nightActivities"
        for item in dataItemsDict[key].nightActivities:
            print item
        print "dayActivities"
        for item in dataItemsDict[key].dayActivities:
            print item
        print ""

def calculateAnalysisDataValues(dataItemsDict):

    for key in dataItemsDict:
        item = dataItemsDict[key]
        # Calculates total seconds slept during night
        secondsSleptInNight = 0.0
        for activity in item.nightActivities:
            #print "night activity = "+str(activity)
            if activity.name == "sleeping":
                secondsSleptInNight += activity.getSeconds()
        item.sleptNightSeconds = secondsSleptInNight
        # Calculates total seconds slept during day
        secondsSleptInDay = 0.0
        for activity in item.dayActivities:
            #print "day activity = "+str(activity)
            if activity.name == "sleeping":
                secondsSleptInDay += activity.getSeconds()
        item.sleptDaySeconds = secondsSleptInDay
        # Calculates total seconds slept in twentyFourHourPeriod
        item.slept24HoursSeconds = item.sleptNightSeconds + item.sleptDaySeconds
    return dataItemsDict

def addActivitiesToDataItems(dataItemsDict,activitiesList):
    activitiesSpillingIntoNextDay = []
    for key in dataItemsDict:
        item = dataItemsDict[key]
        period = item.twentyFourHourPeriod
        nightfall = item.nightfall
        nextDateKey = item.nextDate
        # Depending on when the activity starts and finishes
        for activity in activitiesList:
            # Add activity to the item.daytimeActivities list
            if activity.begins >= period.begins and activity.ends <= nightfall:
                #print "True:activity.begins >= period.begins and activity.ends <= nightfall"
                item.dayActivities.append(activity)
            # Add the activityto the item.nighttimeActivities list
            elif activity.begins >= nightfall and activity.ends <= item.ends:
                item.nightActivities.append(activity)
            # Split the activity in two and add part to the daytimeActivities list and part to the nighttimeActivities list
            elif activity.begins <= nightfall and activity.ends > nightfall:
                daytimeActivityPortion = copy.copy(activity)
                daytimeActivityPortion.ends = nightfall
                item.dayActivities.append(daytimeActivityPortion)
                nighttimeActivityPortion = copy.copy(activity)
                nighttimeActivityPortion.begins = nightfall
                item.nightActivities.append(nighttimeActivityPortion)
            # Split activity in two and add part to nighttimeActivities list and part to daytimeActivities list for following day
            elif activity.begins >= nightfall and activity.begins < item.ends and activity.ends > item.ends:
                nighttimeActivityPortion = copy.copy(activity)
                nighttimeActivityPortion.ends = item.ends
                item.nightActivities.append(nighttimeActivityPortion)
                nextDayActivityPortion = copy.copy(activity)
                nextDayActivityPortion.begins = item.ends
                nextDateDateItem = dataItemsDict[nextDateKey]
                nextDateDateItem.dayActivities.append(nextDayActivityPortion)
    return dataItemsDict

class dataItem(object):
    def __init__(self,name,twentyFourHourPeriod):
        self.name = name
        self.twentyFourHourPeriod = twentyFourHourPeriod
        startDate = self.twentyFourHourPeriod.begins
        nextDate = self.twentyFourHourPeriod.begins + dt.timedelta(days=1)
        self.startDate = startDate.strftime("%Y-%m-%d")
        self.nextDate = nextDate.strftime("%Y-%m-%d")
        self.nightActivities = []
        self.dayActivities = []
        self.subperiods = []
        self.day = twentyFourHourPeriod.subperiods["day"]
        self.night = twentyFourHourPeriod.subperiods["night"]
        self.nightfall = self.night.begins + dt.timedelta(hours=1)
        self.starts = self.twentyFourHourPeriod.begins
        self.ends = self.twentyFourHourPeriod.ends
        self.slept24HoursSeconds = 1.0
        self.sleptNightSeconds = 1.0
        self.sleptDaySeconds = 1.0
        self.avgNightSleepSeconds = 1.0
        self.avgDaySleepSeconds = 1.0
        self.goodNightsSleepScore = 1.0
        #print (self)
    def __str__(self):
        return "name:"+str(self.name)+"; startDate:"+str(self.startDate)+"; nightActivities:"+str(self.nightActivities)+"; dayActivities:"+str(self.dayActivities)+"; subperiods"+str(self.subperiods)+"; day:"+str(self.day)+"; night:"+str(self.night)+"; slept24HoursSeconds:"+str(self.slept24HoursSeconds)+"; sleptNightSeconds:"+str(self.sleptNightSeconds)+"; sleptDaySeconds:"+str(self.sleptDaySeconds)+"; avgNightSleepSeconds:"+str(self.avgNightSleepSeconds)+"; avgDaySleepSeconds:"+str(self.avgDaySleepSeconds)+"; goodNightsSleepScore:"+str(self.goodNightsSleepScore)

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
        startDate = self.begins
        self.startDate = startDate.strftime("%Y-%m-%d")
    def getSeconds(self):
        return (self.ends - self.begins).total_seconds()
    def getHoursMinutesSeconds(self):
        return str(dt.timedelta(seconds=self.getSeconds()))
    def __str__(self):
        return "name:"+str(self.name)+"; startDate:"+str(self.startDate)+" start:"+str(self.begins)+"; end:"+str(self.ends)+"; seconds:"+str(self.getSeconds())

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
