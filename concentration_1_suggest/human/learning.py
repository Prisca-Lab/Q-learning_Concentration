import json
import requests
import numpy as np

from socket import *

from player import Player
from agent import Agent
from game import Game

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

import constants
from util import Util
from plotting import Plotting

# init instances
player = Player()
agent = Agent()
game = Game()

# in order to have a different directory of plots for each user who's gonna play
user_number = Util.get_user_number()
Util.create_directory_for_plots(1, user_number)

# read ip and port from config file
data_file = Util.get_from_json_file("config")
serverName = data_file['ip']
serverPort = int(data_file['port'])

# read final epsilon from robot training file
epsilon_param = Util.get_from_json_file("greedy")

# create TCP socket
clientSocket = socket(AF_INET, SOCK_STREAM)

# connect socket to remote server at (serverName, serverPort)
clientSocket.connect((serverName, serverPort))

# Read from file the Q-table of robot training
Q = Util.get_Q_table_from_file()
print(Q)

# define robot's action
actions = ['none', 'suggest_row_or_column', 'suggest_card']

# define states: {user_state X robot_last_action X game_state}
states = [
    'INIT_STATE',
    'NONE_BEGIN_CORRECT',
    'NONE_BEGIN_WRONG',
    'RC_BEGIN_CORRECT',
    'RC_BEGIN_WRONG',
    'CARD_BEGIN_CORRECT',
    'CARD_BEGIN_WRONG',
    'NONE_MIDDLE_CORRECT',
    'NONE_MIDDLE_WRONG',
    'RC_MIDDLE_CORRECT',
    'RC_MIDDLE_WRONG',
    'CARD_MIDDLE_CORRECT',
    'CARD_MIDDLE_WRONG',
    'NONE_END_CORRECT',
    'NONE_END_WRONG',
    'RC_END_CORRECT',
    'RC_END_WRONG',
    'CARD_END_CORRECT',
    'CARD_END_WRONG'
]

EPISODES = constants.EPISODES_WITH_HUMAN
PAIRS = 12

# Keeps track of useful statistics
stats = Plotting.EpisodeStats(
    episode_lengths = np.zeros(EPISODES),
    episode_rewards = np.zeros(EPISODES),
    episode_click_until_match = np.zeros(PAIRS),
    avg_of_moves_until_match = np.zeros(PAIRS),
    avg_of_suggests_in_specific_episode = np.zeros(PAIRS),
    avg_of_suggests_after_some_episode = np.zeros(PAIRS)
)


def training():
    # define training parameters
    DISCOUNT_FACTOR = 0.8
    LEARNING_RATE = 0.96
    epsilon = epsilon_param['epsilon']  # get last epsilon value (after 100k episodes done by agent) from file

    for episode in range(EPISODES):

        game.start_game(player, clientSocket)

        # initialize S
        current_state = constants.INIT_STATE

        # for each step of episode
        while state_is_not_terminal():
            # Choose A from S using policy derived from Q (e.g., "epsilon-greedy")
            current_action = select_action(current_state, epsilon)

            # Take action A, observe R, S'
            next_state, reward = step(current_state, current_action)

            # update statistics
            Plotting.update_stats(stats, episode, reward, current_action, player, game, Plotting.HUMAN_PLAYER)

            # Update Q
            Q[current_state, current_action] = Q[current_state, current_action] \
                                               + LEARNING_RATE \
                                               * (reward + DISCOUNT_FACTOR
                                               * np.max(Q[next_state, :]) - Q[current_state, current_action])

            # S <- S'
            current_state = next_state

        print("Episode:", episode)
        # epsilon decay
        epsilon = get_new_epsilon(episode)

        # print stats
        print_stats(episode)

    # save new Q-table into the file in order to use that for other human players
    Util.save_Q_table_into_file(Q)
    # save epsilon for the same reason
    Util.save_epsilon_into_file(epsilon)
    # print final table
    print(Q)
    # send msg to server in order to close the connection for both server and client
    close_connection()


def select_action(state, epsilon):
    """
    define an epsilon greedy algorithm that will choose which action to take next
    """

    is_turn_odd = game.get_turn % 2 != 0
    is_pairs_zero = player.get_pairs < 1
    
    if is_pairs_zero or is_turn_odd:
        return constants.SUGGEST_NONE
    else:
        if np.random.random() < epsilon:
            return np.random.randint(3)
        else:
            return np.argmax(Q[state, :])


def step(state, action):
    """
    Take an action and return next state and reward
    """

    # debug
    print("Turn", game.get_turn)
    print("Current action: ", actions[action])
    print("Current state: ", states[state])

    suggest, card, position = agent.take_action(action, game)

    # send suggest to flask server
    send_suggest_through_socket(
        suggest,    # send which suggest(card, row, column)
        card,       # send which card (if suggest is card, otherwise None)
        position,   # send card position([n,n] if suggest card, [n, -1] if row, [-1, n] otherwise)
    )

    # blocking recv: wait until user click a card
    game.update_state_of_game(player, clientSocket)

    next_state = agent.get_next_state(action, game.get_face_up_cards, 
                                      player.get_pairs, player.get_last_pair_was_correct)

    reward = agent.get_reward(state, action, player, game)

    return next_state, reward


def send_suggest_through_socket(suggest, card, position):
    if suggest != "none":
        json_data = ({
            "action": {
                "suggest": suggest,
                "card": card,
                "position": position
            }
        })
        requests.post("http://" + serverName + ":5000", json=json_data)


def state_is_not_terminal():
    return player.get_pairs != 12


def get_new_epsilon(episode):
    START_EPSILON = 1.0   # Probability of random action
    EPSILON_TAPER = 0.01  # How much epsilon is adjusted each step
    
    return START_EPSILON / (1.0 + episode * EPSILON_TAPER)

def close_connection():
    json_data = { "connection": "close" }
    requests.post("http://" + serverName + ":5000", json=json_data)
    clientSocket.close()

##################################################################################################################
#                                                   PLOT                                                         #
##################################################################################################################


def print_stats(episode):
    print("end of episode n.", episode)

    if episode == EPISODES - 1:
        # total turns for each episode
        avg_turn = Util.get_cumulative_avg(stats.episode_lengths, episode)
        Plotting.save_stats(avg_turn, Plotting.AVERAGE_EPISODE_LENGTH, episode, Plotting.HUMAN_PLAYER, user_number)

        # average suggest for very pair for each episode
        tmp = Util.get_avarage(stats.avg_of_suggests_after_some_episode, 12, episode)
        Plotting.save_stats(tmp, Plotting.AVERAGE_OF_ACTIONS_TAKEN, episode, Plotting.HUMAN_PLAYER, user_number)

        # total reward for each episode
        avg_rewards = Util.get_cumulative_avg(stats.episode_rewards, episode)
        Plotting.save_stats(avg_rewards, Plotting.AVERAGE_EPISODE_REWARDS, episode, 
                            Plotting.HUMAN_PLAYER, user_number)

        # average turn for each pair
        avg_turn_for_pair = Util.get_avarage(stats.avg_of_moves_until_match, 12, episode)
        Plotting.save_stats(avg_turn_for_pair, Plotting.AVERAGE_OF_TURNS_FOR_MATCH, episode, 
                            Plotting.HUMAN_PLAYER, user_number)

    # average suggest for every pair of specific episode
    Plotting.save_stats(stats.avg_of_suggests_in_specific_episode, Plotting.ACTION_TAKEN_IN_SPECIFIC_EPISODE, 
                        episode, Plotting.HUMAN_PLAYER, user_number)

    # number of click until pair is founded
    Plotting.save_stats(stats.episode_click_until_match, Plotting.NUMBER_OF_CLICK_UNTIL_MATCH, 
                        episode, Plotting.HUMAN_PLAYER, user_number)


training()
