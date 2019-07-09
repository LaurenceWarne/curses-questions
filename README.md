# Curses Questions

A simple script which uses curses to create a nice TUI for asking questions.

## Demo

[![asciicast](https://asciinema.org/a/VM1Gx7rwbmdSP1vFbd5HecPtx.svg)](https://asciinema.org/a/VM1Gx7rwbmdSP1vFbd5HecPtx)

## Usage

```
usage: curses-questions [-h] [-d DELIMITER] [-p PRECEDE] [-c CHOICES]
                        [-n QUESTIONS | -a | -e]
                        [infile]

Answer questions from a text file using the number keys. Questions and their
answers should be on the same line and split by a common delimeter. The answer
choices displayed by the program for a given question are sampled randomly
from other questions in the input file (in addition to the correct answer).

positional arguments:
  infile                name of file to read questions from, defaults to stdin

optional arguments:
  -h, --help            show this help message and exit
  -d DELIMITER, --delimiter DELIMITER
                        delimiter in input lines which divide the question and
                        answer, default is tab
  -p PRECEDE, --precede PRECEDE
                        precede all question strings with this string
  -c CHOICES, --choices CHOICES
                        number of answers to choose from per question, default
                        is 3
  -n QUESTIONS, --questions QUESTIONS
                        number of questions to answer (no duplicates). If this
                        is greater than the number of questions in the file,
                        all the questions are asked in a random order.
  -a, --all             Ask all questions in the input file, preserving their
                        order
  -e, --endless         keep asking questions until user terminates program
```

## Anki .apkg Compatibility

You can use the ```curses-anki``` script to attempt to convert anki .apkg files to a format usable by ```curses-questions```:
```
$ curses-anki my-file.apkg | curses-questions
```
Note this will create a ```collection.anki2``` file in your working directory.

## Installation

Requires python 3.

```
$ git clone https://github.com/LaurenceWarne/curses-questions.git && cd curses-questions
# Installs locally
$ python3 setup.py install --user
```
