"""Tests."""
import unittest

import extract_tables.positions


class TestSchool(unittest.TestCase):
    """Test pytesseract module."""

    def setUp(self):
        """Run before each test."""
        path = 'tests/resources/Iraq_selection.pdf'
        self.pdf_miner = extract_tables.positions.PdfMiner(path)

    def test_text_extraction(self):
        """Test text extraction from pdf."""
        results = self.pdf_miner.process(pages=(0, 1))

        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0]), 175)
        self.assertEqual(set(results[0][0].keys()), {'x', 'y', 'text'})

if __name__ == '__main__':
    unittest.main()
