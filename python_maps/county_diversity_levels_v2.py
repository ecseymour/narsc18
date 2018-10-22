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

cmap = LinearSegmentedColormap.from_list('mycmap', list(reversed(['#d73027', '#fc8d59', '#fee090', '#e0f3f8', '#91bfdb', '#4575b4'])) )

db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.enable_load_extension(True)
con.execute("SELECT load_extension('mod_spatialite');")
cur = con.cursor()

qry = '''
SELECT A.GISJOIN, B.diversity_4grp_10, B.diversity_4grp_00, B.diversity_4grp_90, 
D.Sus_10, D.Sus_00, D.Sus_90,
E.gini_10, E.gini_00, E.gini_90, 
Hex(ST_AsBinary(C.geometry)) AS geom
FROM us_county_2010 AS A JOIN county_diversity AS B 
	ON A.gisjoin = B.gisjoin
JOIN gz_2010_us_050_00_20m AS C
	ON A.statefp10 = C.state AND A.countyfp10 = C.county
JOIN county_specialization_4grp AS 
	D ON A.gisjoin = D.gisjoin
JOIN county_gini AS E 
	ON A.gisjoin = E.gisjoin
WHERE A.STATEFP10 NOT IN ('02', '15', '72')
;
'''
df = gpd.GeoDataFrame.from_postgis(qry, con, geom_col='geom')
df = df.dropna()
# scale diversity scores
for x in ['90', '00', '10']:
	df['diversity_4grp_{}'.format(x)] = df['diversity_4grp_{}'.format(x)] / np.log(4)
	# create cat var so breaks are consistent across years
	df.loc[df['diversity_4grp_{}'.format(x)]<.20, 'diversity_breaks_{}'.format(x)] = 1
	df.loc[(df['diversity_4grp_{}'.format(x)]>=.20) & (df['diversity_4grp_{}'.format(x)]<.40), 'diversity_breaks_{}'.format(x)] = 2
	df.loc[(df['diversity_4grp_{}'.format(x)]>=.40) & (df['diversity_4grp_{}'.format(x)]<.60), 'diversity_breaks_{}'.format(x)] = 3
	df.loc[(df['diversity_4grp_{}'.format(x)]>=.60) & (df['diversity_4grp_{}'.format(x)]<80), 'diversity_breaks_{}'.format(x)] = 4
	df.loc[(df['diversity_4grp_{}'.format(x)]>=.80), 'diversity_breaks_{}'.format(x)] = 5

	df.loc[df['Sus_{}'.format(x)]<.20, 'specialization_breaks_{}'.format(x)] = 1
	df.loc[(df['Sus_{}'.format(x)]>=.20) & (df['Sus_{}'.format(x)]<.40), 'specialization_breaks_{}'.format(x)] = 2
	df.loc[(df['Sus_{}'.format(x)]>=.40) & (df['Sus_{}'.format(x)]<.60), 'specialization_breaks_{}'.format(x)] = 3
	df.loc[(df['Sus_{}'.format(x)]>=.60) & (df['Sus_{}'.format(x)]<80), 'specialization_breaks_{}'.format(x)] = 4
	df.loc[(df['Sus_{}'.format(x)]>=.80), 'specialization_breaks_{}'.format(x)] = 5

	df.loc[df['gini_{}'.format(x)]<.40, 'gini_breaks_{}'.format(x)] = 1
	df.loc[(df['gini_{}'.format(x)]>=.40) & (df['gini_{}'.format(x)]<.45), 'gini_breaks_{}'.format(x)] = 2
	df.loc[(df['gini_{}'.format(x)]>=.40) & (df['gini_{}'.format(x)]<.45), 'gini_breaks_{}'.format(x)] = 2
	df.loc[(df['gini_{}'.format(x)]>=.45) & (df['gini_{}'.format(x)]<.50), 'gini_breaks_{}'.format(x)] = 3
	df.loc[(df['gini_{}'.format(x)]>=.50), 'gini_breaks_{}'.format(x)] = 4
	# print x
	# print df.groupby('gini_breaks_{}'.format(x)).size()
#######################################################################
# make maps for diversity and specialization levels in 1990, 2000, and 2010
#######################################################################

mylabels1 = ['0.0 - 0.2', '0.2 - 0.4', '0.4 - 0.6', '0.6 - 0.8', '0.8 - 1.0']
mylabels2 = ['0.28 - 0.4', '0.4 - 0.45', '0.45 - 0.50', '0.50 - 0.63']

# for v in ['diversity_4grp', 'Sus', 'gini']:
for v in ['Sus']:
	title = 'diversity'
	mylabels = mylabels1
	if v == 'Sus':
		title = 'specialization'
	elif v == 'gini':
		title = 'gini'
		mylabels = mylabels2
	print title
	for y in ['90', '00', '10']:
		print y
		# if title == 'gini':
		# 	ax=df.plot(column='gini_{}'.format(y), linewidth=.1, edgecolor='white', legend=True, categorical=False, scheme='Fisher_Jenks')
		# else:
		# 	ax=plot_dataframe_custom(df,column='{}_breaks_{}'.format(title,y), linewidth=.1, edgecolor='white', legend=True, categorical=True, cmap=cmap, cust_labels=mylabels)
		ax=plot_dataframe_custom(df,column='{}_breaks_{}'.format(title,y), linewidth=.1, edgecolor='white', legend=True, categorical=True, cmap='YlGnBu', cust_labels=mylabels)
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
		year = None
		if y == '90':
			year = '1990'
		else:
			year = '20{}'.format(y)
		outFile = '/home/eric/Documents/franklin/narsc2018/figures/county_{}_{}'.format(title, year)
		plt.savefig(outFile, bbox_inches='tight')
		plt.close()

############################################################################
# make  maps for diversity and specialization in 1990, 2000, and 2010
############################################################################
periods = [ ['90', '00'], ['00', '10'] ]

# for v in ['specialization', 'gini', 'diversity']:
for v in ['specialization']:

	for p in periods:
		start = p[0]
		end = p[1]
	
		# df['ppctchg_{}{}'.format(start, end)] = ( df['pop{}'.format(end)] - df['pop{}'.format(start)] ) * 1.0 / df['pop{}'.format(start)] * 100
		# df['loss_dummy_{}{}'.format(start, end)] = 0
		# df.loc[df['ppctchg_{}{}'.format(start, end)] < 0, 'loss_dummy_{}{}'.format(start, end)] = 1

		df['specialization_diff_{}{}'.format(start,end)] = df['Sus_{}'.format(end)] - df['Sus_{}'.format(start)]
		df['diversity_diff_{}{}'.format(start,end)] = df['diversity_4grp_{}'.format(end)] - df['diversity_4grp_{}'.format(start)]
		df['gini_diff_{}{}'.format(start,end)] = df['gini_{}'.format(end)] - df['gini_{}'.format(start)]

		df.loc[df['{}_diff_{}{}'.format(v,start, end)]<0, '{}_breaks_{}{}'.format(v,start,end)] = 1 
		df.loc[(df['{}_diff_{}{}'.format(v,start, end)]>=0) & (df['{}_diff_{}{}'.format(v,start, end)]<0.05), '{}_breaks_{}{}'.format(v,start,end)] = 2 
		df.loc[(df['{}_diff_{}{}'.format(v,start, end)]>=0.05) & (df['{}_diff_{}{}'.format(v,start, end)]<0.1), '{}_breaks_{}{}'.format(v,start,end)] = 3 
		df.loc[(df['{}_diff_{}{}'.format(v,start, end)]>=0.1), '{}_breaks_{}{}'.format(v,start,end)] = 4 

		mylabels = ['{} - 0.00'.format(df['{}_diff_{}{}'.format(v,start,end)].min().round(2)), 
			'0.00 - 0.05',
			'0.05 - 0.10', 
			'0.10 - {}'.format(df['{}_diff_{}{}'.format(v,start,end)].max().round(2))]
		# print y
		# cmap = ['#d73027', '#e0f3f8', '#91bfdb', '#4575b4']
		cmap = LinearSegmentedColormap.from_list('mycmap', list(reversed(['#d73027', '#fc8d59', '#fee090', '#4575b4'])) )
		# cmap = LinearSegmentedColormap.from_list('mycmap', cmap)
		# ax=df.plot(column='{}_diff_{}{}'.format(v,start,end), linewidth=.1, edgecolor='white', legend=True, categorical=False, scheme='Fisher_Jenks')
		print df.groupby('specialization_breaks_{}{}'.format(start, end)).size()
		ax=plot_dataframe_custom(df, column='specialization_breaks_{}{}'.format(start,end), linewidth=.1, edgecolor='white', 
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

		outFile = '/home/eric/Documents/franklin/narsc2018/figures/county_{}_diff_{}{}'.format(v, start, end)
		plt.savefig(outFile, bbox_inches='tight')
		plt.close()

con.close()