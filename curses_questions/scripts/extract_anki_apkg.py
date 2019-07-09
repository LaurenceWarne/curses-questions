#!/usr/bin/env python3

import sqlite3
import sys
import zipfile


def main():
    file_name = sys.argv[1]
    with zipfile.ZipFile(file_name, "r") as zip_file:
        zip_file.extract("collection.anki2")
    print_db_data()


def print_db_data():
    conn = sqlite3.connect("collection.anki2")
    c = conn.cursor()
    # See:
    # https://decks.fandom.com/wiki/Anki_APKG_format_documentation
    for (content,) in c.execute("SELECT flds FROM notes"):
        parts = content.split("\x1f")
        # Attempt to get text contents from the note field
        text_content = [s for s in parts if  "[" not in s]
        if len(text_content) < 2:
            print("Invalid note found: " + content, file=sys.stderr)
        else:
            print(text_content[0] + "\t" + text_content[1])
    conn.close()


if __name__ == "__main__":
    main()
