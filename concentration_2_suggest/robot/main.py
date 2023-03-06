import numpy as np

from learning import Qlearning
from environment import Environment

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

import constants
from plotting import Plotting
from util import Util

# define robot's action
actions = ['none', 'suggest_row', 'suggest_col', 'suggest_card']

# define states: {robot_last_action X game_state X user_state}
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

    '(sugg_col, beg, f_correct)',
    '(sugg_col, beg, f_wrong)',
    '(sugg_col, mid, f_correct)',
    '(sugg_col, mid, f_wrong)',
    '(sugg_col, end, f_correct)',
    '(sugg_col, end, f_wrong)',

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

    '(sugg_col, beg, s_correct)',
    '(sugg_col, beg, s_wrong)',
    '(sugg_col, mid, s_correct)',
    '(sugg_col, mid, s_wrong)',
    '(sugg_col, end, s_correct)',
    '(sugg_col, end, s_wrong)',

    '(sugg_card, beg, s_correct)',
    '(sugg_card, beg, s_wrong)',
    '(sugg_card, mid, s_correct)',
    '(sugg_card, mid, s_wrong)',
    '(sugg_card, end, s_correct)',
    '(sugg_card, end, s_wrong)',
]

# define the number of games that the agent will plays
EPISODES = constants.NUMBER_EPISODES

# define number of pair that user need to find
PAIRS = 12

# Keeps track of useful statistics
stats = Plotting.EpisodeStats(
    episode_lengths = np.zeros(EPISODES),
    episode_rewards = np.zeros(EPISODES),
    episode_click_until_match = np.zeros(PAIRS),
    avg_of_moves_until_match = np.zeros(PAIRS),
    avg_of_suggests_in_specific_episode = np.zeros(PAIRS),
    avg_of_suggests_after_some_episode = np.zeros(PAIRS),
    avg_of_suggests_first_card_over_time = np.zeros(PAIRS)
)

# create directory for plots if it doesn't exists
Util.create_directory_for_plots()

#create environment 
env = Environment()

# parameters setting
epsilon = 1.0
alpha = 0.1
gamma = 0.8

# start with training
Q = Qlearning(stats, env, len(states), len(actions), states, actions, epsilon, alpha, gamma)
Q.training(EPISODES)