#!/usr/bin/env python

'''
Main driver to correct a 253 midterm exam.
'''


from Classes import AnswerKey, Class, Configurator
from pathlib import Path
from statistics import mean, median, mode
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

    # writeAllGrades(config.ALL_GRADES, exam_grades)
    # writeIndividualStats(config.OUT_DIR, exam_grades, students)
    # writeClassStats(config.CLASS_STATS, exam_grades)
    writeQuestionStats(config.Q_STATS, exam_grades)

    return exam_grades


def writeQuestionStats(file_path, all_grades):
    '''
    Builds an array of the stats of each question in an exam.

    Parameters:
        file_path  <Path> Path to output file
        all_grades <dict> All the grades for the exam
    '''

    # Transposes the all_grades list of grades by student matrix into a list of
    # grades by question
    # Remove the last one since it contains the students total grades
    grades_by_question = [list(q) for q in zip(*all_grades.values())][:-1]

    quartiles = ()

    def memoizedQuartiles(q_list=None):
        nonlocal quartiles
        if q_list:
            quartiles = getQuartiles(q_list)

        return quartiles

    questions_stats = [{
            'Q': index,
            'Min': min(question),
            'FirstQuartile': memoizedQuartiles(q_list=question)[0],
            'Mean': mean(question),
            'Median': median(question),
            'ThirdQuartile': memoizedQuartiles()[1],
            'Max': max(question),
            'Mode': mode(question)
        }
        for index, question in enumerate(grades_by_question, start=1)]

    with open(file_path, 'w') as out:
        json.dump(questions_stats, out, indent=4)


def writeClassStats(file_path, all_grades):
    '''
    Writes the class statistics for the exam to a json file.

    Parameters:
        file_path  <Path> Path to output file
        all_grades <dict> All the grades for the exam
    '''

    final_grades = [grade[-1] for grade in all_grades.values()]
    firstQ, thirdQ = getQuartiles(final_grades)

    with open(file_path, 'w') as out:
        json.dump({
                'Min': min(final_grades),
                'FirstQuartile': firstQ,
                'Mean': mean(final_grades),
                'Median': median(final_grades),
                'ThirdQuartile': thirdQ,
                'Max': max(final_grades),
                'Mode': mode(final_grades)
            }, out, indent=4)


def writeIndividualStats(out_path, all_grades, students):
    '''
    Creates files for each student with a rundown of how they did for each
    question.

    Parameters:
        all_grades <dict>  All the grades for the exam
        students   <Class> Collection of all the students
    '''

    output = {}

    for student in students.students:
        output[student.student_id] = [
                {
                    'QuestionNumber': answer.question_number,
                    'StudentAnswer': answer.values
                }
                for answer in student.answers.values()
                if answer.grade < answer.points]

    for student_id in output:
        with open(Path.joinpath(out_path, f'{student_id}.json'), 'w') as f:
            json.dump(output[student_id], f, indent=4)


def writeAllGrades(file_path, all_grades):
    '''
    Writes all the student grades to a json file.

    Parameters:
        file_path  <Path> Path to output file
        all_grades <dict> All the grades for the exam
    '''

    output = []

    for student_id, final_grade in all_grades.items():
        output.append({
            'SafeToken': student_id,
            'Grade': final_grade[-1]
            })

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


def getQuartiles(n_list):
    '''
    Calculates the first and third quartiles of a number list.

    Parameters:
        n_list <list> List of numbers

    Returns:
        <tuple> Returns a tuple pair of the first and third list quartiles
    '''

    sorted_list = sorted(n_list)

    length = len(sorted_list)
    mid = length // 2

    if length % 2 == 0:
        firstQ = median(sorted_list[:mid])
        thirdQ = median(sorted_list[mid:])
    else:
        firstQ = median(sorted_list[:mid])
        thirdQ = median(sorted_list[mid+1:])

    return firstQ, thirdQ


if __name__ == '__main__':
    main()
