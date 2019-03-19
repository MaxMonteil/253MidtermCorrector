#!/usr/bin/env python

'''
Midterm corrector classes

    Classes:
        AnswerKey: Entire answer key of the exam
        Student: A student and the collection of their answers
        Answer: Exam answers, from student or answer key
'''

from pathlib import Path
import json


class AnswerKey:
    '''
    The Answer Key class serves to offer a simpler way to deal with the exam
    answer key by correcting and scoring student answers.

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
            ak_lines = [line.strip('\n') for line in ak]

        answers = {}
        for index, line in enumerate(ak_lines, start=1):
            token = line.split('|', 1)
            answers[index] = Answer(question_number=index,
                                    number_of_choices=token[0],
                                    values=token[1])

        return answers

    def correctStudentExam(self, student):
        '''
        Takes a student and corrects all their answers for the exam.

        Parameters:
            student <Student> A Student whose exam will be corrected

        Return:
            <list> An ordered list of their grade for each question
        '''

        return [self.correctAnswer(answer)
                for answer in student.answers.values()]

    def correctAnswer(self, student_answer):
        '''
        Checks if a student answer is correct and grades it.

        Parameters:
            student_answer <Answer> Answer object of the student
            question_number <int> Which question in the exam

        Return:
            <float> Returns the grade for this question
        '''

        question = self.answers[student_answer.question_number]
        answers = student_answer.answers[0]

        # Gives a tuple with the scores the student got for each of the
        # possible answers to the question
        correct = tuple(len(key & answers) * 1/len(key)
                        for key in question.answers)

        # This gives a tuple with the grade deduction for the number of wrong
        # answers the student chose
        incorrect = tuple(
                len(answers - key) * -1/(question.number_of_choices - len(key))
                if question.number_of_choices != len(key)
                else 0
                for key in question.answers)

        # Zip the correct and incorrect answers together into a tuple and
        # choose the pair where the student had the most correct answers.
        # From that pair return the sum of the grades for correct answers and
        # incorrect ones
        # Multiply to the total number of points to get the grade
        # Finally if the result is negative it means the student only chose
        # wrong answers and thus they get 0
        grade = max(round(sum(max(tuple(zip(correct, incorrect)))) *
                          question.points, 2), 0.0)

        student_answer.grade = grade

        return grade


class Class:
    '''
    Class in charge of managing and initializing all the students.

    Parameters:
        students_answers_file <path> Path to the student answers file
    '''

    def __init__(self, students_answers_file):
        self.students = self.createStudents(students_answers_file)

    def createStudents(self, students_answers_file):
        '''
        Reads each line of the student answer file and creates a list of
        students.

        Parameters:
            students_answers_file <path> Path to the student answers file

        Return:
            <list> A list of Student objects
        '''

        with open(students_answers_file, 'r') as sa:
            sa_lines = [line.strip('\n') for line in sa]

        return [Student(student_id=line[0], answers=line[1])
                for line in (line.split('|', 1) for line in sa_lines)]


class Student:
    '''
    Class to manage the student answers and identity.

    Parameters:
        answers    <str> String of all the student's answers ex: a,b|a|...
        student_id <str> Unique id code for the student
    '''

    def __init__(self, *, answers, student_id):
        self.student_id = student_id
        self.answers = self.buildStudentAnswers(answers.split('|'))

    def buildStudentAnswers(self, answers):
        '''
        Creates the Answers dictionary from the answers tokenized list.

        Parameters:
            answers <list> Token list of all the student's answers
                           ex:['a,b', 'a']

        Return:
            <dict> Dictionary mapping question number to student's answer
        '''

        return {q_num: Answer(question_number=q_num, values=answer)
                for (q_num, answer) in enumerate(answers, start=1)}


class Answer:
    '''
    An Answer is a line from the Answer Key file or a student's answer to a
    question.

    Parameters:
        values             <str> String literal of answer
        question_number    <int> Number of the question in the exam
        number_of_choices  <int> How many answer options the question has
        points             <int> The maximum grade possible on this question
        grade              <int> Grade obtained on this question
        ignore_answer_mark <str> The character to mark an answer to ignore
    '''

    def __init__(self, *, values, question_number, number_of_choices=0,
                 points=5, ignore_answer_mark='*'):
        self.values = values
        self.question_number = int(question_number)
        self.number_of_choices = int(number_of_choices)
        self.points = points
        self.grade = 0
        self.ignore_answer_mark = ignore_answer_mark

        # if there is a value to ignore (has a *) splice it out of values
        _ = values.find(self.ignore_answer_mark)
        new_values = values[:_] + values[_ + 3:] if _ != -1 else values

        self.answers = [set(v.split(',')) for v in new_values.split('|')]

    def __repr__(self):
        return '|'.join(','.join(answer) for answer in self.answers)


class Configurator:
    '''
    Reads the configuration file and gives access to all needed paths.

    Parameters:
        config_path <str> Path to configuration file

    Attributes:
        default_config <dict> The default state of the config file

    Exposed Paths:
        ANSWER_KEY
        STUDENT_ANSWERS
        RAW_GRADES
        ALL_GRADES
        Q_STATS
        CLASS_STATS
    '''

    default_config = {
            'answer_key': '',
            'student_answers': '',
            'out_dir': ''
            }

    def __init__(self, config_path):
        config = self.loadConfig(config_path)

        if config:
            out_dir = Path(config['out_dir'])
        else:
            print('There is an error with the configuration file.')
            print('Please ensure it is valid')
            return None

        if not out_dir.exists():
            Path.mkdir(out_dir, exist_ok=True)

        self.OUT_DIR = out_dir
        self.ANSWER_KEY = config['answer_key']
        self.STUDENT_ANSWERS = config['student_answers']
        self.RAW_GRADES = Path.joinpath(out_dir, 'RawGrades.txt')
        self.ALL_GRADES = Path.joinpath(out_dir, 'AllGrades.json')
        self.Q_STATS = Path.joinpath(out_dir, 'qstats.json')
        self.CLASS_STATS = Path.joinpath(out_dir, 'classstats.json')

    def loadConfig(self, config_path):
        '''
        Loads the json data in the config file and verifies its validity. If
        the file does not exist it will create one in the working directory and
        prompt the user to fill it out.

        Parameters:
            config_path <Path> Path to the configuration file
        '''
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            # check that the config dict only has the proper keys
            if all((k in config for k in
                    ['answer_key', 'student_answers', 'out_dir'])):
                return config
            else:
                return False

        except FileNotFoundError:
            print('Configuration file not found.')
            print('Creating one, please fill in the path to the proper files.')

            with open(config_path, 'w') as f:
                json.dump(self.default_config, f, indent=4)
