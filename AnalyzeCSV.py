#!/bin/python3

import csv

"""
TODO: 
1) Encapsulate in class
2) Add parameter for a list of values recognized as "blank" (i.e. "NULL", None, 0, "")
3) Add methods for analyzing and returning more stats than blank columns

"""

class Analyzer:

    # CSV Headers
    headers = None

    # CSV Input File Path
    input_path = None

    # List of CSV Rows (Rows are OrderedDict objects returned by csv.DictReader)
    csv_contents = None
    
    # Lists
    used_headers = None
    blank_headers = None

    # Dictionary
    csv_stats = None

    def __init__(self, input_path='input.csv'):
        # Values passed by args
        self.input_path = input_path

        # Initialize attributes
        self.headers = []
        self.csv_contents = []
        self.unique_rows = []
        self.used_headers = []
        self.blank_headers = []

        # Method calls
        self.read_csv()
        self.generate_csv_stats()

    def read_csv(self):
        # Get CSV Contents
        # i = 0
        with open(self.input_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # i = i+1
                self.csv_contents.append(dict(row))
        # print(i)
        # Get Headers
        for k in self.csv_contents[0].keys():
            self.headers.append(k)

    def get_empty_columns(self):
        # TODO: Improve that ugly "BLANK COLUMN FOUND" bit
        tmp_headers = dict()
        for row in self.csv_contents:
            for k, v in row.items():
                if k not in tmp_headers.keys():
                    tmp_headers[k] = 'BLANK COLUMN FOUND'
                if tmp_headers[k] == 'BLANK COLUMN FOUND':
                    if v:
                        tmp_headers[k] = v

        for k, v in tmp_headers.items():
            if v == 'BLANK COLUMN FOUND':
                self.blank_headers.append(k)
            else:
                self.used_headers.append(k)

    def get_unique_rows(self):
        if not self.unique_rows:
            for row in self.csv_contents:
                if row not in self.unique_rows:
                    self.unique_rows.append(row)
        return self.unique_rows

    def print_csv_stats(self):
        # Format the output strings
        stats_preface_string = "Stats for '{}'".format(self.csv_stats['FileName'])
        csv_row_count_string = "Number of Rows: {}".format(self.csv_stats['RowCount'])
        csv_unique_row_count_string = "Number of Unique Rows: {}".format(self.csv_stats['UniqueRowCount'])
        total_header_string = 'Number of Total Headers: {}'.format(self.csv_stats['TotalHeaderCount'])
        used_header_string = 'Number of Used Headers: {}'.format(self.csv_stats['UsedHeaderCount'])
        blank_header_string = 'Number of Blank Headers: {}'.format(self.csv_stats['BlankHeaderCount'])

        separator = '-' * 120

        # Print the stats
        print(separator)
        print(stats_preface_string)
        print(csv_row_count_string)
        print(csv_unique_row_count_string)
        print(total_header_string)
        print(used_header_string)
        print(blank_header_string)
        print(separator)

    def generate_csv_stats(self):
        self.csv_stats = dict()
        self.csv_stats['FileName'] = self.input_path
        self.csv_stats['RowCount'] = len(self.csv_contents)
        self.csv_stats['UniqueRowCount'] =len(self.get_unique_rows())
        self.csv_stats['TotalHeaderCount'] = len(self.headers)
        self.csv_stats['UsedHeaderCount'] = len(self.used_headers)
        self.csv_stats['BlankHeaderCount'] = len(self.blank_headers)

    def get_csv_stats(self):
        return self.csv_stats

    def export_csv(self, headers_style=None, export_path='output.csv', where_condition=None, **kwargs):
        # Set Headers
        # TODO: Add support for getting blank columns specific to where_condition
        if headers_style == 'EXCLUDE_BLANK':
            headers = self.used_headers
        elif headers_style == 'ONLY_BLANK':
            headers = self.blank_headers
        else:
            headers = self.headers

        # Additional keyword arguments are passed to the csv.DictWriter constructor.
        if not headers:
            headers = self.headers

        # if isinstance(where_condition, dict):
        #     print('Using WHERE conditions: {}'.format(where_condition))
        # else:
        #     print('No WHERE conditions given. Writing all rows.')

        with open(export_path, 'w', newline='') as outfile:
            # class csv.DictWriter(f, fieldnames, restval='', extrasaction='raise', dialect='excel', *args, **kwds)
            # quoting=csv.QUOTE_ALL
            writer = csv.DictWriter(outfile, headers, extrasaction='ignore', **kwargs)
            writer.writeheader()
            for row in self.csv_contents:
                # Check for row restrictions
                if isinstance(where_condition, dict):
                    is_match = True
                    for key, value in where_condition.items():
                        # print('Checking: ({} == {})'.format(row[key], value))
                        if row[key] != value:
                            # print('Continuing: ({} != {})'.format(row[key], value))
                            is_match = False
                            break
                    if is_match:
                        writer.writerow(row)
                else:
                    # print('Writing:\n{}'.format(row))
                    writer.writerow(row)

if __name__ == '__main__':
    analyzer = Analyzer()
    analyzer.get_empty_columns()
    analyzer.print_csv_stats()
    analyzer.export_csv(export_path='output.csv', headers_style='EXCLUDE_BLANK', quoting=csv.QUOTE_ALL)
