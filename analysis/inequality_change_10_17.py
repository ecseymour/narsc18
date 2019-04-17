'''
calc change in gini and 80/20 ratio
calc statistical significance of diff

there are 60 counties (excluding PR)
where the MOE is not calculated for the 95 percentile
so can't test diff in 95:20 ratio for all counties
'''

import sqlite3 as sql
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


def moe_ratio(MOEnum, MOEden, R, Xden):
	return np.sqrt( np.square(MOEnum) + ( np.square(R) * np.square(MOEden)) ) / Xden

def zscore(Est1, Est2, MOEest1, MOEest2):
	return ( np.abs(Est1 - Est2) ) / np.sqrt( np.square(MOEest1) + np.square(MOEest2) )

# connect to db
db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.text_factory=str
cur = con.cursor()

qry = '''
SELECT A.GISJOIN, A.STATE, A.COUNTY,
A.AIIJE001 AS gini_20175, A.AIIJM001 AS gini_20175m, 
B.J4TE001 AS gini_20105, B.J4TM001 AS gini_20105m,
A.AIIGE005, A.AIIGM005, A.AIIGE004, A.AIIGM004, A.AIIGE001, A.AIIGM001,
B.J4QE005, B.J4QM005, B.J4QE004, B.J4QM004, B.J4QE001, B.J4QM001
FROM nhgis0089_ds234_20175_2017_county AS A
	JOIN nhgis0089_ds177_20105_2010_county AS B
	ON A.GISJOIN = B.GISJOIN
WHERE A.STATE <> 'Puerto Rico'
;
'''
df = pd.read_sql(qry, con, index_col='GISJOIN')
print df.dtypes
#############################################################
# calc diff in gini 2010 to 2017
df['gini_diff'] = df['gini_20175'] - df['gini_20105'] 
# calc z score for test of statistical significance in difference
df['gini_diff_z'] = zscore(df['gini_20175'], df['gini_20105'], df['gini_20175m'], df['gini_20105m'])
#############################################################
# calc 80/20 ratio and change in ratio
# 2017
df['ratio_8020_20175'] = df['AIIGE004'] * 1.0 / df['AIIGE001']
df['ratio_8020_20175m'] = moe_ratio(df['AIIGM004'], df['AIIGM001'], df['ratio_8020_20175'], df['AIIGE001'] )
# 2010
df['ratio_8020_20105'] = df['J4QE004'] * 1.0 / df['J4QE001']
df['ratio_8020_20105m'] = moe_ratio(df['J4QM004'], df['J4QM001'], df['ratio_8020_20105'], df['J4QE001'])
# take diff and calc Z
df['ratio_8020_diff'] = df['ratio_8020_20175'] - df['ratio_8020_20105']
df['ratio_8020_diff_z'] = zscore(df['ratio_8020_20175'], df['ratio_8020_20105'], df['ratio_8020_20175m'], df['ratio_8020_20105m'])

# calc 95/20 ratio
# 2017
df['ratio_9520_20175'] = df['AIIGE005'] * 1.0 / df['AIIGE001']
# df['ratio_9520_20175m'] = moe_ratio(df['AIIGM005'], df['AIIGM001'], df['ratio_9520_20175'], df['AIIGE001'] )
# 2010
df['ratio_9520_20105'] = df['J4QE005'] * 1.0 / df['J4QE001']
# df['ratio_9520_20105m'] = moe_ratio(df['J4QM005'], df['J4QM001'], df['ratio_9520_20105'], df['J4QE001'])
# take diff and calc Z
df['ratio_9520_diff'] = df['ratio_9520_20175'] - df['ratio_9520_20105']
# df['ratio_9520_diff_z'] = zscore(df['ratio_9520_20175'], df['ratio_9520_20105'], df['ratio_9520_20175m'], df['ratio_9520_20105m'])
#############################################################

print df.head()

print len(df)
print len(df.loc[df['gini_diff_z']>1])
print len(df.loc[df['ratio_8020_diff_z']>1])


df.to_sql('county_inequality_2010_2017', con, if_exists='replace', index=True, index_label='GISJOIN')

# print df[['ratio_8020_20175', 'gini_20175']].corr()

# df.plot.scatter('ratio_8020_20175', 'gini_20175');plt.show()

con.close()