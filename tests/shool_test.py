"""Tests."""
import unittest

import pandas
import extract_tables.school


class TestSchool(unittest.TestCase):
    """Test pytesseract module."""

    def setUp(self):
        """Run before each test."""
        path = 'tests/resources/Schools_selection.pdf'
        self.reader = extract_tables.school.Reader(path)

    def test_governorate(self):
        """Test if extracting the governorate works."""
        results = []
        for page in range(self.reader.no_pages):
            text = self.reader.extract_text(page=page)
            gov = self.reader.extract_governorate(text)
            results.append(gov)

        self.assertEqual(
            results, ['Ninevah Governorate']*3 + ['Salaheldin Governorate'])

    def test_last_row(self):
        """Test if you can extract the last row."""
        line1 = "Something something"
        line2 = "1500620PrimaryAl-Taherah"
        line3 = "36 16 17.343 22 43.183827"
        line4 = "36444 Something"

        text = "\n".join([line1, line2, line3, line4])
        last_row = self.reader.extract_last_row(text)
        self.assertEqual(last_row, (line2 + line3))

    def test_last_row_as_df(self):
        """Transform the last row into dataframe."""
        text = self.reader.extract_text(page=2)
        row = self.reader.extract_last_row(text)
        row = self.reader.parse_last_row(row)

        print(row)

        self.assertEqual(row['School\rID'], '1501578')
        self.assertEqual(row['School Name'], 'Al-Tahreer')
        self.assertEqual(row['GPS\r- N -'], '36 44 04.4')
        self.assertEqual(row['GPS\r- E -'], '43 05 37.1')
        self.assertEqual(row['Total\rStudent'], '50')
        self.assertEqual(row['Total\rTeachers'], '4')

    def test_process_all(self):
        """Test if a few pages can be processed."""
        huge_table = self.reader.process_all(pages=[2, 3])
        self.assertEqual(len(huge_table), 121)

if __name__ == '__main__':
    unittest.main()
