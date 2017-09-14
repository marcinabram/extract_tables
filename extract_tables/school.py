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
        def series_to_dict(series):
            """Change each field of the row to str."""
            dic = series.to_dict()
            for k in dic:
                dic[k] = str(dic[k])
            return dic

        if not pages:
            pages = range(self.no_pages)

        current_district = None
        results = []
        for i in pages:
            self.logger.info('Processing page {}'.format(i))
            table, gov = self.process(page=i)

            for index, row in table.iterrows():
                if 'District' in str(row[0]):
                    current_district = row[0]
                    continue

                if 'School' in str(row[0]):
                    continue

                row = series_to_dict(row)
                row['Governorate'] = gov
                row['District'] = current_district
                results.append(row)

        return results

    def process(self, page):
        """Process a selected page. Return table and meta-information."""
        text = self.extract_text(page)
        governorate = self.extract_governorate(text)
        last_row = self.extract_last_row(text)
        last_row = self.parse_last_row(last_row)

        table = self.extract_table(page)
        table = table.append(pandas.Series(last_row), ignore_index=True)

        return table, governorate

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

    @staticmethod
    def extract_governorate(text):
        """Extract title of the table.

        The title is at the beginning of the text: 'xxxTITLE Governorate ...',
        where xxx is the number of the page.
        """
        text = text[:100]
        if 'Governorate' in text:
            first_word = text.split()[0]
            return first_word[3:]
        return None

    @staticmethod
    def extract_last_row(text):
        """Extract last row from the free text.

        The test part should have form:
            ['1500620PrimaryAl-Taherah',
            ['36 16 17.343 22 43.183827']
        """

        lines = text.split('\n')

        position = len(lines) - 1
        while position > 0:
            try:
                int(lines[position][:7])
                return lines[position], lines[position + 1]
            except ValueError:
                position -= 1

        return None

    @staticmethod
    def parse_last_row(last_row):
        """Parse last row.

        The last_row has format:
            ('1500620PrimaryAl-Taherah', '36 16 17.343 22 43.183827')
        It must be transformer into a dictionary.
        """
        def find_possition_of_upper_latters(line):
            """Find positions of upper letters."""
            return [i for i in range(len(line)) if line[i] != line[i].lower()]

        def split_school_type_and_name(line):
            """Find school type."""
            pos = find_possition_of_upper_latters(line)
            return line[pos[0]:pos[1]], line[pos[1]:]

        def split_students_and_teachers(line):
            """Find number of students."""
            line = line[20:]
            if len(line) > 5:
                return line[:-2], line[-2:]
            else:
                return line[:-1], line[-1]

        school_type, school_name = split_school_type_and_name(last_row[0])
        no_students, no_teachers = split_students_and_teachers(last_row[1])

        row = {
            'School\rID': last_row[0][:7],
            'School Type': school_type,
            'School Name': school_name,
            'GPS\r- N -': last_row[1][:10],
            'GPS\r- E -': last_row[1][10:20],
            'Total\rStudent': no_students,
            'Total\rTeachers': no_teachers
        }

        return row

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

    def __del__(self):
        """Clean up."""
        self.pdf_file.close()
