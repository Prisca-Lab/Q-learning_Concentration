import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))
from util import constants

from game.card import Card
from game.player import Player
from game.game import Game

class Environment:
    def __init__(self):
        self.__game = Game()
        self.__player = Player(self.__game)
        self.__reward_first_card = 0.4
        self.__has_suggests_for_the_first_card = False
        self._agent = None

    def __reset(self):
        self.__game.reset()
        self.__player.reset()
        self.__player.game = self.__game
        # in order to create the player history game must be initialized first
        self.__player.create_history()
        self.__reward_first_card = 0.4
        self.__has_suggests_for_the_first_card = False
        #self._agent = None

    def start(self):
        self.__reset()

    def get_player(self):
        return self.__player
    
    def set_agent(self, agent):
        self._agent = agent
    
    def get_game(self):
        return self.__game

    def get_turn(self):
        return self.__game.turns
    
    def get_pairs_found(self):
        return self.__player.pairs_found
    
    def get_flip_number(self):
        return self.__player.flip_number
    
    def play(self, suggestion):
        return self.__player.play(suggestion)
    
    def get_current_open_card(self):
        return self.__game.current_open_card_name
    
    def get_other_location(self, card):
        game_board = self.__game.board
        return Card.get_other_location_of_open_card(card, game_board)
    
    def get_cards_by_index(self, type, index):
        game_board = self.__game.board
        return Card.get_face_up_cards_by_index(type, index, game_board)
    
    def was_last_move_a_match(self):
        return self.__player.last_match
    
    def is_game_finished(self):
        return self.__game.is_game_ended()
    
    def print_player_history(self):
        self.__player.print_history()
    
    def get_least_clicked_location_of_most_clicked_card(self):
        history = self.__player.history

        return self.__game.get_least_clicked_location_of_most_clicked_pair(history)
    
    ##################################################################################################################
    #                                                 Step                                                           #
    ##################################################################################################################

    def step(self, state, action, action_string, state_string):
        """
        Takes a step in the environment using the selected action.
        
        Parameters:
            state (int): The current state.
            action (int): The selected action.
            action_string (str): The string associated with the selected action.
            state_string (str): The string associated with the current state.
        
        Returns:
            tuple: The next state, reward, and done flag.
        """
        # get suggestion based on action selected
        suggestion = self._agent.take_action(action)
        
        # click a card and follow the hint provided
        move = self.play(suggestion)
        
        next_state = self.get_next_state(action)

        reward = self.get_reward(action)
        
        # debug
        # print(f"Turn: {self.get_turn()}\n"
        #      f"Current action: {action_string}\n"
        #      f"Current state: {state_string}\n"
        #      f"Suggestion: {suggestion}\n"
        #      f"Clicked: {move}\n"
        #      f"Reward: {reward}\n")

        return next_state, reward

    ##################################################################################################################
    #                                                 State                                                          #
    ##################################################################################################################

    def get_next_state(self, action):
        """
        Returns the next state based on the current state and the agent's action.

        Parameters
        ----------
            action (int): the action the agent takes, represented by an integer code

        Returns
        ----------
            str: the name of the next state

        Raises
        ----------
            AttributeError: if the specified constant name doesn't exist in the constants module
        """

        pairs = self.get_pairs_found()
        is_turn_odd = ((self.get_turn() - 1) % 2) != 0
        is_turn_less_than_six = self.get_turn() - 1 < 6

        if is_turn_less_than_six and pairs == 0:
            return getattr(constants, 'INIT_STATE')

        state_suffix = "CORRECT" if self.was_last_move_a_match() else "WRONG"
        
        if pairs <= 3:
            if is_turn_odd:
                return self.__which_state([
                    self.get_constant('NO_HELP_BEG_S_', state_suffix),
                    self.get_constant('SUGG_ROW_BEG_S_', state_suffix),
                    self.get_constant('SUGG_COL_BEG_S_', state_suffix),
                    self.get_constant('SUGG_CARD_BEG_S_', state_suffix)],
                    action)
            else:
                return self.__which_state([
                    self.get_constant('NO_HELP_BEG_F_', state_suffix),
                    self.get_constant('SUGG_ROW_BEG_F_', state_suffix),
                    self.get_constant('SUGG_COL_BEG_F_', state_suffix),
                    self.get_constant('SUGG_CARD_BEG_F_', state_suffix)],
                    action)
            

        elif 3 < pairs < 8:
            if is_turn_odd:
                return self.__which_state([
                    self.get_constant('NO_HELP_MID_S_', state_suffix),
                    self.get_constant('SUGG_ROW_MID_S_', state_suffix),
                    self.get_constant('SUGG_COL_MID_S_', state_suffix),
                    self.get_constant('SUGG_CARD_MID_S_', state_suffix)],
                    action)
            else:
                return self.__which_state([
                    self.get_constant('NO_HELP_MID_F_', state_suffix),
                    self.get_constant('SUGG_ROW_MID_F_', state_suffix),
                    self.get_constant('SUGG_COL_MID_F_', state_suffix),
                    self.get_constant('SUGG_CARD_MID_F_', state_suffix)],
                    action)

        else:
            if is_turn_odd:
                return self.__which_state([
                    self.get_constant('NO_HELP_END_S_', state_suffix),
                    self.get_constant('SUGG_ROW_END_S_', state_suffix),
                    self.get_constant('SUGG_COL_END_S_', state_suffix),
                    self.get_constant('SUGG_CARD_END_S_', state_suffix)],
                    action)
            else:
                return self.__which_state([
                    self.get_constant('NO_HELP_END_F_', state_suffix),
                    self.get_constant('SUGG_ROW_END_F_', state_suffix),
                    self.get_constant('SUGG_COL_END_F_', state_suffix),
                    self.get_constant('SUGG_CARD_END_F_', state_suffix)],
                    action)

    @staticmethod
    def get_constant(constant_name, state_suffix):
        """
        Returns the value of the specified constant from the constants module, with the given suffix.

        Parameters
        ----------
            constant_name (str): the name of the constant
            state_suffix (str): the suffix to append to the constant name

        Returns
        ----------
            object: the value of the constant

        Raises
        ----------
            AttributeError: if the specified constant name doesn't exist in the constants module
        """
        return getattr(constants, constant_name + state_suffix)

    @staticmethod
    def __which_state(states, action):
        """
        Returns the correct state to transition to based on the last action.

        Parameters
        ----------
            states (List of strings): The possible states to transition to.
            action (int): The last action taken.

        Returns
        ----------
            String: The state to transition to based on the last action.
        """

        if action == constants.SUGGEST_NONE:
            return states[0]
        elif action == constants.SUGGEST_ROW:
            return states[1]
        elif action == constants.SUGGEST_COL:
            return states[2]
        else:
            return states[3]

    ##################################################################################################################
    #                                                 Reward                                                         #
    ##################################################################################################################
        
    def get_reward(self, action):
        """
        Returns a reward for the specified action, based on the current state of the environment.

        Parameters:
        ----------
            action: An integer representing the action taken by the agent.

        Returns:
        --------
            A floating point number representing the reward for the specified action.
        """
        clicks_until_match = self.get_flip_number()
        num_pairs_found = self.get_pairs_found()
        has_found_pair = self.was_last_move_a_match()
        is_turn_even = (self.get_turn() - 1) % 2 == 0

        # for the first six turns the agent can't provide any suggestion, thus the reward is 0
        # n.b the turn is not the current turn, but the next one
        if self.get_turn() < 7 and num_pairs_found == 0:
            return 0
        
        # suggestion for the first card
        if not is_turn_even and self.__should_suggest_for_first_card(clicks_until_match, num_pairs_found):
            return self.__get_reward_for_first_card(action)

        # reset reward for the first card if previous suggestion was not useful
        if is_turn_even and not has_found_pair and self.__has_suggests_for_the_first_card:
            self.__reset_reward_for_first_card()

        # If the agent provided a suggestion for the first card, they shouldn't suggest again
        if is_turn_even and has_found_pair and self.__has_suggests_for_the_first_card and action != constants.SUGGEST_NONE:
            self.__reset_reward_for_first_card()
            self.__has_suggests_for_the_first_card = False
            return 0
        
        # if the player has found a pair
        if has_found_pair and is_turn_even:
            return self.__get_reward_for_second_card(action, num_pairs_found, clicks_until_match)
        
        return 0
    
    def __should_suggest_for_first_card(self, clicks_until_match, pairs):
        """
        Determines if the agent should suggest a card for the first pick.

        Parameters:
        ----------
            clicks_until_match: An integer representing the number of clicks until a match is found.
            pairs: An integer representing the number of pairs found by the user.

        Returns:
        --------
            A boolean indicating whether the agent should suggest a card for the first flip.
        """
        threshold_with_pair = constants.CLICKS_UNTIL_MATCH_THRESHOLD_WITH_PAIR
        threshold_without_pair = constants.CLICKS_UNTIL_MATCH_THRESHOLD_WITHOUT_PAIR

        return (clicks_until_match > threshold_with_pair and pairs > 0) or\
                (clicks_until_match > threshold_without_pair and pairs == 0)
    
    def __reset_reward_for_first_card(self):
        """
        Resets the reward for the first card to its default value.
        """
        self.__reward_first_card = 0.4

    def __get_reward_for_first_card(self, action):
        """
        Calculates the reward for suggesting the first card.

        Parameters:
        -----------
            action (int): The action taken by the agent.

        Returns:
        -------
            float: The calculated reward.
        """
        if action != constants.SUGGEST_NONE:
            self.__has_suggests_for_the_first_card = True
        else:
            self.__has_suggests_for_the_first_card = False

        if action == constants.SUGGEST_ROW:
            self.__reward_first_card += 0.1
        elif action == constants.SUGGEST_COL:
            self.__reward_first_card += 0.2
        elif action == constants.SUGGEST_CARD:
            self.__reward_first_card += 0.3
        else:
            self.__reward_first_card += 0.4

        return self.__reward_first_card

    def __get_reward_for_second_card(self, action, pairs, clicks_until_match):
        """
        Calculates the reward for suggesting the second card.

        Parameters:
        ----------
            action (int): The action taken by the agent.
            pairs (int): The number of pairs already found.
            clicks_until_match (int): The number of clicks until the current match.

        Returns:
        ---------
            float: The calculated reward.
        """
        # reset boolean value cause the agent can suggest again for the first flip
        self.__has_suggests_for_the_first_card = False
        # reset the integer
        self.__reset_reward_for_first_card()

        # multiply the number of flip for the constants assigned based on the game state
        state_clicks = self.__multiply_state_for_clicks(pairs, clicks_until_match)
        # get reward for the second flip
        reward = self.__get_reward_by_state_action_pair(action, state_clicks)

        return reward

    @staticmethod
    def __multiply_state_for_clicks(pairs, attemps_number):
        """
        Calculates the multiplier for the reward based on the number of pairs already found and the 
        number of attempts occured before the match.

        Parameters:
        ----------
            pairs (int): The number of pairs already found.
            clicks (int): The number of clicks until the current match.

        Returns:
        --------
            float: The multiplier for the reward.
        """
        if pairs <= 3:
            return attemps_number * constants.BEGIN_STATE
        elif 3 < pairs < 8:
            return attemps_number * constants.MIDDLE_STATE
        else:
            return attemps_number * constants.END_STATE

    @staticmethod
    def __get_reward_by_state_action_pair(action, state_clicks):
        """
        Calculates the reward for the current state-action pair.

        Parameters:
        ----------
            action (int): The action taken by the agent.
            state_clicks (float): The multiplier for the reward.

        Returns:
        ---------
            float: The calculated reward.
        """
        if action == constants.SUGGEST_ROW:
            return constants.REWARD_SUGGEST_ROW * state_clicks
        
        if action == constants.SUGGEST_COL:
            return constants.REWARD_SUGGEST_COL * state_clicks
        
        elif action == constants.SUGGEST_CARD:
            return constants.REWARD_SUGGEST_CARD * state_clicks
        
        else:
            return constants.REWARD_SUGGEST_NONE / state_clicks