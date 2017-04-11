# Python script to produce a graph of data-set of time spent carrying out daily activities using the matplotlib library. 

## Use Instructions

Activities over time visualisation:

    python timeLog.py

Analysis processing and visualisation:

	python regressionAnalysis.py

## Input
 
The dataset used should be one or more `.csv` files with the following format:

    SleepStartDate,SleepStartTime,SleepStopTime
    17/03/17,23:45,07:25
    19/03/17,01:05,09:10
    19/03/17,23:50,08:25

Visualisation shows hours of the day on the y-axis and calendar days on the x-axis.

Activities over time visualisation:

![Output example](https://github.com/ambidextrous/timeLogGrapher/blob/master/activityData.jpg "Ouput Example")

## Analysis

Hours slept night and day graph:

![Hours slept night and day](https://github.com/ambidextrous/timeLogGrapher/blob/master/hoursSleptNightAndDayBarchart.jpg "Hours slept night and day")

Longest continuous sleep night and day graph:

![Longest continuous sleep night and day](https://github.com/ambidextrous/timeLogGrapher/blob/master/meanDaySleeptimeBarchart.jpg "Longest continuous sleep night and day")

Mean day sleep time graph:

![Mean day sleep time](https://github.com/ambidextrous/timeLogGrapher/blob/master/meanDaySleeptimeBarchart.jpg "Mean day sleep time)

## Multi-variable linear regression analysis

R script:

	> sleepData = read.csv("sleepAnalysisData.csv")
	> sleepModel = lm(hoursSleptNight ~ hoursSleptDay + longestSleepHoursDay + meanSleepTimeDay, data = sleepData)
	> summary(sleepModel)

Output:

	Call:
	lm(formula = hoursSleptNight ~ hoursSleptDay + longestSleepHoursDay + 
	    meanSleepTimeDay, data = sleepData)
	
	Residuals:
	     Min       1Q   Median       3Q      Max 
	-1.12426 -0.47274 -0.00412  0.47776  1.10430 
	
	Coefficients:
	                     Estimate Std. Error t value Pr(>|t|)    
	(Intercept)            9.2361     1.6871   5.475  1.1e-05 ***
	hoursSleptDay          0.1969     0.1426   1.380   0.1798    
	longestSleepHoursDay  -0.8010     0.3050  -2.626   0.0145 *  
	meanSleepTimeDay      -0.2275     0.1174  -1.937   0.0641 .  
	---
	Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1
	
	Residual standard error: 0.7036 on 25 degrees of freedom
	Multiple R-squared:  0.2845,	Adjusted R-squared:  0.1986 
	F-statistic: 3.313 on 3 and 25 DF,  p-value: 0.03626
	
