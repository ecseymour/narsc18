'''
plot change in diversity against pct pct pop change for each age group 

add 4 subplots, 1 for each age group
'''

from pysqlite2 import dbapi2 as sql
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.enable_load_extension(True)
con.execute("SELECT load_extension('mod_spatialite');")


qry = '''
SELECT A.GISJOIN, B.*
FROM us_county_2010 AS A JOIN county_diversity_by_age AS B 
	ON A.gisjoin = B.gisjoin
JOIN gz_2010_us_050_00_20m AS C
	ON A.statefp10 = C.state AND A.countyfp10 = C.county
WHERE A.STATEFP10 NOT IN ('02', '15', '72')
;
'''
df = pd.read_sql(qry, con, index_col='GISJOIN')

# calc pct change
ages = ['under5', '5to17', '18to64', '65plus']

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, sharey=True, sharex=True, figsize=(12,8))
axli = [ax1, ax2, ax3, ax4]

for a in ages:
	df['diversity_diff_{}'.format(a)] = df['diversity_4grp_{}_2010'.format(a)] - df['diversity_4grp_{}_2000'.format(a)]
	df['ppctchg_{}'.format(a)] = (df['total_{}_2010'.format(a)] - df['total_{}_2000'.format(a)]) * 1.0 / df['total_{}_2000'.format(a)] * 100

for a, x in zip(axli,ages):

	# df.plot.scatter('ppctchg_{}'.format(x), 'diversity_diff_{}'.format(x), ax=a)
	sns.regplot(x='ppctchg_{}'.format(x), y='diversity_diff_{}'.format(x), data=df, ax=a)

# plt.show()
plt.suptitle('pct. pop. change and difference in county specific diversity 2000-2010')
outFile = '/home/eric/Documents/franklin/narsc2018/figures/county_diversity_diff_by_age_2000-2010'
plt.savefig(outFile, bbox_inches='tight')

con.close()