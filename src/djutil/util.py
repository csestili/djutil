import logging
import os
from pathlib import Path
import re
import subprocess

import pandas as pd

# Custom words to remove
EXCLUDE_LIST = ['[FREE DL]', '[DUPLOC10YRS]', '[Digital Bonus]', '[Premiere]', '[Bassrush Premiere]', '(DDD118)']
REPLACE_DICT = {
    "¿": ""
}


def get_file_df(dir_path, glob_pat="*"):
    path = []
    parent = []
    name = []
    stem = []
    suffix = []
    for pp in dir_path.glob(glob_pat):
        path.append(pp.resolve())
        parent.append(pp.parent)
        name.append(pp.name)
        stem.append(pp.stem)
        suffix.append(pp.suffix)
    df = pd.DataFrame({"path": path, "parent": parent, "name": name, "stem": stem, "suffix": suffix})
    return df


def strip_digit_prefix(stem):
    # "2.Sub Basics - Shipment Pt.2" => "Sub Basics - Shipment Pt.2"
    return re.sub(r'^\d+\.', '', stem)


def strip_underscore_digits(stem):
    # "Criso & Breathworkz - Wicked_2051092604 - Criso" => "Criso & Breathworkz - Wicked - Criso"
    return re.sub(r'_\d+', '', stem)


def remove_words(series):
    replace = REPLACE_DICT
    remove = {s: "" for s in EXCLUDE_LIST}
    replace.update(remove)
    series = series.str.replace(replace)
    # Remove consecutive whitespace and strip
    series = series.str.replace(r'\s+', ' ', regex=True).str.strip()
    return series


def run_ffmpeg(row):
    assert row.path
    assert row.new_sample_fmt
    assert row.new_sample_rate
    assert row.new_path
    if row.new_path.is_file():
        logging.warning(f"File exists, skipping: {row.new_path}")
        return None
    else:
        command = [
            'ffmpeg',
            '-i', row.path,
            '-sample_fmt', row.new_sample_fmt,
            '-ar', row.new_sample_rate,
            row.new_path
        ]
        process = subprocess.Popen(command)
        return_code = process.wait()
        return int(return_code)
