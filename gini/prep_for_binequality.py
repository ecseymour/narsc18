'''
data needs to be grouped by fips and income bin
may want to create separate csvs for each decade
test first w/ 2012
'''
import sqlite3 as sql
from collections import OrderedDict
import pandas as pd

db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
cur = con.cursor()

data_dict = OrderedDict()

years = ['125', '2000', '1990'] # 125 indicates 2012 5-year ACS estimates

for y in years:
	print y

	# collect counties to iterate over
	fips_list = []

	cur.execute('''
		SELECT GISJOIN
		FROM nhgis_pop_race_norm_90_10
		WHERE CL8AA2010 <> '' AND STATE <> 'Puerto Rico'
		;
		''')
	results = cur.fetchall()
	for row in results:
		fips_list.append(row[0])
	
	for fips in fips_list:

		qry = '''
			SELECT
			GISJOIN,
			B71AA{},
			B71AB{},
			B71AC{},
			B71AD{},
			B71AE{},
			B71AF{},
			B71AG{},
			B71AH{},
			B71AI{},
			B71AJ{},
			B71AK{},
			B71AL{},
			B71AM{},
			B71AN{},
			B71AO{}
			FROM county_income
			WHERE GISJOIN = '{}';
			'''.format(y,y,y,y,y,y,y,y,y,y,y,y,y,y,y,fips)
		
		cur.execute(qry)
		row = cur.fetchone()
		# STATEFP = row[0]
		# COUNTYFP = row[1]
		GISJOIN = row[0]

		data_dict[GISJOIN+'A'] = {'FIPS': GISJOIN, 'bin_min': 0, 'bin_max': 9999, 'pop': row[1]}
		data_dict[GISJOIN+'B'] = {'FIPS': GISJOIN, 'bin_min': 10000, 'bin_max': 14999, 'pop': row[2]}
		data_dict[GISJOIN+'C'] = {'FIPS': GISJOIN, 'bin_min': 15000, 'bin_max': 19999, 'pop': row[3]}
		data_dict[GISJOIN+'D'] = {'FIPS': GISJOIN, 'bin_min': 20000, 'bin_max': 24999, 'pop': row[4]}
		data_dict[GISJOIN+'E'] = {'FIPS': GISJOIN, 'bin_min': 25000, 'bin_max': 29999, 'pop': row[5]}
		data_dict[GISJOIN+'F'] = {'FIPS': GISJOIN, 'bin_min': 30000, 'bin_max': 34999, 'pop': row[6]}
		data_dict[GISJOIN+'G'] = {'FIPS': GISJOIN, 'bin_min': 35000, 'bin_max': 39999, 'pop': row[7]}
		data_dict[GISJOIN+'H'] = {'FIPS': GISJOIN, 'bin_min': 40000, 'bin_max': 44999, 'pop': row[8]}
		data_dict[GISJOIN+'I'] = {'FIPS': GISJOIN, 'bin_min': 45000, 'bin_max': 49999, 'pop': row[9]}
		data_dict[GISJOIN+'J'] = {'FIPS': GISJOIN, 'bin_min': 50000, 'bin_max': 59999, 'pop': row[10]}
		data_dict[GISJOIN+'K'] = {'FIPS': GISJOIN, 'bin_min': 60000, 'bin_max': 74999, 'pop': row[11]}
		data_dict[GISJOIN+'L'] = {'FIPS': GISJOIN, 'bin_min': 75000, 'bin_max': 99999, 'pop': row[12]}
		data_dict[GISJOIN+'M'] = {'FIPS': GISJOIN, 'bin_min': 100000, 'bin_max': 124999, 'pop': row[13]}
		data_dict[GISJOIN+'N'] = {'FIPS': GISJOIN, 'bin_min': 125000, 'bin_max': 149999, 'pop': row[14]}
		data_dict[GISJOIN+'O'] = {'FIPS': GISJOIN, 'bin_min': 150000, 'bin_max': 'NA', 'pop': row[15]}


	df = pd.DataFrame.from_dict(data_dict, orient='index')

	df.to_csv("/home/eric/Documents/franklin/narsc2018/generated_data/binned_income/county_bins_{}.csv".format(y), index_label='index')

con.close()

print 'done'