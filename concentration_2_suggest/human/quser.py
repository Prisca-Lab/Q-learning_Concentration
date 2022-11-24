from player import Player
from agent import Agent
from game import Game

import requests
import signal
import random
import numpy as np
import pandas as pd

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

import constants

class Q_User():
    # define robot's action
    __actions = ['none', 'suggest_row_or_column', 'suggest_card']

    # define states: {user_state X robot_last_action X game_state}
    __states = [
        'INIT_STATE',

        'FIRST_FLIPPING_NONE_BEGIN_CORRECT',
        'FIRST_FLIPPING_NONE_BEGIN_WRONG',
        'FIRST_FLIPPING_NONE_MIDDLE_CORRECT',
        'FIRST_FLIPPING_NONE_MIDDLE_WRONG',
        'FIRST_FLIPPING_NONE_END_CORRECT',
        'FIRST_FLIPPING_NONE_END_WRONG',

        'FIRST_FLIPPING_SUGGEST_RC_BEGIN_CORRECT',
        'FIRST_FLIPPING_SUGGEST_RC_BEGIN_WRONG',
        'FIRST_FLIPPING_SUGGEST_RC_MIDDLE_CORRECT',
        'FIRST_FLIPPING_SUGGEST_RC_MIDDLE_WRONG',
        'FIRST_FLIPPING_SUGGEST_RC_END_CORRECT',
        'FIRST_FLIPPING_SUGGEST_RC_END_WRONG',

        'FIRST_FLIPPING_SUGGEST_CARD_BEGIN_CORRECT',
        'FIRST_FLIPPING_SUGGEST_CARD_BEGIN_WRONG',
        'FIRST_FLIPPING_SUGGEST_CARD_MIDDLE_CORRECT',
        'FIRST_FLIPPING_SUGGEST_CARD_MIDDLE_WRONG',
        'FIRST_FLIPPING_SUGGEST_CARD_END_CORRECT',
        'FIRST_FLIPPING_SUGGEST_CARD_END_WRONG',

        'SECOND_FLIPPING_NONE_BEGIN_CORRECT',
        'SECOND_FLIPPING_NONE_BEGIN_WRONG',
        'SECOND_FLIPPING_NONE_MIDDLE_CORRECT',
        'SECOND_FLIPPING_NONE_MIDDLE_WRONG',
        'SECOND_FLIPPING_NONE_END_CORRECT',
        'SECOND_FLIPPING_NONE_END_WRONG',

        'SECOND_FLIPPING_SUGGEST_RC_BEGIN_CORRECT',
        'SECOND_FLIPPING_SUGGEST_RC_BEGIN_WRONG',
        'SECOND_FLIPPING_SUGGEST_RC_MIDDLE_CORRECT',
        'SECOND_FLIPPING_SUGGEST_RC_MIDDLE_WRONG',
        'SECOND_FLIPPING_SUGGEST_RC_END_CORRECT',
        'SECOND_FLIPPING_SUGGEST_RC_END_WRONG',

        'SECOND_FLIPPING_SUGGEST_CARD_BEGIN_CORRECT',
        'SECOND_FLIPPING_SUGGEST_CARD_BEGIN_WRONG',
        'SECOND_FLIPPING_SUGGEST_CARD_MIDDLE_CORRECT',
        'SECOND_FLIPPING_SUGGEST_CARD_MIDDLE_WRONG',
        'SECOND_FLIPPING_SUGGEST_CARD_END_CORRECT',
        'SECOND_FLIPPING_SUGGEST_CARD_END_WRONG'
    ]
    
    def __init__(self, client_socket, player, game, agent, server_name):
        self._client_socket = client_socket
        self._player = player
        self._game = game
        self._agent = agent
        self._server_name = server_name

    def user_play(self, Q, epsilon):
	    # print Q_table
        print("\n", pd.DataFrame(Q, self.__states, self.__actions))
        EPISODES = constants.EPISODES_WITH_HUMAN

        # choose the robot that's gonna help the user
        robot_type = self.choose_robot_type()
        print("\nrobot type:", robot_type)

        for episode in range(EPISODES):
            # create board game and init player's data
            self._game.start_game(self._player, self._client_socket)

            # initialize S
            current_state = constants.INIT_STATE

            # for each step of episode
            while self._game.is_game_ended() is not True:  
                # Choose A from S using policy derived from Q (e.g., "epsilon-greedy")
                current_action = self.select_action(Q, current_state, epsilon, robot_type)

                # Take action A, observe R, S'
                next_state = self.step(current_state, current_action, robot_type)

                # S <- S'
                current_state = next_state
                
            print("Episode:", episode)

        # send msg to server in order to close the connection for both server and client
        self.close_connection()

    def select_action(self, Q, state, epsilon, robot_type):
        """
        This function will return the best action to do in the current state.
        If the robot is faulty it will choose randomly between row/col and card suggestions.
        """
        
        is_turn_less_than_seven = self._game.get_turn < 7
        is_turn_odd = self._game.get_turn % 2 != 0
        clicks_until_match = self._player.get_number_of_clicks_for_current_pair
        pairs = self._player.get_pairs

        if self._player.get_last_pair_was_correct and is_turn_odd:
            clicks_until_match = 0

        if is_turn_less_than_seven:
            return constants.SUGGEST_NONE
        # the agent can't provide a suggestion for the first card until 4 turn have been passed
        elif is_turn_odd and clicks_until_match < 4 and pairs > 0:
            return constants.SUGGEST_NONE
        elif is_turn_odd and clicks_until_match < 10 and pairs == 0:
            return constants.SUGGEST_NONE
        else:
            if robot_type == 'faulty' and is_turn_odd is False:
                action = self.epsilon_greedy(Q, state, epsilon)
                if action == constants.SUGGEST_ROW_COLUMN:
                    print("choose random action")
                    # choose randomly if the agent should provide row/column suggestion or card suggestion
                    return action if random.choice([0, 1]) == 0 else constants.SUGGEST_CARD
                else:
                    return action 
            else:
                return self.epsilon_greedy(Q, state, epsilon)

    def epsilon_greedy(self, Q, state, epsilon):
        if np.random.random() < epsilon:
            return np.random.randint(3)
        else:
            return np.argmax(Q[state, :])
    
    def step(self, state, action, robot_type):
        """
        Take an action and return next state and reward
        """

        # debug
        print("Turn", self._game.get_turn)
        print("Current action: ", self.__actions[action])
        print("Current state: ", self.__states[state])

        open_card = self._game.get_current_open_card_name
        suggestion, card, position = self._agent.take_action(action, self._player, self._game, robot_type)

        if robot_type == 'faulty' and open_card != card and open_card != '':
            # it must suggest the open card
            card = open_card

        if robot_type != 'noToM':
            flag_ToM, flag_suggestion = self._agent.get_flag_for_ToM(suggestion, card, position, self._player, self._game)
        else:
            flag_ToM = -1
            flag_suggestion = 0        

        # send suggest to flask server
        self.send_suggest_through_socket(
            suggestion,     # send which suggestion(card, row, column)
            card,           # send which card (if suggestion is card, otherwise None)
            position,       # send card position([n,n] if suggest card, [n, -1] if row, [-1, n] otherwise)
            robot_type,     
            flag_ToM,       # 0 for no ToM, 1 for ToM with no history, 2 for ToM with 1 click, 3 for ToM with card seen multiple times
            flag_suggestion # 0 for no ToM, 1 for suggestion on first card, 2 otherwise
        )

        # blocking recv: wait until user click a card
        self._game.update_state_of_game(self._player, self._client_socket)

        next_state = self._agent.get_next_state(action, self._game.get_face_up_cards, self._game.get_turn,
                                        self._player.get_pairs, self._player.get_last_pair_was_correct)

        return next_state

    def send_suggest_through_socket(self, suggestion, card, position, robot_type, flag_ToM, flag_suggestion):
        json_data = ({
                "action": {
                    "suggestion": suggestion,
                    "card": card,
                    "position": position,
                    "robot_type": robot_type,
                    "flagToM": flag_ToM,
                    "flagSuggestion": flag_suggestion
                }
            })
        requests.post("http://" + self._server_name + ":5000", json=json_data)

    def close_connection(self):
        json_data = { "connection": "close" }
        requests.post("http://" + self._server_name + ":5000", json=json_data)
        self._client_socket.close()

    def choose_robot_type(self):
        # choose mod
        # 'noToM', 'ToM', 'faulty'
        type = 'faulty'
        # send mod to server
        json_data = { "robot_type": type }
        requests.post("http://" + self._server_name + ":5000", json=json_data)

        return type
