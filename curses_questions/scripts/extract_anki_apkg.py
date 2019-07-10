#!/usr/bin/env python3

"""

"""

import argparse
import re
import sqlite3
import sys
import zipfile


def main():
    description = """Extract question/answer strings and output them tab
                     separated to stdout."""
    parser = argparse.ArgumentParser(description=description)
    # positional argument: infile
    # description: apkg file to extract questions from
    parser.add_argument(
        "infile",
        help="name of apkg file to extract questions from",
    )
    parser.add_argument(
        "-f",
        "--fields",
        nargs=2,
        help="Fields to use from the apkg file"
    )
    args = parser.parse_args()

    with zipfile.ZipFile(args.infile, "r") as zip_file:
        zip_file.extract("collection.anki2")
    
    # Sort out fields
    if args.fields:
        f1, f2 = args.fields
        if not f1.isdigit() or not f2.isdigit():
            print("Detected non-numeric input for field number!")
            return
        else:
            f1, f2 = int(f1) - 1, int(f2) - 1
            print_db_data(f1, f2)
    else:
        print_db_data()


def print_db_data(question_index=-1, answer_index=-1):
    conn = sqlite3.connect("collection.anki2")
    c = conn.cursor()
    # See:
    # https://decks.fandom.com/wiki/Anki_APKG_format_documentation
    for (content,) in c.execute("SELECT flds FROM notes"):
        parts = content.split("\x1f")
        if question_index < 0 or answer_index < 0:
            question_index = 0
            answer_index = 1
            # Attempt to get text contents from the note field
            parts = [s for s in parts if  "[" not in s]
        if len(parts) < 2:
            print("Invalid note found: " + content, file=sys.stderr)
        elif max(question_index, answer_index) > len(parts) - 1:
            print("Field indices out of range")
        else:
            print("{question}\t{answer}".format(
                question=prettify_text(parts[question_index]),
                answer=prettify_text(parts[answer_index])
            ))
    conn.close()


def prettify_text(text):
    return re.sub("<.*?>", " ", text)


if __name__ == "__main__":
    main()
