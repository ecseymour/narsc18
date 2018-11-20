from pysqlite2 import dbapi2 as sql
import geopandas as gpd
from geopandas.plotting import plot_dataframe
from custom_geopandas_plotting import plot_dataframe_custom
import pandas as pd
import csv
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
np.seterr(invalid='ignore')

plt.style.use('diss_style_small.mplstyle')

# cmap = LinearSegmentedColormap.from_list('mycmap', list(reversed(['#d73027', '#fc8d59', '#fee090', '#e0f3f8', '#91bfdb', '#4575b4'])) )

db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.enable_load_extension(True)
con.execute("SELECT load_extension('mod_spatialite');")
cur = con.cursor()

qry = '''
SELECT A.GISJOIN, B.*, Hex(ST_AsBinary(C.geometry)) AS geom
FROM us_county_2010 AS A JOIN county_diversity_by_age AS B 
	ON A.gisjoin = B.gisjoin
JOIN gz_2010_us_050_00_20m AS C
	ON A.statefp10 = C.state AND A.countyfp10 = C.county
WHERE A.STATEFP10 NOT IN ('02', '15', '72')
;
'''
df = gpd.GeoDataFrame.from_postgis(qry, con, geom_col='geom', index_col='gisjoin')

print len(df)

# # update miami-dade county w/ 1990 dade county values
# qry = '''
# SELECT GISJOIN, AX7AA1990 * 1.0 / (AX7AA1990 + AX7AB1990) AS poverty_start
# 	FROM county_poverty
# 	WHERE GISJOIN = 'G1200250';
# '''
# dade = pd.read_sql(qry, con, index_col='GISJOIN')
# df.loc['G1200860', 'povrate_90'] = dade.loc['G1200250']['poverty_start']
# drop null counties
df = df.dropna()


periods = [ ['2000', '2010'] ]

ages = ['under5', '5to17', '18to64', '65plus']

for v in ['diversity']:

	for p in periods:
		start = p[0]
		end = p[1]

		for a in ages:

			print "+" * 80
			print a	
			
			df['diversity_diff_{}{}'.format(start,end)] = df['diversity_4grp_{}_{}'.format(a, end)] - df['diversity_4grp_{}_{}'.format(a, start)]
			
			print df['diversity_diff_{}{}'.format(start,end)].describe()
			print df['diversity_diff_{}{}'.format(start,end)].head()
			##############################################################################################################################
			df.loc[df['diversity_diff_{}{}'.format(start, end)]<0, 'diversity_breaks_{}{}'.format(start,end)] = 1 
			df.loc[(df['diversity_diff_{}{}'.format(start, end)]>=0) & (df['diversity_diff_{}{}'.format(start, end)]<0.05), 'diversity_breaks_{}{}'.format(start,end)] = 2 
			df.loc[(df['diversity_diff_{}{}'.format(start, end)]>=0.05) & (df['diversity_diff_{}{}'.format(start, end)]<0.1), 'diversity_breaks_{}{}'.format(start,end)] = 3 
			df.loc[(df['diversity_diff_{}{}'.format(start, end)]>=0.1), 'diversity_breaks_{}{}'.format(start,end)] = 4 


			mylabels = ['{} - 0.00'.format(df['diversity_diff_{}{}'.format(start,end)].min().round(2)), 
				'0.00 - 0.05',
				'0.05 - 0.10', 
				'0.10 - {}'.format(df['diversity_diff_{}{}'.format(start,end)].max().round(2))]

			cmap = LinearSegmentedColormap.from_list('mycmap', list(reversed(['#d73027', '#fc8d59', '#fee090', '#4575b4'])) )

			print df.groupby('diversity_breaks_{}{}'.format( start, end)).size()

			ax=plot_dataframe_custom(df, column='diversity_breaks_{}{}'.format(start,end), linewidth=.1, edgecolor='white', 
				legend=True, categorical=True, cust_labels=mylabels, cmap=cmap)
			# add state borders
			qry = '''
			SELECT geo_id, Hex(ST_AsBinary(geometry)) AS geom
			FROM gz_2010_us_040_00_20m
			WHERE state NOT IN ('02', '15', '72')
			-- WHERE state = '26'
			;
			'''
			df_state = gpd.GeoDataFrame.from_postgis(qry, con, geom_col='geom')
			df_state.plot(ax=ax, linewidth=.6, edgecolor='black', color="None")

			ax.spines['top'].set_visible(False)
			ax.spines['right'].set_visible(False)
			ax.spines['bottom'].set_visible(False)
			ax.spines['left'].set_visible(False)
			ax.get_xaxis().set_visible(False)
			ax.get_yaxis().set_visible(False)
			leg = ax.get_legend()
			leg.set_bbox_to_anchor((0., 0.1, 0.2, 0.2))

			outFile = '/home/eric/Documents/franklin/narsc2018/figures/county_diversity_diff_{}-{}_{}'.format(start, end, a)
			plt.savefig(outFile, bbox_inches='tight')
			plt.close()

con.close()