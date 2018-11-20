'''
calc age-specific county diversity scores
for 80, 00 and 10

age groups include:
* under 5 years
* 5 to 17 years
* 18 to 64 years
* 65 years and over

racial/ethnic groups:
* NH White
* NH Black
* Hispanic
* Other

NOTE: Asian is grouped with American Indian, not an independent category in these TS tables

think about how to merge separate dataframes for age AND decade

Need to handle 1980 "two or more races" differently
first write script to handle 2000 and 2010
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

def calc_entropy(df):
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
	return df


years = ['2010', '2000']

# for each decade, iterate through age groups, collecting race/ethnicity data for each age group
# unfortunately, data are organized first by hispanic origin and race

for y in years:
	
	print y

	if y in ['2010', '2000']:

		# under 5
		qry = '''
			SELECT GISJOIN, 
			AW9AA{} AS nh_white, --NH white--
			AW9AE{} AS nh_black, --NH black--
			AW9AQ{} + AW9AU{} + AW9AY{} + AW9BC{} AS hisp,
			AW9AI{} + AW9AM{} AS other  
			FROM county_hispanic_origin_age 
			WHERE AW9AA{} <> '' AND AW9AA{} > 0 AND STATE <> 'Puerto Rico'
			;
			'''.format(y,y,y,y,y,y,y,y,y,y)	
		df = pd.read_sql(qry, con, index_col='GISJOIN')
		df['total'] = df.sum(axis=1)
		df_under5 = calc_entropy(df)

		# 5 to 17
		qry = '''
			SELECT GISJOIN, 
			AW9AB{} AS nh_white, --NH white--
			AW9AF{} AS nh_black, --NH black--
			AW9AR{} + AW9AV{} + AW9AZ{} + AW9BD{} AS hisp,
			AW9AJ{} + AW9AN{} AS other  
			FROM county_hispanic_origin_age 
			WHERE AW9AB{} <> '' AND AW9AB{} > 0 AND STATE <> 'Puerto Rico'
			;
			'''.format(y,y,y,y,y,y,y,y,y,y)	
		df = pd.read_sql(qry, con, index_col='GISJOIN')
		df['total'] = df.sum(axis=1)
		df_5to17 = calc_entropy(df)

		# 18 to 64
		qry = '''
			SELECT GISJOIN, 
			AW9AC{} AS nh_white, --NH white--
			AW9AG{} AS nh_black, --NH black--
			AW9AS{} + AW9AW{} + AW9BA{} + AW9BE{} AS hisp,
			AW9AK{} + AW9AO{} AS other  
			FROM county_hispanic_origin_age 
			WHERE AW9AC{} <> '' AND AW9AC{} > 0 AND STATE <> 'Puerto Rico'
			;
			'''.format(y,y,y,y,y,y,y,y,y,y)	
		df = pd.read_sql(qry, con, index_col='GISJOIN')
		df['total'] = df.sum(axis=1)
		df_18to64 = calc_entropy(df)

		# 65+
		qry = '''
			SELECT GISJOIN, 
			AW9AD{} AS nh_white, --NH white--
			AW9AH{} AS nh_black, --NH black--
			AW9AT{} + AW9AX{} + AW9BB{} + AW9BF{} AS hisp,
			AW9AL{} + AW9AP{} AS other  
			FROM county_hispanic_origin_age 
			WHERE AW9AD{} <> '' AND AW9AC{} > 0 AND STATE <> 'Puerto Rico'
			;
			'''.format(y,y,y,y,y,y,y,y,y,y)	
		df = pd.read_sql(qry, con, index_col='GISJOIN')
		df['total'] = df.sum(axis=1)
		df_65plus = calc_entropy(df)

		# merged dfs
		merged = pd.merge(df_under5, df_5to17, left_index=True, right_index=True, suffixes=('_under5', '_5to17'))
		df_18to64 = df_18to64.add_suffix('_18to64')
		df_65plus = df_65plus.add_suffix('_65plus')
		merged = pd.merge(merged, df_18to64, left_index=True, right_index=True)
		merged = pd.merge(merged, df_65plus, left_index=True, right_index=True)

		if y=='2010':
			merged_2010 = merged
			merged_2010 = merged_2010.add_suffix('_2010')
		elif y=='2000':
			merged_2000 = merged
			merged_2000 = merged_2000.add_suffix('_2000')

merged = pd.merge(merged_2010, merged_2000, left_index=True, right_index=True)
print merged.head()

merged.to_sql("county_diversity_by_age", con, if_exists="replace")

con.close()

print 'done'