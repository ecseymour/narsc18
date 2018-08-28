from pysqlite2 import dbapi2 as sql
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf

db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.enable_load_extension(True)
con.execute("SELECT load_extension('mod_spatialite');")

qry = '''
SELECT A.STATE,
A.CL8AA1990 AS pop90,
A.CL8AA2000 AS pop00,
A.CL8AA2010 AS pop10,
B.*
FROM nhgis_pop_race_norm_90_10 AS A
JOIN county_diversity AS B
    ON A.GISJOIN = B.GISJOIN
AND A.STATEA NOT IN ('72', '02', '15', '11')
;
'''

df = pd.read_sql(qry, con, index_col='GISJOIN')
len(df)


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
print len(df)

df['diversity_diff'] = df['diversity_4grp_10'] - df['diversity_4grp_00']
df['pct_pop_chg'] = (df['pop10'] - df['pop00']) * 1.0 / df['pop00'] * 100

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



# formula = "diversity_diff ~ pop_loss + pop_gain + np.log(pop00) + pwhite_00 + STATE"
# # formula = "diversity_decline ~ pop_loss + pop_gain + np.log(pop00) + pwhite_00 + region"
# # formula = "diversity_decline ~ intl + intg + np.log(pop00) + pwhite_00 + STATE"
# # results = smf.ols(formula=formula, data=df).fit(cov_type='cluster', cov_kwds={'groups': df['CBSA_Code']})
# # results = smf.logit(formula=formula, data=df).fit()
# results = smf.ols(formula=formula, data=df).fit(cov_type='HC3')
# print results.summary()

df.to_csv('/home/eric/Documents/franklin/narsc2018/generated_data/county_regression_data.csv', index_label='gisjoin')
print len(df)