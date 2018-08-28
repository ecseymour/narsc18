import sqlite3 as sql
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

import statsmodels.api as sm
import statsmodels.formula.api as smf

db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
cur = con.cursor()
# attach to sharmistha db for CBSA population 
db2 = "/home/eric/Documents/franklin/sharmistha/generated_data/foreign_born.sqlite"
cur.execute("ATTACH DATABASE '{}' AS db2;".format(db2))

# find 50 largest MSAs and join to their respective counties
# join to tracts on state and county

qry = '''
SELECT B.CBSA_Code, B.CBSA_Title, B.State_Name, 
B.County_County_Equivalent, B.Central_Outlying_County, B.fips5digit,
C.GISJOIN, C.CL8AA2000 AS pop00, C.CL8AA2010 AS pop10,
D.diversity_4grp_10, D.diversity_4grp_00, D.pwhite_00
FROM (SELECT *
	FROM db2.research_dataset
	WHERE cbsa_metro_micro = 'Metropolitan Statistical Area' 
	ORDER BY cbsa_pop00 DESC
	LIMIT 50) AS A 
JOIN db2.cbsa_county_xwalk_15 AS B
	ON A.CBSA_Code = B.CBSA_Code
JOIN main.nhgis_race_norm_90_10_tract AS C
	ON B.FIPS_State_Code = C.STATEA AND B.FIPS_County_Code = C.COUNTYA
JOIN main.tract_diversity AS D
	ON C.GISJOIN = D.GISJOIN
; 
'''

df = pd.read_sql(qry, con, index_col='GISJOIN')
con.close()
print len(df)

# remove outlier tracts
df = df.loc[df['pop00']>=100]
# calc main DV and IV
df['diversity_diff'] = df['diversity_4grp_10'] - df['diversity_4grp_00']
df['pct_pop_chg'] = (df['pop10'] - df['pop00']) * 1.0 / df['pop00'] * 100
# df = df.loc[df['pct_pop_chg'] <	3000]
df['chg_ln'] = np.log(df['pct_pop_chg']+101)

# df['pct_pop_chg'].hist(bins=30);plt.show()
# print df.loc[df['pct_pop_chg']>3000][['State_Name', 'County_County_Equivalent', 'pop00', 'pop10']]

# print df['pct_pop_chg'].describe()

# df['chg_ln'].hist(bins=15);plt.show()

# df['diversity_diff'].hist(bins=30);plt.show()
# df.plot.scatter('chg_ln', 'diversity_diff');plt.show()
# sns.lmplot(x='pct_pop_chg', y='diversity_diff', data=df);plt.show()

# formula = "diversity_diff ~ chg_ln + pop00 + pwhite_00 + CBSA_Title + Central_Outlying_County"
# results = smf.ols(formula, data=df.sample(n=10000)).fit(cov_type='HC3')
# print results.summary()


# df = df.sample(n=25000)

df['diversity_decline'] = 0
df.loc[df['diversity_diff'] < 0, 'diversity_decline'] = 1
print df.groupby('diversity_decline').size()

# gen new var with increasing values for pop change tracts alone
df['pop_loss'] = 0
df.loc[df['pct_pop_chg'] < 0, 'pop_loss'] = df['pct_pop_chg'] * -1
df['intl'] = 1
df.loc[df['pct_pop_chg'] >= 0, 'intl'] = 0

df['pop_gain'] = 0
df.loc[df['pct_pop_chg'] >= 0, 'pop_gain'] = df['pct_pop_chg']
df['intg'] = 1
df.loc[df['pct_pop_chg'] < 0, 'intg'] = 0

# formula = "diversity_decline ~ pop_loss + pop00 + pwhite_00 + CBSA_Title + Central_Outlying_County"
# results = smf.ols(formula, data=df.sample(n=20000)).fit(cov_type='HC3')
# print results.summary()

# df['diversity_diff'].hist(bins=15);plt.show()

# formula = "diversity_decline ~ pop_loss + pop_gain + np.log(pop00) + pwhite_00 + CBSA_Title + Central_Outlying_County"
# # results = smf.ols(formula=formula, data=df).fit(cov_type='cluster', cov_kwds={'groups': df['CBSA_Code']})
# results = smf.ols(formula=formula, data=df).fit(cov_type='HC3')
# # results = smf.ols(formula=formula, data=df).fit()
# print results.summary()

df.to_csv('/home/eric/Documents/franklin/narsc2018/generated_data/tract_regression_data.csv', index_label='gisjoin')
print len(df)

# formula = "diversity_diff ~ intl + intg + pop_loss + pop_gain + np.log(pop00) + pwhite_00 + CBSA_Title + Central_Outlying_County -1"
# # results = smf.ols(formula=formula, data=df).fit(cov_type='HC3')
# results = smf.ols(formula=formula, data=df).fit(cov_type='cluster', cov_kwds={'groups': df['CBSA_Code']})
# print results.summary()


# y = df['diversity_diff']
# df['pop00_ln'] = np.log(df['pop00'])
# cols_to_keep = ['intl', 'intg', 'pop_loss', 'pop_gain', 'pwhite_00', 'pop00_ln']

# # create dummies for cbsa
# dummy_cbsas = pd.get_dummies(df['CBSA_Title'], prefix='cbsa')
# X = df[cols_to_keep].join(dummy_cbsas.ix[:, 'cbsa_Austin-Round Rock, TX':])
# results = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': df['CBSA_Code']})
# print results.summary()




# formula = "diversity_decline ~ pop_loss + pop_gain + np.log(pop00) + pwhite_00 + CBSA_Title + Central_Outlying_County"
# results = smf.logit(formula=formula, data=df).fit()
# print results.summary()


# df.plot.scatter('pop_loss', 'diversity_diff');plt.show()

# formula = "diversity_diff ~ pct_pop_chg + np.log(pop00) + pwhite_00 + CBSA_Title + Central_Outlying_County"
# results = smf.ols(formula=formula, data=df.sample(n=20000)).fit(cov_type='HC3')
# print results.summary()

# fig, ax = plt.subplots()
# fig = sm.graphics.plot_ccpr(results, "pop_growth", ax=ax)
# plt.show()


# formula = "diversity_decline ~ pop_loss + pop_gain + np.log(pop00) + pwhite_00 + CBSA_Title + Central_Outlying_County"
# results = smf.logit(formula=formula, data=df.sample(n=25000)).fit()
# print results.summary()

# df = df.sample(n=10000)
# ivs = ['chg_ln', 'pop00', 'pwhite_00', 'CBSA_Title', 'Central_Outlying_County']
# results = sm.Logit(df['diversity_decline'], df[ivs]).fit()
# print results.summary()


