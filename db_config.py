#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Persistent per-database settings: delimiter, quote char, and field groups."""

import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db_config.json')
LAST_DB_KEY = '__last_db__'


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, encoding='utf-8') as f:
        return json.load(f)


def save_config(config: dict) -> None:
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)


def get_db_entry(path: str) -> dict | None:
    return load_config().get(os.path.abspath(path))


def set_db_entry(path: str, delim: str, quote: str) -> None:
    config = load_config()
    entry = config.setdefault(os.path.abspath(path), {'groups': {}})
    entry['delim'] = delim
    entry['quote'] = quote
    save_config(config)


def save_group(path: str, name: str, fields: list) -> None:
    config = load_config()
    entry = config.setdefault(os.path.abspath(path), {'groups': {}})
    entry.setdefault('groups', {})[name] = fields
    save_config(config)


def delete_group(path: str, name: str) -> None:
    config = load_config()
    entry = config.get(os.path.abspath(path))
    if entry and name in entry.get('groups', {}):
        del entry['groups'][name]
        save_config(config)


def set_last_group(path: str, name: str) -> None:
    config = load_config()
    entry = config.setdefault(os.path.abspath(path), {'groups': {}})
    entry['last_group'] = name
    save_config(config)


def get_last_db() -> str | None:
    return load_config().get(LAST_DB_KEY)


def set_last_db(path: str) -> None:
    config = load_config()
    config[LAST_DB_KEY] = os.path.abspath(path)
    save_config(config)
