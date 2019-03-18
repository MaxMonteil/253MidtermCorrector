#!/usr/bin/env python

'''
Main driver to correct a 253 midterm exam.
'''


from Classes import AnswerKey, Class, Configurator
from pathlib import Path
import json

# CONSTANTS
CONFIG_PATH = Path('./exam_corr.cfg')


def main():
    config = Configurator(CONFIG_PATH)

    if not config:
        return

    answerKey = AnswerKey(config.ANSWER_KEY)
    students = Class(config.STUDENT_ANSWERS)

    exam_grades = gradeExam(answerKey, students)

    writeAllGrades(config.ALL_GRADES, exam_grades)

    return exam_grades


def writeAllGrades(file_path, all_grades):
    '''
    Writes all the student grades to a json file.

    Parameters:
        file_path  <Path> Path to output file
        all_grades <dict> All the grades for the exam
    '''

    output = {}

    for student_id, final_grade in all_grades.items():
        output[student_id] = final_grade[-1]

    with open(file_path, 'w') as out:
        json.dump(output, out, indent=4)


def gradeExam(answerKey, students, output_file=None):
    '''
    Grades the entire exam for all given students.

    Parameters:
        answerKey <AnswerKey> The exam's answer key
        students  <Class> A Class object that contains all students
        output_file <Path> Optional If given is the path to output all grades

    Returns:
        <dict> Mapping of student ID to all their grades for the exam
    '''

    exam_grades = {}
    for student in students.students:
        float_answers = answerKey.correctStudentExam(student)
        float_answers.append(sum(float_answers))
        exam_grades[student.student_id] = float_answers

    if output_file:
        with open(output_file, 'w') as out:
            for student_id, grades in exam_grades.items():
                str_answers = [str(grade) for grade in grades]

                out.write(student_id)
                out.write(f'|{"|".join(str_answers)}\n')

    return exam_grades


if __name__ == '__main__':
    main()
