'''
prep data for regression in R
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

# qry = '''
# SELECT
# A.STATE,
# A.COUNTY,
# A.CL8AA1990 AS pop90,
# A.CL8AA2000 AS pop00,
# A.CL8AA2010 AS pop10,
# B.*,
# C.pwhite_10,
# C.pwhite_00,
# C.pwhite_90,
# C.diversity_4grp_10,
# C.diversity_4grp_00,
# C.diversity_4grp_90,
# IFNULL(D.Status, 0) AS metro_status
# FROM nhgis_pop_race_norm_90_10 AS A
# JOIN county_specialization AS B
#     ON A.GISJOIN = B.GISJOIN
# JOIN county_diversity AS C
#     ON A.GISJOIN = C.GISJOIN
# LEFT JOIN cbsa_county_xwalk_2003 AS D ON A.STATEA || A.COUNTYA = D.FIPS
# ;
# '''
# df = pd.read_sql(qry, con, index_col='GISJOIN')
# print df.head()
# print len(df)

# what are the largest non-metro counties?
# print df.loc[df['metro_status']==0][['STATE', 'COUNTY', 'pop00']].sort_values('pop00', ascending=False).head(10)
#########################################################3
qry = '''
SELECT
A.STATE, A.COUNTY,
A.CL8AA1990 AS pop90,
A.CL8AA2000 AS pop00,
A.CL8AA2010 AS pop10,
B.*,
C.pwhite_10,
C.pwhite_00,
C.pwhite_90,
C.diversity_4grp_10,
C.diversity_4grp_00,
C.diversity_4grp_90,
D.gini_10,
D.gini_00,
D.gini_90
FROM nhgis_pop_race_norm_90_10 AS A
JOIN county_specialization AS B
	ON A.GISJOIN = B.GISJOIN
JOIN county_diversity AS C
	ON A.GISJOIN = C.GISJOIN
JOIN county_gini AS D
	ON A.GISJOIN = D.GISJOIN
;
'''
df = pd.read_sql(qry, con, index_col='GISJOIN')
################################################
# collect counties inside metro areas in 2000
qry = '''
SELECT A.gisjoin, B.msacmsa AS msacmsa00
FROM us_county_2010 AS A, us_msacmsa_2000 AS B
WHERE ST_Contains(B.geometry, ST_Centroid(A.geometry))
AND A.ROWID IN (SELECT ROWID FROM SpatialIndex
	WHERE f_table_name='us_county_2010' AND search_frame=B.geometry) 
;
'''
df2 = pd.read_sql(qry, con, index_col='gisjoin')
# merge records using left join to keep all non-metro counties
df = pd.merge(df, df2, left_index=True, right_index=True, how='left')
# create new variable for metro status 
df.fillna(value={'msacmsa00':0}, inplace=True)
df['metro_status00'] = 0
df.loc[df['msacmsa00']!=0, 'metro_status00'] = 1
################################################
# collect counties inside metro areas in 1990
qry = '''
SELECT A.gisjoin, B.msacmsa AS msacmsa90 
FROM us_county_2010 AS A, us_msacmsa_1990 AS B
WHERE ST_Contains(B.geometry, ST_Centroid(A.geometry))
AND A.ROWID IN (SELECT ROWID FROM SpatialIndex
	WHERE f_table_name='us_county_2010' AND search_frame=B.geometry) 
;
'''
df2 = pd.read_sql(qry, con, index_col='gisjoin')
# merge records using left join to keep all non-metro counties
df = pd.merge(df, df2, left_index=True, right_index=True, how='left')
# create new variable for metro status 
df.fillna(value={'msacmsa90':0}, inplace=True)
df['metro_status90'] = 0
df.loc[df['msacmsa90']!=0, 'metro_status90'] = 1
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
df = pd.merge(df, df3, left_index=True, right_index=True)
###############################
# code variables for regression
# calc pop change in each decade
# calc diff in specialization and diversity
periods = [ ['90', '00'], ['00', '10'] ]

for p in periods:
	start = p[0]
	end = p[1]
	
	df['ppctchg_{}{}'.format(start, end)] = ( df['pop{}'.format(end)] - df['pop{}'.format(start)] ) * 1.0 / df['pop{}'.format(start)] * 100
	df['loss_dummy_{}{}'.format(start, end)] = 0
	df.loc[df['ppctchg_{}{}'.format(start, end)] < 0, 'loss_dummy_{}{}'.format(start, end)] = 1

	df['specialization_diff_{}{}'.format(start,end)] = df['Sus_{}'.format(end)] - df['Sus_{}'.format(start)]
	df['diversity_diff_{}{}'.format(start,end)] = df['diversity_4grp_{}'.format(end)] - df['diversity_4grp_{}'.format(start)]
	df['gini_diff_{}{}'.format(start,end)] = df['gini_{}'.format(end)] - df['gini_{}'.format(start)]

# output to file
df.to_csv("/home/eric/Documents/franklin/narsc2018/generated_data/diversity_regression_data.csv", index_label='GISJOIN')        
# close db
con.close()
print "DONE"