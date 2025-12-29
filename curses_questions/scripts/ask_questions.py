#!/usr/bin/env python3

"""
Uses curses to display questions when run as a script.
"""

import argparse
import curses
import os
import sys
from collections import OrderedDict

from curses_questions.widgets import (
    QuestionWidget, AnswerWidget, RunningTotalWidget
)
from curses_questions.answer_providers import (
    RandomizedAnswerProvider, PresetAnswerProvider
)
from curses_questions.question_providers import (
    randomized_question_generator, inf_question_generator
)


def check_positive(value):
    try:
        int_value = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Invalid int value: '{value}'".format(value=value)
        )
    if int_value <= 0:
        raise argparse.ArgumentTypeError(
            "Expected positive integer but got: '{value}'".format(value=value)
        )
    return int_value


def questions_loop(stdscr, question_gen, answer_provider, preceding_str):
    # Sets bg colour to black, curses.wrapper resets this on termination
    curses.init_color(0, 0, 0, 0)
    # We must call this to be able to use -1 in the next command
    curses.use_default_colors()
    # Hide the cursor
    curses.curs_set(0)
    # -1 sets the text bg colour to the current bg colour of the terminal
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_BLUE, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.init_pair(4, curses.COLOR_RED, -1)
    curses.init_pair(5, curses.COLOR_YELLOW, -1)

    question_widget = QuestionWidget("???", preceding_str, curses.color_pair(1), curses.color_pair(2), 0)
    answer_widget = AnswerWidget([], 3, 4, curses.A_DIM, curses.A_BOLD)
    running_total_widget = RunningTotalWidget()
    for question_no, (question, correct_answer) in enumerate(question_gen, 1):
        # Print out the question
        stdscr.clear()
        question_widget.next_question(question)

        # Print out running total of questions answered correctly
        running_total_widget.draw(stdscr)

        # Print out the answers
        try:
            answers = answer_provider.get_answers(question)
        except ValueError:
            answers = ["???"]
        answer_widget.clear_coloured_answers()
        answer_widget.answers = answers

        curses.ungetch(curses.KEY_RESIZE)
        # Here we wait for user input and react accordingly
        answer_chosen = False
        while True:
            c = stdscr.getch()
            if chr(c) == "q":  # User has quit
                return
            elif c == curses.KEY_RESIZE:  # We redraw on resize
                stdscr.clear()
                question_widget.draw(stdscr)
                answer_widget.draw(stdscr, question_no % 2)
                running_total_widget.draw(stdscr)
                stdscr.border(0)
                stdscr.refresh()
            elif answer_chosen:  # User has gone to next question
                answer_chosen = False
                break
            elif chr(c).isdigit() and 1 <= int(chr(c)) <= len(answers):
                answer_chosen = True
                chosen_answer = answers[int(chr(c)) - 1]
                answer_widget.add_green_answer(
                    answers.index(correct_answer) + 1
                )
                if chosen_answer == correct_answer:
                    running_total_widget.increment(True)
                else:
                    answer_widget.add_red_answer(int(chr(c)))
                    running_total_widget.increment(False)
                # Set next key to resize so our changes are drawn
                curses.ungetch(curses.KEY_RESIZE)


def main():
    description = """Answer questions from a text file using the number
                     keys. Questions and their answers should be on the
                     same line and split by a common delimeter. The
                     answer choices displayed by the program for a given
                     question are sampled randomly from other questions
                     in the input file (in addition to the correct
                     answer)."""
    # Here we define our command line arguments
    parser = argparse.ArgumentParser(description=description)
    # Dictates if user wants a set number, or infinite questions
    question_group = parser.add_mutually_exclusive_group()
    # Dictates how answers for questions are obtained
    answer_format_group = parser.add_mutually_exclusive_group()

    # positional argument: infile
    # description: name of file to read questions from
    parser.add_argument(
        "infile",
        nargs="?",
        type=argparse.FileType("r"),
        help="name of file to read questions from, defaults to stdin",
        default=sys.stdin,
    )
    # optional argument: delimiter
    # description: describes delimiter in input lines which divides question
    #              and answer
    parser.add_argument(
        "-d",
        "--delimiter",
        help="""delimiter in input lines which divide the question and answer,
        default is tab""",
        default="\t",
    )
    # optional argument: precede
    # description: text to precede all questions
    parser.add_argument(
        "-p",
        "--precede",
        help="precede all question strings with this string",
        default="",
    )
    # optional argument: choices
    # description: number of answer choices for a question
    answer_format_group.add_argument(
        "-c",
        "--choices",
        type=check_positive,
        help="number of answers to choose from per question, default is 3",
        default=3,
    )
    # optional argument: preset-answers
    # description: use preset answers dictated in input file
    answer_format_group.add_argument(
        "-pa",
        "--preset-answers",
        help="using this option will replace the programs default behaviour of obtaining possible answers for a question by sampling answers to other questions. Instead, the program will interpret input lines as a question followed by one or more answers; the question/answers being seperated by the --delimiter option and the question always being taken as the string before the first occurrence of the delimiter. The correct answer will be taken as the string after.",
        action="store_true"
    )
    # optional argument: questions
    # description: number of questions to ask
    question_group.add_argument(
        "-n",
        "--questions",
        type=check_positive,
        help="number of questions to answer (no duplicates). If this is greater than the number of questions in the file, all the questions are asked in a random order.",
        default=10
    )
    # optional argument: all
    # description: asks all questions in the order they appear in the input
    question_group.add_argument(
        "-a",
        "--all",
        help="Ask all questions in the input file, preserving their order",
        action="store_true",
    )
    # Optional argument: endless
    # description: tells program to keep asking questions until terminated
    question_group.add_argument(
        "-e",
        "--endless",
        help="keep asking questions until user terminates program",
        action="store_true",
    )
    # Optional argument: regex
    # description: use regex for question/answer extraction
    question_group.add_argument(
        "-r",
        "--regex",
        help="Use only lines matching the given regex, taking question/answer as the first/second capture group respectively",
    )
    args = parser.parse_args()

    file_lines = args.infile.readlines()
    delim = args.delimiter
    regex = args.regex

    ##########################################
    # Create the correct answer provider obj #
    ##########################################
    if args.preset_answers:
        answer_provider = PresetAnswerProvider.parse_from_iter(
            file_lines,
            delim
        )
    elif regex:
        answer_provider = RandomizedAnswerProvider.parse_from_iter_regex(
            file_lines,
            regex,
            args.choices,
        )
    else:
        answer_provider = RandomizedAnswerProvider.parse_from_iter(
            file_lines,
            args.choices,
            delim
        )

    ############################################
    # Create the correct question provider obj #
    ############################################
    # Assert there are actually questions in the input file
    question_to_answer_mapping = answer_provider.get_all_questions()
    if not question_to_answer_mapping:
        print("Input file is empty or has no lines in the correct format!")
        return
    # Create the correct question generator object according to cmdline args
    if args.endless:
        question_gen = inf_question_generator(question_to_answer_mapping)
    elif args.all:
        question_gen = question_to_answer_mapping.items()
    else:
        question_gen = randomized_question_generator(
            question_to_answer_mapping, args.questions
        )

    # To read from standard input and still be able to handle user key
    # presses we need to do the following, see:
    # https://stackoverflow.com/questions/53696818/how-to-i-make-python-curses-application-pipeline-friendly
    f = open("/dev/tty")
    os.dup2(f.fileno(), 0)
    # wrapper() calls cbreak() and noecho() so we don't have to
    curses.wrapper(
        lambda stdscr: questions_loop(
            stdscr, question_gen, answer_provider, args.precede
        )
    )


if __name__ == "__main__":
    main()
