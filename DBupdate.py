# DBupdate_raw_data.py

# Written by Casey Gierke of AlbuGierke Environmental Solutions
# 12/29/2020

# With Notepad++, use F5 then copy this into box
# C:\Users\Casey\Anaconda3\python.exe -i "$(FULL_CURRENT_PATH)"

# ------------------------------------------------------
# IMPORTS
# ------------------------------------------------------

import os
import glob
import pymysql.cursors
import datetime
import configparser

# ------------------------------------------------------
# DEFINE FUNCTIONS
# ------------------------------------------------------

# Define a database command
def DB(SQL):
	connection = pymysql.connect(host=config['mysql']['host'], user=config['mysql']['user'], password=config['mysql']['password'], db= config['mysql']['db'], charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, local_infile=True)

	try:
		with connection.cursor() as cursor:
			cursor.execute(SQL)
		connection.commit()
	finally:
		connection.close()

def DB_get(SQL):
	db = pymysql.connect(host=config['mysql']['host'], user=config['mysql']['user'], password=config['mysql']['password'], db= config['mysql']['db'], charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, local_infile=True)
	db.autocommit = True

	# Prepare a cursor object using cursor() method
	cursor = db.cursor()
	cursor.execute(SQL)
	result = cursor.fetchall()
	db.close()
	return result

def SQLpath(filePath):
	return filePath.replace(os.sep,'/')
	
# # Define maxTimer to get the max time from user defined table
# def maxTimer(table):
	# sql = 'SELECT MAX(Timestamp) FROM '+table
	# MaxTime = DB_get(sql)[0]['MAX(Timestamp)']
	# month = str(MaxTime.month)
	# day = str(MaxTime.day)
	# # Check if they are single digits
	# if len(month) == 1:
		# month = '0'+month
	# if len(day) == 1:
		# day = '0'+day
	# return str(MaxTime.year) + month + day

# def datetimeToString(dt):
	# for item in dt[0]:
		# key = item
		# # print(key)
	# # print(dt[0])
	# dt = dt[0][key]
	# return str(dt.year) + str(dt.month) + str(dt.day)

# ------------------------------------------------------
# INPUTS
# ------------------------------------------------------

# Define path
path = os.path.abspath(os.path.dirname(__file__))
os.chdir(path)

# Get DB configuration
config = configparser.ConfigParser()
config.read(path+os.sep+'db.ini')

# Shorten path to one folder up
path = path[:-path[::-1].find(os.sep)]

# Define database to use
database = 'cl_properties'

# ------------------------------------------------------
# Initial setup commands
# ------------------------------------------------------

# DROP TABLE cl_properties;
# CREATE TABLE cl_properties (City VARCHAR(50), Nation VARCHAR(50), Title VARCHAR(300), Price DOUBLE, URL VARCHAR(300), Post_Date DATE);
# # ALTER DATABASE cl_properties CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci;

# ------------------------------------------------------
# Upload new data
# ------------------------------------------------------
	
# Read in all input file names
inputFiles = glob.glob(f'{path}txt Files{os.sep}*.txt')
# # Short circuit
# inputFiles = [inputFiles[-1]]

# Get dates from DB
sql = 'SELECT Post_Date FROM cl_properties GROUP BY Post_Date'
DBdatesObject = DB_get(sql)
DBdates = []

for item in DBdatesObject:
	DBdates.append(item['Post_Date'])
	
# Loop through inputFiles
for file in inputFiles:
	
	# Get date from file name
	date = datetime.datetime.strptime(file[-14:-4], '%Y-%m-%d')
	# Shave off time
	date = datetime.date(date.year, date.month, date.day)
	
	# Check if this data has been entered
	if date in DBdates:
		print(f'{date} in DB')
		continue
	else:
		print(f'{date} not in DB, adding now.')
		
		# Convert file path to sql format
		filePath = SQLpath(file)
		# Create sql
		sql = f'LOAD DATA LOCAL INFILE "{filePath}" INTO TABLE cl_properties CHARACTER SET utf8mb4'
		# Send to DB
		DB(sql)

# # Select most recent folder
# downDate = max(Folders)

# # Convert for naming
# downDate = downDate.replace('-','')
# print('RD 1. Most recent download file is '+downDate)

# # ------------------------------------------------------
# # Find most recent backup files
# # ------------------------------------------------------

# # First, we must find the most recent update file, get the update files available
# backups_Raw = []
# for file in glob.glob(path+os.sep+'Data Files'+os.sep+'Backup Files'+os.sep+'Raw_Data_*.txt'):
    # backups_Raw.append(file[-12:-4])

# # Select most recent folder
# backup_Raw = max(backups_Raw)
# print('RD 2. Most recent Raw_Data backup file is '+backup_Raw)

# # ------------------------------------------------------
# # Get list of tables
# # ------------------------------------------------------
	
# sql = "SHOW TABLES"
# tablesObject = DB_get(sql)

# # Get table names from tablesObject
# tables = []
# for item in tablesObject:
	# tables.append(item['Tables_in_'+database])

# # ------------------------------------------------------
# # Run SQL commands on DB
# # ------------------------------------------------------

# # Get MaxTimeRaw from DB
# MaxTimeRaw = maxTimer('raw_data')

# # ------------------------------------------------------
# # Import new raw data
# # ------------------------------------------------------

# # Check if MaxTimeRaw is similar to the download date
# if abs(int(MaxTimeRaw) - int(downDate)) < 30:
	# print('RD 3. It appears that the most recent raw data has already been uploaded \nto the DB so we will move on.')

# else:
	# # Check if recent download table exists, import it if not
	# if 'raw_data_'+downDate not in tables:
		# print('RD 3.a Need to import raw_data_'+downDate)

		# sql = 'CREATE TABLE raw_data_'+downDate+' (Site_ID VARCHAR(20), Timestamp Datetime, Water_m DOUBLE, TempC DOUBLE)'
		# DB(sql)
		
		# # Create a dynamic infilePath variable with SQL formatting
		# infilePath = SQLpath(path+os.sep+'Data Files'+os.sep+'DB Input Files'+os.sep+'raw_data_'+downDate+'.txt')
		
		# sql = 'LOAD DATA LOCAL INFILE "'+ infilePath +'" INTO TABLE raw_data_'+downDate
		# DB(sql)
		# sql = 'ALTER TABLE raw_data_'+downDate+' ADD COLUMN ID_KEY VARCHAR(30)'
		# DB(sql)
		# sql = "UPDATE raw_data_"+downDate+" SET ID_KEY = CONCAT(Site_ID, '- ', Timestamp)"
		# DB(sql)
		# print('RD 3.b raw_data_'+downDate+' imported')
	# else:
		# print('RD 3. raw_data_'+downDate+' already exists, moving on.')
	
	# # ------------------------------------------------------
	# # Cull new raw data down to only what we need to update
	# # ------------------------------------------------------

	# F.maxTimesTableMaker('raw_data', tables, downDate)
		
	# # ------------------------------------------------------
	# # Insert most recent download data into raw_data_update table
	# # ------------------------------------------------------

	# print('RD 5.b.i Need to process new data.')
	
	# # Drop update table if it exists
	# sql = 'DROP TABLE IF EXISTS raw_data_update'
	# DB(sql)

	# # Create a raw_data_update table and populate it with the new data
	# print('RD 5.b.ii Create raw_data_update table.')
	# sql = 'CREATE TABLE raw_data_update AS SELECT New.* FROM raw_data_'+downDate+' New JOIN max_times_raw_data Old ON New.Site_ID = Old.Site_ID WHERE New.Timestamp > Old.MaxTime'
	# DB(sql)
	
	# # # Add the ID_Key column
	# # sql = 'ALTER TABLE raw_data_update ADD COLUMN ID_KEY VARCHAR(30)'
	# # DB(sql)
	# # sql = "UPDATE raw_data_update SET ID_KEY = CONCAT(Site_ID, '- ', Timestamp)"
	# # DB(sql)
		
	# # Insert only the data from the most recent download that is new
	# print('RD 5.b.iii Insert data from raw_data_update into raw_data.')
	# sql = 'INSERT INTO raw_data SELECT * FROM raw_data_update'
	# DB(sql)
	# print('RD 5.b.iv All data compiled into raw_data')
		
	# # # We should not need the raw_data_date table anymore so we can drop that
	# # sql = 'DROP TABLE IF EXISTS raw_data_'+downDate
	# # DB(sql)

# # Drop update table if it exists
# if 'raw_data_update' in tables:
	# sql = 'DROP TABLE IF EXISTS raw_data_update'
	# DB(sql)
	# print('RD 3. raw_data_update table dropped.')

# # ------------------------------------------------------
# # Create new raw_data backup file if it does not already exist
# # ------------------------------------------------------

# print('RD 6. Backup...')
# F.backup('raw_data', downDate)
	