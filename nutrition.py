#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 11:45:13 2023

@author: kronq
"""

__version__ = '1.0.1'

from tabulate import tabulate
from pprint import pprint
import csv
import os
import re
import sys
import pyinputplus as pyip
import argparse
import db_config

# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Nutrition',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-f', '--file',
                        help='DB file name',
                        metavar='str',
                        type=str,
                        default='usda_data.csv')
    parser.add_argument('-d', '--delim',
                        help='Field delimiter character (only used the first time this DB is loaded)',
                        metavar='str',
                        type=str,
                        default=',')
    parser.add_argument('-q', '--quote',
                        help='Quote character (only used the first time this DB is loaded)',
                        metavar='str',
                        type=str,
                        default='"')
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'%(prog)s {__version__}')
    return parser.parse_args()


def get_header_fields(db_file, delim, quote) -> list:
    """Return the column names from a CSV file's header row."""
    with open(db_file, newline='', encoding='latin-1') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delim, quotechar=quote)
        return reader.fieldnames


args = get_args()
db_file = args.file

db_entry = db_config.get_db_entry(db_file)
if db_entry:
    delim = db_entry.get('delim', args.delim)
    quote = db_entry.get('quote', args.quote)
else:
    delim = args.delim
    quote = args.quote
    db_config.set_db_entry(db_file, delim, quote)

col_names = get_header_fields(db_file, delim, quote)
descr = col_names[1]
ingredient_cols = col_names[2:]
col_dict = dict(enumerate(ingredient_cols, start=1))

groups = (db_config.get_db_entry(db_file) or {}).get('groups', {})
if 'default' not in groups:
    db_config.save_group(db_file, 'default', ingredient_cols)
    groups['default'] = ingredient_cols
default_fields = groups['default']


def main():

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
                fields = choose_fields(fields)
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

def choose_fields(current_fields) -> list:
    """
    Choose a field selection by column number, or manage saved groupings.

    Parameters
    ----------
    current_fields : List
        Currently active column headers (ingredients, nutrients).

    Returns
    -------
    list
        User defined list of column headers.

    """
    while True:
        saved_groups = (db_config.get_db_entry(db_file) or {}).get('groups', {})
        print(f'Saved groups: {", ".join(saved_groups) if saved_groups else "(none)"}')
        print('Enter "D" for default column headers')
        print('Enter "L <name>" to load a saved group')
        print('Enter "X <name>" to delete a saved group')
        entry = input('Enter column numbers(separated by space): ').split()

        if not entry:
            return current_fields

        cmd = entry[0].lower()

        if cmd == 'd':
            return default_fields

        if cmd == 'l' and len(entry) > 1:
            name = entry[1]
            if name in saved_groups:
                return saved_groups[name]
            print(f'No such group: {name}')
            print()
            continue

        if cmd == 'x' and len(entry) > 1:
            name = entry[1]
            db_config.delete_group(db_file, name)
            print(f'Deleted group: {name}')
            print()
            continue

        invalid = [n for n in entry if not n.isdigit() or int(n) not in col_dict]
        if invalid:
            print(f'Invalid entry: {" ".join(invalid)}')
            print(f'Please enter "D" or numbers between {min(col_dict)} '
                  f'and {max(col_dict)}, separated by spaces.')
            print()
            continue

        new_fields = [col_dict[int(n)] for n in entry]

        name = input('Save this selection as a group? Enter a name, or leave blank to skip: ').strip()
        if name:
            db_config.save_group(db_file, name, new_fields)

        return new_fields

def validate_food(food):

    valid = True
    if not food:
        return False, 'Enter a food item'

    return True, ''

if __name__ == '__main__':
    main()
