"""Extract positions of text from pdf.

The code was inspired by a sample that was presented at
https://stackoverflow.com/questions/22898145
"""
import pdfminer
import pdfminer.pdfparser
import pdfminer.pdfdocument
import pdfminer.pdfpage
import pdfminer.pdfinterp
import pdfminer.pdfdevice
import pdfminer.layout
import pdfminer.converter


class PdfMiner:
    """Wrapper for pdfminer."""

    def __init__(self, path):
        """Initialize the pdfminer."""
        self.file = open(path, 'rb')
        self.parser = pdfminer.pdfparser.PDFParser(self.file)
        self.document = pdfminer.pdfdocument.PDFDocument(self.parser)

        if not self.document.is_extractable:
            raise pdfminer.pdfpage.PDFTextExtractionNotAllowed

        self.resource_manager = pdfminer.pdfinterp.PDFResourceManager()
        self.lap_params = pdfminer.layout.LAParams()
        self.device = pdfminer.converter.PDFPageAggregator(
            self.resource_manager, laparams=self.lap_params)
        self.interpreter = pdfminer.pdfinterp.PDFPageInterpreter(
            self.resource_manager, self.device)

    def __del__(self):
        """Close all files."""
        self.file.close()

    def parse_obj(self, lt_objs):
        """Loop over the object list. Extract the text and its position."""
        parsed = []
        for obj in lt_objs:
            # if it's a textbox, print text and location
            if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
                x = obj.bbox[0]
                y = obj.bbox[1]
                text = obj.get_text().replace('\n', ' __nextpage__ ')
                parsed.append({'x': x, 'y': y, 'text': text})

            # if it's a container, recurse
            elif isinstance(obj, pdfminer.layout.LTFigure):
                self.parse_obj(obj._objs)

        return parsed

    def process(self, pages=tuple()):
        """Process pdf, return list of extracted items."""
        processed = []
        pdf_page = pdfminer.pdfpage.PDFPage
        for i, page in enumerate(pdf_page.create_pages(self.document)):
            if not pages or pages[0] <= i <= pages[1]:
                # read the page into a layout object
                self.interpreter.process_page(page)
                layout = self.device.get_result()

                # extract text from this object
                processed.append(self.parse_obj(layout._objs))

        return processed
