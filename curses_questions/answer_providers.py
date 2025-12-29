#!/usr/bin/env python3

"""
Classes for generating answers based on a specified question.
"""

import random, re
from collections import OrderedDict


class RandomizedAnswerProvider:
    """
    Obtains false answers for a question by randomly selecting correct answers
    from other questions.
    """

    def __init__(self, question_pool, no_choices=3):
        self.question_pool = question_pool
        self.no_choices = no_choices
        # Just to be safe
        if not self.question_pool:
            self.question_pool = {"Your question Here": "Your answer here"}

    @classmethod
    def parse_from_iter(cls, iterable, no_choices=3, delimiter="\t"):
        question_pool = OrderedDict()
        for line in iterable:
            split = line.split(delimiter, 1)
            if (len(split) == 2):
                question_pool[split[0]] = split[1]
        return cls(question_pool, no_choices)

    @classmethod
    def parse_from_iter_regex(cls, iterable, regex, no_choices=3):
        question_pool = OrderedDict()
        for line in iterable:
            match = re.match(regex, line)
            if not match:
                continue
            try:
                q, a = match.group(1), match.group(2)
            except IndexError:
                continue
            else:
                question_pool[q] = a
        return cls(question_pool, no_choices)

    def get_all_questions(self):
        """
        Return a mapping of questions to their correct answers.
        """
        return dict(self.question_pool)

    def get_answers(self, chosen_question):
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
        choices = random.sample(sorted(choice_set), no_choices - 1)
        correct_answer = self.question_pool[chosen_question]
        # Insert correct answer into random place in list
        choices.insert(random.randint(0, no_choices - 1), correct_answer)
        return choices


class PresetAnswerProvider:
    """
    Provides answers for questions from a pre-determined list of answers per
    question.
    """

    def __init__(self, question_to_answers_map):
        # Mapping of questions to lists of answers, correct answer is
        # implicitly first string in list
        self.question_to_answers_map = question_to_answers_map
        if not self.question_to_answers_map:
            self.question_pool = {"Your question Here": "Your answer here"}

    def get_all_questions(self):
        """
        Return a mapping of questions to their correct answers.
        """
        return {
            question: self.question_to_answers_map[question][0]
            for question in self.question_to_answers_map.keys()
        }

    @classmethod
    def parse_from_iter(cls, iterable, delimiter="\t"):
        question_to_answers_map = dict()
        for line in iterable:
            question, *answers = line.split(delimiter)
            if answers:
                question_to_answers_map[question] = answers
        return cls(question_to_answers_map)

    def get_answers(self, chosen_question):
        if chosen_question not in self.question_to_answers_map:
            raise ValueError(
                "chosen_question: '{question}' is not a registered question."
                .format(question=chosen_question)
            )
        else:
            answers = self.question_to_answers_map[chosen_question][:]
            # non mutator shuffling
            return random.sample(answers, len(answers))
