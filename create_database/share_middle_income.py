'''
calculate county share of "middle-income" households
for each county, find pct of households earning 
btw 80% and 150% of state median hh income
might want to play with percentile breaks
after prelim results

collect for 1990, 2000, and 2008-2010
'''

import sqlite3 as sql
import pandas as pd
import numpy as np
from collections import OrderedDict

# connect to db
db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.text_factory=str
cur = con.cursor()

final_county_dict = {}

state_dict = {}
# collect state median household income
cur.execute('''
	SELECT STATEFP, B79AA125
	FROM state_med_hh_income
	WHERE STATEFP NOT IN ('72', '02', '15')
	-- AND STATEFP = '44'
	; 
	''')
results = cur.fetchall()
for row in results:
	state_dict[row[0]] = {'med': row[1], 'LB': row[1] * 0.8, 'UB': row[1] * 1.5}

# iterative over states, collecting data for all counties
for state_k, state_v in state_dict.iteritems():
	county_list = []
	cur.execute('''
		SELECT COUNTYFP
		FROM county_income
		WHERE STATEFP = ?
		AND B71AH1990 <> '' AND B71AH2000 <> '' AND B71AH125 <> '';
		''', ([state_k]))
	results = cur.fetchall()
	for row in results:
		county_list.append(row[0])

	for c in county_list:
		final_county_dict['G'+state_k+'0'+c+'0'] = OrderedDict()


years = ['1990', '2000', '125']

# iterate over years
for y in years:
	print "+" * 60
	print y
	state_dict = {}
	# collect state median household income
	cur.execute('''
		SELECT STATEFP, B79AA{}
		FROM state_med_hh_income
		WHERE STATEFP NOT IN ('72', '02', '15')
		-- AND STATEFP = '44'
		; 
		'''.format(y))
	results = cur.fetchall()
	for row in results:
		state_dict[row[0]] = {'med': row[1], 'LB': row[1] * 0.8, 'UB': row[1] * 1.5}

	# iterative over states, collecting data for all counties
	for state_k, state_v in state_dict.iteritems():
		county_list = []
		cur.execute('''
			SELECT COUNTYFP
			FROM county_income
			WHERE STATEFP = ?
			AND B71AH1990 <> '' AND B71AH2000 <> '' AND B71AH125 <> '';
			''', ([state_k]))
		results = cur.fetchall()
		for row in results:
			county_list.append(row[0])
		# print k, v,  len(county_list)

		'''
		for each county, find income bins containing .8 and 1.5 times state median income
		'''
		for c in county_list:
			# print "-" * 60
			# print state_k, c
			
			bin_dict = {
				'AA': {'LB': 0, 'UB': 9999},
				'AB': {'LB': 10000, 'UB': 14999},
				'AC': {'LB': 15000, 'UB': 19999},
				'AD': {'LB': 20000, 'UB': 24999},
				'AE': {'LB': 25000, 'UB': 29999},
				'AF': {'LB': 30000, 'UB': 34999},
				'AG': {'LB': 35000, 'UB': 39999},
				'AH': {'LB': 40000, 'UB': 44999},
				'AI': {'LB': 45000, 'UB': 49999},
				'AJ': {'LB': 50000, 'UB': 59999},
				'AK': {'LB': 60000, 'UB': 74999},
				'AL': {'LB': 75000, 'UB': 99999},
				'AM': {'LB': 10000, 'UB': 124999},
				'AN': {'LB': 125000, 'UB': 149999},
				'AO': {'LB': 150000, 'UB': float('inf')}
				}

			bin_dict = OrderedDict(sorted(bin_dict.items(), key=lambda t: t[0]))
			for bin_k, bin_v in bin_dict.iteritems():
				cur.execute('''
					SELECT  B71{}{}
					FROM county_income
					WHERE STATEFP = ? AND COUNTYFP = ?;
					'''.format(bin_k, y), (state_k, c))
				result = cur.fetchone()
				bin_dict[bin_k]['count'] = result[0]

			# find bin containing LB of percentage of state median income
			lower_bin = None; lower_count = None
			upper_bin = None; upper_count = None

			for bin_k, bin_v, in bin_dict.iteritems():
				# print bin_k, bin_v
				if state_v['LB'] > bin_v['LB'] and state_v['LB'] < bin_v['UB']:
					# print "**", state_v['LB'], bin_v
					lower_bin = bin_k
					# take diff btw bin LB and state LB
					bin_diff = state_v['LB'] - bin_v['LB']
					# take len of bin
					bin_len = bin_v['UB'] - bin_v['LB']
					# divide bin_diff by bin_len
					bin_share = bin_diff * 1.0 / bin_len
					# multiply by bin cases
					lower_count = bin_v['count'] - (bin_share * bin_v['count'])
					# print lower_count
					break

			for bin_k, bin_v, in bin_dict.iteritems():
				# print bin_k, bin_v
				if state_v['UB'] > bin_v['LB'] and state_v['UB'] < bin_v['UB']:
					# print "**", state_v['UB'], bin_v
					upper_bin = bin_k
					# take diff btw bin LB and state LB 
					bin_diff = state_v['UB'] - bin_v['LB']
					# take len of bin
					bin_len = bin_v['UB'] - bin_v['LB']
					# divide bin_diff by bin_len
					bin_share = bin_diff * 1.0 / bin_len
					# multiply by bin cases
					upper_count = bin_share * bin_v['count']
					# print bin_share, upper_count
					break

			total = 0
			for bin_k, bin_v, in bin_dict.iteritems():
				total+=bin_v['count']

			# collect count in bins between lower and upper bins
			middle_income_count = 0
			middle_income_count+=lower_count
			middle_income_count+=upper_count
			for bin_k, bin_v, in bin_dict.iteritems():
				if bin_k > lower_bin and bin_k < upper_bin:
					middle_income_count+=bin_v['count']
			# print y, middle_income_count, middle_income_count * 1.0 / total * 100 
			final_county_dict['G'+state_k+'0'+c+'0']['state'] = state_k
			final_county_dict['G'+state_k+'0'+c+'0']['county'] = c	
			final_county_dict['G'+state_k+'0'+c+'0']['share_{}'.format(y)] = middle_income_count * 1.0 / total * 100


df = pd.DataFrame.from_dict(final_county_dict, orient='index')
print df.head()

df.to_sql('county_share_middle_inc', con, if_exists='replace')
				
con.close()