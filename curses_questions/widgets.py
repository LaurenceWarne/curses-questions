import curses
import textwrap


class QuestionWidget:

    def __init__(self, question, question_no, preceding_str):
        self.question = question
        self.question_no = question_no
        self.intro_colour = curses.color_pair()
        self.question_colour = curses.color_pair()

    def draw(self, stdscr):
        """
        Draw the specified question at the top of the screen, with
        'Question <question_no>' having colour intro_colour, and
        the question itself having colour question_colour
        """
        stdscr.addstr(
            1, 2, "Question " + str(self.question_no),
            curses.color_pair(self.intro_colour)
        )
        stdscr.addstr(": " + self.preceding_str)
        stdscr.addstr(
            self.question, curses.color_pair(self.question_colour)
        )


class AnswerWidget:

    CORRECT_COLOUR_DEFAULT = curses.init_pair(3, curses.COLOR_GREEN, -1)
    WRONG_COLOUR_DEFAULT = curses.init_pair(4, curses.COLOR_RED, -1)

    def __init__(self, answers, indent=6):
        self.answers = answers
        self.indent = indent
        self.green_answers = []
        self.red_answers = []
        self.correct_colour = self.CORRECT_COLOUR_DEFAULT
        self.correct_colour = self.WRONG_COLOUR_DEFAULT

    def draw(self, stdscr):
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
            flag = curses.A_BOLD if (number % 2) else curses.A_DIM
            # Green or red text overrides bold and dim effects
            if number in self.green_answers:
                flag = curses.color_pair(3)
            elif number in self.red_answers:
                flag = curses.color_pair(4)
            for line in text_wrap:
                stdscr.addstr(current_line, 0, line, flag)
                current_line += 1


class RunningTotalWidget:
    """Draws a 'running total' at the top left of a curses window."""

    def __init__(self):
        self.no_correct = 0
        self.no_questions = 0

    def draw(self, stdscr):
        # Print out running total of questions answered at the top right
        # of the screen
        max_y, max_x = stdscr.getmaxyx()
        running_total_str = """
        {questions_answered_correctly}/{total_questions_asked}
        """.format(
            questions_answered_correctly=self.no_correct,
            total_questions_asked=self.no_questions
        )
        stdscr.addstr(1, max_x - len(running_total_str) - 2, running_total_str)
