"""Tests."""
import unittest

import extract_tables.school


class TestSchool(unittest.TestCase):
    """Test pytesseract module."""

    def setUp(self):
        """Run before each test."""
        self.path = 'tests/resources/Schools_selection.pdf'

    def test_governorate(self):
        """Test if extracting the governorate works."""
        reader = extract_tables.school.Reader(self.path)

        results = []
        for page in range(reader.no_pages):
            text = reader.extract_text(page=page)
            print(text[:50])
            gov = reader.extract_governorate(text)
            results.append(gov)

        self.assertEqual(results, ['Ninevah']*3 + ['Salaheldin'])

    def test_process_all(self):
        """Test if a few pages can be processed."""
        reader = extract_tables.school.Reader(self.path)

        huge_table = reader.process_all(pages=[2, 3])

        print(huge_table)

        self.assertEqual(len(huge_table), 120)

if __name__ == '__main__':
    unittest.main()
