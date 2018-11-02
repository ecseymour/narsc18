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
			WHERE CW7AA{} <> '' AND CW7AA{} > 0 AND STATE NOT IN ('Puerto Rico', 'Alaska', 'Hawaii')
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
			WHERE CW7AA{} <> '' AND CW7AA{} > 0 AND STATE NOT IN ('Puerto Rico', 'Alaska', 'Hawaii')
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

	cols = ['nh_white', 'nh_black', 'nh_asian', 'hisp', 'other']
	totals = df[cols].sum()
	totals = pd.DataFrame(totals)
	totals.columns = ['total']
	print totals
	totals['share'] = totals['total'] * 1.0 / totals['total'].sum(axis=0)
	diversity = 0
	for i, x in totals.iterrows():
		diversity += x['share'] * np.log(1.0/x['share'])

	diversity = diversity /  np.log(len(cols))

	print "diversity: {}".format(round(diversity,2))

con.close()

print 'done'