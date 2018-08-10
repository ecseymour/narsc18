'''
count block groups per county
iterate through each county, counting block groups
'''

from pysqlite2 import dbapi2 as sql
import pandas as pd

# connect to db
db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.text_factory=str
con.enable_load_extension(True)
con.execute("SELECT load_extension('mod_spatialite');")
cur = con.cursor()

data_dict = {}

# collect counties
cur.execute("SELECT gisjoin FROM us_county_2010;")
results = cur.fetchall()
for row in results:
	data_dict[row[0]] = None

# count block groups per county
for k, v in data_dict.iteritems():
	cur.execute('''
		SELECT COUNT(*)
		FROM us_county_2010 AS A, us_blck_grp_2010 AS B
		WHERE ST_Contains(A.geometry, ST_Centroid(B.geometry))
		AND B.ROWID IN (SELECT ROWID FROM SpatialIndex
			WHERE f_table_name='us_blck_grp_2010' AND search_frame=A.geometry)
		AND A.gisjoin = ?
		;
		''', ([k]))
	results = cur.fetchone()
	result = results[0]
	data_dict[k] = result


df = pd.DataFrame.from_dict(data_dict, orient='index')
df.columns = ['block_groups']

# df.to_csv('/home/eric/Documents/franklin/narsc2018/generated_data/blck_grp_county.csv', index_label='GISJOIN')
df.index.names =['GISJOIN']
df.to_sql('county_block_group_count', con, if_exists='replace')

print df.describe()

con.close()

print "done"