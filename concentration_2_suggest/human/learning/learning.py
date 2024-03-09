from learning.agent import Agent

import random
import numpy as np

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

from util import constants

class Qlearning():
    
    def __init__(self, final_Q, env, experimental_condition, state_space, action_space, states, actions, epsilon, alpha, gamma):
        """
        Initializes the Q table and Q-Learning parameters.
        
        Parameters:
            final_Q (array): The q-table trained
            env (object): The game environment.
            experimental_condition (int): The type of robot that's gonna help the user.
            state_space (int): The number of states in the environment.
            action_space (int): The number of actions available in the environment.
            states (array of string): The name of states
            actions (array of string): The name of actions
            epsilon (float): The probability of choosing a random action during exploration.
            alpha (float): The learning rate.
            gamma (float): The discount factor.
            sentence_generator(object): the instance that provide sentences based on hint provided
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
        self.agent = Agent(env, experimental_condition)
        env.set_agent(self.agent)

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
                next_state = self.env.step(current_state, current_action, 
                                           self.actions[current_action], self.states[current_state])

                # S <- S'
                current_state = next_state

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

        # the number of attempts is not updated yet because it is needed for the reward
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
            deceptive_modes = [constants.DECEPTION]
            # if the agent has deceptive behavior then choose randomly if suggest row/col or card
            if self.agent.type in deceptive_modes and is_turn_odd is False:
                action = self.epsilon_greedy(state)
                if action == constants.SUGGEST_ROW or constants.SUGGEST_COL:
                    print("choose random action")
                    return action if random.choice([0, 1]) == 0 else constants.SUGGEST_CARD
                
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
    
   