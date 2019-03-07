#!/bin/python3

import csv
import sys
import re


csv.field_size_limit(sys.maxsize)
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
    wildcard_headers = None

    # Dictionary
    csv_stats = None

    def __init__(self, input_path='input.csv'):
        # Values passed by args
        self.input_path = input_path

        # Initialize list attributes
        self.headers = []
        self.csv_contents = []
        self.unique_rows = []
        self.used_headers = []
        self.blank_headers = []

        # Initialize dict attributes
        self.wildcard_stats = dict()

        # Method calls
        self.read_csv()
        self.get_empty_columns()
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

    def get_wildcard_stats(self):
        return self.wildcard_stats

    def export_csv(self, headers_style=None, export_path='output.csv', where_condition=None, zero_length_match=None,
                   **kwargs):
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
            print('Processing {}'.format(export_path))
            writer = csv.DictWriter(outfile, headers, extrasaction='ignore', **kwargs)
            writer.writeheader()
            for row in self.csv_contents:

                # TODO: Encapsulate condition checks into separate method
                # Check for row restrictions
                if isinstance(where_condition, dict):

                    # If the wildcard is the only condition, default to false and skip to checking the wildcard
                    if list(where_condition.keys()) == ['*']:
                        condition_met = False
                    # Otherwise, default to true and check other conditions first
                    else:
                        condition_met = True

                        # Iterate through conditions, breaking at the first failed condition test
                        # Key is the name of the column to compare with, value is the pattern for the compare
                        for key, value in where_condition.items():
                            # Wild cards are processed below, skip them here
                            if key == '*':
                                continue
                            re_match = re.match(value, row[key])

                            if re_match:
                                if not zero_length_match:
                                    # Reject zero-length matches
                                    if (re_match.end() - re_match.start()) == 0:
                                            condition_met = False
                                            break
                            # If not a match, break and move onto the next row
                            else:
                                if key != 'script_name' and key != 'action_type':
                                    print('Continuing: ({} does not match pattern {})'.format(row[key], value))
                                condition_met = False
                                break

                    # If field was disqualified by above checks, check for wildcard
                    if not condition_met:
                        if '*' in where_condition:
                            wildcard = where_condition['*']
                            for column, field in row.items():
                                # if field:
                                #     print('\nChecking {} against pattern {}'.format(field, wildcard))
                                # Check Wildcard (wildcards apply to all columns, not to all field values)
                                wildcard_match = re.match(wildcard, field)
                                # Find all columns that contain the value (to allow for searching what
                                # columns have a given pattern
                                if wildcard_match:
                                    print('Match found:\n{} matches {}'.format(field, wildcard))
                                    # If zero length matches are allowed, or the match is of non-zero length
                                    if zero_length_match or ((wildcard_match.end() - wildcard_match.start()) > 0):
                                        self.wildcard_stats[column] = wildcard
                                        condition_met = True

                    # Write row if conditions are met (vacuously or otherwise)
                    if condition_met:
                        writer.writerow(row)
                else:
                    # print('Writing:\n{}'.format(row))
                    writer.writerow(row)


# Demo Output
if __name__ == '__main__':
    analyzer = Analyzer()
    analyzer.print_csv_stats()
    analyzer.export_csv(export_path='output.csv', headers_style='EXCLUDE_BLANK', quoting=csv.QUOTE_ALL)
