import sqlite3 as sql
import pandas as pd
from string import ascii_uppercase
from matplotlib import pyplot as plt
import seaborn as sns

db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.text_factory=str
cur = con.cursor()

qry = '''
SELECT A.*,
B.CL8AA1990 AS pop90,
B.CL8AA2000 AS pop00,
B.CL8AA2010 AS pop10
FROM county_income AS A 
	JOIN nhgis_pop_race_norm_90_10 AS B 
	ON A.GISJOIN = B.GISJOIN
WHERE A.B71AA1990 <> ''
AND A.B71AA125 <> ''
;
'''

df = pd.read_sql(qry, con, index_col='GISJOIN')
############################################################
df['loss'] = 'growth'
df.loc[df['pop10'] < df['pop90'], 'loss'] = 'loss'
############################################################
# calc total by summing all cols
alpha_list = []
for c in ascii_uppercase:
	alpha_list.append(c)
	if c=='O':
		break

years = ['1990', '125']

for y in years:
	df['total_{}'.format(y)] = 0
	for a in alpha_list:
		df['total_{}'.format(y)] += df['B71A{}{}'.format(a,y)]

	df['share_75_100_{}'.format(y)] = (df['B71AL{}'.format(y)] + df['B71AM{}'.format(y)] ) * 1.0 / df['total_{}'.format(y)] * 100

# print df.groupby('loss')['share_75_100_1990', 'share_75_100_125'].describe().transpose()


ax = sns.boxplot(data=df, x='loss', y='share_75_100_125')
plt.show()


con.close()