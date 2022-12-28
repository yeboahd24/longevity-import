import re
from langdetect import detect, lang_detect_exception
from collections import Counter
from translate import Translator

from mainapp.parsers.constants import KEYWORD_UNITS, KEYWORD_COMMENT


class ExcelFileParser:
    """Excel and csv document parser."""

    def __init__(self, df):
        self.df = df
        self.data_dict = dict()
        self.language = self.detect_language()

    def detect_language(self):
        """Determine the document language."""

        lang_list = list()
        for header in self.df.head():
            for item in self.df[header].tolist():
                if isinstance(item, str):
                    item_list = re.sub(r'[.,\/#!$%\^&\*;:{}=\-–—_`~()<>]',
                                       '', item).split(' ')
                    for word in item_list:
                        try:
                            lang_list.append(detect(word))
                        except lang_detect_exception.LangDetectException:
                            pass

        # convert the list with languages into a Counter and get
        # the most common language
        counter_lang = Counter(lang_list)
        language = counter_lang.most_common(1)[0][0]
        return language

    def _get_index_analyzes_row(self, units_on_lang):
        """Get the index of the first analysis row."""

        # find the index of the line in which the word "units" is present
        # in accordance with the language of the document,
        # increase by 1 and get the first line of analyses
        analysis_row_index = 1
        for head in self.df.head():
            for u in units_on_lang:
                if len(self.df.loc[self.df[head].str.contains(u, na=False, flags=re.IGNORECASE)]):
                    analysis_row_index = self.df.loc[self.df[head].str.contains(u, na=False,
                                 flags=re.IGNORECASE)].index.values.astype(int)[0] + 1
        return analysis_row_index

    def _get_index_col(self, values):
        """Get the index of the column."""

        # find the index of the column by keyword
        col_index = None
        for head in self.df.head():
            for j in values:
                if len(self.df.loc[self.df[head].str.contains(j, na=False, flags=re.IGNORECASE)]):
                    col_index = self.df.columns.get_loc(head)
        return col_index

    def _get_index_reference_col(self):
        """Get the index of the reference values column."""

        # we find the index of the column of reference
        # values according to the regular expression pattern
        max_match = 0
        index_col = 0
        for index, head in enumerate(self.df.head()):
            current_match = 0
            for i in self.df[head].tolist():
                if isinstance(i, str) and \
                        re.fullmatch(r'\d+\.\d+\s[\-–—]\s\d+\.\d+', i):
                    current_match += 1
            if current_match > max_match:
                max_match = current_match
                index_col = index
        return index_col

    def _get_analyzes(self, analyzes_row_index, comment_col_index,
                      units_col_index, reference_col_index):
        """Get analysis data."""

        analyzes_list = list()
        translator = Translator(from_lang=self.language, to_lang='en')
        while True:
            item_dict = dict()

            # read the name of the analysis from the first row of the
            # analysis table, if empty, go to the next row
            param_name = self.df.iloc[analyzes_row_index][0]
            if param_name:
                param_name = translator.translate(param_name)
                param_name = param_name.lower()
                item_dict['parameter'] = param_name
            else:
                analyzes_row_index += 1
                continue

            # read the result of the analysis
            param_value = self.df.iloc[analyzes_row_index][1]
            if param_value:
                item_dict['value'] = param_value
            else:
                item_dict['value'] = None

            # read the comment to the analysis
            if comment_col_index:
                param_comment = self.df.iloc[analyzes_row_index][comment_col_index]
                if param_comment:
                    param_comment = translator.translate(param_comment)
                    item_dict['comment'] = param_comment
                else:
                    item_dict['comment'] = None
            else:
                item_dict['comment'] = None

            # read the units of measurement of the analysis result
            units = self.df.iloc[analyzes_row_index][units_col_index]
            if units:
                units = translator.translate(units)
                item_dict['units'] = units
            else:
                item_dict['units'] = None

            # read and parse the field of reference values
            reference_value = self.df.iloc[analyzes_row_index][reference_col_index]
            reference_values = self._parse_ref_value(reference_value)
            item_dict['reference_values'] = reference_values

            # adding a dictionary with the received data to the list of analyses
            analyzes_list.append(item_dict)
            analyzes_row_index += 1

            # if the units of measurement field of the next line is empty,
            # exit the loop
            if not self.df.iloc[analyzes_row_index][units_col_index]:
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

        analyzes_row_index = self._get_index_analyzes_row(units_on_lang)
        comments_col_index = self._get_index_col(comment_on_lang)
        units_col_index = self._get_index_col(units_on_lang)
        reference_col_index = self._get_index_reference_col()

        analyzes_list = self._get_analyzes(
            analyzes_row_index,
            comments_col_index,
            units_col_index,
            reference_col_index)

        self.data_dict['analyzes'] = analyzes_list

    def get_data(self):
        """Get the parsing result."""

        return self.data_dict