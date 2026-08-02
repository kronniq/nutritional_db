#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 11:45:13 2023

@author: kronq
"""

__version__ = '1.0.1'

from col_heads import col_heads, heads
from col_heads import col_dict, heads_dict
from col_heads import default_fields, default_heads
from tabulate import tabulate
from pprint import pprint
import csv
import os
import re
import sys
import pyinputplus as pyip
import argparse

# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Nutrition',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # parser.add_argument('DBfile',
    #                     metavar='str',
    #                     help='DB file to load',
    #                     default='usda_data.csv')
    
    parser.add_argument('-f', '--file',
                        '-v', '--version',
                        action='version',
                        version=f'%(prog)s {__version__}',
                        help='DB file name',
                        metavar='str',
                        type=str,
                        default='usda_data.csv')
    return parser.parse_args()


db_file = get_args().file
if db_file == 'usda_data.csv':
    delim = '^'
    quote = '$'
    descr = 'Shrt_Desc'
elif db_file == 'usda_dataC.csv':     # comma delimited file
    delim = ','
    quote = '~'
    descr = 'Shrt_Desc'
else:
    delim = ','
    quote = '"'
    descr = 'name'
    col_heads = heads
    col_dict = heads_dict
    default_fields = default_heads


def main():

    args = get_args()
    db_file = args.file    
    db = read_csv(db_file)
    convert_lower(db)
    fields = default_fields
    choice = None

    try:
        while True:
            # if not choice:
            choice = choose_action()
            if choice == 'Search food database':
                if os.name == 'posix':
                    print('<control-D> to quit')
                    print('enter "<" to return main menu')
                elif os.name == 'nt':
                    print('Enter search words separated by a space')
                    print('  ("Q" or "q" to quit)')
                    print('  ("<" to return main menu)')
                    print()
                while True:
                    foods = search_foods()
                    if ord(foods[0][0]) == 60:
                        break
                    entries = search_Shrt_Desc(foods, fields, db)
                    for entry in entries:
                        print(tabulate(entry, fields))  
                        print()
            elif choice == 'Choose your own columns(ingredients, nutrients)':
                fields = choose_fields(default_fields)
                # choice = None
            elif choice == 'Print list of available column names(ingredients, nutrients)':
                pprint(col_dict, compact=True, depth=40)
                # choice = None
            elif choice == 'Quit':
                sys.exit()

    except EOFError:
        sys.exit()

def read_csv(db_file) -> list:
    """
    Returns
    -------
    list
        List of lists(rows in database).
    """        
    with open(db_file, newline='', encoding='latin-1') as csvfile:
        reader = csv.DictReader(csvfile,
                                # fieldnames=col_heads,
                                delimiter = delim,
                                quotechar = quote)

        return [row for row in reader]


def convert_lower(db) -> list:
    """
    Parameters
    ----------
    db : List
        List of lists(rows in database.

    Returns
    -------
    list
        Same list of lists converted to lower case.
    """
    for row in db:
        row[descr] = row[descr].lower()


def search_Shrt_Desc(foods, fields, db) -> list:

    matches = []
    for row in db:
        match = []
        match_row = True
        for food in foods:
            if not re.search(food, row[descr]):
                match_row = False 
        if match_row:
            match.append(row[descr])
            for field in fields:
                match.append(row[field])
            matches.append(match)

    return matches,


def search_foods() -> list:

    while True:

        try:
            print()
            print('Enter food item(s) to search: ', end='')
            foods = input().lower()
            print()
            if foods == 'q':
                sys.exit()
            foods = foods.split()
            valid, err = validate_food(foods)
            if valid:
                return foods
            else:
                print(err)
                print()
                continue
        except EOFError:
            sys.exit()


def choose_action():
    
    print()
    choice = pyip.inputMenu(['Search food database',
                            'Print list of available column names(ingredients, nutrients)',
                            'Choose your own columns(ingredients, nutrients)',
                            'Quit'], numbered=True)
    print(f' - {choice}\n')
    return choice

def choose_fields(default_fields) -> list:
    """
    Parameters
    ----------
    default_fields : List
        Default column headers (ingredients, nutrients).

    Returns
    -------
    list
        User defined list of column headers.

    """
    while True:
        print('Enter "D" for default column headers')
        field_nums = input('Enter column numbers(separated by space): ').split()
        new_fields = []
        if not field_nums:
            return default_fields
        if any(n.lower() == 'd' for n in field_nums):
            return default_fields

        invalid = [n for n in field_nums if not n.isdigit() or int(n) not in col_dict]
        if invalid:
            print(f'Invalid entry: {" ".join(invalid)}')
            print(f'Please enter "D" or numbers between {min(col_dict)} '
                  f'and {max(col_dict)}, separated by spaces.')
            continue

        for n in field_nums:
            new_fields.append(col_dict[int(n)])
        return new_fields

def validate_food(food):

    valid = True
    if not food:
        return False, 'Enter a food item'

    return True, ''

if __name__ == '__main__':
    main()