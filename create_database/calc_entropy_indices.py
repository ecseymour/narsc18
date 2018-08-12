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

years = ['90', '00', '10']

for y in years:
	
	data_dict = {}
	
	cur.execute('''
		SELECT A.gisjoin, 
		A.total_{}, 
		A.total_3grp_{},
		A.diversity_5grp_{}, 
		A.diversity_4grp_{}, 
		A.diversity_3grp_{}		 
		FROM county_diversity AS A JOIN county_block_group_count AS B
		ON A.GISJOIN = B.GISJOIN
		WHERE B.block_groups >= 10
		;
		'''.format(y, y, y, y, y))
	results = cur.fetchall()
	for row in results:
		data_dict[row[0]] = {}
		data_dict[row[0]]['total_r'] = row[1]
		data_dict[row[0]]['total_r_3grp'] = row[2]
		data_dict[row[0]]['diversity_r_5grp'] = row[3]
		data_dict[row[0]]['diversity_r_4grp'] = row[4]
		data_dict[row[0]]['diversity_r_3grp'] = row[5]

	# collect block group total and entropy
	# calculate entropy index

	print '{} counties'.format(len(data_dict))

	counter = 0
	for k, v in data_dict.iteritems():
		counter += 1
		if counter % 100 == 0:
			print counter

		# init counters for entropy indices
		entropy_index_5grp = 0
		entropy_index_4grp = 0
		entropy_index_3grp = 0
		
		cur.execute('''
			SELECT total_{}, 
			total_3grp_{},
			diversity_5grp_{}, 
			diversity_4grp_{}, 
			diversity_3grp_{}	
			FROM blck_grp_diversity
			WHERE SUBSTR(GISJOIN, 1, 8) = ?
			'''.format(y, y, y, y, y), ([k]))
		results = cur.fetchall()
		for i, row in enumerate(results):
			total_s = row[0]
			total_s_3grp = row[1]
			diversity_s_5grp = row[2]
			diversity_s_4grp = row[3]
			diversity_s_3grp = row[4]

			# calc 5 group entripy
			entropy_index_5grp += ( total_s * ( data_dict[k]['diversity_r_5grp'] - diversity_s_5grp ) ) / ( data_dict[k]['diversity_r_5grp'] * data_dict[k]['total_r'] )
			# calc 4 group entripy
			entropy_index_4grp += ( total_s * ( data_dict[k]['diversity_r_4grp'] - diversity_s_4grp ) ) / ( data_dict[k]['diversity_r_4grp'] * data_dict[k]['total_r'] )
			# calc 3 group entropy CHANGE TOTAL TO EXCLUDE ASIAN AND OTHER 
			entropy_index_3grp += ( total_s_3grp * ( data_dict[k]['diversity_r_3grp'] - diversity_s_3grp ) ) / ( data_dict[k]['diversity_r_3grp'] * data_dict[k]['total_r_3grp'] )

		data_dict[k]['entropy_index_5grp'] = entropy_index_5grp
		data_dict[k]['entropy_index_4grp'] = entropy_index_4grp
		data_dict[k]['entropy_index_3grp'] = entropy_index_3grp

	df = pd.DataFrame.from_dict(data_dict, orient='index')

	if y == "10":
		df_2010 = df
	elif y == "00":
		df_2000 = df
	elif y == "90":
		df_1990 = df

merged = pd.merge(df_2010, df_2000, left_index=True, right_index=True, suffixes=("_10", "_00"))
df_1990 = df_1990.add_suffix("_90")
merged = pd.merge(merged, df_1990, left_index=True, right_index=True, )

merged.index.names =['GISJOIN']
merged.to_sql('county_segregation', con, if_exists='replace')

con.close()

print "done"