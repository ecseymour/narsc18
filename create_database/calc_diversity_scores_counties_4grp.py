'''
calc county diversity score
for 90, 00 and 10

need to handle 1990 data differently because of 
diff number of available cols
'''

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

years = ['2010', '2000', '1990']

for y in years:
	
	print y

	if y in ['2010', '2000']:
		qry = '''
			SELECT GISJOIN, 
			CW7AA{},
			CW7AB{},
			CW7AC{},
			CW7AD{},
			CW7AE{},
			CW7AF{},
			CW7AG{},
			CW7AH{},
			CW7AI{},
			CW7AJ{},
			CW7AK{},
			CW7AL{}
			FROM nhgis_pop_race_norm_90_10 
			WHERE CW7AA{} <> '' AND CW7AA{} > 0 AND STATE <> 'Puerto Rico'
			;
			'''.format(y,y,y,y,y,y,y,y,y,y,y,y,y,y)

	else: # remove F and L cols from query
		qry = '''
			SELECT GISJOIN, 
			CW7AA{},
			CW7AB{},
			CW7AC{},
			CW7AD{},
			CW7AE{},
			CW7AG{},
			CW7AH{},
			CW7AI{},
			CW7AJ{},
			CW7AK{}
			FROM nhgis_pop_race_norm_90_10 
			WHERE CW7AA{} <> '' AND CW7AA{} > 0 AND STATE <> 'Puerto Rico'
			;
			'''.format(y,y,y,y,y,y,y,y,y,y,y,y)

	# print qry

	
	df = pd.read_sql(qry, con, index_col='GISJOIN')

	# calc total by summing all cols
	alpha_list = []
	for c in ascii_uppercase:
		alpha_list.append(c)
		if c=='L':
			break

	df['total'] = 0
	total_us = 0
	if y in ['2010', '2000']:
		for a in alpha_list:
			df['total'] += df['CW7A{}{}'.format(a, y)]
	else:
		for a in alpha_list:
			if a not in ['F', 'L']:
				df['total'] += df['CW7A{}{}'.format(a, y)]
			else:
				pass

	df['nh_white'] = df['CW7AA{}'.format(y)]
	df['nh_black'] = df['CW7AB{}'.format(y)]
	df['nh_asian'] = df['CW7AD{}'.format(y)]	
	# count total hispanic and other
	df['hisp'] = 0
	if y in ['2010', '2000']:
		for alpha in ['G', 'H', 'I', 'J', 'K', 'L']:
			df['hisp'] += df['CW7A{}{}'.format(alpha, y)] 
	
		df['other'] = df['CW7AC{}'.format(y)] + df['CW7AE{}'.format(y)] + df['CW7AF{}'.format(y)]
	
	else: # if 1990
		for alpha in ['G', 'H', 'I', 'J', 'K']:
			df['hisp'] += df['CW7A{}{}'.format(alpha, y)] 

		df['other'] = df['CW7AC{}'.format(y)] + df['CW7AE{}'.format(y)]

	# add asian to other
	df['other'] += df['nh_asian']

	# calc pct of total for each group
	cols = ['nh_white', 'nh_black', 'hisp', 'other'] 
	for c in cols:
		if 'nh' in c:
			c2 = c.split('_')[1]
		else:
			c2 = c
		df['p{}'.format(c2)] = df[c] * 1.0 / df['total'] 

	# calc multigroup entropy index four GROUPS
	# calc score excluding asian
	# need to handle 0 values for group proportion
	groups = ['pwhite', 'pblack', 'phisp', 'pother']
	df['diversity_4grp'] = 0
	for group in groups:
		df.loc[df['{}'.format(group)] > 0.0, 'diversity_4grp'] += df['{}'.format(group)] * np.log( 1.0 / df['{}'.format(group)] )
	# scale value
	df['diversity_4grp'] = df['diversity_4grp'] / np.log(4) 
	print df['diversity_4grp'].describe()
	##################################################################################
	# create separate dataframes for each year to merge into single df
	groups = ['nh_white', 'nh_black', 'nh_asian', 'hisp', 'other', 'total', 
		'pwhite', 'pblack', 'phisp', 'pother', 'diversity_4grp',]
	
	if y == "2010":
		df_2010 = df[groups]
	elif y == "2000":
		df_2000 = df[groups]
	elif y == "1990":
		df_1990 = df[groups]

merged = pd.merge(df_2010, df_2000, left_index=True, right_index=True, suffixes=("_10", "_00"))
df_1990 = df_1990.add_suffix("_90")
merged = pd.merge(merged, df_1990, left_index=True, right_index=True, )

merged.to_sql("county_diversity", con, if_exists="replace")

con.close()

print 'done'