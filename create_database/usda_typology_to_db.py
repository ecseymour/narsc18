import csv
import sqlite3 as sql

db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
cur = con.cursor()

infile = "/home/eric/Documents/franklin/narsc2018/source_data/usda/2015CountyTypologyCodes.csv"

cur.execute("DROP TABLE IF EXISTS usda_typology_2015;")
cur.execute('''
	CREATE TABLE usda_typology_2015 (
	fips TEXT,
	state TEXT,
	county_name TEXT,
	metro_status INT,
	economic_type INT,
	economic_type_label
	)
	;
	''')
# create insert template
cur.execute("SELECT * FROM usda_typology_2015;")
fields = list([cn[0] for cn in cur.description])
qmarks = ["?"] * len(fields)
insert_tmpl = "INSERT INTO usda_typology_2015 ({}) VALUES ({});".format(', '.join(map(str, fields)),', '.join(map(str, qmarks)))

with open(infile, 'rb') as f:
	reader = csv.reader(f)
	header = reader.next()
	for row in reader:
		if len(row[0])==4: # add leading zero
			row[0] = '0'+row[0]
		data = row[0:6]
		cur.execute(insert_tmpl, data)

con.commit()
print "{} changes made".format(con.total_changes)
con.close()