'''
calc coef of specialization for each county,
comparing county to 1) state and 2) US
compare across periods (1990, 2000, 2010)
need to collect state race/diversity data
or can aggregate from counties, iterating through counties
output a single table with S for each period
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
			STATEA, 
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
			STATEA, 
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

	# calc pct NH white, NH black, and NH asian
	df['white'] = df['CW7AA{}'.format(y)]
	df['pwhite'] = df['white'] * 1.0 / df['total']

	df['black'] = df['CW7AB{}'.format(y)]
	df['pblack'] = df['black'] / df['total']
	
	df['asian'] = df['CW7AD{}'.format(y)]	
	df['pasian'] = df['asian'] * 1.0 / df['total']

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
	###############################################################
	# aggregate to counties and calc coef of specialization
	###############################################################
	# aggregate counties to state and calc state-level percentages of each group
	cols = ['STATEA', 'white', 'black', 'asian', 'hisp', 'other']
	states = df[cols].groupby('STATEA').sum()
	cols = ['white', 'black', 'asian', 'hisp', 'other']
	states['total'] = states.sum(axis=1)
	for c in cols:
		states['p{}'.format(c)] = states[c] * 1.0 / states['total']
	# for each state, compare each county nested in that state across each pop group
	df['Sstate'] = 0
	cols = ['pwhite', 'pblack', 'pasian', 'phisp', 'pother']
	for i, x in states.iterrows():
		for i2, x2 in df.loc[df['STATEA']==i].iterrows():
			S = 0
			for c in cols:
				S += np.abs(x[c] - x2[c])
			df.loc[i2, 'Sstate'] = S * 0.5
	###############################################################
	# aggregate to US and calc coef of specialization
	###############################################################
	# aggregate counties to state and calc state-level percentages of each group
	cols = ['white', 'black', 'asian', 'hisp', 'other']
	total_us = pd.DataFrame(df[cols].sum(axis=0))
	total_us.columns = ['count']
	# calc share of total in each category
	total_us['share'] = total_us['count'] * 1.0 / total_us['count'].sum(axis=0)
	# print total_us.loc['white']['share']
	# for each county, compare to us distributions
	df['Sus'] = 0
	cols = ['pwhite', 'pblack', 'pasian', 'phisp', 'pother']
	for i, x in df.iterrows():
		S = 0
		for c in cols:
			S += np.abs(total_us.loc[c[1:]]['share'] - x[c])
		df.loc[i, 'Sus'] = S * 0.5

	# create separate dataframes for each year to merge into single df
	groups = ['Sus', 'Sstate']
	
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

merged.to_sql("county_specialization", con, if_exists="replace")

con.close()

print 'done'