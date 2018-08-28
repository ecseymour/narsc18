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
			FROM nhgis_race_norm_90_10_tract 
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
			FROM nhgis_race_norm_90_10_tract 
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

	# calc pct NH white, NH black, and NH asian
	df['nh_white'] = df['CW7AA{}'.format(y)]
	df['pwhite'] = df['nh_white'] * 1.0 / df['total']

	df['nh_black'] = df['CW7AB{}'.format(y)]
	df['pblack'] = df['nh_black'] / df['total']
	
	df['nh_asian'] = df['CW7AD{}'.format(y)]	
	df['pasian'] = df['nh_asian'] * 1.0 / df['total']

	# calc total and share hispanic
	df['hisp'] = 0
	if y in ['2010', '2000']:
		for alpha in ['G', 'H', 'I', 'J', 'K', 'L']:
			df['hisp'] += df['CW7A{}{}'.format(alpha, y)] 
	
		df['other'] = df['CW7AC{}'.format(y)] + df['CW7AE{}'.format(y)] + df['CW7AF{}'.format(y)]
	
	else: # if 1990
		for alpha in ['G', 'H', 'I', 'J', 'K']:
			df['hisp'] += df['CW7A{}{}'.format(alpha, y)] 

		df['other'] = df['CW7AC{}'.format(y)] + df['CW7AE{}'.format(y)]

	df['phisp'] = df['hisp'] * 1.0 / df['total']		
	df['pother'] = df['other'] * 1.0 / df['total']

	# calc multigroup entropy index FIVE GROUPS
	# calc score excluding asian
	# need to handle 0 values for group proportion
	groups = ['pwhite', 'pblack', 'pasian', 'phisp', 'pother']
	df['diversity_5grp'] = 0
	for group in groups:
		df.loc[df['{}'.format(group)] > 0.0, 'diversity_5grp'] += df['{}'.format(group)] * np.log( 1.0 / df['{}'.format(group)] )

	print df['diversity_5grp'].describe()
	##################################################################################
	# calc second measure grouping asian w/ "other" populations
	df['other_4grp'] = df['other'] + df['nh_asian']
	df['pother_4grp'] = df['other_4grp'] * 1.0 / df['total']
	groups = ['pwhite', 'pblack', 'phisp', 'pother_4grp']
	df['diversity_4grp'] = 0
	for group in groups:
		df.loc[df['{}'.format(group)] > 0.0, 'diversity_4grp'] += df['{}'.format(group)] * np.log( 1.0 / df['{}'.format(group)] )
	##################################################################################
	# calc diversity excluding asian and "other" populations
	# recalculate percantages using sum of nh white, nh black, and hispanic
	# get counts for those groups and sum to create total
	
	df['total_3grp'] = df['nh_white'] + df['nh_black'] + df['hisp']

	df['pwhite_3grp'] = df['nh_white'] * 1.0 / df['total_3grp']
	df['pblack_3grp'] = df['nh_black'] * 1.0 / df['total_3grp']
	df['phisp_3grp'] = df['hisp'] * 1.0 / df['total_3grp']

	groups_3grp = ['pwhite_3grp', 'pblack_3grp', 'phisp_3grp']
	df['diversity_3grp'] = 0
	for group in groups_3grp:
		df.loc[df['{}'.format(group)] > 0.0, 'diversity_3grp'] += df['{}'.format(group)] * np.log( 1.0 / df['{}'.format(group)] )
	##################################################################################

	# create separate dataframes for each year to merge into single df
	groups = ['nh_white', 'nh_black', 'nh_asian', 'hisp', 'other', 
		'pwhite', 'pblack', 'pasian', 'phisp', 'pother', 
		'diversity_5grp', 'diversity_4grp', 'diversity_3grp', 'total', 'total_3grp']
	
	if y == "2010":
		df_2010 = df[groups]
	elif y == "2000":
		df_2000 = df[groups]
	elif y == "1990":
		df_1990 = df[groups]

	# df.to_csv("/home/eric/Documents/franklin/depop_impacts/data/{}_diversity_{}.csv".format(g, y))

merged = pd.merge(df_2010, df_2000, left_index=True, right_index=True, suffixes=("_10", "_00"))
df_1990 = df_1990.add_suffix("_90")
merged = pd.merge(merged, df_1990, left_index=True, right_index=True, )
# print merged.columns

merged.to_sql("tract_diversity", con, if_exists="replace")

cur.execute("CREATE INDEX idx_tract_diversity_gisjoin ON tract_diversity(GISJOIN);")

con.close()

print 'done'