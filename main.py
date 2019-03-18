#!/usr/bin/env python

'''
Main driver to correct a 253 midterm exam.
'''


import json
from pathlib import Path

# CONSTANTS
CONFIG_PATH = Path('./exam_corr.cfg')


def main():
    config = configurator()

    if config:
        print(config)


def configurator():
    '''
    Reads the configuration file and returns the path to the exam files.

    :param config_path: <str> Path to configuration file
    :return: <dict> Returns the path to the answer key and student answer files
             <bool> False if there was an error with the config file
    '''

    config = {
            'answer_key': '',
            'student_answers': ''
            }

    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)

        # check that the config dict only has the proper keys
        if all((v in config for v in ['answer_key', 'student_answers'])):
            return config
        else:
            return False

    except FileNotFoundError:
        print('Configuration file not found.')
        print('Creating one, please fill in the path to the proper files.')

        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f)


if __name__ == '__main__':
    main()
