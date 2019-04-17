import sqlite3 as sql
import csv
import re
import glob


# connect to db
db = "/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite"
con = sql.connect(db)
con.text_factory=str
cur = con.cursor()

path = "/home/eric/Documents/franklin/narsc2018/source_data/census/nhgis0089_csv/*.csv"
for fname in glob.glob(path):
	print "+" * 60
	print fname
	codebook = fname.replace('.csv', '_codebook.txt')
	print codebook
	tablename = fname.split('/')[-1].split('.')[0]
	print tablename

	field_only = []
	schema = []
	# add context fields to schema
	with open(codebook, 'rb') as f:
		for line in f:
			if "Context Fields" in line:
				break
		for line in f:
			if "---" in line:
				break
			if line.startswith(' '*8):
				# print line				
				field_name = line.strip().split(":")[0]
				if any(i.isdigit() for i in field_name):
					field = (field_name, 'INT')
				else:
					field = (field_name, 'TEXT')
				field = ' '.join(field)
				if field_name != '':
					field_only.append(field_name)
					schema.append(field)

	cur.execute("DROP TABLE IF EXISTS {};".format(tablename))
	cur.execute("CREATE TABLE IF NOT EXISTS {} ({});".format(tablename,  ', '.join(map(str, schema))))

	# create insert template
	cur.execute("SELECT * FROM {};".format(tablename))
	fields = list([cn[0] for cn in cur.description])
	qmarks = ["?"] * len(fields)
	insert_tmpl = "INSERT INTO {} ({}) VALUES ({});".format(tablename, ', '.join(map(str, fields)),', '.join(map(str, qmarks)))
	print insert_tmpl
	#################################################################
	# insert data into newly created table
	with open(fname, 'rb') as f:
		reader = csv.reader(f)
		header = reader.next()
		for row in reader:
			cur.execute(insert_tmpl,row)

	con.commit()

	cur.execute("CREATE INDEX idx_{}_gisjoin ON {}('GISJOIN');".format(tablename, tablename))
	
	con.commit()

con.close()