import re
import fitz
import tabula
from langdetect import detect, lang_detect_exception
from collections import Counter
from translate import Translator

from mainapp.parsers.constants import KEYWORD_UNITS, KEYWORD_COMMENT


class PDFFileParser:
    """Pdf document parser."""

    def __init__(self, file_path):
        self.doc = fitz.open(file_path)
        self.data_dict = dict()
        self.tables = tabula.read_pdf(file_path, pages='all')
        self.language = self.detect_language()

    def detect_language(self):
        """Determine the document language."""

        page = self.doc.loadPage(0)
        page_text = page.getText("text")
        page_text = re.sub(r'[.,\/#!$%\^&\*;:{}=\-–—_`~()<>]', '',
                           page_text).split('\n')
        page_text = [res.strip() for res in page_text if res!=' ']

        lang_list = list()
        for word in page_text:
            try:
                lang_list.append(detect(word))
            except lang_detect_exception.LangDetectException:
                pass

        # convert the list with languages into a Counter and get
        # the most common language
        counter_lang = Counter(lang_list)
        language = counter_lang.most_common(1)[0][0]
        return language

    def get_analyzes_table(self, units_on_lang):
        """Get the analysis table."""

        # from the list of tables obtained, determine
        # which is the table with keyword analyses
        for table in self.tables:
            for i in units_on_lang:
                res = [head for head in table.columns
                       if head.lower() == i.lower()]
                if res:
                    return table

    def _get_index_col(self, current_table, values):
        """Get the index of the column."""

        # find the index of the column by keyword
        for i in values:
            col_name = [head for head in current_table.columns
                        if head.lower() == i.lower()][0]
            col_index = current_table.columns.get_loc(col_name)
            return col_index

    def _get_index_reference_col(self, current_table):
        """Get the index of the reference values column."""

        # we find the index of the column of reference
        # values according to the regular expression pattern
        max_match = 0
        index_col = 0
        for index, head in enumerate(current_table.head()):
            current_match = 0
            for i in current_table[head].tolist():
                if isinstance(i, str) and \
                        re.fullmatch(r'\d+\.\d+\s[\-–—]\s\d+\.\d+', i):
                    current_match += 1
            if current_match > max_match:
                max_match = current_match
                index_col = index
        return index_col

    def _get_analyzes(self, current_table, comment_col_index,
                      units_col_index, reference_col_index):
        """Get analysis data."""

        analyzes_list = list()
        translator = Translator(from_lang=self.language, to_lang='en')
        analyzes_row_index = 0
        while True:
            item_dict = dict()

            # read the name of the analysis from the first row of the
            # analysis table, if empty, go to the next row
            param_name = current_table.iloc[analyzes_row_index][0]
            if param_name:
                param_name = translator.translate(param_name)
                param_name = param_name.lower()
                item_dict['parameter'] = param_name
            else:
                analyzes_row_index += 1
                continue

            # read the result of the analysis
            param_value = current_table.iloc[analyzes_row_index][1]
            if param_name:
                item_dict['value'] = param_value
            else:
                item_dict['value'] = None

            # read the comment to the analysis
            if comment_col_index:
                param_comment = current_table.iloc[analyzes_row_index][comment_col_index]
                if param_comment:
                    param_comment = translator.translate(param_comment)
                    item_dict['comment'] = param_comment
                else:
                    item_dict['comment'] = None
            else:
                item_dict['comment'] = None

            # read the units of measurement of the analysis result
            units = current_table.iloc[analyzes_row_index][units_col_index]
            if units:
                units = translator.translate(units)
                item_dict['units'] = units
            else:
                item_dict['units'] = None

            # read and parse the field of reference values
            reference_value = current_table.iloc[analyzes_row_index][reference_col_index]
            reference_values = self._parse_ref_value(reference_value)
            item_dict['reference_values'] = reference_values

            # adding a dictionary with the received data to the list of analyses
            analyzes_list.append(item_dict)
            analyzes_row_index += 1

            # if we get an error when accessing the units of measurement
            # field of the next line, we exit the loop
            try:
                current_table.iloc[analyzes_row_index][units_col_index]
            except IndexError:
                break

        return analyzes_list

    def _parse_ref_value(self, value):
        """Parse the string reference values."""

        min_value = None
        max_value = None
        if value:
            res = re.search('[\-–—]', value)
            if res:
                value_list = re.split('[\-–—]', value)
                min_value = value_list[0].strip()
                max_value = value_list[1].strip()
            else:
                if value.find('<') != -1:
                    max_value = re.findall('\d.+', value)
                elif value.find('>') != -1:
                    min_value = re.findall('\d+\.?\d+', value)
        return min_value, max_value

    def run(self):
        """Run file parsing."""

        self.data_dict['language'] = self.language

        # creating a translator object to translate
        # data into the document language
        translator = Translator(to_lang=self.language)
        units_on_lang = translator.translate(KEYWORD_UNITS).split(' ')
        comment_on_lang = translator.translate(KEYWORD_COMMENT).split(' ')

        current_table = self.get_analyzes_table(units_on_lang)

        comments_col_index = self._get_index_col(current_table, comment_on_lang)
        units_col_index = self._get_index_col(current_table, units_on_lang)
        reference_col_index = self._get_index_reference_col(current_table)

        analyzes_list = self._get_analyzes(
            current_table,
            comments_col_index,
            units_col_index,
            reference_col_index)

        self.data_dict['analyzes'] = analyzes_list

    def get_data(self):
        """Get the parsing result."""

        return self.data_dict