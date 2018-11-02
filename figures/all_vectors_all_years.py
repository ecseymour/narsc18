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
D.gini_90,
F.povrate_90,
F.povrate_00,
F.povrate_10
FROM nhgis_pop_race_norm_90_10 AS A
JOIN county_specialization_4grp AS B
	ON A.GISJOIN = B.GISJOIN
JOIN county_diversity AS C
	ON A.GISJOIN = C.GISJOIN
JOIN county_gini AS D
	ON A.GISJOIN = D.GISJOIN
JOIN county_povrate AS F
   	ON A.GISJOIN = F.GISJOIN
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
df.loc[df['ppctchg_0010'] >= 5, 'growth_cat_0010'] = 'growing'
df.loc[(df['ppctchg_0010'] < 5) & (df['ppctchg_0010'] >= 0 ), 'growth_cat_0010'] = 'stable'
df.loc[df['ppctchg_0010'] < 0, 'growth_cat_0010'] = 'shrinking'
# growth categories 1990-2000
df['growth_cat_90s'] = 0
df.loc[df['ppctchg_9000'] >= 5, 'growth_cat_9000'] = 'growing'
df.loc[(df['ppctchg_9000'] < 5) & (df['ppctchg_9000'] >= 0 ), 'growth_cat_9000'] = 'stable'
df.loc[df['ppctchg_9000'] < 0, 'growth_cat_9000'] = 'shrinking'

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


def get_axis_limits(ax, scale=.9):
	return ax.get_xlim()[1]*scale, ax.get_ylim()[1]*scale

myvars = ['gini', 'specialization', 'diversity', 'povrate', 'pwhite']
regions = df['region'].unique()
regions = sorted(regions)
years = [['90', '00', '9000'], ['00', '10', '0010']]

for y in years:

	for v in myvars:
		print v

		fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=False, figsize=(12,8))
		axli = [ax1, ax2, ax3, ax4]

		for a, x in zip(axli,regions):
			print "+" * 50
			print y[2], v, x	
			temp = df.loc[(df['region']==x) & (df['growth_cat_{}'.format(y[2])] != 'stable')]		

			# calc chare that increased or decrease in each region
			temp2 = df.loc[df['region']==x]
			pct_increase_growth = None
			pct_increase_loss = None
			
			X = temp['zeros']
			U = temp['ppctchg_{}'.format(y[2])]

			if v == 'specialization':
				Y = temp['Sus_{}'.format(y[0])]
				V = temp['S_us_diff_{}'.format(y[2])]
				pct_increase_growth = len(temp2.loc[(temp2['Sus_{}'.format(y[1])] > temp2['Sus_{}'.format(y[0])]) & (temp2['ppctchg_{}'.format(y[2])] >= 0)]) * 1.0 / len(temp2.loc[temp2['ppctchg_{}'.format(y[2])]>=0]) * 100
				pct_increase_loss = len(temp2.loc[(temp2['Sus_{}'.format(y[1])] > temp2['Sus_{}'.format(y[0])]) & (temp2['ppctchg_{}'.format(y[2])] < 0)]) * 1.0 / len(temp2.loc[temp2['ppctchg_{}'.format(y[2])]<0]) * 100
			elif v =='gini':
				Y = temp['gini_{}'.format(y[0])]
				V = temp['gini_{}'.format(y[1])] - temp['gini_{}'.format(y[0])]
				pct_increase_growth = len(temp2.loc[(temp2['gini_{}'.format(y[1])] > temp2['gini_{}'.format(y[0])]) & (temp2['ppctchg_{}'.format(y[2])] >= 0)]) * 1.0 / len(temp2.loc[temp2['ppctchg_{}'.format(y[2])]>=0]) * 100
				pct_increase_loss = len(temp2.loc[(temp2['gini_{}'.format(y[1])] > temp2['gini_{}'.format(y[0])]) & (temp2['ppctchg_{}'.format(y[2])] < 0)]) * 1.0 / len(temp2.loc[temp2['ppctchg_{}'.format(y[2])]<0]) * 100
			elif v =='diversity':
				Y = temp['diversity_4grp_{}'.format(y[0])]
				V = (temp['diversity_4grp_{}'.format(y[1])]) - (temp['diversity_4grp_{}'.format(y[0])])
				pct_increase_growth = len(temp2.loc[(temp2['diversity_4grp_{}'.format(y[1])] > temp2['diversity_4grp_{}'.format(y[0])]) & (temp2['ppctchg_{}'.format(y[2])] >= 0)]) * 1.0 / len(temp2.loc[temp2['ppctchg_{}'.format(y[2])]>=0]) * 100
				pct_increase_loss = len(temp2.loc[(temp2['diversity_4grp_{}'.format(y[1])] > temp2['diversity_4grp_{}'.format(y[0])]) & (temp2['ppctchg_{}'.format(y[2])] < 0)]) * 1.0 / len(temp2.loc[temp2['ppctchg_{}'.format(y[2])]<0]) * 100
			elif v =='povrate':
				Y = temp['povrate_{}'.format(y[0])]
				V = (temp['povrate_{}'.format(y[1])]) - (temp['povrate_{}'.format(y[0])])
				pct_increase_growth = len(temp2.loc[(temp2['povrate_{}'.format(y[1])] > temp2['povrate_{}'.format(y[0])]) & (temp2['ppctchg_{}'.format(y[2])] >= 0)]) * 1.0 / len(temp2.loc[temp2['ppctchg_{}'.format(y[2])]>=0]) * 100
				pct_increase_loss = len(temp2.loc[(temp2['povrate_{}'.format(y[1])] > temp2['povrate_{}'.format(y[0])]) & (temp2['ppctchg_{}'.format(y[2])] < 0)]) * 1.0 / len(temp2.loc[temp2['ppctchg_{}'.format(y[2])]<0]) * 100
			elif v =='pwhite':
				Y = temp['pwhite_{}'.format(y[0])]
				V = (temp['pwhite_{}'.format(y[1])]) - (temp['pwhite_{}'.format(y[0])])
				pct_increase_growth = len(temp2.loc[(temp2['pwhite_{}'.format(y[1])] > temp2['pwhite_{}'.format(y[0])]) & (temp2['ppctchg_{}'.format(y[2])] >= 0)]) * 1.0 / len(temp2.loc[temp2['ppctchg_{}'.format(y[2])]>=0]) * 100
				pct_increase_loss = len(temp2.loc[(temp2['pwhite_{}'.format(y[1])] > temp2['pwhite_{}'.format(y[0])]) & (temp2['ppctchg_{}'.format(y[2])] < 0)]) * 1.0 / len(temp2.loc[temp2['ppctchg_{}'.format(y[2])]<0]) * 100



			temp.loc[temp['growth_cat_{}'.format(y[2])]=='shrinking', 'color'] = '#5e3c99'
			temp.loc[temp['growth_cat_{}'.format(y[2])]=='growing', 'color'] = '#e66101'

			# temp.loc[temp['growth_cat']=='stable', 'color'] = 'red'

			a.quiver(X, Y, U, V, scale_units='xy', angles='xy', scale=1, color=temp['color'], alpha=0.5, width=0.003)
			a.set_xlim([-50,150])
			a.set_ylim([0,1])
			a.set_title(x)
			# a.annotate('increase counties: {}%'.format(round(pct_increase,0)), xy=get_axis_limits(a))
			a.annotate('growth w/ increase: {}%\nloss w/ increase: {}%'.format(round(pct_increase_growth,0), round(pct_increase_loss,0)), xy=(40,.9))
		
		for a in [ax3, ax4]:
			if y[0]=='00': 
				a.set_xlabel('% pop change 2000-2010')
			else:
				a.set_xlabel('% pop change 1990-2000')				
		for a in [ax1,ax3]:
			a.set_ylabel(v)

		plt.savefig("/home/eric/Documents/franklin/narsc2018/figures/{}_{}_quiver.png".format(v, y[2]), dpi=300, bbox_inches='tight')
		plt.close()