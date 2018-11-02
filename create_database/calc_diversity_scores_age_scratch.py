
import sqlite3 as sql
from string import ascii_uppercase
import pandas as pd
import numpy as np
import math

# connect to db
db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.text_factory=str
cur = con.cursor()

years = ['2010', '2000', '1980']

for y in years:

	print y

	doubleaplphas = []
	# collect vars AA - BF
	for c in ascii_uppercase:
		doubleaplphas.append('AW9A{}{}'.format(c,y))
	for c in ascii_uppercase:
		doubleaplphas.append('AW9B{}{}'.format(c,y))
		if c=='F':
			break
	myvars = ', '.join(map(str,doubleaplphas))
	qry = "SELECT {} FROM county_hispanic_origin_age WHERE STATEFP NOT IN ('72', '02', '15');".format(myvars)
	print qry

con.close()