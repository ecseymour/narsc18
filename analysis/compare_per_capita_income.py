'''
compare change in per capita income 
relative to national average
track change from 1990 to 2012
'''

import sqlite3 as sql
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
# connect to db
db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.text_factory=str
cur = con.cursor()


qry = '''
SELECT A.GISJOIN, A.BD5AA1990, A.BD5AA2000, A.BD5AA125,
B.CL8AA1990 AS pop90,
B.CL8AA2000 AS pop00,
B.CL8AA2010 AS pop10
FROM nhgis0090_ts_nominal_county AS A
	JOIN nhgis_pop_race_norm_90_10 AS B 
	ON A.GISJOIN = B.GISJOIN
WHERE A.BD5AA1990 <> ''
;
'''
df = pd.read_sql(qry, con, index_col='GISJOIN')
con.close()
print df.dtypes

df['loss'] = 'growth'
df.loc[df['pop10'] < df['pop90'], 'loss'] = 'loss'

df['pciIdx1990'] = df['BD5AA1990'] * 1.0 / df['BD5AA1990'].mean() * 100
df['pciIdx2000'] = df['BD5AA2000'] * 1.0 / df['BD5AA2000'].mean() * 100
df['pciIdx125'] = df['BD5AA125'] * 1.0 / df['BD5AA125'].mean() * 100

# df['pciIdx1990'] = df['pciIdx1990'] * df['pop90'] 
# df['pciIdx2000'] = df['pciIdx2000'] * df['pop90']
# df['pciIdx125'] = df['pciIdx125'] * df['pop90']

# df.groupby('loss')[['pciIdx1990', 'pciIdx2000', 'pciIdx125']].mean().transpose().plot();plt.show()
fig = plt.subplot(111)
df.boxplot(column=['pciIdx1990', 'pciIdx2000', 'pciIdx125'], by=['loss'], showfliers=False)
plt.savefig("/home/eric/Documents/franklin/narsc2018/figures/per_capita_income_relative.png")

# df[['pciIdx1990', 'pciIdx2000', 'pciIdx125']].transpose().plot();plt.show()

