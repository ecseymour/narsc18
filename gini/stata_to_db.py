import pandas as pd
import sqlite3 as sql

# connect to db
db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.text_factory=str
cur = con.cursor()

years = ['1990', '2000', '125']

for y in years:	

	df = pd.read_csv('/home/eric/Documents/franklin/narsc2018/generated_data/binned_income/county_ests_{}.csv'.format(y))
	df.index = df['fips_new']
	# print df.head()

	cols = ['gini', 'mean', 'median']

	if y == '125':
		df_125 = df[cols]
	elif y == '2000':
		df_2000 = df[cols]
	elif y == '1990':
		df_1990 = df[cols]
		df_1990.loc['G1200860', 'gini'] = df_1990.loc['G1200250']['gini']

# use left join to retain Broomfield County, CO - only exists after 2001
merged = pd.merge(df_125, df_2000, left_index=True, right_index=True, suffixes=("_10", "_00"), how='left')
df_1990 = df_1990.add_suffix("_90")
merged = pd.merge(merged, df_1990, left_index=True, right_index=True, how='left')

merged.index.names =['GISJOIN']
merged.to_sql('county_gini_rpme', con, if_exists='replace')

con.close()

print "done"