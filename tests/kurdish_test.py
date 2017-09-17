"""Tests."""
import unittest

import extract_tables.kurdish


class TestSchool(unittest.TestCase):
    """Test pytesseract module."""

    def setUp(self):
        """Run before each test."""
        path = 'tests/resources/Iraq_selection.pdf'
        self.reader = extract_tables.kurdish.Reader(path)

    def test_how_tables_are_built(self):
        """Test if tables are built."""
        texts = [
            [(1, 1, 'page_1 text_1'), [1, 2, 'page_1 text_2']],
            [(1, 1, 'page_1 text_2'), [10, 22, 'page_2 text_2']]
        ]

        tables = self.reader.build_tables(texts)
        self.assertEqual(len(tables), 2)

    def test_one_table(self):
        """Test if a table is correctly created."""
        texts = [(1, 1, 'page_1 text_1'), [1, 2, 'page_1 text_2']]

        tables = self.reader.build_tables(texts)
        self.assertEqual(len(tables), 2)

if __name__ == '__main__':
    unittest.main()
