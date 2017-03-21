import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import datetime as dt
import csv
import sys

MINUTES_IN_DAY = 1440.0

def plotData(data): 

    #fig, ax = plt.subplots()
    #df.plot(kind='scatter', x='GDP_per_capita', y='life_expectancy', ax=ax)

    # Turn on the grid
    #ax.grid()



    #Make a series of events 1 day apart
    x = mpl.dates.drange(dt.datetime(2017,3,16), 
                         dt.datetime(2017,4,25), 
                         dt.timedelta(days=1))
    # Vary the datetimes so that they occur at random times
    # Remember, 1.0 is equivalent to 1 day in this case...

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
    
    # I'm just plotting points here, but you could just as easily use a bar.
    fig = plt.figure()

    fig.suptitle('Daily Sleep Patterns', fontsize=14, fontweight='bold')
    ax = fig.add_subplot(111)


    ax.plot_date(x, times, 'ro', color='w', visible=False)

    #ax.plot_date()

    ax.yaxis_date()
    fig.autofmt_xdate()

    start, end = ax.get_ylim()
    ax.yaxis.set_ticks(np.arange(start,end, 0.041666666666666))
    ax.set_yticklabels(['Midnight','1am','2am','3am','4am','5am','6am','7am','8am','9am','10am','11am','Midday','1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm','9pm','10pm','11pm','Midnight'])

    #plt.axvline(dt.datetime(2017,3,17),0.14,0.16, linewidth=4, color='b')
    for i in range(0,len(data)):

        if data[i].startTime > data[i].stopTime:
            plt.axvline(dt.datetime(data[i].year,data[i].month,data[i].day),data[i].startTime,1, linewidth=1, color = 'b')


            nextDay = dt.datetime(data[i].year,data[i].month,data[i].day)

            nextDay += dt.timedelta(days=1)

            plt.axvline(nextDay,0,data[i].stopTime, linewidth=1, color = 'b')

        else:
            plt.axvline(dt.datetime(data[i].year,data[i].month,data[i].day),data[i].startTime,data[i].stopTime, linewidth=1, color = 'b')

    ax.add_patch(
        mpl.patches.Rectangle(
            (736411.0, 0.5), # (x,y)
            0.5,        # width
            0.5,        # height
        )
    )

    ax.set_xlabel('Days',fontweight='bold')
    ax.set_ylabel('Hours',fontweight='bold')

    ax.legend()
    ax.grid(True)


    #ax.set_ylim([0,1])

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

dataFile = 'sleepData.csv'
listOfInputLists = readDataFromFile(dataFile)
plotDataList = formatDataForPlot(listOfInputLists)
plotData(plotDataList)

