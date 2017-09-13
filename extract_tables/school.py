"""Reader for the document regarding schools."""
import logging

import pandas
import PyPDF2
import tabula


class Reader:
    """Read pages and extract tables."""

    def __init__(self, path):
        """Initialize the reader."""
        self.path = path
        self.logger = logging

        self.pdf_file = open(path, 'rb')
        self.pdfReader = PyPDF2.PdfFileReader(self.pdf_file)
        self.no_pages = self.pdfReader.numPages

    def process_all(self, pages=list()):
        """Process the whole document.

        Args:
            pages (list[int]): pages to be processed, e.g. [1, 2, 5].

        Returns:
            table (pandas.DataFrame): one table from all the pages.
        """
        def change_each_field_to_str(series):
            """Change each field of the row to str."""
            dic = series.to_dict()
            for k in dic:
                dic[k] = str(dic[k])
            return pandas.Series(dic)

        if not pages:
            pages = range(self.no_pages)

        current_district = None
        results = pandas.DataFrame()
        for i in pages:
            self.logger.info('Processing page {}'.format(i))
            table, gov = self.process(page=i)

            for index, row in table.iterrows():
                if 'District' in str(row[0]):
                    current_district = row[0]
                    continue

                row = change_each_field_to_str(row)
                extra_fields = pandas.Series(
                    {'Governorate': gov, 'District': current_district})
                row = row.append(extra_fields)
                results = results.append(row, ignore_index=True)

        return results

    def process(self, page):
        """Process a selected page. Return table and meta-information."""
        table = self.extract_table(page)
        text = self.extract_text(page)
        governorate = self.extract_governorate(text)

        # TODO: add last line to the table.

        return table, governorate

    def extract_table(self, page):
        """Extract table from page.

        Args:
            page (int)

        Return:
            table (pandas.DataFrame)
        """
        page += 1  # tabula counts from 1
        assert 0 < page <= self.no_pages

        args_for_tabula_java = {'pages': page, 'lattice': True}
        return tabula.read_pdf(self.path, **args_for_tabula_java)

    def extract_governorate(self, text):
        """Extract title of the table.

        The title is at the beginning of the text: 'xxxTITLE Governorate ...',
        where xxx is the number of the page.
        """
        text = text[:100]
        if 'Governorate' in text:
            first_word = text.split()[0]
            return first_word[3:]
        return None

    def extract_text(self, page):
        """Extract text from page..

        Args:
            page (int): number of page

        Return:
            text of the page (str)
        """
        self.logger.debug('Processing'.format(page))
        assert 0 <= page < self.no_pages
        page_object = self.pdfReader.getPage(page)
        return page_object.extractText()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up."""
        self.pdf_file.close()
