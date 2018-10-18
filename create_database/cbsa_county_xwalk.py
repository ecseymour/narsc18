'''
read cbsa to county xwalk to db
use 2003 definitions taken from here
https://www.census.gov/geographies/reference-files/time-series/demo/metro-micro/historical-delineation-files.html
https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2003/historical-delineation-files/030606omb-cbsa-csa.xls
'''

import pandas as pd
import sqlite3 as sql

# connect to db
db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.text_factory=str
cur = con.cursor()
# read in excel w/ xwalk data
inFile = "/home/eric/Documents/franklin/narsc2018/source_data/census/reference_files/030606omb-cbsa-csa.xls"
# keep/convert fips codes as text/string
converters = {
	'Metropolitan Division Code': str, 
	'CSA Code': str, 
	'FIPS': str 
	}
	
df = pd.read_excel(inFile, skiprows=2, skipfooter=4, converters=converters)
# replace spaces in col names w/ underscores
df.columns = [x.strip().replace(' ', '_') for x in df.columns]
df.columns = [x.strip().replace('/', '_') for x in df.columns]
df.rename(columns={'Status,_1=metro_2=micro': 'Status'}, inplace=True)
# set county FIPS as index
df.index = df['FIPS']
# print df.head()
# print df.groupby('Status').size()
# print len(df)
# keep all cols except CBSA code, now that it is stored as index
df = df.loc[:,:'State']
# make custom 5 digit county fips code
# df['fips5digit'] = df['FIPS_State_Code'] + df['FIPS_County_Code']
# print top 20 rows
print df.head(20)
# save to research db
df.to_sql('cbsa_county_xwalk_2003', con, if_exists='replace')
# index fips code
con.close()