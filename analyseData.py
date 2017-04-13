import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.patches as patches
import datetime as dt
import csv
import sys
import time
import pandas
import copy
from scipy import stats
from pylab import figtext, plot, show
from statsmodels.formula.api import ols
from matplotlib.backends.backend_pdf import PdfPages

# Analyses activity and time-use data and produces visualisations thereof
def analyseData(activitiesList,maxDate,minDate):
    
    birthDate = dt.datetime(2017,2,6)
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

    dataItemsDict = setAgeInDays(dataItemsDict,birthDate)

    dataItemsDateOrderedList = removeMissingSleepDataItems(dataItemsDateOrderedList)

    dataItemsDateOrderedList = calculateValuesForAndPlotDayNightHoursSleptBarChart(dataItemsDateOrderedList)

    dataItemsDateOrderedList = calculateValuesForAndPlotDayNightLongestContinuousSleepBarChart(dataItemsDateOrderedList)

    dataItemsDateOrderedList = calculateValuesForAndPlotDayMeanTimeSleepLineGraph(dataItemsDateOrderedList)

    writeSleepAnalysisDataToFile(dataItemsDateOrderedList)

    generateScatterPlots(dataItemsDateOrderedList)

    regress(dataItemsDateOrderedList)


def updateReadme(regressionString):

    disclaimer = """\n\n# Disclaimer

This software is used subject to the following conditions:

THIS SOFTWARE (INCLUDING, WITHOUT LIMITATION, ADVICE OR RECOMMENDATIONS) IS INTENDED SOLELY AS A GENERAL EDUCATIONAL AID AND ARE NEITHER MEDICAL NOR HEALTHCARE ADVICE FOR ANY INDIVIDUAL PROBLEM NOR A SUBSTITUTE FOR MEDICAL OR OTHER PROFESSIONAL ADVICE AND SERVICES FROM A QUALIFIED HEALTHCARE PROVIDER FAMILIAR WITH YOUR UNIQUE FACTS. ALWAYS SEEK THE ADVICE OF YOUR PHYSICIAN OR OTHER QUALIFIED HEALTHCARE PROVIDER REGARDING ANY MEDICAL CONDITION AND BEFORE STARTING ANY NEW TREATMENT. NOTHING CONTAINED IN THE SOFTWARE IS INTENDED TO BE USED FOR MEDICAL DIAGNOSIS OR TREATMENT. THE SOFTWARE IS PROVIDED WITH THE UNDERSTANDING THAT NEITHER THE AUTHORS OF THE SOFTWARE NOR ANY OF ITS CONTRIBUTORS OR USERS ARE ENGAGED IN RENDERING LEGAL, MEDICAL, COUNSELING, OR OTHER PROFESSIONAL SERVICES OR ADVICE. YOUR USE OF THE SOFTWARE IS SUBJECT TO THE ADDITIONAL DISCLAIMERS AND CAVEATS THAT MAY APPEAR THROUGHOUT THE SOFTWARE. THE AUTHORS ASSUME NO RESPONSIBILITY FOR ANY CONSEQUENCE RELATING DIRECTLY OR INDIRECTLY TO ANY ACTION OR INACTION YOU TAKE BASED ON THE SOFTWARE. 

IN NO EVENT WILL THE AUTHORS OR THEIR AFFILIATES BE LIABLE FOR ANY DIRECT, SPECIAL, INDIRECT, INCIDENTAL, CONSEQUENTIAL (INCLUDING AMONG OTHER THINGS LOSS OF REVENUE OR PROFITS), PUNITIVE, OR EXEMPLARY, DAMAGES OF ANY KIND OR SUBJECT TO EQUITABLE OR INJUNCTIVE REMEDIES (WHETHER BASED ON BREACH OF CONTRACT, TORT, NEGLIGENCE, STRICT LIABILITY OR OTHERWISE) ARISING OUT OF USE OF THIS SOFTWARE, OR DELAY OR INABILITY TO USE THE SOFTWARE, OR ANY INFORMATION CONTAINED IN THE SOFTWARE. NOTHING IN THIS LIMITATION OF LIABILITY SHALL EXCLUDE LIABILITIES NOT PERMITTED TO BE EXCLUDED BY APPLICABLE LAW."""

    readmeBaseFile = open("readMeMinusRegressionData.md","r")
    baseString = readmeBaseFile.read()
    readmeBaseFile.close()

    regressionString = regressionString.replace("\n","\n    ")
    readmeString = baseString + regressionString + disclaimer

    testFile = open("readme.md","w")
    testFile.write(readmeString)
    testFile.close()

# Calls function to generate scatter plots for regression dependent variable and independent variables
def generateScatterPlots(dataItemsList):
    hoursSleptNightList = []
    hoursSleptDayList = []
    longestSleepHoursDayList = []
    meanSleepTimeDayList = []
    ageInDaysList = []
    for item in dataItemsList:
        hoursSleptNightList.append(item.hoursSleptDuringNight)
        hoursSleptDayList.append(item.hoursSleptDuringDay)
        longestSleepHoursDayList.append(item.longestDaySleepHours)
        meanSleepTimeDayList.append(item.meanSleepTimeDayHoursSinceMidnight)
        ageInDaysList.append(item.ageInDays)
    hoursSleptNightLable = 'Hours slept per night'
    hoursSleptDayLable = 'Hours slept per day'
    longestSleepHoursDayLable = 'Longest continuous sleep period during day'
    meanSleepTimeDayLable = 'Mean sleep time during day\n (lower = closer sleep more earlier in day; higher = slept more later in day)'
    ageInDaysLable = 'Age in days'
    dependentVariableList = hoursSleptNightList
    dependentVariableLable = hoursSleptNightLable
    generateScatterPlot(dependentVariableList,hoursSleptDayList,dependentVariableLable,hoursSleptDayLable)
    generateScatterPlot(dependentVariableList,longestSleepHoursDayList,dependentVariableLable,longestSleepHoursDayLable)
    generateScatterPlot(dependentVariableList,meanSleepTimeDayList,dependentVariableLable,meanSleepTimeDayLable)
    generateScatterPlot(dependentVariableList,ageInDaysList,dependentVariableLable,ageInDaysLable)

# Generates scatter plot for regression depdnent variable and independent variable
def generateScatterPlot(dependentVariableList,independentVariableList,dependentLable,independentLable):
    #plt.scatter(dependentVariableList,independentVariableList)

    fig, ax = plt.subplots(figsize=(12,10))

    plt.scatter(independentVariableList,dependentVariableList)

    plt.ylabel("Dependent variable: "+dependentLable,fontweight='bold')
    plt.xlabel("Independent variable: "+independentLable,fontweight='bold')

    # Removing spaces from lables
    dependentLable = "".join(dependentLable.split())
    independentLable = "".join(independentLable.split())

    # Saves to file 
    plt.savefig(dependentLable+independentLable+'Scatterplot.pdf')
    plt.savefig(dependentLable+independentLable+'Scatterplot.jpg')

    plt.show()

# Sets ageInDays variable for each dataItem
def setAgeInDays(dataItemsDict,birthDate):
    secondDayConversion = 60 * 60 * 24
    for key in dataItemsDict:
        item = dataItemsDict[key]
        item.ageInDays = round(((item.starts - birthDate).total_seconds() / secondDayConversion),0)
    return dataItemsDict

# Carries out regression analysis of data, prints to command line and writes to file
def regress(dataItems):
    df = pandas.read_csv('sleepAnalysisData.csv')
    model = ols('hoursSleptNight ~ hoursSleptDay + longestSleepHoursDay + meanSleepTimeDay + ageInDays', df).fit()
    print model.summary()
    textFile = open("regressionAnalysisOutput.txt","w")
    textFile.write(str(model.summary()))
    textFile.close()

    updateReadme(str(model.summary()))

# Writes sleep analysis data to a .csv file
def writeSleepAnalysisDataToFile(dataItemsList):
    with open('sleepAnalysisData.csv','wb') as csvfile:
        w = csv.writer(csvfile)
        # Write name rows header
        w.writerow(['date','hoursSleptNight','hoursSleptDay','longestSleepHoursDay','longestSleepHourNight','meanSleepTimeDay','ageInDays'])
        # Write data rows
        for item in dataItemsList:
            w.writerow([str(item.startDate),str(item.hoursSleptDuringNight),str(item.hoursSleptDuringDay),str(item.longestDaySleepHours),str(item.longestNightSleepHours),str(item.meanSleepTimeDayHoursSinceMidnight),str(item.ageInDays)])

# Removes dataItems with less than a minimum number of hours sleep for either the day or night periods from dataItemsList
def removeMissingSleepDataItems(dataItemsList):
    listWithMissingItemsRemoved = []
    minDayHoursSleepThreshhold = 1
    minNightHoursSleepThreshhold = 1
    secHourConversion = 60 * 60
    for item in dataItemsList:
        if (item.sleptDaySeconds/secHourConversion) >= minDayHoursSleepThreshhold and (item.sleptNightSeconds/secHourConversion) >= minNightHoursSleepThreshhold:
            listWithMissingItemsRemoved.append(item)
    return listWithMissingItemsRemoved

# Calculates mean sleep time values for each day, adds them to data items, saves them to file and shows them on-screen
def calculateValuesForAndPlotDayMeanTimeSleepLineGraph(dataItemsList):
    
    # Data to plot
    n_groups = len(dataItemsList)
    meanDaySleepTimes = []
    dates = []

    secHourConversion = 60 * 60

    firstItem = dataItemsList[0]
    hoursMidnightToDawn = int(firstItem.starts.strftime("%H"))

    for item in dataItemsList:
        # Adds mean day sleep time
        meanDaySleepTimes.append((item.meanSleepDaySecsSinceDaybreak/secHourConversion)+hoursMidnightToDawn)
        # Adds mean day sleep time to dataItem
        item.meanSleepTimeDayHoursSinceMidnight = (item.meanSleepDaySecsSinceDaybreak/secHourConversion) + hoursMidnightToDawn
        # Adds date
        dates.append((item.starts).strftime("%A, %d %B %Y %H:%M"))

    # Create plot
    fig, ax = plt.subplots(figsize=(20,10))
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8

    item = dataItemsList[0]
    daybreak = item.starts.strftime("%H:%M")
    nightfall = item.nightfall.strftime("%H:%M")
    nightsEnd = item.ends.strftime("%H:%M")
    avgSleepTime = round(sum(meanDaySleepTimes)/len(meanDaySleepTimes),2)


    ax.axhline(y=avgSleepTime,linewidth=1,alpha=0.5,ls='dashed')

    plt.plot(index,meanDaySleepTimes,label='Mean day-time sleep time [Avg='+str(avgSleepTime)+']',linewidth=4)

    ax.grid(True)

    plt.xlabel('24-hour period beginning',fontweight='bold')
    plt.ylabel('Mean sleep time during daytime period, hours since mid-night \n (Earlier = slept longer in morning; later = slept more in afternoon)',fontweight='bold')
    plt.title('Mean sleep time during day',fontweight='bold')
    plt.xticks(index, dates)

    plt.legend()

    plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right')

    plt.tight_layout()

    # Saves to file 
    plt.savefig('meanDaySleeptimeLineGraph.pdf')
    plt.savefig('meanDaySleeptimeLineGraph.jpg')

    plt.show()

    return dataItemsList

# Calculates longest continues sleep time values for each night, day and twenty-four hour period, adds them to data items, saves them to file and shows them on-screen
def calculateValuesForAndPlotDayNightLongestContinuousSleepBarChart(dataItemsList):
    
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
        # Adds longest time slept each night to dataItem
        item.longestNightSleepHours = longestSleep/secHourConversion
        # Adds longest time slept each day
        longestSleep = dt.timedelta(days=0).total_seconds()
        for activity in item.dayActivities:
            if activity.name == "sleeping" and (activity.ends - activity.begins).total_seconds() > longestSleep:
                longestSleep = (activity.ends - activity.begins).total_seconds()
        longestTimesSleptDuringDay.append(longestSleep/secHourConversion)
        # Adds longest time slept each day to dataItem
        item.longestDaySleepHours = longestSleep/secHourConversion
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


    ax.axhline(y=averageNightsSleep,linewidth=1,color=nightColour,alpha=0.5,ls='dashed')
    ax.axhline(y=averageDaysSleep,linewidth=1,color=dayColour,alpha=0.5,ls='dashed')

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

    return dataItemsList

# Calculates total hours slept values for each day and night, adds them to data items, saves them to file and shows them on-screen
def calculateValuesForAndPlotDayNightHoursSleptBarChart(dataItemsList): 

    # Data to plot
    n_groups = len(dataItemsList)
    timeSleptDuringDay = []
    timeSleptDuringNight = []
    timeSleptDuringNightAndDay = []
    dates = []

    secHourConversion = 60 * 60

    for item in dataItemsList:
        timeSleptDuringDay.append(item.sleptDaySeconds/secHourConversion)
        item.hoursSleptDuringDay = item.sleptDaySeconds/secHourConversion
        timeSleptDuringNight.append(item.sleptNightSeconds/secHourConversion)
        item.hoursSleptDuringNight = item.sleptNightSeconds/secHourConversion
        timeSleptDuringNightAndDay.append((item.sleptDaySeconds+item.sleptNightSeconds)/secHourConversion)
        item.hoursSleptDuring24Hours = (item.sleptDaySeconds+item.sleptNightSeconds) / secHourConversion 
        #dates.append(item.startDate)
        dates.append((item.starts).strftime("%A, %d %B %Y %H:%M"))
    

    dayAvg = round(sum(timeSleptDuringDay)/len(timeSleptDuringDay),2)
    nightAvg = round(sum(timeSleptDuringNight)/len(timeSleptDuringNight),2)
    twentyFourHourAvg = round((sum(timeSleptDuringDay)+sum(timeSleptDuringNight))/len(timeSleptDuringDay),2)

    dayColour = 'b'
    nightColour = 'r'
    twentyFourHourColour = 'k'

    # Create plot
    fig, ax = plt.subplots(figsize=(20,10))
    index = np.arange(n_groups)
    bar_width = 0.25
    opacity = 0.8

    ax.axhline(y=dayAvg,linewidth=1,color=dayColour,alpha=0.5,ls='dashed')
    ax.axhline(y=nightAvg,linewidth=1,color=nightColour,alpha=0.5,ls='dashed')
    ax.axhline(y=twentyFourHourAvg,linewidth=1,color=twentyFourHourColour,alpha=0.5,ls='dashed')

    rects1 = plt.bar(index,timeSleptDuringDay, bar_width,
                    alpha=opacity,
                    color=dayColour,
                    label='Day [Avg='+str(dayAvg)+']')


    rects2 = plt.bar(index+bar_width,timeSleptDuringNight, bar_width,
                    alpha=opacity,
                    color=nightColour,
                    label='Night [Avg='+str(nightAvg)+']')
    
    rects3 = plt.bar(index+(2*bar_width),timeSleptDuringNightAndDay, bar_width,
                    alpha=opacity,
                    color=twentyFourHourColour,
                    label='Night and Day [Avg='+str(twentyFourHourAvg)+']')

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

    return dataItemsList

# Calculates mean sleep time for day and night for each twentyFourHourPeriod and adds them to data items
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

# Sets values for longest sleep period for each day and night, adds them to data items
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

# Converts and integer or float value for a number of seconds to a datetime object with values for HH:MM:SS
def convertSecondsToHMS(secs):
    return str(dt.timedelta(seconds=secs))

# Sets hours slept during day and night and adds them to data items
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

# Calculates seconds slept during night, day and twentyFourHourPeriod
def calculateAnalysisDataValues(dataItemsDict):
    for key in dataItemsDict:
        item = dataItemsDict[key]
        # Calculates total seconds slept during night
        secondsSleptInNight = 0.0
        for activity in item.nightActivities:
            if activity.name == "sleeping":
                secondsSleptInNight += activity.getSeconds()
        item.sleptNightSeconds = secondsSleptInNight
        # Calculates total seconds slept during day
        secondsSleptInDay = 0.0
        for activity in item.dayActivities:
            if activity.name == "sleeping":
                secondsSleptInDay += activity.getSeconds()
        item.sleptDaySeconds = secondsSleptInDay
        # Calculates total seconds slept in twentyFourHourPeriod
        item.slept24HoursSeconds = item.sleptNightSeconds + item.sleptDaySeconds
    return dataItemsDict

# Adds activities to data items
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

# Data item object to store information on activities carried out within a given twentyFourHourPeriod
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
        self.hoursSleptDuringNight = 0
        self.hoursSleptDuringDay = 0
        self.longestDaySleepHours = 0
        self.longestNightSleepHours = 0
        self.meanSleepTimeDayHoursSinceMidnight = 0
        self.ageInDays = 0
        #print (self)
    def __str__(self):
        return "name:"+str(self.name)+"; startDate:"+str(self.startDate)+"; nightActivities:"+str(self.nightActivities)+"; dayActivities:"+str(self.dayActivities)+"; subperiods"+str(self.subperiods)+"; day:"+str(self.day)+"; night:"+str(self.night)+"; slept24HoursSeconds:"+str(self.slept24HoursSeconds)+"; sleptNightSeconds:"+str(self.sleptNightSeconds)+"; sleptDaySeconds:"+str(self.sleptDaySeconds)+"; avgNightSleepSeconds:"+str(self.avgNightSleepSeconds)+"; avgDaySleepSeconds:"+str(self.avgDaySleepSeconds)+"; goodNightsSleepScore:"+str(self.goodNightsSleepScore)

# Object to store information of a time period of arbitrary length
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

# Object to store information on an instance of an arbitrary activity
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

# Main function to call functions to read in activity data, process it into data items dealing with activities carried out over distinct twentyFourHourPeriods and visualise the data through graphs and regression analysis.
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
