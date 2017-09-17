"""Reader for the document regarding schools."""
import logging

import re

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
            """Change pandas.Series to native dictionary."""
            dic = series.to_dict()
            for k in dic:
                dic[k] = str(dic[k])
            return dic

        if not pages:  # pragma: no cover
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

        return self.clean_keys(results)

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

        The title is at the beginning of the text.
        The format is 'xxxTitleGovernorateSchool...', where xxx is a number.
        """
        def add_missing_spaces(line):
            """Add spaces in middle of a small-letter-upper-letter sequence."""
            prev_lower = set([i+1 for i, c in enumerate(line) if c.islower()])
            current_upper = set([i for i, c in enumerate(line) if c.isupper()])
            split = prev_lower & current_upper
            line = [' ' + c if i in split else c for i, c in enumerate(line)]
            return "".join(line)

        def remove_numers(line):
            """Remove numbers from string."""
            return "".join([i for i in line if i.isalpha()])

        gov = text.split('School')[0]
        gov = remove_numers(gov)
        gov = add_missing_spaces(gov)

        return gov

    @staticmethod
    def extract_last_row(text):
        """Extract last row from the free text of the page."""
        def recognize_beginning(line):
            """Return True if the the line looks like a beginning of a row.

            Usually the line starts with a school id (7 numbers).
            """
            school_id = line[:7]
            if len(school_id) == 7 and school_id.isnumeric():
                return True
            return False

        def recognize_end(line):
            """Return True if the line looks like an end of a row.

            Usually, such line ends with '2digits.a_number' or a long number.
            """
            section = line.split()
            try:
                part = section[-1].split('.')
                if len(part) == 2:
                    if len(part[0]) == 2 and part[0].isnumeric():
                        if len(part[1]) >= 3 and part[1].isnumeric():
                            return True
                elif line and len(line[-4:]) == 4 and line[-4:].isnumeric():
                    return True
            except IndexError:
                return False
            return False

        lines = text.split('\n')

        beginning, end = None, None
        position = len(lines) - 1
        while position > 0:
            if recognize_end(lines[position]):
                end = position
            if recognize_beginning(lines[position]):
                beginning = position
                break
            position -= 1

        if beginning is not None and end is not None:
            return "".join(lines[beginning:end+1])
        return None

    @staticmethod
    def parse_last_row(last_row):
        """Parse last row.

        The last_row has format:
            ('1500620PrimaryAl-Taherah', '36 16 17.343 22 43.183827')
        It must be transformer into a dictionary.
        """
        def extract_id(line):
            """Extract school id."""
            letters = find_position_of_letters(line)
            return line[:letters[0]][:7], line[letters[0]:]

        def find_position_of_letters(line):
            """Find positions of upper letters."""
            return [i for i in range(len(line)) if line[i].isalpha()]

        def extract_school_type(line):
            """Extract school type. Return the rest of the """
            upper = find_position_of_upper_letters(line)
            return line[:upper[1]], line[upper[1]:]

        def find_position_of_upper_letters(line):
            """Find positions of upper letters."""
            return [i for i in range(len(line)) if line[i].isupper()]

        def extract_school_name(line):
            """Extract school name from the string."""
            numbers = find_position_of_numbers(line)
            return line[:numbers[0]], line[numbers[0]:]

        def find_position_of_numbers(line):
            """Find positions of numbers."""
            return [i for i in range(len(line)) if line[i].isdigit()]

        def extract_latitude(line):
            """Extract the latitude of the place."""
            return line[:10], line[10:]

        def extract_longitude(line):
            """Extract the longitude of the place."""
            return line[:10], line[10:]

        def split_students_and_teachers(line):
            """Find number of students."""
            if len(line) >= 5:
                return line[:-2], line[-2:]
            else:
                return line[:-1], line[-1]

        print('**', last_row)

        school_id, rest = extract_id(last_row)
        school_type, rest = extract_school_type(rest)
        school_name, rest = extract_school_name(rest)
        latitude, rest = extract_latitude(rest)
        longitude, rest = extract_longitude(rest)
        no_students, no_teachers = split_students_and_teachers(rest)

        row = {
            'School\rID': school_id,
            'School Type': school_type,
            'School Name': school_name,
            'GPS\r- N -': latitude,
            'GPS\r- E -': longitude,
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

    @staticmethod
    def clean_keys(table):
        """Save table to csv."""
        def replace_line(line):
            """Translate keys."""
            return {n: clean(line[old]) for n, old in zip(new_keys, old_keys)}

        def clean(word):
            """Clean the word from extra signs."""
            if word is None:
                return None

            table = {8482: "'", 8217: "'", 8250: ""}
            word = word.translate(table)  # translate above unicode characters
            word = re.sub("[^(\w{ ,'-})]", " ", word)  # remove odd characters
            word = re.sub("\s\B", "", word)  # replace many spaces to one

            if word.isnumeric() and len(word) != 7:
                return int(word)
            return word

        old_keys = table[0].keys()
        new_keys = [k.replace('\r', ' ') for k in table[0].keys()]
        return [replace_line(line) for line in table if line]

    def __del__(self):
        """Clean up."""
        self.pdf_file.close()
