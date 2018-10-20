'''
read rural-urban continuum codes to db
'''

import pandas as pd
import sqlite3 as sql

# connect to db
db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.text_factory=str
cur = con.cursor()
# read in excel w/ xwalk data
inFile = "/home/eric/Documents/franklin/narsc2018/source_data/usda/ruralurbancodes2003.xls"
# keep/convert fips codes as text/string
converters = {
	'Metropolitan Division Code': str, 
	'CSA Code': str, 
	'FIPS Code': str 
	}
	
df = pd.read_excel(inFile, converters=converters)
# replace spaces in col names w/ underscores
# df.columns = [x.strip().replace(' ', '_') for x in df.columns]
# df.columns = [x.strip().replace('/', '_') for x in df.columns]
df.columns = ['fips', 'state', 'county', 'code1993', 'code2003', 'pop2000', 'percent_commuting', 'description']
df.index = df['fips']
df = df.loc[:,'state':]
print df.head()
df.to_sql('usda_rural_urban', con, if_exists='replace')

con.close()