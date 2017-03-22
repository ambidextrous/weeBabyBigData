import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.patches as patches
import datetime as dt
import csv
import sys

MINUTES_IN_DAY = 1440.0
COLUMN_COLOUR = 'b'

def plotData(data,columnColour,maxDate,minDate): 

    #Make a series of events 1 day apart
#    x = mpl.dates.drange(dt.datetime(2017,3,16), 
#                         dt.datetime(2017,4,25), 
#                         dt.timedelta(days=1))
    # Vary the datetimes so that they occur at random times
    # Remember, 1.0 is equivalent to 1 day in this case...

    x = mpl.dates.drange(minDate,maxDate,dt.timedelta(days=1))

    print "x = "+str(x)

    print "x[0] = "+str(x[0])

    x[0] += 0.85

    print "x[0] = "+str(x[0])
    print "x = "+str(x)
    #x += np.random.random(x.size)
    test = dt.datetime(2017,3,20)
    print "test = "+str(test)


    print "x.size = "+str(x.size)
    print "x = "+str(x)


    # Setting up an invisible background scatterplot give graph the correct size
    # We can extract the time by using a modulo 1, and adding an arbitrary base date
    times = x % 1 + int(x[0]) # (The int is so the y-axis starts at midnight...)
    
    fig = plt.figure()

    fig.suptitle('Daily Sleep Patterns', fontsize=14, fontweight='bold')
    ax = fig.add_subplot(111)

    ax.plot_date(x, times, 'ro', color='w', visible=False)

    ax.yaxis_date()
    fig.autofmt_xdate()

    start, end = ax.get_ylim()
    ax.yaxis.set_ticks(np.arange(start,end, 0.041666666666666))
    ax.set_yticklabels(['Midnight','1am','2am','3am','4am','5am','6am','7am','8am','9am','10am','11am','Midday','1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm','9pm','10pm','11pm','Midnight'])

    for i in range(0,len(data)):

        if data[i].startTime > data[i].stopTime:

            currentDataItem = data[i]

            currentDate = dt.datetime(currentDataItem.year,currentDataItem.month,currentDataItem.day)
          
            currentDate -= dt.timedelta(days=0.5)

            tomorrow = currentDate + dt.timedelta(days=1)
            
            plt.axvspan(xmin=currentDate, xmax=tomorrow, ymin=currentDataItem.startTime, ymax=1, facecolor=columnColour, alpha=0.5)


            theDayAfterTomorrow = tomorrow + dt.timedelta(days=1)


            plt.axvspan(xmin=tomorrow, xmax=theDayAfterTomorrow, ymin=0, ymax=currentDataItem.stopTime, facecolor=columnColour, alpha=0.5)


        else:

            currentDataItem = data[i]

            currentDate = dt.datetime(currentDataItem.year,currentDataItem.month,currentDataItem.day)
          
            currentDate -= dt.timedelta(days=0.5)

            tomorrow = currentDate + dt.timedelta(days=1)
            

            plt.axvspan(xmin=currentDate, xmax=tomorrow, ymin=currentDataItem.startTime, ymax=currentDataItem.stopTime, facecolor=columnColour, alpha=0.5)

    ax.set_ylabel('Hours',fontweight='bold')

    ax.legend()
    ax.grid(True)

    rect = patches.Rectangle((736404,1.0),10,5,linewidth=1,edgecolor='r',facecolor='none')
    ax.add_patch(rect)

    plt.show()

def readDataFromFile(dataFile):
    f = open(dataFile,'rt')
    listOfInputLists = []
    try:
        reader = csv.reader(f)
        for row in reader:
            listOfInputLists.append(row)
            print row
    finally:
        f.close()
    return listOfInputLists

class sleepInstance(object):
    def __init__(self,listOfInputLists):
        self.day = 0
        self.month = 0
        self.year = 0
        print "listOfInputLists[0] = "+listOfInputLists[0]
        self.formatDate(listOfInputLists[0])
        self.startTime = self.formatTime(listOfInputLists[1])
        self.stopTime = self.formatTime(listOfInputLists[2])

    def formatDate(self,unformattedDate):
        date = dt.datetime.strptime(unformattedDate,"%d/%m/%y")
        print "date = "+str(date)

        self.day = int(date.strftime("%d"))
        self.month = int(date.strftime("%m"))
        self.year = int(date.strftime("%Y"))
        print "self.day = "+str(self.day)
        print "self.month = "+str(self.month)
        print "self.year  = "+str(self.year)

    def formatTime(self,unformattedTime):
        timeSinceMidnight = dt.datetime.strptime(unformattedTime,'%H:%M:%S')
        midnight = dt.datetime(1900,1,1)
        minutesSinceMidnight = ((timeSinceMidnight - midnight).total_seconds() / 60.0)
        fractionOfDay = minutesSinceMidnight / MINUTES_IN_DAY
        return fractionOfDay

def formatDataForPlot(listOfInputLists):
    sleeps = []
    for i in range(1,len(listOfInputLists)):
        sleeps.append(sleepInstance(listOfInputLists[i]))
    return sleeps

def getMaxAndMinDates(plotDataList):
    dateTimeList = []
    for item in plotDataList:
        nextDate = dt.datetime(item.year,item.month,item.day)
        print "nextDate = "+str(nextDate)
        dateTimeList.append(nextDate)
    print "dateTimeList = "+str(dateTimeList)
    maxDate = max(dateTimeList)
    minDate = min(dateTimeList)
    print "maxDate = "+str(maxDate)
    print "minDate = "+str(minDate)
    return maxDate, minDate

dataFile = 'sleepData.csv'
listOfInputLists = readDataFromFile(dataFile)
plotDataList = formatDataForPlot(listOfInputLists)
maxDate, minDate = getMaxAndMinDates(plotDataList)
plotData(plotDataList,COLUMN_COLOUR,maxDate,minDate)


