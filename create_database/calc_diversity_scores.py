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

	df['pwhite'] = df['CW7AA{}'.format(y)] * 1.0 / df['total']
	df['pblack'] = df['CW7AB{}'.format(y)] * 1.0 / df['total']
	df['pasian'] = df['CW7AD{}'.format(y)] * 1.0 / df['total']

	if y in ['2010', '2000']:
		df['phisp'] = ( df['CW7AG{}'.format(y)] + df['CW7AH{}'.format(y)] + df['CW7AI{}'.format(y)] + df['CW7AJ{}'.format(y)] + df['CW7AK{}'.format(y)] + df['CW7AL{}'.format(y)] ) * 1.0 / df['total']
	else:
		df['phisp'] = ( df['CW7AG{}'.format(y)] + df['CW7AH{}'.format(y)] + df['CW7AI{}'.format(y)] + df['CW7AJ{}'.format(y)] + df['CW7AK{}'.format(y)] ) * 1.0 / df['total']		

	df['pother'] = ( df['CW7AC{}'.format(y)] + df['CW7AE{}'.format(y)] ) * 1.0 / df['total']

	# print df.dtypes
	
	# calc multigroup entropy index
	# calc score excluding asian
	# need to handle 0 values for group proportion
	groups = ['pwhite', 'pblack', 'pasian', 'phisp', 'pother']
	df['theil'] = 0
	for group in groups:
		df.loc[df['{}'.format(group)] > 0.0, 'theil'] += df['{}'.format(group)] * np.log( 1.0 / df['{}'.format(group)] )

	print df['theil'].describe()
	##################################################################################
	# calc second measure of diversity excluding asian and "other" populations
	# recalculate percantages using sum of nh white, nh black, and hispanic
	# get counts for those groups and sum to create total
	
	df['total2'] = 0

	if y in ['2010', '2000']:
		df['total2'] += df['CW7AA{}'.format(y)] # add nh whites
		df['total2'] += df['CW7AB{}'.format(y)] # add nh blacks
		# add hispanics
		df['total2'] += ( df['CW7AG{}'.format(y)] + df['CW7AH{}'.format(y)] + df['CW7AI{}'.format(y)] + df['CW7AJ{}'.format(y)] + df['CW7AK{}'.format(y)] + df['CW7AL{}'.format(y)] ) 		
	else:
		df['total2'] += df['CW7AA{}'.format(y)] # add nh whites
		df['total2'] += df['CW7AB{}'.format(y)] # add nh blacks
		df['total2'] += ( df['CW7AG{}'.format(y)] + df['CW7AH{}'.format(y)] + df['CW7AI{}'.format(y)] + df['CW7AJ{}'.format(y)] + df['CW7AK{}'.format(y)] )

	df['pwhite2'] = df['CW7AA{}'.format(y)] * 1.0 / df['total2']
	df['pblack2'] = df['CW7AA{}'.format(y)] * 1.0 / df['total2']
	
	if y in ['2010', '2000']: 
		df['phisp2'] = ( df['CW7AG{}'.format(y)] + df['CW7AH{}'.format(y)] + df['CW7AI{}'.format(y)] + df['CW7AJ{}'.format(y)] + df['CW7AK{}'.format(y)] + df['CW7AL{}'.format(y)] ) * 1.0 / df['total2'] 
	else:
		df['phisp2'] = ( df['CW7AG{}'.format(y)] + df['CW7AH{}'.format(y)] + df['CW7AI{}'.format(y)] + df['CW7AJ{}'.format(y)] + df['CW7AK{}'.format(y)] ) * 1.0 / df['total2']

	groups2 = ['pwhite2', 'pblack2', 'phisp2']
	df['theil2'] = 0
	for group in groups2:
		df.loc[df['{}'.format(group)] > 0.0, 'theil2'] += df['{}'.format(group)] * np.log( 1.0 / df['{}'.format(group)] )
	##################################################################################

	# create separate dataframes for each year to merge into single df
	groups = ['pwhite', 'pblack', 'pasian', 'phisp', 'pother', 'theil', 'theil2', 'total', 'total2']
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


merged.to_sql("county_diversity", con, if_exists="replace")
# cur.execute("DROP TABLE IF EXISTS county_diversity")
# cur.execute("CREATE TABLE county_diversity;")

con.close()