import curses
import textwrap


class QuestionWidget:
    def __init__(
        self,
        question,
        preceding_str,
        intro_flag,
        question_flag,
        starting_question_number=1,
    ):
        self.question = question
        self.preceding_str = preceding_str
        self.intro_flag = intro_flag
        self.question_flag = question_flag
        self.question_number = starting_question_number

    def next_question(self, question):
        self.question = question
        self.question_number += 1

    def draw(self, stdscr):
        """
        Draw the specified question at the top of the screen, with
        'Question <question_no>' having flag intro_flag, and
        the question itself having flag question_flag
        """
        stdscr.addstr(
            1,
            2,
            "Question " + str(self.question_number),
            self.intro_flag,
        )
        stdscr.addstr(": " + self.preceding_str)
        stdscr.addstr(self.question, self.question_flag)


class AnswerWidget:
    def __init__(
            self, answers, correct_colour, false_colour, even_flag, odd_flag,
            indent=6):
        self.answers = answers
        self.correct_colour = correct_colour
        self.false_colour = false_colour
        self.even_flag = even_flag
        self.odd_flag = odd_flag
        self.indent = indent
        self.green_answers = []
        self.red_answers = []

    def add_green_answer(self, answer_index):
        self.green_answers.append(answer_index)

    def add_red_answer(self, answer_index):
        self.red_answers.append(answer_index)

    def clear_coloured_answers(self):
        self.green_answers.clear()
        self.red_answers.clear()

    def draw(self, stdscr, switch_flags=False):
        """
        Draw the contents of self.answers on the screen. answers whose index
        is in self.green_answers or self.red_answers will be drawn with those
        respective colours.
        """
        current_line = 2
        for number, answer in enumerate(self.answers, 1):
            current_line += 1  # Ensure we leave a blank line between answers
            # Prepend number to answer
            answer = str(number) + ": " + answer
            text_wrap = textwrap.wrap(
                answer,
                width=stdscr.getmaxyx()[1] - (self.indent + 1),
                initial_indent=" " * self.indent,
                subsequent_indent=" " * (self.indent + 3),
            )
            oddp = not (number % 2) if (switch_flags) else (number % 2)
            flag = self.odd_flag if oddp else self.even_flag
            # Green or red text overrides bold and dim effects
            if number in self.green_answers:
                flag = curses.color_pair(self.correct_colour)
            elif number in self.red_answers:
                flag = curses.color_pair(self.false_colour)
            for line in text_wrap:
                stdscr.addstr(current_line, 0, line, flag)
                current_line += 1


class RunningTotalWidget:
    """Draws a 'running total' at the top left of a curses window."""

    def __init__(self):
        self.no_correct = 0
        self.no_questions = 0

    def increment(self, is_answer_correct):
        self.no_questions += 1
        if is_answer_correct:
            self.no_correct += 1

    def draw(self, stdscr):
        # Print out running total of questions answered at the top right
        # of the screen
        max_y, max_x = stdscr.getmaxyx()
        running_total_str = \
            "{questions_answered_correctly}/{total_questions_asked}".format(
                questions_answered_correctly=self.no_correct,
                total_questions_asked=self.no_questions,
            )
        stdscr.addstr(1, max_x - len(running_total_str) - 2, running_total_str)
