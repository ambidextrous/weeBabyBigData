import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.patches as patches
import datetime as dt
import csv
import sys
from matplotlib.backends.backend_pdf import PdfPages

MINUTES_IN_DAY = 1440.0

# Graph data using matplotlib visualization
def plotData(data,maxDate,minDate): 
    colourChoices = ['b','r','g','y']
    activityChoices = ['Sleeping','Feeding']
    # Set up an invisible background scatterplot give graph the correct size
    # Make a series of events that are one day apart 
    x = mpl.dates.drange(minDate,maxDate,dt.timedelta(days=1))

    # Offset first event to top of graph to give correct height
    x[0] += 0.85

    # Extract the time using a modulo 1, and adding an arbitrary base date
    # int used so that y-axis starts at midnight
    times = x % 1 + int(x[0])
    
    fig = plt.figure()
    fig.set_size_inches(11.69,8.27)
    fig.suptitle('Daily Activity Patterns', fontsize=14, fontweight='bold')
    ax = fig.add_subplot(111)

    # Set background scatterplot to invisible 
    ax.plot_date(x, times, 'ro', color='w', visible=False)
    ax.yaxis_date()
    fig.autofmt_xdate()
    start, end = ax.get_ylim()

    # Fix division sizes and labels to show hours on y-axis
    hourDivision = 1.0 / 24.0
    ax.yaxis.set_ticks(np.arange(start,end,hourDivision))
    ax.set_yticklabels(['Midnight','1am','2am','3am','4am','5am','6am','7am','8am','9am','10am','11am','Midday','1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm','9pm','10pm','11pm','Midnight'])

    # Iterate through data 
    for i in range(0,len(data)):

        # If period starts and finishes on different days, split and add to both days
        if data[i].startTime > data[i].stopTime:
            currentDataItem = data[i]
            currentDate = dt.datetime(currentDataItem.year,currentDataItem.month,currentDataItem.day)
            currentDate -= dt.timedelta(days=0.5)
            tomorrow = currentDate + dt.timedelta(days=1)
            plt.axvspan(xmin=currentDate, xmax=tomorrow, ymin=currentDataItem.startTime, ymax=1, facecolor=colourChoices[data[i].activityIndex], alpha=0.5)
            theDayAfterTomorrow = tomorrow + dt.timedelta(days=1)
            plt.axvspan(xmin=tomorrow, xmax=theDayAfterTomorrow, ymin=0, ymax=currentDataItem.stopTime, facecolor=colourChoices[data[i].activityIndex], alpha=0.5)

        # Else, add to given day
        else:
            currentDataItem = data[i]
            currentDate = dt.datetime(currentDataItem.year,currentDataItem.month,currentDataItem.day)
            currentDate -= dt.timedelta(days=0.5)
            tomorrow = currentDate + dt.timedelta(days=1)
            plt.axvspan(xmin=currentDate, xmax=tomorrow, ymin=currentDataItem.startTime, ymax=currentDataItem.stopTime, facecolor=colourChoices[currentDataItem.activityIndex], alpha=0.5)

    # Labels x and y axes
    ax.set_ylabel('Hours of day',fontweight='bold')
    ax.set_xlabel('Days: '+str(minDate.strftime("%A, %d %B %Y"))+' to '+str(maxDate.strftime("%A, %d %B %Y")),fontweight='bold')

    ax.grid(True)

    # Adds legend
    labels = []
    for i in range(len(activityChoices)):
        labels.append(patches.Patch(color=colourChoices[i], label=activityChoices[i], alpha=0.5))
    plt.legend(handles=labels)

    # Ensures axis labels not cut off
    plt.tight_layout()
    # Ensures suptitle doesn't overlap graph
    plt.subplots_adjust(top=0.92)

    # Saves to file
    plt.savefig('activityData.pdf')
    plt.savefig('activityData.jpg')

    # Shows file onscreen
    plt.show()


def formatDataForAnalysis(plotDataList,maxDate,minDate):
    nighttimeBegins = dt.time(23)
    daytimeBegins = dt.time(07)
    twentyFourHourPeriods = []

    startTimePoint = minDate + daytimeBegins
    endingPoint = maxDate + daytimeBegins
    delta = endingPoint - startingPoint

    for i in range(delta.days + 1):
        day = timePeriod(startingPoint+dt.timedelta(days=i),startingPoint+dt.timedelta(days=i+1))
        days.append(day)

    nights = []
    startOfFirstNight = minDate + nighttimeBegins
    for i in range(delta.days + 1):
        night = timePeriod(startOfFirstNight+dt.timedelta(days=i,hours=23),startOfFirstNight+dt.timedelta(days=i,hours=31))

    endOfFirstNight = minDate + dt.timedelta(days=1,hours=7)


class timePeriod(object):
    def __init__(self,begins,ends):
        self.begins = begins
        self.ends = ends
        self.activitiesAndTimePercentages = {}

class activityInstance(object):
    def __init__(self,startTime,endTime):
        self.name = name
        self.startTime = startTime
        self.endTime = endTime

# Read data from csv file
def readDataFromFile(dataFile,eventIndex):
    f = open(dataFile,'rt')
    listOfInputLists = []

    try:
        reader = csv.reader(f)
        for row in reader:
            row.append(str(eventIndex))
            listOfInputLists.append(row)
    finally:
        f.close()
    return listOfInputLists

# Class to store time and date data read from file
class activityInstance(object):
    def __init__(self,listOfInputLists):
        self.day = 0
        self.month = 0
        self.year = 0
        self.formatDate(listOfInputLists[0])
        self.startTime = self.formatTime(listOfInputLists[1])
        self.stopTime = self.formatTime(listOfInputLists[2])
        self.activityIndex = int(listOfInputLists[3])

    # Extracts date information variables
    def formatDate(self,unformattedDate):
        date = dt.datetime.strptime(unformattedDate,"%d/%m/%y")
        self.day = int(date.strftime("%d"))
        self.month = int(date.strftime("%m"))
        self.year = int(date.strftime("%Y"))

    # Formats time as a decimal fraction of day, for use in graph
    def formatTime(self,unformattedTime):
        timeSinceMidnight = dt.datetime.strptime(unformattedTime,'%H:%M:%S')
        midnight = dt.datetime(1900,1,1)
        minutesSinceMidnight = ((timeSinceMidnight - midnight).total_seconds() / 60.0)
        fractionOfDay = minutesSinceMidnight / MINUTES_IN_DAY
        return fractionOfDay

# Formats data read from file as a list of eventInstance objects
def formatDataForPlot(listOfInputLists):
    activities = []
    for i in range(len(listOfInputLists)):
        for j in range(1,len(listOfInputLists[i])):
            activities.append(activityInstance(listOfInputLists[i][j]))
    return activities

# Extracts earliest (min) and latest (max) dates from data, for use in setting graph limits
def getMaxAndMinDates(plotDataList):
    dateTimeList = []
    for item in plotDataList:
        nextDate = dt.datetime(item.year,item.month,item.day)
        dateTimeList.append(nextDate)
    maxDate = max(dateTimeList)
    minDate = min(dateTimeList)
    # Ensure minimun of three days displayed 
    if not maxDate > minDate + dt.timedelta(days=1):
        maxDate = minDate + dt.timedelta(days=2)
    return maxDate, minDate

def go():
    dataFiles = ['sleepDataStartingMarch22.csv','feedingDataStartingMarch22.csv']
    listOfInputLists = []
    for i in range(len(dataFiles)):
        nextList = readDataFromFile(dataFiles[i],i)
        listOfInputLists.append(nextList)
    plotDataList = formatDataForPlot(listOfInputLists)
    maxDate, minDate = getMaxAndMinDates(plotDataList)
    plotData(plotDataList,maxDate,minDate)

go()
