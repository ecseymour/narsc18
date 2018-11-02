'''
read calculated gini into database
iterate over each years and merge into single table
'''

import sqlite3 as sql
import pandas as pd

# connect to db
db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.text_factory=str
cur = con.cursor()

years = ['1990', '2000', '125']

for y in years:

	infile = "/home/eric/Documents/franklin/narsc2018/generated_data/binned_income/county_gini_{}_fit.csv".format(y)

	df = pd.read_csv(infile, dtype={'aic.FIPS': str})
	df.index = df['aic.FIPS']
	df.index.name = 'FIPS'
	cols = ['aic.gini', 'aic.theil', 'aic.distribution']
	df = df[cols]
	df.rename(columns={'aic.gini': 'gini', 'aic.theil': 'theil', 'aic.distribution': 'distribution'}, inplace=True)

	if y == '125':
		df_125 = df
	elif y == '2000':
		df_2000 = df
	elif y == '1990':
		df_1990 = df

merged = pd.merge(df_125, df_2000, left_index=True, right_index=True, suffixes=("_10", "_00"))
df_1990 = df_1990.add_suffix("_90")
merged = pd.merge(merged, df_1990, left_index=True, right_index=True, )

merged.index.names =['GISJOIN']
merged.to_sql('county_gini_bestfit', con, if_exists='replace')

con.close()

print "done"