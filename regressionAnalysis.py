import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.patches as patches
import datetime as dt
import csv
import sys
import time
import copy
from pylab import figtext
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

    # Creates a dictionary of dataItem objects and a list of them ordered by date, with start date keys of the form "2019-01-27" 
    dataItemsDict = {}
    dataItemsDateOrderedList = []
    for period in twentyFourHourPeriods:
        item = dataItem("dataItem",period)
        dataItemsDict[item.startDate] = item
        dataItemsDateOrderedList.append(item)


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

    dataItemsDict = setLongestSleepDayAndNight(dataItemsDict)

    dataItemsDict = getmeanSleepDayAndNight(dataItemsDict)

    #testPrintSpecificItemKey(dataItemsDict,"2017-03-13")
    #testPrintSpecificItemKey(dataItemsDict,"2017-03-14")

    dataItemsDateOrderedList = removeMissingSleepDataItems(dataItemsDateOrderedList)

    plotDayNightHoursSleptBarChart(dataItemsDateOrderedList)

    plotDayNightLongestContinuousSleepBarChart(dataItemsDateOrderedList)

    plotDayMeanTimeSleepBarChart(dataItemsDateOrderedList)

def removeMissingSleepDataItems(dataItemsList):
    listWithMissingItemsRemoved = []
    minDayHoursSleepThreshhold = 1
    minNightHoursSleepThreshhold = 1
    secHourConversion = 60 * 60
    for item in dataItemsList:
        if (item.sleptDaySeconds/secHourConversion) >= minDayHoursSleepThreshhold and (item.sleptNightSeconds/secHourConversion) >= minNightHoursSleepThreshhold:
            listWithMissingItemsRemoved.append(item)
    return listWithMissingItemsRemoved

def plotDayMeanTimeSleepBarChart(dataItemsList):
    
    # Data to plot
    n_groups = len(dataItemsList)
    meanDaySleepTimes = []
    dates = []

    secHourConversion = 60 * 60

    for item in dataItemsList:
        # Adds mean day sleep time
        if item.startDate == '2017-03-21':
            meanDaySleepTimes.append(0)
            print "item.startDate = "+str(item.startDate)
        else:
            meanDaySleepTimes.append(item.meanSleepDaySecsSinceDaybreak/secHourConversion)
        #print "item.meanSleepDaySecsSinceDaybreak = "+str(item.meanSleepDaySecsSinceDaybreak)
        #print "item.meanSleepDaySecsSinceDaybreak = "+str(item.meanSleepDaySecsSinceDaybreak)
        # Adds date
        dates.append((item.starts).strftime("%A, %d %B %Y %H:%M"))

    # Create plot
    fig, ax = plt.subplots(figsize=(20,10))
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8

    #averageDaysSleep = round(sum(longestTimesSleptDuringDay)/len(longestTimesSleptDuringDay),2)

    item = dataItemsList[0]
    daybreak = item.starts.strftime("%H:%M")
    nightfall = item.nightfall.strftime("%H:%M")
    nightsEnd = item.ends.strftime("%H:%M")

    rects1 = plt.bar(index,meanDaySleepTimes, bar_width,
                    alpha=opacity,
                    color='b',
                    label='Day [Period='+'-'+'] (Avg='+str()+'hrs)')

    ax.grid(True)

    plt.xlabel('24-hour period beginning',fontweight='bold')
    plt.ylabel('Hours duration of longest continuous sleep during',fontweight='bold')
    plt.title('Longest continuous period of sleep during night and day, by date',fontweight='bold')
    plt.xticks(index + bar_width, dates)

    plt.legend()

    plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right')

    plt.tight_layout()

    # Saves to file 
    plt.savefig('meanDaySleeptimeBarchart.pdf')
    plt.savefig('meanDaySleeptimeBarchart.jpg')

    plt.show()

def plotDayNightLongestContinuousSleepBarChart(dataItemsList):
    
    # Data to plot
    n_groups = len(dataItemsList)
    longestTimesSleptDuringDay = []
    longestTimesSleptDuringNight = []
    dates = []

    secHourConversion = 60 * 60

    for item in dataItemsList:
        # Adds longest time slept each night
        longestSleep = dt.timedelta(days=0).total_seconds()
        for activity in item.nightActivities:
            if activity.name == "sleeping" and (activity.ends - activity.begins).total_seconds() > longestSleep:
                longestSleep = (activity.ends - activity.begins).total_seconds()
        longestTimesSleptDuringNight.append(longestSleep/secHourConversion)
        # Adds longest time slept each day
        longestSleep = dt.timedelta(days=0).total_seconds()
        for activity in item.dayActivities:
            if activity.name == "sleeping" and (activity.ends - activity.begins).total_seconds() > longestSleep:
                longestSleep = (activity.ends - activity.begins).total_seconds()
        longestTimesSleptDuringDay.append(longestSleep/secHourConversion)
        # Adds date
        dates.append((item.starts).strftime("%A, %d %B %Y %H:%M"))

    # Create plot
    fig, ax = plt.subplots(figsize=(20,10))
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8

    nightColour = 'b'
    dayColour = 'k'

    averageNightsSleep = round(sum(longestTimesSleptDuringNight)/len(longestTimesSleptDuringNight),2)
    averageDaysSleep = round(sum(longestTimesSleptDuringDay)/len(longestTimesSleptDuringDay),2)

    item = dataItemsList[0]
    daybreak = item.starts.strftime("%H:%M")
    nightfall = item.nightfall.strftime("%H:%M")
    nightsEnd = item.ends.strftime("%H:%M")

    rects1 = plt.bar(index+bar_width,longestTimesSleptDuringDay, bar_width,
                    alpha=opacity,
                    color=dayColour,
                    label='Day [Period='+nightfall+'-'+nightsEnd+'] (Avg='+str(averageDaysSleep)+'hrs)')
    

    rects2 = plt.bar(index,longestTimesSleptDuringNight, bar_width,
                    alpha=opacity,
                    color=nightColour,
                    label='Night [Period='+daybreak+'-'+nightfall+'] (Avg='+str(averageNightsSleep)+'hrs)')

    ax.grid(True)

    plt.xlabel('24-hour period beginning',fontweight='bold')
    plt.ylabel('Hours duration of longest continuous sleep during',fontweight='bold')
    plt.title('Longest continuous period of sleep during night and day, by date',fontweight='bold')
    plt.xticks(index + bar_width, dates)

    plt.legend()

    plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right')

    plt.tight_layout()

    # Saves to file 
    plt.savefig('longestContinuousSleepNightAndDayBarchart.pdf')
    plt.savefig('longestContinuousSleepNightAndDayBarchart.jpg')

    plt.show()

# Graph data using matplotlib visualization
def plotDayNightHoursSleptBarChart(dataItemsList): 

    # Data to plot
    n_groups = len(dataItemsList)
    timeSleptDuringDay = []
    timeSleptDuringNight = []
    timeSleptDuringNightAndDay = []
    dates = []

    secHourConversion = 60 * 60

    for item in dataItemsList:
        timeSleptDuringDay.append(item.sleptDaySeconds/secHourConversion)
        timeSleptDuringNight.append(item.sleptNightSeconds/secHourConversion)
        timeSleptDuringNightAndDay.append((item.sleptDaySeconds+item.sleptNightSeconds)/secHourConversion)
        #dates.append(item.startDate)
        dates.append((item.starts).strftime("%A, %d %B %Y %H:%M"))
    

    # Create plot
    fig, ax = plt.subplots(figsize=(20,10))
    index = np.arange(n_groups)
    bar_width = 0.25
    opacity = 0.8

    rects1 = plt.bar(index,timeSleptDuringDay, bar_width,
                    alpha=opacity,
                    color='b',
                    label='Day')


    rects2 = plt.bar(index+bar_width,timeSleptDuringNight, bar_width,
                    alpha=opacity,
                    color='r',
                    label='Night')
    
    rects3 = plt.bar(index+(2*bar_width),timeSleptDuringNightAndDay, bar_width,
                    alpha=opacity,
                    color='k',
                    label='Night and Day')

    ax.grid(True)

    plt.xlabel('24-hour period beginning',fontweight='bold')
    plt.ylabel('Hours Slept During',fontweight='bold')
    plt.title('Hours slept during night and day, by date',fontweight='bold')
    plt.xticks(index + bar_width, dates)
    plt.legend()

    plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right')

    plt.tight_layout()


    # Saves to file 
    plt.savefig('hoursSleptNightAndDayBarchart.pdf')
    plt.savefig('hoursSleptNightAndDayBarchart.jpg')

    plt.show()
#
#    # Set up an invisible background scatterplot give graph the correct size
#    # Make a series of events that are one day apart 
#    x = mpl.dates.drange(minDate,maxDate,dt.timedelta(days=1))
#
#    # Offset first event to top of graph to give correct height
#    x[0] += 0.85
#
#    # Extract the time using a modulo 1, and adding an arbitrary base date
#    # int used so that y-axis starts at midnight
#    times = x % 1 + int(x[0])
#    
#    fig = plt.figure()
#    fig.set_size_inches(11.69,8.27)
#    fig.suptitle('Daily Activity Patterns', fontsize=14, fontweight='bold')
#    ax = fig.add_subplot(111)
#
#    # Set background scatterplot to invisible 
#    ax.plot_date(x, times, 'ro', color='w', visible=False)
#    ax.yaxis_date()
#    fig.autofmt_xdate()
#    start, end = ax.get_ylim()
#
#    # Fix division sizes and labels to show hours on y-axis
#    hourDivision = 1.0 / 24.0
#    ax.yaxis.set_ticks(np.arange(start,end,hourDivision))
#    ax.set_yticklabels(['Midnight','1am','2am','3am','4am','5am','6am','7am','8am','9am','10am','11am','Midday','1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm','9pm','10pm','11pm','Midnight'])
#
#    # Iterate through data 
#    for i in range(0,len(data)):
#
#        # If period starts and finishes on different days, split and add to both days
#        if data[i].startTime > data[i].stopTime:
#            currentDataItem = data[i]
#            currentDate = dt.datetime(currentDataItem.year,currentDataItem.month,currentDataItem.day)
#            currentDate -= dt.timedelta(days=0.5)
#            tomorrow = currentDate + dt.timedelta(days=1)
#            plt.axvspan(xmin=currentDate, xmax=tomorrow, ymin=currentDataItem.startTime, ymax=1, facecolor=colourChoices[data[i].activityIndex], alpha=0.5)
#            theDayAfterTomorrow = tomorrow + dt.timedelta(days=1)
#            plt.axvspan(xmin=tomorrow, xmax=theDayAfterTomorrow, ymin=0, ymax=currentDataItem.stopTime, facecolor=colourChoices[data[i].activityIndex], alpha=0.5)
#
#        # Else, add to given day
#        else:
#            currentDataItem = data[i]
#            currentDate = dt.datetime(currentDataItem.year,currentDataItem.month,currentDataItem.day)
#            currentDate -= dt.timedelta(days=0.5)
#            tomorrow = currentDate + dt.timedelta(days=1)
#            plt.axvspan(xmin=currentDate, xmax=tomorrow, ymin=currentDataItem.startTime, ymax=currentDataItem.stopTime, facecolor=colourChoices[currentDataItem.activityIndex], alpha=0.5)
#
#    # Labels x and y axes
#    ax.set_ylabel('Hours of day',fontweight='bold')
#    ax.set_xlabel('Days: '+str(minDate.strftime("%A, %d %B %Y"))+' to '+str(maxDate.strftime("%A, %d %B %Y")),fontweight='bold')
#
#    ax.grid(True)
#
#    # Adds legend
#    labels = []
#    for i in range(len(activityChoices)):
#        labels.append(patches.Patch(color=colourChoices[i], label=activityChoices[i], alpha=0.5))
#    plt.legend(handles=labels)
#
#    # Ensures axis labels not cut off
#    plt.tight_layout()
#    # Ensures suptitle doesn't overlap graph
#    plt.subplots_adjust(top=0.92)
#
#    # Saves to file
#    plt.savefig('activityData.pdf')
#    plt.savefig('activityData.jpg')
#
#    # Shows file onscreen
#    plt.show()
#
def getmeanSleepDayAndNight(dataItemsDict):
    epoch = dt.datetime.utcfromtimestamp(0)
    for key in dataItemsDict:
        item = dataItemsDict[key]
        # Calculates mean night sleep time
        nightActivities = item.nightActivities
        minutesSleeping = []
        currentMinute = item.nightfall
        while currentMinute < item.ends:
            for activity in nightActivities:
                if currentMinute >= activity.begins and currentMinute <= activity.ends:
                    minutesSleeping.append(currentMinute)
            currentMinute += dt.timedelta(minutes=1)
        totalMinutesSleeping = dt.timedelta(0).total_seconds()
        for minute in minutesSleeping:
            totalMinutesSleeping += (minute-epoch).total_seconds()
        # Avoid dividing by zero
        if len(minutesSleeping) > 0:
            item.meanSleepTimeNight = totalMinutesSleeping / len(minutesSleeping)
        else:
            item.meanSleepTimeNight = 0
        item.meanSleepNightSecsSinceNightfall = item.meanSleepTimeNight-(item.nightfall-epoch).total_seconds()
        # Calculates mean day sleep time
        dayActivities = item.dayActivities
        minutesSleeping = []
        currentMinute = item.starts
        while currentMinute < item.nightfall:
            for activity in dayActivities:
                if currentMinute >= activity.begins and currentMinute <= activity.ends:
                    minutesSleeping.append(currentMinute)
            currentMinute += dt.timedelta(minutes=1)
        totalMinutesSleeping = dt.timedelta(0).total_seconds()
        for minute in minutesSleeping:
            totalMinutesSleeping += (minute-epoch).total_seconds()
        # Avoid dividing by zero
        if len(minutesSleeping) > 0:
            item.meanSleepTimeDay = totalMinutesSleeping / len(minutesSleeping)
        else:
            item.meanSleepTimeDay = 0
        item.meanSleepDaySecsSinceDaybreak = item.meanSleepTimeDay-(item.starts-epoch).total_seconds()
    return dataItemsDict

def setLongestSleepDayAndNight(dataItemsDict):
    for key in dataItemsDict:
        item = dataItemsDict[key]
        longestSleepNightInSecs = 0.0
        for activity in item.nightActivities:
            if activity.getSeconds() > longestSleepNightInSecs:
                longestSleepNightInSecs = activity.getSeconds()
        longestSleepDayInSecs = 0.0
        item.longestNightSleepSecs = longestSleepNightInSecs
        for activity in item.dayActivities:
            if activity.getSeconds() > longestSleepDayInSecs:
                longestSleepDayInSecs = activity.getSeconds()
        item.longestDaySleepSecs = longestSleepDayInSecs
    return dataItemsDict

def convertSecondsToHMS(secs):
    return str(dt.timedelta(seconds=secs))

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
    print "longestSleepNight = "+convertSecondsToHMS(dataItemsDict[key].longestNightSleepSecs)
    print "longestSleepDay = "+convertSecondsToHMS(dataItemsDict[key].longestDaySleepSecs)
    print "meanSleepTimeNight = "+str(dataItemsDict[key].meanSleepTimeNight)
    print "meanSleepTimeNight = "+str(dt.datetime.fromtimestamp(dataItemsDict[key].meanSleepTimeNight).strftime('%c'))
    print "meanSleepNightSecsSinceNightfall = "+str(dataItemsDict[key].meanSleepNightSecsSinceNightfall)
    print "meanSleepTimeDay = "+str(dataItemsDict[key].meanSleepTimeDay)
    print "meanSleepTimeDay = "+str(dt.datetime.fromtimestamp(dataItemsDict[key].meanSleepTimeDay).strftime('%c'))
    print "meanSleepDaySecsSinceDaybreak = "+str(dataItemsDict[key].meanSleepDaySecsSinceDaybreak)
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
        self.longestNightSleepSecs = 1.0
        self.longestDaySleepSecs = 1.0
        self.meanSleepTimeNight = 0
        self.meanSleepTimeDay = 0
        self.meanSleepNightSecsSinceNightfall = 0
        self.meanSleepDaySecsSinceDaybreak = 0
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
            #print "nextActivityInstance = "+str(nextActivityInstance)
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
    #print "earliestDate = "+str(earliestDate)
    #print "latestDate = "+str(latestDate)
    return latestDate, earliestDate

def go():
    dataFiles = ['sleepingData.csv']#,'feedingData.csv']
    activityTypes = ['sleeping','feeding']
    listOfInputLists = []
    for i in range(len(dataFiles)):
        nextList = readDataFromFile(dataFiles[i],activityTypes[i])
        listOfInputLists.append(nextList)
    activitiesList = formatDataForAnalysis(listOfInputLists)
    maxDate, minDate = getMaxAndMinDates(activitiesList)

    analyseData(activitiesList,maxDate,minDate)

go()
