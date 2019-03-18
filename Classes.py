#!/usr/bin/env python

'''
Midterm corrector classes

    Classes:
        AnswerKey: Entire answer key of the exam
        Student: A student and the collection of their answers
        Answer: Exam answers, from student or answer key
'''


class AnswerKey:
    '''
    The Answer Key class serves to offer a simpler way to deal with student
    answers by correcting and scoring them.

    Parameters:
        answer_key <path> Path to the text file with the answer key
    '''

    def __init__(self, answer_key):
        self.answers = self.buildAnswerKey(answer_key)

    def buildAnswerKey(self, answer_key):
        '''
        Reads the answer key file and builds up the list of exam answers.

        Parameters:
            answer_key <path> Path to the answer key file

        Return:
            <dict> Dictionary mapping question number to answer
        '''

        with open(answer_key, 'r') as ak:
            ak_lines = ak.readlines()

        answers = {}
        for index, line in enumerate(ak_lines, start=1):
            token = line.split('|', 1)
            answers[index] = Answer(question_number=index,
                                    number_of_choices=token[0],
                                    values=token[1])

        return answers

    def correctAnswer(self, *, question_number, student_answer):
        '''
        Checks if a student answer is correct and grades it.

        Parameters:
            student_answer <Answer> Answer object of the student
            question_number <int> Which question in the exam

        Return:
            <float> Returns the grade for this question
        '''

        question = self.answers[question_number]
        answers = student_answer.answers[0]

        # Gives a tuple with the scores the student got for each of the
        # possible answers to the question
        correct = tuple(len(key & answers) * 1/len(key)
                        for key in question.answers)

        # This gives a tuple with the grade deduction for the number of wrong
        # answers the student chose
        incorrect = tuple(
                len(answers - key) * -1/(question.number_of_choices - len(key))
                for key in question.answers)

        # Zip the correct and incorrect answers together into a tuple and
        # choose the pair where the student had the most correct answers.
        # From that pair return the sum of the grades for correct answers and
        # incorrect ones
        return sum(max(tuple(zip(correct, incorrect))))


class Student:
    '''

    Attributes:
        id <str> Unique student ID
    '''
    pass


class Answer:
    '''
    An Answer is a line from the Answer Key file or a student's answer to a
    question.

    Parameters:
        values             <str> String literal of answer
        question_number    <int> Number of the question in the exam
        number_of_choices  <int> How many answer options the question has
        points             <int> The maximum grade possible on this question
        ignore_answer_mark <str> The character to mark an answer to ignore
    '''

    def __init__(self, *, values, question_number, number_of_choices=0,
                 points=5, ignore_answer_mark='*'):
        self.number_of_choices = number_of_choices
        self.question_number = question_number
        self.points = points
        self.ignore_answer_mark = ignore_answer_mark

        # if there is a value to ignore (has a *) splice it out of values
        _ = values.find(self.ignore_answer_mark)
        new_values = values[:_] + values[_ + 3:] if _ == -1 else values

        self.answers = [set(v.split(',')) for v in new_values.split('|')]
