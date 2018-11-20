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

	infile = "/home/eric/Documents/franklin/narsc2018/generated_data/binned_income/county_gini_{}_GA.csv".format(y)

	df = pd.read_csv(infile, dtype={'FIPS': str})
	df.index = df['FIPS']

	cols = ['gini', 'theil']

	if y == '125':
		df_125 = df[cols]
	elif y == '2000':
		df_2000 = df[cols]
	elif y == '1990':
		df_1990 = df[cols]
		df_1990.loc['G1200860', 'gini'] = df_1990.loc['G1200250']['gini']
		df_1990.loc['G1200860', 'theil'] = df_1990.loc['G1200250']['theil']
		df_1990.drop('G1200250', inplace=True)	

merged = pd.merge(df_125, df_2000, left_index=True, right_index=True, suffixes=("_10", "_00"))
df_1990 = df_1990.add_suffix("_90")
merged = pd.merge(merged, df_1990, left_index=True, right_index=True)

merged.index.names =['GISJOIN']
merged.to_sql('county_gini_GA', con, if_exists='replace')

con.close()

print "done"