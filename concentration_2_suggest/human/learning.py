from player import Player
from agent import Agent
from game import Game

import requests
import random
import numpy as np
import pandas as pd

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

import constants

class Qlearning():
    
    def __init__(self, final_Q, env, robot_type, state_space, action_space, states, actions, epsilon, alpha, gamma):
        """
        Initializes the Q table and Q-Learning parameters.
        
        Parameters:
            final_Q (array): The q-table trained
            env (object): The game environment.
            robot_type (int): The type of robot that's gonna help the user.
            state_space (int): The number of states in the environment.
            action_space (int): The number of actions available in the environment.
            states (array of string): The name of states
            actions (array of string): The name of actions
            epsilon (float): The probability of choosing a random action during exploration.
            alpha (float): The learning rate.
            gamma (float): The discount factor.
        """
        self.action_space = action_space
        self.state_space = state_space
        self.Q = final_Q
        self.epsilon = epsilon
        self.gamma = gamma
        self.alpha = alpha
        self.states = states
        self.actions = actions
        self.env = env
        self.agent = Agent(env, robot_type)

    def training(self, number_episodes):
        """
        The Q-Learning agent.

        Parameters:
            max_episode (int): how many games the agent will play
        """
        for episode in range(number_episodes):
            self.env.start()

            # initialize S
            current_state = constants.INIT_STATE

            # for each step of episode
            while self.env.is_game_finished() is False: 
                # Choose A from S using policy derived from Q
                current_action = self.select_action(current_state)

                # Take action A, observe R, S'
                next_state = self.step(current_state, current_action)

                # S <- S'
                current_state = next_state
                
            print("Episode:", episode)

    def select_action(self, state):
        """
        Selects the best action for the given state based on the Q table.
        
        Parameters:
            state (int): The current state.
        
        Returns:
            int: The selected action.
        """
        
        is_turn_less_than_seven = self.env.get_turn() < 7
        is_turn_odd = self.env.get_turn() % 2 != 0
        clicks_until_match = self.env.get_flip_number()
        pairs = self.env.get_pairs_found()

        # the number of attempts is not yet updated because it is needed for the reward
        # therefore, if the user has found a pair we set the copy of the number of attempts to zero 
        if self.env.was_last_move_a_match() and is_turn_odd:
            clicks_until_match = 0

        if is_turn_less_than_seven:
            return constants.SUGGEST_NONE
        # the agent can't provide a suggestion for the first card until 4 turn have been passed
        elif is_turn_odd and clicks_until_match < 4 and pairs > 0:
            return constants.SUGGEST_NONE
        elif is_turn_odd and clicks_until_match < 10 and pairs == 0:
            return constants.SUGGEST_NONE
        else:
            if self.agent.type == constants.DECEPTION and is_turn_odd is False:
                action = self.epsilon_greedy(state)
                if action == constants.SUGGEST_ROW or constants.SUGGEST_COL:
                    print("choose random action")
                    # choose randomly if the agent should provide row/column suggestion or card suggestion
                    return action if random.choice([0, 1]) == 0 else constants.SUGGEST_CARD
                else:
                    return action 
            else:
                return self.epsilon_greedy(state)

    def epsilon_greedy(self, state):
        """
        Selects an action using the epsilon-greedy algorithm.
        N.B epsilon is completely greedy
        
        Parameters:
            state (int): The current state.
        
        Returns:
            int: The selected action.
        """
        return np.argmax(self.Q[state, :])
    
    def step(self, state, action):
        """
        Takes a step in the environment using the selected action.
        
        Parameters:
            state (int): The current state.
            action (int): The selected action.
        
        Returns:
            tuple: The next state, reward, and done flag.
        """

        # debug
        print("Turn", self.env.get_turn())
        print("Current action: ", self.actions[action])
        print("Current state: ", self.states[state])

        open_card = self.env.get_current_open_card()
        suggestion = self.agent.take_action(action)
        print("suggestion", suggestion)

        suggest, card, position = suggestion
        
        if self.agent.type == constants.DECEPTION and open_card != card and open_card != '':
            # it must suggest the open card
            card = open_card

        if self.agent.type != constants.NO_TOM:
            flag_ToM, flag_suggestion = self.agent.get_flag_for_ToM(suggest, card, position)
        else:
            flag_ToM = -1
            flag_suggestion = 0        

        # send suggest to flask server
        self.send_suggest_through_socket(
            suggest,        # send which suggestion(card, row, column)
            card,           # send which card (if suggestion is card, otherwise None)
            position,       # send card position([n,n] if suggest card, [n, -1] if row, [-1, n] otherwise)
            self.agent.type,     
            flag_ToM,       # check doc in self.agent.get_flag_for_ToM(suggest, card, position)
            flag_suggestion # 0 for no ToM, 1 for suggestion on first card, 2 otherwise
        )


        self.env.update_environment()

        next_state = self.agent.get_next_state(action)

        return next_state

    def send_suggest_through_socket(self, suggestion, card, position, robot_type, flag_ToM, flag_suggestion):
        if robot_type == constants.TOM:
            robot_type ='ToM'
        elif robot_type == constants.NO_TOM:
            robot_type = 'noToM'
        else:
            robot_type = 'deception'
            
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
        requests.post("http://" + self.env.get_server_name() + ":5000", json=json_data)
