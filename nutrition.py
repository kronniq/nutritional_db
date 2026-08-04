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
                        help='DB file name (defaults to the last DB used, if any)',
                        metavar='str',
                        type=str,
                        default=None)
    parser.add_argument('-d', '--delim',
                        help='Field delimiter character (defaults to ",", or the value stored '
                             'for this DB if seen before; passing this always overrides the stored value)',
                        metavar='str',
                        type=str,
                        default=None)
    parser.add_argument('-q', '--quote',
                        help='Quote character (defaults to \'"\', or the value stored '
                             'for this DB if seen before; passing this always overrides the stored value)',
                        metavar='str',
                        type=str,
                        default=None)
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'%(prog)s {__version__}')
    return parser.parse_args()


def get_header_fields(db_file, delim, quote) -> list:
    """Return the column names from a CSV file's header row."""
    with open(db_file, newline='', encoding='latin-1') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delim, quotechar=quote)
        return reader.fieldnames


def find_csv_files() -> list:
    """CSV files present in the current directory."""
    return sorted(f for f in os.listdir('.') if f.lower().endswith('.csv'))


args = get_args()
db_file = args.file or db_config.get_last_db()

if not db_file or not os.path.isfile(db_file):
    if db_file:
        print(f"DB file '{db_file}' was not found.")
    else:
        print('No DB file specified and no previously used DB on record.')
    candidates = find_csv_files()
    if candidates:
        print('CSV files available in this folder:')
        for candidate in candidates:
            print(f'  {candidate}')
        print('Re-run with -f <filename> to choose one.')
    else:
        print('No CSV files found in this folder either.')
    sys.exit(1)

db_config.set_last_db(db_file)

db_entry = db_config.get_db_entry(db_file) or {}
delim = args.delim or db_entry.get('delim') or ','
quote = args.quote or db_entry.get('quote') or '"'

col_names = get_header_fields(db_file, delim, quote)
if len(col_names) < 2:
    sys.exit(f"Error: parsing '{db_file}' with delimiter {delim!r} and quote {quote!r} "
             f"produced only {len(col_names)} column(s) (need at least id + name). "
             f"Pass the correct -d/--delim and -q/--quote for this file.")

db_config.set_db_entry(db_file, delim, quote)

descr = col_names[1]
ingredient_cols = col_names[2:]
col_dict = dict(enumerate(ingredient_cols, start=1))

db_entry = db_config.get_db_entry(db_file) or {}
groups = db_entry.get('groups', {})
if 'default' not in groups:
    db_config.save_group(db_file, 'default', ingredient_cols)
    groups['default'] = ingredient_cols
default_fields = groups['default']

last_group = db_entry.get('last_group', 'default')
if last_group not in groups:
    last_group = 'default'
initial_fields = groups[last_group]


def main():

    db = read_csv(db_file)
    convert_lower(db)
    fields = initial_fields
    group_name = last_group
    choice = None

    try:
        while True:
            # if not choice:
            choice = choose_action(group_name)
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
                    headers = [group_name] + fields
                    colalign = ['right'] + ['left'] * len(fields)
                    for entry in entries:
                        print(tabulate(entry, headers, colalign=colalign))
                        print()
            elif choice == 'Choose your own columns(ingredients, nutrients)':
                fields, group_name = choose_fields(fields, group_name)
                # choice = None
            elif choice == 'Print list of available column names(ingredients, nutrients)':
                pprint(col_dict, compact=True, depth=40)
                # choice = None
            elif choice == 'List available databases':
                list_databases(group_name)
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


def print_banner(group_name) -> None:
    label = f'Database: {os.path.basename(db_file)}   |   Group: {group_name or "(unsaved selection)"}'
    rule = '=' * len(label)
    print(rule)
    print(label)
    print(rule)


def choose_action(group_name):

    print()
    print_banner(group_name)
    print()
    choice = pyip.inputMenu(['Search food database',
                            'Print list of available column names(ingredients, nutrients)',
                            'Choose your own columns(ingredients, nutrients)',
                            'List available databases',
                            'Quit'], numbered=True)
    print(f' - {choice}\n')
    return choice


def list_databases(group_name) -> None:
    print()
    print(f'Current database: {os.path.basename(db_file)}')
    print(f'Current group: {group_name or "(unsaved selection)"}')
    print()
    candidates = find_csv_files()
    if not candidates:
        print('No CSV files found in this folder.')
        return
    print('Databases in this folder:')
    for candidate in candidates:
        marker = '*' if os.path.abspath(candidate) == os.path.abspath(db_file) else ' '
        entry = db_config.get_db_entry(candidate)
        if entry:
            group_names = ', '.join(entry.get('groups', {})) or '(none)'
            print(f' {marker} {candidate} -- groups: {group_names} '
                  f'(last used: {entry.get("last_group", "default")})')
        else:
            print(f' {marker} {candidate} -- not configured yet')

def choose_fields(current_fields, current_group) -> tuple:
    """
    Choose a field selection by column number, or manage saved groupings.

    Parameters
    ----------
    current_fields : List
        Currently active column headers (ingredients, nutrients).
    current_group : str
        Name of the currently active group.

    Returns
    -------
    tuple
        (list of column headers, name of the active group or '' if unsaved)

    """
    while True:
        saved_groups = (db_config.get_db_entry(db_file) or {}).get('groups', {})
        print(f'Saved groups: {", ".join(saved_groups) if saved_groups else "(none)"}')
        print('Enter "D" for default column headers')
        print('Enter "L <name>" to load a saved group')
        print('Enter "X <name>" to delete a saved group')
        entry = input('Enter column numbers(separated by space): ').split()

        if not entry:
            return current_fields, current_group

        cmd = entry[0].lower()

        if cmd == 'd':
            db_config.set_last_group(db_file, 'default')
            return default_fields, 'default'

        if cmd == 'l' and len(entry) > 1:
            name = entry[1]
            if name in saved_groups:
                db_config.set_last_group(db_file, name)
                return saved_groups[name], name
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
        print(f'Selected: {", ".join(new_fields)}')

        while True:
            name = input('Save this selection as a group? Enter a single-word name '
                          '(letters/digits/_/-), or leave blank to skip: ').strip()
            if not name:
                return new_fields, ''
            if not re.fullmatch(r'[A-Za-z_][\w-]*', name):
                print(f'Invalid name: {name!r}. Use one word, starting with a letter or '
                      f'underscore, containing only letters/digits/_/- (no spaces).')
                print()
                continue
            db_config.save_group(db_file, name, new_fields)
            db_config.set_last_group(db_file, name)
            return new_fields, name

def validate_food(food):

    valid = True
    if not food:
        return False, 'Enter a food item'

    return True, ''

if __name__ == '__main__':
    main()
