"""Parse school pdf."""
import pandas

import extract_tables.school


path = 'tests/resources/Schools_selection.pdf'
reader = extract_tables.school.Reader(path)
table = reader.process_all()

for line in table:
    print(line)

table = pandas.DataFrame(table)
table.to_csv('schools.csv', index=False)
