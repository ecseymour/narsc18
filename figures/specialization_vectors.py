'''
specialization vector plots
'''
from pysqlite2 import dbapi2 as sql
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.enable_load_extension(True)
con.execute("SELECT load_extension('mod_spatialite');")

# qry database
qry = '''
SELECT 
A.CL8AA1990 AS pop90,
A.CL8AA2000 AS pop00,
A.CL8AA2010 AS pop10,
B.*
FROM nhgis_pop_race_norm_90_10 AS A
JOIN county_specialization AS B
    ON A.GISJOIN = B.GISJOIN
;
'''
df = pd.read_sql(qry, con, index_col='GISJOIN')

# merge with census regions
qry = '''
SELECT A.gisjoin, B.name AS region
FROM us_county_2010 AS A, census_regions_10 AS B
WHERE ST_Contains(B.geometry, ST_Centroid(A.geometry))
AND A.ROWID IN (SELECT ROWID FROM SpatialIndex
    WHERE f_table_name = 'us_county_2010' AND search_frame = B.geometry )
;
'''

df2 = pd.read_sql(qry, con, index_col='gisjoin')
con.close()
df = pd.merge(df, df2, left_index=True, right_index=True)
###################################################################################33
# create categories for pop change 2000 to 2010
# calc pop change in each decade
df['ppctchg_0010'] = ( df['pop10'] - df['pop00'] ) * 1.0 / df['pop00'] * 100
df['ppctchg_9000'] = ( df['pop00'] - df['pop90'] ) * 1.0 / df['pop90'] * 100
# growth categories 2000-2010
df['growth_cat'] = 0
df.loc[df['ppctchg_0010'] >= 5, 'growth_cat'] = 'growing'
df.loc[(df['ppctchg_0010'] < 5) & (df['ppctchg_0010'] >= 0 ), 'growth_cat'] = 'stable'
df.loc[df['ppctchg_0010'] < 0, 'growth_cat'] = 'shrinking'
# growth categories 1990-2000
df['growth_cat_90s'] = 0
df.loc[df['ppctchg_9000'] >= 5, 'growth_cat_90s'] = 'growing'
df.loc[(df['ppctchg_9000'] < 5) & (df['ppctchg_9000'] >= 0 ), 'growth_cat_90s'] = 'stable'
df.loc[df['ppctchg_9000'] < 0, 'growth_cat_90s'] = 'shrinking'

# calc diff in specialization
periods = [ ['90', '00'], ['00', '10'] ]
benchmarks = ['us', 'state']

for p in periods:
    start = p[0]
    end = p[1]
    for b in benchmarks:
        df['S_{}_diff_{}{}'.format(b,start,end)] = df['S{}_{}'.format(b, end)] - df['S{}_{}'.format(b, start)]
###################################################################################33
# df = df.dfle(n=250)
df['zeros'] = 0
# X = df['zeros']
# Y = df['Sus_00']
# U = df['ppctchg_0010']
# V = df['S_us_diff_0010']

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=False, figsize=(12,8))

regions = df['region'].unique()
regions = sorted(regions)
print regions
axli = [ax1, ax2, ax3, ax4]

for a, x in zip(axli,regions):

	temp = df.loc[(df['region']==x) & (df['growth_cat'] != 'stable')]

	X = temp['zeros']
	Y = temp['Sus_00']
	U = temp['ppctchg_0010']
	V = temp['S_us_diff_0010']

	# temp.loc[temp['growth_cat']=='shrinking', 'color'] = '#4575b4'
	# temp.loc[temp['growth_cat']=='growing', 'color'] = '#d73027'

	temp.loc[temp['growth_cat']=='shrinking', 'color'] = 'blue'
	temp.loc[temp['growth_cat']=='growing', 'color'] = 'red'

	# temp.loc[temp['growth_cat']=='stable', 'color'] = 'red'

	a.quiver(X, Y, U, V, scale_units='xy', angles='xy', scale=1, color=temp['color'], alpha=0.5, width=0.003)
	a.set_xlim([-50,120])
	a.set_ylim([0,1])
	a.set_title(x)

for a in [ax3, ax4]:
	a.set_xlabel('% pop change 2000-2010')
for a in [ax1,ax3]:
	a.set_ylabel('specialization')

plt.savefig("/home/eric/Documents/franklin/narsc2018/figures/specialization_quiver.png", dpi=300, bbox_inches='tight')