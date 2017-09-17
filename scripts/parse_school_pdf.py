"""Parse school pdf."""
import pandas
import csv
import extract_tables.school


path = '/data/pdf-tables/shools-tables.pdf'
reader = extract_tables.school.Reader(path)
table = reader.process_all(list(range(167)))

# save
table = pandas.DataFrame(table)
table.to_csv('schools.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)
table.to_json('schools.json')
