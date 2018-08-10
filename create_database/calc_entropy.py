'''
calculate  entropy index
using county as region and block groups as subunits

iterate over each county
'''

import sqlite3 as sql
import pandas as pd
import numpy as np

# connect to db
db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.text_factory=str
cur = con.cursor()


# collect counties
# for each county also collect total pop and diversity score
# first calc using diversity including asian and 'other'
# calculate for 90, 00, and 2010

# years = ['90', '00', '10']
years = ['10']

for y in years:
	
	data_dict = {}
	
	cur.execute('''
		SELECT A.gisjoin, A.total_{}, A.theil_{} 
		FROM county_diversity AS A JOIN county_block_group_count AS B
		ON A.GISJOIN = B.GISJOIN
		WHERE B.block_groups >= 10
		;
		'''.format(y, y))
	results = cur.fetchall()
	for row in results:
		data_dict[row[0]] = {}
		data_dict[row[0]]['total_r'] = row[1]
		data_dict[row[0]]['entropy_r'] = row[2]

	# collect block group total and entropy
	# calculate entropy index

	print '{} counties'.format(len(data_dict))

	counter = 0
	for k, v in data_dict.iteritems():
		counter += 1
		if counter % 100 == 0:
			print counter

		entropy_index = 0
		
		cur.execute('''
			SELECT total_{}, theil_{}
			FROM blck_grp_diversity
			WHERE SUBSTR(GISJOIN, 1, 8) = ?
			'''.format(y, y), ([k]))
		results = cur.fetchall()
		for i, row in enumerate(results):
			total_s = row[0]
			entropy_s = row[1]
			entropy_index += ( total_s * ( data_dict[k]['entropy_r'] - entropy_s ) ) / ( data_dict[k]['entropy_r'] * data_dict[k]['total_r'] )

		data_dict[k]['entropy_index_{}'.format(y)] = entropy_index

	df = pd.DataFrame.from_dict(data_dict, orient='index')

df.index.names =['GISJOIN']
df.to_sql('county_entropy_index', con, if_exists='replace')

con.close()

print "done"