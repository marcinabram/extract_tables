"""Parse school pdf."""
import pandas

import extract_tables.school


path = 'tests/resources/Schools_selection.pdf'
reader = extract_tables.school.Reader(path)
table = reader.process_all()
table = pandas.DataFrame(table)

print(table)

table.to_csv('schools.csv')
