import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

from util import Util

# define robot's action
actions = ['none', 'suggest_row_col', 'suggest_card']

# define states: {user_state X robot_last_action X game_state}
states = [
    'INIT_STATE',

    '(no_help, beg, f_correct)',
    '(no_help, beg, f_wrong)',
    '(no_help, mid, f_correct)',
    '(no_help, mid, f_wrong)',
    '(no_help, end, f_correct)',
    '(no_help, end, f_wrong)',

    '(sugg_row, beg, f_correct)',
    '(sugg_row, beg, f_wrong)',
    '(sugg_row, mid, f_correct)',
    '(sugg_row, mid, f_wrong)',
    '(sugg_row, end, f_correct)',
    '(sugg_row, end, f_wrong)',

    '(sugg_card, beg, f_correct)',
    '(sugg_card, beg, f_wrong)',
    '(sugg_card, mid, f_correct)',
    '(sugg_card, mid, f_wrong)',
    '(sugg_card, end, f_correct)',
    '(sugg_card, end, f_wrong)',

    '(no_help, beg, s_correct)',
    '(no_help, beg, s_wrong)',
    '(no_help, mid, s_correct)',
    '(no_help, mid, s_wrong)',
    '(no_help, end, s_correct)',
    '(no_help, end, s_wrong)',

    '(sugg_row, beg, s_correct)',
    '(sugg_row, beg, s_wrong)',
    '(sugg_row, mid, s_correct)',
    '(sugg_row, mid, s_wrong)',
    '(sugg_row, end, s_correct)',
    '(sugg_row, end, s_wrong)',

    '(sugg_card, beg, s_correct)',
    '(sugg_card, beg, s_wrong)',
    '(sugg_card, mid, s_correct)',
    '(sugg_card, mid, s_wrong)',
    '(sugg_card, end, s_correct)',
    '(sugg_card, end, s_wrong)',
]

# parameters setting
epsilon_param = Util.get_from_json_file("greedy")   # read final epsilon from robot training file
epsilon = epsilon_param['epsilon']                  # get last epsilon value (after 100k episodes done by agent) from file
alpha = 0.95
gamma = 0.8