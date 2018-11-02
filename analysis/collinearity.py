import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

df = pd.read_csv('/home/eric/Documents/franklin/narsc2018/generated_data/diversity_regression_data.csv', index_col='GISJOIN')

# print df[['region', 'STATE']].corr()
print df.columns

dfa = pd.get_dummies(df['region'])
dfb = pd.get_dummies(df['STATE'])
# print dfb
# fig, ax = plt.subplots()
# grouped = df.groupby(['region', 'STATE'])['specialization_diff_0010'].mean()
# ax=grouped.plot(kind='barh')
# plt.show()




# df = pd.DataFrame({'col1':np.random.choice(list('abcde'),100),
#                   'col2':np.random.choice(list('xyz'),100)}, dtype='category')
# df1 = pd.DataFrame({'col1':np.random.choice(list('abcde'),100),
#                    'col2':np.random.choice(list('xyz'),100)}, dtype='category')

# dfa = pd.get_dummies(df)
# dfb = pd.get_dummies(df1)
