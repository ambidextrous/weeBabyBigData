import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.patches as patches
import datetime as dt
import csv
import sys

MINUTES_IN_DAY = 1440.0
COLUMN_COLOUR = 'b'

# Graph data using matplotlib visualization
def plotData(data,columnColour,maxDate,minDate): 
    # Set up an invisible background scatterplot give graph the correct size
    # Make a series of events that are one day apart 
    x = mpl.dates.drange(minDate,maxDate,dt.timedelta(days=1))

    # Offset first event to top of graph to give correct height
    x[0] += 0.85

    # Extract the time using a modulo 1, and adding an arbitrary base date
    # int used so that y-axis starts at midnight
    times = x % 1 + int(x[0])
    
    fig = plt.figure()
    fig.suptitle('Daily Sleep Patterns', fontsize=14, fontweight='bold')
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

        # If period starts and finishes on different days, slit and add to both days
        if data[i].startTime > data[i].stopTime:
            currentDataItem = data[i]
            currentDate = dt.datetime(currentDataItem.year,currentDataItem.month,currentDataItem.day)
            currentDate -= dt.timedelta(days=0.5)
            tomorrow = currentDate + dt.timedelta(days=1)
            plt.axvspan(xmin=currentDate, xmax=tomorrow, ymin=currentDataItem.startTime, ymax=1, facecolor=columnColour, alpha=0.5)
            theDayAfterTomorrow = tomorrow + dt.timedelta(days=1)
            plt.axvspan(xmin=tomorrow, xmax=theDayAfterTomorrow, ymin=0, ymax=currentDataItem.stopTime, facecolor=columnColour, alpha=0.5)

        # Else, add to given day
        else:
            currentDataItem = data[i]
            currentDate = dt.datetime(currentDataItem.year,currentDataItem.month,currentDataItem.day)
            currentDate -= dt.timedelta(days=0.5)
            tomorrow = currentDate + dt.timedelta(days=1)
            plt.axvspan(xmin=currentDate, xmax=tomorrow, ymin=currentDataItem.startTime, ymax=currentDataItem.stopTime, facecolor=columnColour, alpha=0.5)

    ax.set_ylabel('Hours',fontweight='bold')

    ax.grid(True)

    plt.show()

# Read data from csv file
def readDataFromFile(dataFile):
    f = open(dataFile,'rt')
    listOfInputLists = []
    try:
        reader = csv.reader(f)
        for row in reader:
            listOfInputLists.append(row)
    finally:
        f.close()
    return listOfInputLists

# Class to store time and date data read from file
class sleepInstance(object):
    def __init__(self,listOfInputLists):
        self.day = 0
        self.month = 0
        self.year = 0
        self.formatDate(listOfInputLists[0])
        self.startTime = self.formatTime(listOfInputLists[1])
        self.stopTime = self.formatTime(listOfInputLists[2])

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

# Formats data read from file as a list of sleepInstance objects
def formatDataForPlot(listOfInputLists):
    sleeps = []
    for i in range(1,len(listOfInputLists)):
        sleeps.append(sleepInstance(listOfInputLists[i]))
    return sleeps

# Extracts earliest (min) and latest (max) dates from data, for use in setting graph limits
def getMaxAndMinDates(plotDataList):
    dateTimeList = []
    for item in plotDataList:
        nextDate = dt.datetime(item.year,item.month,item.day)
        dateTimeList.append(nextDate)
    maxDate = max(dateTimeList)
    minDate = min(dateTimeList)
    return maxDate, minDate

dataFile = 'sleepData.csv'
listOfInputLists = readDataFromFile(dataFile)
plotDataList = formatDataForPlot(listOfInputLists)
maxDate, minDate = getMaxAndMinDates(plotDataList)
plotData(plotDataList,COLUMN_COLOUR,maxDate,minDate)

