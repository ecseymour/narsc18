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
SELECT B.diversity_4grp_10, B.diversity_4grp_00, Hex(ST_AsBinary(C.geometry)) AS geom
FROM us_county_2010 AS A JOIN county_diversity AS B 
	ON A.gisjoin = B.gisjoin
JOIN gz_2010_us_050_00_20m AS C 
	ON A.statefp10 = C.state AND A.countyfp10 = C.county
WHERE A.STATEFP10 NOT IN ('02', '15', '72')
;
'''

df = gpd.GeoDataFrame.from_postgis(qry, con, geom_col='geom')
df['diversity_diff_0010'] = df['diversity_4grp_10'] - df['diversity_4grp_00']
print df['diversity_diff_0010'].describe()

#######################################################################
ax=df.plot(column='diversity_4grp_10', linewidth=.1, edgecolor='white', legend=True, categorical=False, scheme='Fisher_Jenks')

# add state borders
qry = '''
SELECT geo_id, Hex(ST_AsBinary(geometry)) AS geom
FROM gz_2010_us_040_00_20m
WHERE state NOT IN ('02', '15', '72')
-- WHERE state = '26'
;
'''
df_state = gpd.GeoDataFrame.from_postgis(qry, con, geom_col='geom')
con.close()
df_state.plot(ax=ax, linewidth=.6, edgecolor='white', color="None")

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
leg = ax.get_legend()
leg.set_bbox_to_anchor((0., 0.1, 0.2, 0.2))
plt.title("Diversity (4-group entropy) 2012")
outFile = "/home/eric/Documents/franklin/narsc2018/figures/diversity_map.png"
plt.savefig(outFile)
plt.close()
#######################################################################
# categorize change in Gini
# simple binary: increase or decrease
# df['chgcat'] = None
df.loc[df['diversity_diff_0010'] < 0, 'chgcat'] = 'decrease' 
df.loc[df['diversity_diff_0010'] > 0, 'chgcat'] = 'increase' 
df.loc[df['diversity_diff_0010'] > df['diversity_diff_0010'].std() * 2, 'chgcat'] = 'maj. increase' 
print df.groupby('chgcat').size()

ax=df.plot(column='chgcat', linewidth=0.1, edgecolor='white', legend=True, categorical=True, cmap=cmap)
df_state.plot(ax=ax, linewidth=.6, edgecolor='white', color="None")

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
leg = ax.get_legend()
leg.set_bbox_to_anchor((0., 0.1, 0.2, 0.2))
plt.title("Difference in Diversity 2000 - 2012")
outFile = "/home/eric/Documents/franklin/narsc2018/figures/diversity_diffmap.png"
plt.savefig(outFile)
plt.close()