import subprocess
import pandas as pd
from test_task.settings import MEDIA_ROOT
from mainapp.parsers.excel_parser import ExcelFileParser
from mainapp.parsers.pdf_parser import PDFFileParser
from mainapp.parsers.word_parser import WordFileParser
import os


def get_file_data(file_name):
    """Get data from a file."""

    file_format = file_name.split('.')[-1]
    file_path = f'{MEDIA_ROOT}/patient_files/{file_name}'
    if file_format in ['xlsx', 'xltx', 'xls', 'xlt', 'ods', 'ots']:
        df = pd.read_excel(file_path).fillna(value=False)
        parser_obj = ExcelFileParser(df)
        parser_obj.run()
        data = parser_obj.get_data()
    elif file_format in ['csv']:
        df = pd.read_csv(file_path).fillna(value=False)
        parser_obj = ExcelFileParser(df)
        parser_obj.run()
        data = parser_obj.get_data()
    elif file_format in ['pdf']:
        parser_obj = PDFFileParser(file_path)
        parser_obj.run()
        data = parser_obj.get_data()
    elif file_format in ['docx']:
        if file_format != 'docx':
            bashCommand = f"lowriter --convert-to docx {file_path}"
            os.system(bashCommand)
        parser_obj = WordFileParser(file_path)
        parser_obj.run()
        data = parser_obj.get_data()
    return data