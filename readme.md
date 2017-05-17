# Wee Baby, Big Data

## Statistical analysis versus child-based insomnia: a parental survival aid

Rougly hacked together Python scripts to visualise sleep patterns and analyse the relationship between daytime sleep patterns and those of the subsequent night.

`graphActivities.py` produces a graphical representation a of data-set of time spent carrying out daily activities, using the matplotlib library. 

`analyseData.py` processes the activity data into `dataItem` objects containing daily sleep time and duration information. Then produces graphical represtentions of said data items and carries out a regression analysis to determine daily sleep patterns corresponding with increased or decreased sleep over the following night.

No UI developed as of yet, so alterations need to be made directly to Python files.

## Why?

### Sleep schedule visualisation

Babies are creatures of habit. The aim of this graph is to let you see what your baby's habits are, so that you understand what's going on and better plan your day. It also allows you to get a visual representation of what daytime sleep patterns are most conducive to your baby (and you) getting a good night's sleep, e.g. does your baby tend to sleep better if put to bed at 22:00 or 23:00? Obviously a lot of this stuff is pretty intuitive and common-sensical, but the graph can be a helpful way of looking at a large ammount of information in a single glance.

### Anaylsis

The analysis script follows on from the graphic representation, its aim is to break down the data used to make the graph in different visual and statistical ways to bring out information that may not be immediately apparent from the main visualisation. E.g. it examines whether longer daytime naps correllate with a baby's getting more sleep at night in a statistically significant way.

### Use and contact info

All of this is available under the MIT license and subject to the below-stated disclaimer. If you find it useful or have any suggestions for additions or improvements, let me know at butleraidan at gmail dot com.

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

# Multi-variable linear regression analysis

## Scatter plots

![Hours slept per night vs. hours slept per day scatter plot](https://github.com/ambidextrous/weeBabyBigData/blob/master/HourssleptpernightHourssleptperdayScatterplot.jpg "Hours slept per night vs. hours slept per day scatterplot")


![Hours slept per night vs. longest period of continuous sleep during day scatter plot](https://github.com/ambidextrous/weeBabyBigData/blob/master/HourssleptpernightLongestcontinuoussleepperiodduringdayScatterplot.jpg "Hours slept per night vs. longest period of continuous sleep during day scatterplot")


![Hours slept per night vs. hours slept per day scatter plot](https://github.com/ambidextrous/weeBabyBigData/blob/master/HourssleptpernightHourssleptperdayScatterplot.jpg "Hours slept per night vs. hours slept per day scatterplot")

![Hours slept per night vs. age in days scatter plot](https://github.com/ambidextrous/weeBabyBigData/blob/master/HourssleptpernightAgeindaysScatterplot.jpg "Hours slept per night vs. age in days scatterplot")

                            OLS Regression Results                            
    ==============================================================================
    Dep. Variable:        hoursSleptNight   R-squared:                       0.269
    Model:                            OLS   Adj. R-squared:                  0.221
    Method:                 Least Squares   F-statistic:                     5.532
    Date:                Wed, 17 May 2017   Prob (F-statistic):           0.000738
    Time:                        23:05:29   Log-Likelihood:                -66.806
    No. Observations:                  65   AIC:                             143.6
    Df Residuals:                      60   BIC:                             154.5
    Df Model:                           4                                         
    Covariance Type:            nonrobust                                         
    ========================================================================================
                               coef    std err          t      P>|t|      [95.0% Conf. Int.]
    ----------------------------------------------------------------------------------------
    Intercept                7.3049      1.426      5.124      0.000         4.453    10.157
    hoursSleptDay            0.0435      0.101      0.430      0.669        -0.159     0.246
    longestSleepHoursDay    -0.3600      0.215     -1.677      0.099        -0.789     0.069
    meanSleepTimeDay        -0.1280      0.089     -1.444      0.154        -0.305     0.049
    ageInDays                0.0156      0.005      3.040      0.004         0.005     0.026
    ==============================================================================
    Omnibus:                        3.409   Durbin-Watson:                   1.121
    Prob(Omnibus):                  0.182   Jarque-Bera (JB):                3.123
    Skew:                          -0.535   Prob(JB):                        0.210
    Kurtosis:                       2.906   Cond. No.                     1.16e+03
    ==============================================================================
    
    Warnings:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
    [2] The condition number is large, 1.16e+03. This might indicate that there are
    strong multicollinearity or other numerical problems.

# Disclaimer

This software is used subject to the following conditions:

THIS SOFTWARE (INCLUDING, WITHOUT LIMITATION, ADVICE OR RECOMMENDATIONS) IS INTENDED SOLELY AS A GENERAL EDUCATIONAL AID AND ARE NEITHER MEDICAL NOR HEALTHCARE ADVICE FOR ANY INDIVIDUAL PROBLEM NOR A SUBSTITUTE FOR MEDICAL OR OTHER PROFESSIONAL ADVICE AND SERVICES FROM A QUALIFIED HEALTHCARE PROVIDER FAMILIAR WITH YOUR UNIQUE FACTS. ALWAYS SEEK THE ADVICE OF YOUR PHYSICIAN OR OTHER QUALIFIED HEALTHCARE PROVIDER REGARDING ANY MEDICAL CONDITION AND BEFORE STARTING ANY NEW TREATMENT. NOTHING CONTAINED IN THE SOFTWARE IS INTENDED TO BE USED FOR MEDICAL DIAGNOSIS OR TREATMENT. THE SOFTWARE IS PROVIDED WITH THE UNDERSTANDING THAT NEITHER THE AUTHORS OF THE SOFTWARE NOR ANY OF ITS CONTRIBUTORS OR USERS ARE ENGAGED IN RENDERING LEGAL, MEDICAL, COUNSELING, OR OTHER PROFESSIONAL SERVICES OR ADVICE. YOUR USE OF THE SOFTWARE IS SUBJECT TO THE ADDITIONAL DISCLAIMERS AND CAVEATS THAT MAY APPEAR THROUGHOUT THE SOFTWARE. THE AUTHORS ASSUME NO RESPONSIBILITY FOR ANY CONSEQUENCE RELATING DIRECTLY OR INDIRECTLY TO ANY ACTION OR INACTION YOU TAKE BASED ON THE SOFTWARE. 

IN NO EVENT WILL THE AUTHORS OR THEIR AFFILIATES BE LIABLE FOR ANY DIRECT, SPECIAL, INDIRECT, INCIDENTAL, CONSEQUENTIAL (INCLUDING AMONG OTHER THINGS LOSS OF REVENUE OR PROFITS), PUNITIVE, OR EXEMPLARY, DAMAGES OF ANY KIND OR SUBJECT TO EQUITABLE OR INJUNCTIVE REMEDIES (WHETHER BASED ON BREACH OF CONTRACT, TORT, NEGLIGENCE, STRICT LIABILITY OR OTHERWISE) ARISING OUT OF USE OF THIS SOFTWARE, OR DELAY OR INABILITY TO USE THE SOFTWARE, OR ANY INFORMATION CONTAINED IN THE SOFTWARE. NOTHING IN THIS LIMITATION OF LIABILITY SHALL EXCLUDE LIABILITIES NOT PERMITTED TO BE EXCLUDED BY APPLICABLE LAW.