'''
prep data for regression in R

split data into separate sets for 1990-2000 and 2000-2010
assign vars same name in both periods
will be incorporating results from both periods in single output table
stargazer package needs vars in both periods to have the same name
'''
from pysqlite2 import dbapi2 as sql
import pandas as pd
import numpy as np

########################################################
'''
DIVERSITY AND SPECIALIZATION
prepare diversity and specialization datasets
these should have the same number of counties in both periods
because i used NHGIS data normalized to 2010.
inequalty is based on non-normalized time-series data


ISSUE: collecting metro status from prior period
the datafiles i found with metro/micro status for counties
only includes counties included in metro/micro areas
if i take a left join btw these tables and code all NULL
values as 0, does that mean metro counties that changed FIPS
btw 2000 and 2010 will not be coded as metro?
what are the largest 'non-metro' counties

'''
########################################################
# load data
db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.text_factory=str
con.enable_load_extension(True)
con.execute("SELECT load_extension('mod_spatialite');")
########################################################
years = [ ['90', '00'], ['00', '10'] ]

for y in years:
	print y
	start = y[0]
	end = y[1]
	full_start = None
	full_end = None

	if start=='90':
		full_start = '1990'
		full_end = '2000'
	else:
		full_start = '2000'
		full_end = '2010'

	qry = '''
	SELECT A.GISJOIN,
	A.STATE, A.COUNTY,
	A.CL8AA{} AS pop_start,
	A.CL8AA{} AS pop_end,
	B.Sus_{} AS specialization_start,
	B.Sus_{} AS specialization_end,
	C.pwhite_{} AS pwhite_start,
	C.pwhite_{} AS pwhite_end,
	C.diversity_4grp_{} AS diversity_start,
	C.diversity_4grp_{} AS diversity_end,
	D.gini_{} AS gini_start,
	D.gini_{} AS gini_end,
	E.code1993,
	E.code2003,
	F.povrate_{} AS poverty_start,
	F.povrate_{} AS poverty_end
	FROM nhgis_pop_race_norm_90_10 AS A
	JOIN county_specialization_4grp AS B
		ON A.GISJOIN = B.GISJOIN
	JOIN county_diversity AS C
		ON A.GISJOIN = C.GISJOIN
	JOIN county_gini_rpme AS D
		ON A.GISJOIN = D.GISJOIN
	JOIN usda_rural_urban AS E
		ON E.fips = A.STATEA || A.COUNTYA
	JOIN county_povrate AS F
    	ON A.GISJOIN = F.GISJOIN
	;
	'''.format(full_start, full_end, start, end, start, end, start, end, start, end, start, end)
	print qry
	df = pd.read_sql(qry, con, index_col='GISJOIN')
	################################################
	# collect counties inside metro areas in base year
	qry = '''
	SELECT A.gisjoin, B.msacmsa AS msacmsa{}
	FROM us_county_2010 AS A, us_msacmsa_{} AS B
	WHERE ST_Contains(B.geometry, ST_Centroid(A.geometry))
	AND A.ROWID IN (SELECT ROWID FROM SpatialIndex
		WHERE f_table_name='us_county_2010' AND search_frame=B.geometry) 
	;
	'''.format(start, full_start)
	df2 = pd.read_sql(qry, con, index_col='gisjoin')
	# merge records using left join to keep all non-metro counties
	df = pd.merge(df, df2, left_index=True, right_index=True, how='left')
	# create new variable for metro status 
	df.fillna(value={'msacmsa{}'.format(start):0}, inplace=True)
	df['metro_status{}'.format(start)] = 0
	df['metro_dummy'] = 0
	df.loc[df['msacmsa{}'.format(start)]!=0, 'metro_dummy'] = 1
	################################################
	# merge with regions
	qry = '''
	SELECT A.gisjoin, B.name AS region
	FROM us_county_2010 AS A, census_regions_10 AS B
	WHERE ST_Contains(B.geometry, ST_Centroid(A.geometry))
	AND A.ROWID IN (SELECT ROWID FROM SpatialIndex
		WHERE f_table_name = 'us_county_2010' AND search_frame = B.geometry )
	;
	'''
	df3 = pd.read_sql(qry, con, index_col='gisjoin')
	# add missing regions
	df3.loc['G2600830'] = 'Midwest'
	df3.loc['G4400050'] = 'Northeast'
	df3.loc['G5300290'] = 'West'

	df = pd.merge(df, df3, left_index=True, right_index=True)
	###############################
	df.loc[df['STATE']=='Missouri', 'region'] = 'Midwest'
	# code variables for regression
	# calc pop change in each decade
	# calc diff in specialization and diversity
	df['ppctchg'] = ( df['pop_end'] - df['pop_start'] ) * 1.0 / df['pop_start'] * 100
	df['loss_dummy'.format(start, end)] = 0
	df.loc[df['ppctchg'] < 0, 'loss_dummy'] = 1

	df['specialization_diff'] = df['specialization_end'] - df['specialization_start']
	df['diversity_diff'] = df['diversity_end'] - df['diversity_start']
	df['gini_diff'] = df['gini_end'] - df['gini_start']
	df['poverty_diff'] = df['poverty_end'] - df['poverty_start']
	df['pwhite_diff'] = df['pwhite_end'] - df['pwhite_start']
	###############################
	# create 'diff in diff' vars as as cty pct chg - us pct chg
	us_diversity_1990 = 0.50
	us_diversity_2000 = 0.61
	us_diversity_2010 = 0.67

	if full_start=='1990':
		us_pct_chg = (us_diversity_2000 - us_diversity_1990) * 1.0 / us_diversity_1990 * 100
		print "us pct change: {}".format(us_pct_chg)
		df['diversity_pctchg'] = (df['diversity_end'] - df['diversity_start']) * 1.0 / df['diversity_start'] * 100 
		df['diversity_diff2'] = df['diversity_pctchg'] - us_pct_chg
		df['diversity_diff3'] = df['diversity_diff'] - (us_diversity_2000 - us_diversity_1990)
	else:
		us_pct_chg = (us_diversity_2010 - us_diversity_2000) * 1.0 / us_diversity_2000 * 100
		print "us pct change: {}".format(us_pct_chg)
		df['diversity_pctchg'] = (df['diversity_end'] - df['diversity_start']) * 1.0 / df['diversity_start'] * 100
		df['diversity_diff2'] = df['diversity_pctchg'] - us_pct_chg
		df['diversity_diff3'] = df['diversity_diff'] - (us_diversity_2010 - us_diversity_2000)

	# output to file
	df.to_csv("/home/eric/Documents/franklin/narsc2018/generated_data/regression_data_{}{}.csv".format(start,end), index_label='GISJOIN')        

# close db
con.close()
print "DONE"