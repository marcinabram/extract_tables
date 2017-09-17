"""Reader for the document regarding Kurdish villages."""
import extract_tables.positions


class Reader:
    """Read pages and extract tables."""

    def __init__(self, path):
        """Initialize."""
        self.path = path
        self.h_tolerance = 5
        self.v_tolerance = 5

    def process(self, pages=tuple()):
        """Extract tables from the pdfs."""
        texts = self.extract_text_from_pdfs(pages)
        tables = self.build_tables(texts)
        return tables

    def extract_text_from_pdfs(self, pages):
        """Extract text and position for text from pages."""
        pdf_miner = extract_tables.positions.PdfMiner(self.path)
        return pdf_miner.process(pages)

    def build_tables(self, texts):
        """Build a table from a list of (position, text)."""
        return [self.build_one_table(text) for text in texts]

    def build_one_table(self, text):
        """Build one table from a text extracted form one page."""
        return {}
