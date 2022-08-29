# FigureGenerator.py

# Written by Casey Gierke of AlbuGierke Environmental Solutions
# on 12/30/2020

# With Notepad++, use F5 then copy this into box
# C:\Users\Casey\Anaconda3\python.exe -i "$(FULL_CURRENT_PATH)"

# ------------------------------------------------------
# IMPORTS
# ------------------------------------------------------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import os
import configparser
from sqlalchemy import create_engine
import pymysql.cursors
import seaborn as sns
import matplotlib.gridspec as gridspec
import scipy.stats as stats
import datetime

# Adjust size of output plots
font = {'family' : 'Times New Roman',
	'weight' : 'normal',
	'size'   : 12}

plt.rc('font', **font)

# ------------------------------------------------------
# DEFINE FUNCTIONS
# ------------------------------------------------------

def DB_get(SQL):
	db = pymysql.connect(host=config['mysql']['host'], user=config['mysql']['user'], password=config['mysql']['password'], db= config['mysql']['db'], charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, local_infile=True)
	db.autocommit = True

	# Prepare a cursor object using cursor() method
	cursor = db.cursor()
	cursor.execute(SQL)
	result = cursor.fetchall()
	# Disconnect from server
	db.close()
	return result
	
# ------------------------------------------------------
# COMPUTATIONS
# ------------------------------------------------------

# Define path
path = os.path.abspath(os.path.dirname(__file__))
# Define path as working directory
os.chdir(path)

# Get DB configuration
config = configparser.ConfigParser()
config.read(path+os.sep+'db.ini')

# Shorten path to one folder up for outputs
path = path[:-path[::-1].find(os.sep)]

# Define path as working directory
os.chdir(path)

# Define a connection
connection = create_engine("mysql+pymysql://"+config['mysql']['user']+":"+config['mysql']['password']+"@"+config['mysql']['host']+"/"+config['mysql']['db']+"")    

# Get date
today = str(datetime.datetime.today())[:10]

# ------------------------------------------------------
# INPUTS
# ------------------------------------------------------

# # Define data types
# dataTypes = ['WLE', 'Temperature', 'Streamflow']

# # Short circuit
# dataTypes = [dataTypes[2]]

# # Loop through datatypes
# for dataType in dataTypes:

# # Define columnName
# if dataType == 'Temperature':
	# columnName = 'TempF'
	# plotScheme = '-r'
	# yLabel = 'Temperature [$^\circ$F]'
# elif dataType == 'Streamflow':
	# columnName = 'flow'
	# plotScheme = '-b'
	# yLabel = 'Streamflow [cfs]'
# elif dataType == 'WLE':
	# columnName = 'wle'
	# plotScheme = '-b'
	# yLabel = 'Water Level Elevation'
	
print(f'Getting date')

# Select the data from the table
sql = f"SELECT Post_Date FROM cl_properties ORDER BY Post_Date DESC"
# Query out data
date = pd.read_sql(sql, con=connection)

# Get just date
date = date['Post_Date'][0]

print(f'Getting data')

# Select the data from the table
sql = f"SELECT * FROM cl_properties where Post_Date = '{date}' ORDER BY City"

# Query out data
data = pd.read_sql(sql, con=connection)

# # Remove zeros from data
# data['Data'] = data['Data'].replace({0:np.nan})

# # Convert to cfs if it is Streamflow
# if dataType == 'Streamflow':
	# data['Data'] *= 0.00222801

# -----------------------------------------
# Nation Boxplot
# -----------------------------------------

# Open figure 
fig = plt.figure(figsize = (12, 7))

flierprops = dict(markerfacecolor='b', markersize=.1,
	  linestyle='none', markeredgecolor='b')
sns.boxplot(x = data['Nation'], y = data['Price'], flierprops=flierprops)
plt.ylabel('US $')
plt.xlabel('Nation')
plt.xticks(rotation=75)
plt.yscale('log')

# Make plot title
plt.title(f'Real Estate Price Data by Nation')

# Add grid
plt.grid(True)

fig.tight_layout()

# Check that the save file path exists
if not os.path.exists('Figures'+os.sep):
	os.makedirs('Figures'+os.sep)

# Save the figure
fig.savefig(f'Figures{os.sep}Price by Nation- {date}.png',dpi=500)
# plt.show()

# -----------------------------------------
# City Boxplot
# -----------------------------------------

# Open figure 
fig = plt.figure(figsize = (12, 7))

# flierprops = dict(markerfacecolor='b', markersize=.1,
	  # linestyle='none', markeredgecolor='b')
sns.boxplot(x = data['City'], y = data['Price'], flierprops=flierprops)
plt.ylabel('US $')
plt.xlabel('City')
plt.xticks(rotation=75)
plt.yscale('log')

# Make plot title
plt.title(f'Real Estate Price Data by City')

# Add grid
plt.grid(True)

fig.tight_layout()

# Check that the save file path exists
if not os.path.exists('Figures'+os.sep):
	os.makedirs('Figures'+os.sep)

# Save the figure
fig.savefig(f'Figures{os.sep}Price by City- {date}.png',dpi=500)
# plt.show()

# -----------------------------------------
# Time Series
# -----------------------------------------

# # Open figure 
# fig = plt.figure(figsize = (12, 7))

# Select cities from the table
sql = f"SELECT City FROM cl_properties GROUP BY City"

# sql = f"SELECT * FROM cl_properties"

# Query out data
cities = pd.read_sql(sql, con=connection)

# # Create folder to save files in 
# if not os.path.exists(f'Figures{os.sep}Price Time Series{os.sep}{str(date)[:10]}{os.sep}'):
	# os.makedirs(f'Figures{os.sep}Price Time Series{os.sep}{str(date)[:10]}{os.sep}')
		
# Loop through cities
for city in cities.iterrows():

	city = city[1]['City']
	
	# Make sure it is not blank
	if city != '':
	
		print(f'Querying data for {city}')
		
		# Select the average daily data from the table
		sql = f"SELECT Post_Date, AVG(Price) AS 'Average Price' FROM cl_properties WHERE City = '{city}' AND Post_Date > '2021-03-01' GROUP BY Post_Date ORDER BY Post_Date"

		# Query out data
		timeSeriesAverages = pd.read_sql(sql, con=connection)
		
		# ----------------------------------------
		
		# Select the average daily data from the table
		sql = f"SELECT Post_Date, Price FROM cl_properties WHERE City = '{city}' AND Post_Date > '2021-03-01' ORDER BY Post_Date"

		# Query out data
		timeSeriesData = pd.read_sql(sql, con=connection)
		
		# Get dates 
		dates = list(timeSeriesData['Post_Date'].map(pd.Timestamp).unique())
		
		upperBounds = []
		lowerBounds = []
		volume = []
		plotDates = []
		lastDay = dates[0]
		
		# Loop through dates 
		for i, date in enumerate(dates):
		
			# # Check for data gaps
			# if int(date - lastDay) > 86400000000000*5:
				# print(f'{date} to {lastDay} is more than 1 day')
				
				# # * Close bounds on begining after gap 
				
				# # Close bounds 
				# upperBounds.append(lastLowerBounds)
				# lowerBounds.append(lastLowerBounds)
				# plotDates.append(datetime.datetime.strptime(str(lastDay)[:10], '%Y-%m-%d'))
				# # plotDates = np.insert(plotDates, i, date, 0) 
				
				# # Break for visualization 
				# upperBounds.append(None)
				# lowerBounds.append(None)
				# volume.append(None)
				# plotDates.append(datetime.datetime.strptime(str(lastDay)[:10], '%Y-%m-%d'))
				# # plotDates = np.insert(plotDates, i, None, 0) 
				
			# # Update lastDay
			# lastDay = date
			
			# Get dataset 
			dataset = timeSeriesData[timeSeriesData['Post_Date'].map(pd.Timestamp) == date]['Price']
			
			# Get sampleSize
			sampleSize = dataset.count()
			
			# Get degree of freedom from sampleSize 
			degreesOfFreedom = sampleSize - 1
			
			# Define confidence level
			confidenceLevel = 95
			alpha = (1-confidenceLevel/100)/2
			
			# Look up the tValue
			tValue = stats.t.ppf(1-alpha, degreesOfFreedom)
			
			# Get the std
			std = dataset.std()
			
			# Divide sample std by square root of the sampleSize
			stdDivSS = std/(sampleSize)**0.5
			
			# Calculate standardError
			standardError = tValue*stdDivSS
			
			# Get sampleMean
			sampleMean = dataset.mean()
			
			# Calculate upper and lower bounds
			upperBound = sampleMean + standardError
			lowerBound = sampleMean - standardError
			lastLowerBounds = lowerBound
			
			# Check for data gaps
			if int(date - lastDay) > 86400000000000*5:
				print(f'{date} to {lastDay} is more than 1 day')
				
				# Close bounds 
				upperBounds.append(lastLowerBounds)
				lowerBounds.append(lastLowerBounds)
				volume.append(None)
				plotDates.append(datetime.datetime.strptime(str(lastDay)[:10], '%Y-%m-%d'))
				# plotDates = np.insert(plotDates, i, date, 0) 
				
				# Break for visualization 
				upperBounds.append(None)
				lowerBounds.append(None)
				volume.append(None)
				plotDates.append(datetime.datetime.strptime(str(lastDay)[:10], '%Y-%m-%d'))
				# plotDates = np.insert(plotDates, i, None, 0) 
				
				# Close bounds after gap 
				upperBounds.append(lowerBound)
				lowerBounds.append(lowerBound)
				volume.append(None)
				plotDates.append(datetime.datetime.strptime(str(date)[:10], '%Y-%m-%d'))
				
			# Update lastDay
			lastDay = date
			
			# Add to placeholder lists
			upperBounds.append(upperBound)
			lowerBounds.append(lowerBound)
			plotDates.append(datetime.datetime.strptime(str(lastDay)[:10], '%Y-%m-%d'))
			# plotDates = np.insert(plotDates, i, date, 0) 
			volume.append(sampleSize)
			
		# ----------------------------------------
		
		# Handle begining and end bounds
		upperBounds.insert(0,lowerBounds[0])
		lowerBounds.insert(0,lowerBounds[0])
		volume.insert(0, None)
		plotDates.insert(0, datetime.datetime.strptime(str(dates[0])[:10], '%Y-%m-%d'))
		# plotDates = np.insert(plotDates, i, dates[0], 0) 
		upperBounds.append(lowerBounds[-1])
		lowerBounds.append(lowerBounds[-1])
		plotDates.append(datetime.datetime.strptime(str(dates[-1])[:10], '%Y-%m-%d'))
		volume.append(None)
		# plotDates = np.insert(plotDates, i, dates[-1], 0) 
		
		# Open figure 
		fig = plt.figure(figsize = (12, 7))

		# Get current axis 
		ax = plt.gca()
		# Make secondary axis 
		ax2 = ax.twinx()
		
		# Convert arrays 
		upperBounds = np.array(upperBounds, dtype=float)
		lowerBounds = np.array(lowerBounds, dtype=float)
		
		# Plot the data 
		lns1 = ax.plot_date(dates, timeSeriesAverages['Average Price'], '-b', label='Average Daily Price')
		lns1 = ax.plot_date(plotDates, upperBounds, '-', color='k', label='Daily Fences')
		ax.plot_date(plotDates, lowerBounds, '-', color='k')
		ax.fill_between(plotDates, lowerBounds, upperBounds, color='cyan')
		
		# Plot volume on separate axis 
		lns2 = ax2.plot_date(plotDates, volume, '-.k', label='Volume')

		# Get labels *
		lns = lns1 + lns2
		labs = [l.get_label() for l in lns]
		# plt.legend([inp+'- '+Output,'Ground Surface'], loc='upper left', prop={'size':9}, numpoints=1)
		fig.legend(lns, labs, loc='upper left', prop={'size':9}, numpoints=1)
		
		ax.set_ylabel('US $')
		ax2.set_ylabel('# of Properties')
		ax.set_xlabel('Date')
		plt.xticks(rotation=75)
		plt.setp( ax.xaxis.get_majorticklabels(), rotation=35 )
		ax.ticklabel_format(axis='y', style='plain')
		ax2.ticklabel_format(axis='y', style='plain')
		ax.set_yscale('log')
		# ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())
		formatter = ScalarFormatter()
		formatter.set_scientific(False)
		ax.yaxis.set_major_formatter(formatter)
		ax.yaxis.set_minor_formatter(formatter)

		# * Make ax2 scale fit 
		ax.set_ylim(0, max(filter(None.__ne__, upperBounds))*1.1)
		ax2.set_ylim(0, max(filter(None.__ne__, volume))*1.1)
		
		# Make plot title
		plt.title(f'Real Estate Price Data for {city}')

		# Add grid
		ax.grid(True)

		fig.tight_layout()

		# Check that the save file path exists
		if not os.path.exists('Figures'+os.sep):
			os.makedirs('Figures'+os.sep)

		# Create folder to save files in 
		if not os.path.exists(f'Figures{os.sep}Price Time Series{os.sep}{str(date)[:10]}{os.sep}'):
			os.makedirs(f'Figures{os.sep}Price Time Series{os.sep}{str(date)[:10]}{os.sep}')

		# Save the figure
		fig.savefig(f'Figures{os.sep}Price Time Series{os.sep}{str(date)[:10]}{os.sep}{city}.png', dpi=500)
		# plt.show()

# # Group into daily for each city 
# timeSeriesData.groupby(['City','Post_Date'])

# # Group into daily data
# timeSeriesData.groupby(pd.Grouper(freq='D')).mean()

# -----------------------------------------
# Length of time on market
# -----------------------------------------

sql = '''select url, min(post_date), max(post_date) 
from cl_properties 
where city = 'Albuquerque' 
group by url'''

# * Add box plot to time series. 
# * Length of time on market