import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import datetime as dt
import csv
import sys

MINUTES_IN_DAY = 1440.0

def plotData(data): 
    #Make a series of events 1 day apart
    x = mpl.dates.drange(dt.datetime(2017,3,16), 
                         dt.datetime(2017,3,30), 
                         dt.timedelta(days=1))
    # Vary the datetimes so that they occur at random times
    # Remember, 1.0 is equivalent to 1 day in this case...
    x += np.random.random(x.size)
    
    # We can extract the time by using a modulo 1, and adding an arbitrary base date
    times = x % 1 + int(x[0]) # (The int is so the y-axis starts at midnight...)
    
    # I'm just plotting points here, but you could just as easily use a bar.
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot_date(x, times, 'ro')
    ax.yaxis_date()
    fig.autofmt_xdate()

    #plt.axvline(dt.datetime(2017,3,17),0.14,0.16, linewidth=4, color='b')
?!?jedi=0, ?!?                  (start, *_*stop=None*_*, step=1) ?!?jedi?!?
    for i in range(0,len(data)):
        plt.axvline(dt.datetime(data[i].year,data[i].month,data[i].day),data[i].startTime,data[i].stopTime)
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

class sleepInstance:
    def __init__(self,listOfInputLists):
        self.day = 0
        self.month = 0
        self.year = 0
        self.formatDate(listOfInputLists[0])
        self.startTime = this.formatTime(listOfInputLists[1])
        self.stopTime = this.formatTime(listOfInputLists[2])

    def formatDate(unformattedDate):
        date = strptime(unformattedDate, "%d/%m/%Y")
        self.day = int("%d")
        self.month = int("%m")
        self.year = int("%Y")

    def formatTime(unformattedTime):
        timeSinceMidnight = dt.datetime.strptime(unformattedTime,'H%:%M:%S')
        midnight = dt.datetime(1900,1,1)
        minutesSinceMidnight = ((timeSinceMidnight - midnight).total_seconds() / 60.0)
        fractionOfDay = minutesSinceMidnight / MINUTES_IN_DAY
        return fractionOfDay

def formatDataForPlot(listOfInputLists):
    sleeps = []
    for i in range(1,len(listOfInputLists)):
        sleeps.append(sleepInstance(listOfInputLists[i]))
    return sleeps

dataFile = 'sleepData.csv'
listOfInputLists = readDataFromFile(dataFile)
plotDataList = formatDataForPlot(listOfInputLists)
plotData(plotDataList)

