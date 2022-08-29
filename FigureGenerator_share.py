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

# Shorten path to one folder up for outputs
path = path[:-path[::-1].find(os.sep)]

# Define path as working directory
os.chdir(path)

# I'm using a local DB, you will need to read in from .csv

# # Get DB configuration
# config = configparser.ConfigParser()
# config.read(path+os.sep+'db.ini')

# # Define a connection
# connection = create_engine("mysql+pymysql://"+config['mysql']['user']+":"+config['mysql']['password']+"@"+config['mysql']['host']+"/"+config['mysql']['db']+"")    

# Get date
today = str(datetime.datetime.today())[:10]

# ------------------------------------------------------
# INPUTS
# ------------------------------------------------------
	
print(f'Getting most recent date')

# Select the data from the table
sql = f"SELECT Post_Date FROM cl_properties GROUP BY Post_Date ORDER BY Post_Date DESC"
# Query out data
date = pd.read_sql(sql, con=connection)

# Get just date
date = date['Post_Date'][0]

print(f'Getting data from most recent date')

# Select the data from the table
sql = f"SELECT * FROM cl_properties where Post_Date = '{date}' ORDER BY City"

# Query out data
data = pd.read_sql(sql, con=connection)

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
plt.show()

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
plt.show()

# -----------------------------------------
# Time Series
# -----------------------------------------

# Open figure 
fig = plt.figure(figsize = (12, 7))

# Select cities from the table
sql = f"SELECT City FROM cl_properties GROUP BY City"

# Query out data
cities = pd.read_sql(sql, con=connection)

# Loop through cities
for city in cities.iterrows():

	city = city[1]['City']
	
	# Make sure it is not blank
	if city != '':
	
		print(f'Querying data for {city}')
		
		# Select the data from the table
		sql = f"SELECT Post_Date, AVG(Price) AS 'Average Price' FROM cl_properties WHERE City = '{city}' GROUP BY Post_Date ORDER BY Post_Date"

		# Query out data
		timeSeriesData = pd.read_sql(sql, con=connection)
		
		# Plot the data 
		plt.plot_date(timeSeriesData['Post_Date'], timeSeriesData['Average Price'], '-', label=city)

# Get labels *

plt.ylabel('US $')
plt.xlabel('Date')
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
fig.savefig(f'Figures{os.sep}Price Time Series- {date}.png',dpi=500)
plt.show()

# # Or get all data and do the grouping and sorting on ite
# sql = f"SELECT * FROM cl_properties"

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