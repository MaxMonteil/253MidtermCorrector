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

    def correctAnswer(self, *, student_answer, question_number):
        '''
        Checks if a student answer is correct and grades it.

        Parameters:
            student_answer <Answer> Answer object of the student
            question_number <int> Which question in the exam

        Return:
            <float> Returns the grade for this question
        '''

        # Makes a tuple with the number of correct student answers
        # ex: (1, 2)
        correct_answers = tuple(
                len(a.intersection(student_answer.answers))
                for a in self.answers)

        wrong_answers = tuple(self.number_of_choices - a for a in self.answers)

        correct_point_weight = 1/len(self.answers)
        incorrect_point_weight = 1/(self.number_of_choices - len(self.answers))

        # Gets the grade for the question based on correct and incorrect
        # answers into a list, it then takes the option that gives the highest
        # score
        grade = max(list(zip(
            correct_answers * correct_point_weight,
            wrong_answers * incorrect_point_weight)))

        return grade


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

    def __init__(
            self, *, values, question_number, number_of_choices=0, points=5,
            ignore_answer_mark='*'):
        self.number_of_choices = number_of_choices
        self.question_number = question_number
        self.points = points
        self.ignore_answer_mark = ignore_answer_mark

        # if there is a value to ignore (has a *) splice it out of values
        _ = values.find(self.ignore_answer_mark)
        new_values = values[:_] + values[_ + 3:] if _ == -1 else values

        self.answers = [set(v.split(',')) for v in new_values.split('|')]
