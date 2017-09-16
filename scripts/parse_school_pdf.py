"""Parse school pdf."""
import pandas

import extract_tables.school


path = '/data/pdf-tables/shools-tables.pdf'
reader = extract_tables.school.Reader(path)
table = reader.process_all(list(range(167)))
table = pandas.DataFrame(table)
table.to_csv('schools.csv', index=False)
