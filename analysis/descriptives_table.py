'''
make table of descriptive states 
for narsc presentation
'''

import pandas as pd

# collect 9000 data
inFile9000 = "/home/eric/Documents/franklin/narsc2018/generated_data/regression_data_9000.csv"
df9000 = pd.read_csv(inFile9000, index_col='GISJOIN')

# output mean and stdev
cols = [
# 'specialization_diff', 'specialization_start', 'specialization_end',
'diversity_start', 'diversity_end', 'diversity_diff',
'pwhite_start', 'pwhite_end', 'pwhite_diff',
'gini_start', 'gini_end', 'gini_diff',
'poverty_start', 'poverty_end', 'poverty_diff',
'pop_start', 'pop_end', 'ppctchg'
]

df9000['pop_end'] = df9000['pop_end'] * 1.0 / 1000
df9000['pop_start'] = df9000['pop_start'] * 1.0 / 1000
df9000 = df9000[cols]
mydict = {
	'diversity_diff': 'Diversity diff.',
	'diversity_start': 'Diversity start',
	'diversity_end': 'Diversity end',
	'gini_start': 'Gini start',
	'gini_end': 'Gini end',
	'gini_diff': 'Gini diff.',
	'pwhite_start': 'Pct. White start',
	'pwhite_end': 'Pct. White end',
	'pwhite_diff': 'Pct. White diff.',
	'pop_start': 'Pop. start',
	'pop_end': 'Pop. end',
	'ppctchg': 'Pop. pct. change',
	'poverty_start': 'Pov. rate start',
	'poverty_end': 'Pov. rate end',
	'poverty_diff': 'Pov. rate diff.'
}
df9000.rename(columns=mydict, inplace=True)
stats_9000 = df9000.describe().transpose()[['mean', 'std']]
# print stats_9000
####################################################################
# collect 9000 data
inFile0010 = "/home/eric/Documents/franklin/narsc2018/generated_data/regression_data_0010.csv"
df0010 = pd.read_csv(inFile0010, index_col='GISJOIN')
df0010 = df0010[cols]
df0010['pop_end'] = df0010['pop_end'] * 1.0 / 1000
df0010['pop_start'] = df0010['pop_start'] * 1.0 / 1000
df0010.rename(columns=mydict, inplace=True)
##########################################################
# what share of counties lost pop in each period?
loss9000 = len(df9000.loc[df9000['Pop. pct. change']<0]) * 1.0 / len(df9000) * 100
print "share loss 90-00: {}".format(round(loss9000,0))

loss0010 = len(df0010.loc[df0010['Pop. pct. change']<0]) * 1.0 / len(df0010) * 100
print "share loss 00-10: {}".format(round(loss0010,0))
##########################################################
stats_0010 = df0010.describe().transpose()[['mean', 'std']]
# print stats_0010
merged = pd.merge(stats_9000, stats_0010, left_index=True, right_index=True, suffixes=['9000', '0010'])

print merged

outF = "/home/eric/Documents/franklin/narsc2018/presentations/variable_descriptives.csv"
merged.round(2).to_csv(outF)
merged = merged.round(2)

print merged.to_latex()
# outF = "/home/eric/Documents/franklin/narsc2018/scripts/latex/descriptives.tex"
# merged.to_latex(outF)