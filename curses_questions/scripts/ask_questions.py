#!/usr/bin/env python3

"""
Uses curses to display questions when run as a script.
"""

import argparse
import curses
import os
import random
import sys
from collections import OrderedDict

from curses_questions.widgets import (
    QuestionWidget, AnswerWidget, RunningTotalWidget
)


class FalseAnswerProducer:
    """
    Obtains false answers via random selection from a question pool.
    """

    def __init__(self, question_pool, no_choices=3):
        self.question_pool = question_pool
        self.no_choices = no_choices
        # Just to be safe
        if not self.question_pool:
            self.question_pool = {"Your question Here": "Your answer here"}

    def get_random_answers(self, chosen_question):
        """
        Get iterable of answers which consists of the answer of the chosen
        question and (no_choices - 1) randomly chosen incorrect answers.
        """
        # Ensure random.sample works, note deliberate method local variable
        no_choices = min(self.no_choices, len(self.question_pool))
        # Check chosen_question is actually in the answer pool:
        if chosen_question not in self.question_pool:
            raise ValueError(
                "chosen_question: '{question}' is not in the question_pool"
                .format(question=chosen_question)
            )
        exclusion_set = set([self.question_pool[chosen_question]])
        choice_set = set(self.question_pool.values()) - exclusion_set
        # random choice without replacement
        choices = random.sample(choice_set, no_choices - 1)
        correct_answer = self.question_pool[chosen_question]
        # Insert correct answer into random place in list
        choices.insert(random.randint(0, no_choices - 1), correct_answer)
        return choices


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


def question_generator(question_pool, no_questions, with_replacement=False):
    """
    Generator which yields <no_questions> questions from the specified
    question_pool (which should be a valid argument to dict(), ie consist of
    (question, answer) tuples). If with_replacement is True and
    no_questions > len(questions_pool), the generator will yield
    len(question_pool) items.
    """
    question_pool = dict(question_pool)
    if with_replacement:
        for i in range(no_questions):
            yield random.choice(question_pool.items())
    else:
        no_questions = min(len(question_pool), no_questions)
        chosen_questions = random.sample(question_pool.items(), no_questions)
        for question in chosen_questions:
            yield question


def inf_question_generator(question_pool, error_question=("???", "???")):
    """
    Generator which will yield random questions from a pool continuously.
    If the pool is empty error_question is yielded instead.
    """
    question_pool = dict(question_pool)
    items = list(question_pool.items())
    while True:
        yield random.choice(items) if items else error_question


def questions_loop(stdscr, question_gen, answer_producer, preceding_str):
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
            answers = answer_producer.get_random_answers(question)
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
        help="delimiter in input lines which divide the question and answer, default is tab",
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
    parser.add_argument(
        "-c",
        "--choices",
        type=check_positive,
        help="number of answers to choose from per question, default is 3",
        default=3,
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
    args = parser.parse_args()

    file_lines = args.infile.readlines()
    delim = args.delimiter
    # Split file lines by delimiter, we do a bit a validation here too
    question_pool = OrderedDict()
    for line in file_lines:
        split = line.split(delim, 1)
        if (len(split) == 2):
            question_pool[split[0]] = split[1]
        else:
            print("Skipping incorrectly formatted line: " + line)
    # Assert there are actually questions in the input file
    if not question_pool:
        print("Input file is empty or has no lines in the correct format!")
        return
    # Create the correct question generator object according to cmdline args
    if args.endless:
        question_gen = inf_question_generator(question_pool)
    elif args.all:
        question_gen = iter(question_pool.items())
    else:
        question_gen = question_generator(question_pool, args.questions)
    # Create a false answer generator object
    false_answer_producer = FalseAnswerProducer(question_pool, args.choices)

    # To read from standard input and still be able to handle user key
    # presses we need to do the following, see:
    # https://stackoverflow.com/questions/53696818/how-to-i-make-python-curses-application-pipeline-friendly
    f = open("/dev/tty")
    os.dup2(f.fileno(), 0)
    # wrapper() calls cbreak() and noecho() so we don't have to
    curses.wrapper(
        lambda stdscr: questions_loop(
            stdscr, question_gen, false_answer_producer, args.precede
        )
    )


if __name__ == "__main__":
    main()
