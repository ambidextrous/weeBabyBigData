# Wee Baby, Big Data

## Statistical analysis versus child-based insomnia: a parental survival aid

Rougly hacked together Python scripts to visualise sleep patterns and analyse the relationship between daytime sleep patterns and those of the subsequent night

`graphActivities.py` produces a graphical representation a of data-set of time spent carrying out daily activities, using the matplotlib library. 

`analyseData.py` processes the activity data into `dataItem` objects containing daily sleep time and duration information. Then produces graphical represtentions of said data items and carries out a regression analysis to determine daily sleep patterns corresponding with increased or decreased sleep over the following night.

If you find this useful or have any suggestions for additions or improvements, let me know at butleraidan at gmail dot com.

## Use Instructions

Written in Python 2.7.

Activities over time visualisation:

    python graphActivities.py

Analysis processing and visualisation:

	python analyseData.py

## Input
 
The dataset used should be one or more `.csv` files with the following format:

    SleepStartDate,SleepStartTime,SleepStopTime
    17/03/17,23:45,07:25
    19/03/17,01:05,09:10
    19/03/17,23:50,08:25

Visualisation shows hours of the day on the y-axis and calendar days on the x-axis.

Activities over time visualisation:

![Output example](https://github.com/ambidextrous/weeBabyBigData/blob/master/activityData.jpg "Ouput Example")

## Analysis

Hours slept night and day graph:

![Hours slept night and day](https://github.com/ambidextrous/weeBabyBigData/blob/master/hoursSleptNightAndDayBarchart.jpg "Hours slept night and day")

Mean day sleep time graph:

![Mean day sleep time](https://github.com/ambidextrous/weeBabyBigData/blob/master/meanDaySleeptimeLineGraph.jpg "Mean day sleep time")

Longest continuous sleep night and day graph:

![Longest continuous sleep night and day](https://github.com/ambidextrous/weeBabyBigData/blob/master/longestContinuousSleepNightAndDayBarchart.jpg "Longest continuous sleep night and day")

## Multi-variable linear regression analysis

Sample ordianry least squares regression analysis output:

		                            OLS Regression Results                            
	==============================================================================
	Dep. Variable:        hoursSleptNight   R-squared:                       0.276
	Model:                            OLS   Adj. R-squared:                  0.193
	Method:                 Least Squares   F-statistic:                     3.309
	Date:                Wed, 12 Apr 2017   Prob (F-statistic):             0.0357
	Time:                        15:56:01   Log-Likelihood:                -30.852
	No. Observations:                  30   AIC:                             69.70
	Df Residuals:                      26   BIC:                             75.31
	Df Model:                           3                                         
	Covariance Type:            nonrobust                                         
	========================================================================================
	                           coef    std err          t      P>|t|      [95.0% Conf. Int.]
	----------------------------------------------------------------------------------------
	Intercept                9.7911      1.708      5.732      0.000         6.280    13.302
	hoursSleptDay            0.1582      0.145      1.088      0.287        -0.141     0.457
	longestSleepHoursDay    -0.7681      0.314     -2.443      0.022        -1.414    -0.122
	meanSleepTimeDay        -0.2576      0.120     -2.149      0.041        -0.504    -0.011
	==============================================================================
	Omnibus:                        3.877   Durbin-Watson:                   0.597
	Prob(Omnibus):                  0.144   Jarque-Bera (JB):                1.568
	Skew:                           0.066   Prob(JB):                        0.457
	Kurtosis:                       1.888   Cond. No.                         179.
	==============================================================================

	Warnings:
	[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.

Sample R output, for comparisson purposes:

R input:

	> sleepData = read.csv("sleepAnalysisData.csv")
	> sleepModel = lm(hoursSleptNight ~ hoursSleptDay + longestSleepHoursDay + meanSleepTimeDay, data = sleepData)
	> summary(sleepModel)

R output:

	Call:
	lm(formula = hoursSleptNight ~ hoursSleptDay + longestSleepHoursDay + 
    	meanSleepTimeDay, data = sleepData)

	Residuals:
	     Min       1Q   Median       3Q      Max 
	-1.15801 -0.45246  0.01101  0.48262  1.18274 

	Coefficients:
	                     Estimate Std. Error t value Pr(>|t|)    
	(Intercept)            9.7911     1.7081   5.732 4.93e-06 ***
	hoursSleptDay          0.1582     0.1454   1.088   0.2865    
	longestSleepHoursDay  -0.7681     0.3144  -2.443   0.0217 *  
	meanSleepTimeDay      -0.2576     0.1198  -2.149   0.0411 *  
	---
	Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

	Residual standard error: 0.7269 on 26 degrees of freedom
	Multiple R-squared:  0.2763,	Adjusted R-squared:  0.1928 
	F-statistic: 3.309 on 3 and 26 DF,  p-value: 0.03571
