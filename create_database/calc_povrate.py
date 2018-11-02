import sqlite3 as sql
from string import ascii_uppercase
import pandas as pd
import numpy as np
import math

# connect to db
db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.text_factory=str
cur = con.cursor()

years = ['125', '2000', '1990']

for y in years:

	qry = '''
	SELECT GISJOIN,
	AX7AA{} * 1.0 / (AX7AA{} + AX7AB{}) AS povrate
	FROM county_poverty;
	'''.format(y, y, y)
	df = pd.read_sql(qry, con, index_col='GISJOIN')
	print df.head()

	if y == "125":
		df_2010 = df
	elif y == "2000":
		df_2000 = df
	elif y == "1990":
		df_1990 = df
		# update miami-date 1990 w/ dade values
		df_1990.loc['G1200860', 'povrate'] = df_1990.loc['G1200250']['povrate']
		df_1990.drop('G1200250', inplace=True)

merged = pd.merge(df_2010, df_2000, left_index=True, right_index=True, suffixes=("_10", "_00"))
df_1990 = df_1990.add_suffix("_90")
merged = pd.merge(merged, df_1990, left_index=True, right_index=True, )

print merged.head()



merged.to_sql("county_povrate", con, if_exists="replace")

con.close()