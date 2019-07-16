#!/usr/bin/env python3

"""
Classes for generating answers based on a specified question.
"""

import random


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
        choices = random.sample(choice_set, no_choices - 1)
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
        self.questions_to_answers_map = question_to_answers_map
        if not self.question_pool:
            self.question_pool = {"Your question Here": "Your answer here"}

    @classmethod
    def parse_from_iter(cls, iterable, delimiter="\t"):
        question_to_answers_map = dict()
        for line in iterable:
            question, *answers = line.split(delimiter)
            if answers:
                question_to_answers_map[question] = answers
        return cls(question_to_answers_map)

    def get_answers(self, chosen_question):
        if chosen_question not in self.question_pool:
            raise ValueError(
                "chosen_question: '{question}' is not a registered question."
                .format(question=chosen_question)
            )
        else:
            # Return a copy, not a view
            return self.questions_to_answers_map[chosen_question][:]
