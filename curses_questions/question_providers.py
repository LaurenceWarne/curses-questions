import random


def randomized_question_generator(
        question_pool,
        no_questions,
        with_replacement=False
):
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
            yield random.choice(sorted(question_pool.items()))
    else:
        no_questions = min(len(question_pool), no_questions)
        chosen_questions = random.sample(sorted(question_pool.items()), no_questions)
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
