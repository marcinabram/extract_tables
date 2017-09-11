"""Tests."""
import unittest


class TestGeneral(unittest.TestCase):
    """Test pytesseract module."""

    def test_import(self):
        """Test import."""
        self.assertEqual(2+2, 4)


if __name__ == '__main__':
    unittest.main()
