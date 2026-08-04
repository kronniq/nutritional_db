# nutritional_db

A command-line tool to search a CSV database of foods and display a chosen
subset of macro and micro nutrients. Column names, delimiter, quote
character, and saved column groupings are all derived from and stored
per-database — no hardcoded schema, so any CSV that follows the required
column layout (below) can be used as-is.

## Requirements

- Python 3.10+
- [`tabulate`](https://pypi.org/project/tabulate/)
- [`pyinputplus`](https://pypi.org/project/pyinputplus/)

Install dependencies:

```
pip install tabulate pyinputplus
```

## CSV column convention

Any database file used with this tool must have its columns laid out as:

| Position | Meaning                              |
|----------|---------------------------------------|
| 1        | id / number (e.g. `NDB_No`)           |
| 2        | name / description (e.g. `Shrt_Desc`) |
| 3+       | macro/micro nutrient fields           |

Column 2 is used as the searchable food description. Columns 3 onward are
what you filter/select/group when choosing which nutrients to display.

## Usage

```
./nutrition.py [-f FILE] [-d DELIM] [-q QUOTE]
./nutrition.py -v   # print version and exit
```

| Flag             | Meaning                                                                 |
|------------------|--------------------------------------------------------------------------|
| `-f`, `--file`   | Path to the database CSV. Defaults to the last database used, if any.   |
| `-d`, `--delim`  | Field delimiter character. Defaults to `,`, or the stored value for this DB if it's been loaded before. Passing this always overrides the stored value. |
| `-q`, `--quote`  | Quote character. Defaults to `"`, or the stored value for this DB. Passing this always overrides the stored value. |
| `-v`, `--version`| Print the version number and exit.                                     |

**First time loading a new database**, pass the correct `-d`/`-q` for its
format, e.g.:

```
./nutrition.py -f usda_data.csv -d '^' -q '~'
```

From then on, `./nutrition.py -f usda_data.csv` alone reuses the stored
delimiter/quote automatically. If you run with no `-f` at all, the app
reuses whichever database you last used — anywhere on the filesystem, not
just the current directory.

**If no database can be resolved** (nothing specified, nothing remembered,
or the remembered/specified file no longer exists), the app prints the CSV
files it finds in the current directory and exits instead of crashing:

```
No DB file specified and no previously used DB on record.
CSV files available in this folder:
  myfooddata.csv
  usda_data.csv
Re-run with -f <filename> to choose one.
```

## Interactive menu

Every menu prompt is preceded by a banner showing the active database and
column group:

```
=============================================
Database: myfooddata.csv   |   Group: default
=============================================
```

Menu options:

- **Search food database** — enter one or more search terms (space-separated,
  matched as regex against the food description, case-insensitive). Results
  are shown in a table with the active group name right-aligned above the
  description column. Enter `<` to return to the main menu, or `Ctrl-D`
  (`Q`/`q` on Windows) to quit.
- **Print list of available column names(ingredients, nutrients)** — prints
  the numbered dict of selectable nutrient columns for the current database.
- **Choose your own columns(ingredients, nutrients)** — pick a custom set of
  nutrient columns, and manage saved column groupings (see below).
- **List available databases** — lists every CSV in the current directory,
  marks the active one, and shows each database's configured column groups.
- **Quit** — exit the app.

## Column groups

A "group" is a named, saved selection of nutrient columns for a specific
database (e.g. `default`, `fats`, `vitamins`). Groups are managed from the
**Choose your own columns** menu:

| Input                  | Action                                                        |
|-------------------------|----------------------------------------------------------------|
| `1 4 7 ...`             | Select columns by number (from the numbered list).            |
| `D`                     | Load the `default` group (all nutrient columns).               |
| `L <name>`              | Load a previously saved group.                                 |
| `X <name>`              | Delete a saved group.                                          |
| *(blank)*               | Keep the current selection unchanged.                          |

After picking columns by number, you're prompted to save the selection under
a name (letters/digits/`_`/`-`, single word, no spaces) — leave it blank to
use the selection without saving it. Whichever group you load, save, or pick
`D` for becomes the database's **last-used group**, and is loaded
automatically the next time you open that database.

## Persisted configuration

`db_config.json` (gitignored — it's local, machine-specific state) stores,
per database file (keyed by absolute path):

- `delim` / `quote` — the CSV delimiter and quote character
- `groups` — named column-group selections, including `default`
- `last_group` — the group to load automatically next time

It also stores a top-level pointer to the last database used across the
whole app, so running with no `-f` at all picks up where you left off.

## Versioning

Releases are tagged in git and mirrored by the hardcoded `__version__` in
`nutrition.py` (shown via `-v`/`--version`). See [VERSIONING.md](VERSIONING.md)
for the full workflow — how releases are tagged, and how to check out or
patch a previous version.

## Project files

| File               | Purpose                                                        |
|--------------------|------------------------------------------------------------------|
| `nutrition.py`     | Main application — CLI, menu, search, and column-group logic.  |
| `db_config.py`     | Persistence layer for per-database settings (`db_config.json`). |
| `VERSIONING.md`    | Git tagging/branching workflow for releases.                   |
