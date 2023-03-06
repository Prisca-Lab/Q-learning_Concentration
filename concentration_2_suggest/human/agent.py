import random

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

import constants

from card import Card

class Agent:
    def __init__(self, env, type):
        """
        Initializes an Agent object.

        Parameters
        ----------
            env (Environment): the environment the agent operates in
            type (int): The type of robot that's gonna help the user. 
        """
        self.env = env
        self.__reward_first_card = 0.4
        self.__has_suggests_for_the_first_card = False
        self.type = type

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

        pairs = self.env.get_pairs_found()
        is_turn_odd = ((self.env.get_turn() - 1) % 2) != 0
        is_turn_less_than_six = self.env.get_turn() - 1 < 6

        if is_turn_less_than_six and pairs == 0:
            return getattr(constants, 'INIT_STATE')

        state_suffix = "CORRECT" if self.env.was_last_move_a_match() else "WRONG"
        
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

    def take_action(self, action):
        """
        Executes an action based on the current game state and returns a tuple with the suggested action.

        Parameters
        ----------
            action (int): The action to be taken.

        Returns
        ----------
            Tuple of strings and integers:
                The first element indicates the type of the suggested action ('row'/'col' for suggesting row and column,
                'card' for suggesting a card and 'none' for not suggesting).
                The second element is a string rapresenting the name of the card suggested.
                The third element is an integer representing coordinates of suggested card.
        """
        if action != constants.SUGGEST_NONE:
            current_open = self.env.get_current_open_card()

            if current_open == '':
                name_card, other_location = self.__handle_first_flip()
            else:
                name_card, other_location = self.__handle_second_flip(action)

            if action == constants.SUGGEST_ROW:
                return ("row", name_card, (other_location[0] + 1, - 1))
            elif action == constants.SUGGEST_COL:
                return ("column", name_card, (- 1, other_location[1] + 1))
            else:
                # increase position to make it clear for human
                row, col = other_location
                return ("card", name_card, (row + 1, col + 1))

        return ("none", None, None)
    
    def __handle_first_flip(self):
        """
        Choose a card and its other location to flip for the first time, based on the agent's type.

        Returns:
        -------
        Tuple of (str, Tuple of (int, int))
            The name of the card chosen and its other location on the game board.
        """
        
        if self.type == constants.TOM:
            # choose randomly a card from the list of most clicked cards
            card_name, other_pos = self.env.get_least_clicked_location_of_most_clicked_card()
        elif self.type == constants.NO_TOM:
            # choose randomly a card from set of available cards
            card_name, other_pos = self.env.get_random_card()
        else:
            # choose less clicked card from set of visitated card
            card_name, other_pos = self.env.get_least_clicked_location_from_visitated()

        return (card_name, other_pos)
    
    def __handle_second_flip(self, action):
        """
        Choose a card and its other location to flip for the second time, based on the agent's type and the current game state.

        Parameters:
        ----------
        action: str
            The agent's chosen action for the current turn.

        Returns:
        -------
        Tuple of (str, Tuple of (int, int))
            The name of the card chosen and its other location on the game board.
        """
        current_open = self.env.get_current_open_card()
        current_pos = self.env.get_current_open_card_pos()
        can_suggest_wrong = random.choice([0, 1]) == 0


        if self.type == constants.DECEPTION and can_suggest_wrong and action == constants.SUGGEST_CARD:
            card_name, position = self.__get_wrong_card()
        else:
            card_name = current_open
            position = self.env.get_other_location(current_open, current_pos)

        return (card_name, position)

    def __get_which_position_to_suggest(self, other_location):
        """
        Determines which position to suggest for the next action based on the number of face-up cards in each row and column.

        Parameters
        ----------
            other_location (Tuple of integers): A tuple with two integers representing the location of the current open card.

        Returns
        ----------
            Tuple of a string and a tuple of integers:
                - The first element indicates whether to suggest a row or a column ('row' or 'column').
                - The second element is a tuple of two integers representing the suggested row and column indexes. 
        """
        row, col = other_location
        # rimuovere len se non funziona
        face_up_card_rows = (self.env.get_cards_by_index("row", row))
        face_up_card_cols = (self.env.get_cards_by_index("column", col))

        if face_up_card_cols > 2 and face_up_card_rows < 5:
            # suggest the row cause the column has already 2/4 face up card
            return ('row', (row, -1))
        elif face_up_card_cols <= 2 and face_up_card_rows > 3:
            # suggest the column cause the row has already 4/6 face up card
            return ('column', (-1, col))
        else:
            # the suggest can be random
            choice = random.randint(0, 1)  # 0: suggest row, 1: suggest column
            if choice == 0:
                return ('row', (row, -1))
            else:
                return ('column', (-1, col)) 
             
    def __get_wrong_card(self):
        """
        With this function tha agent suggests the wrong card based on the card currently open.

        Parameters:
        ----------
            None
        
        Returns:
        -------
            card_name (str): the name of the selected card to suggest
            other_pos (tuple) the position of selected card
        """
        
        print("wrong card") # choose neighbour card

        open_card_name = self.env.get_current_open_card()
        open_card_pos = self.env.get_current_open_card_pos()
        game_board = self.env.get_board()

        # get other location of current open card
        other_pos = self.env.get_other_location(open_card_name, open_card_pos)
        
        # choose what suggest (row or column)
        suggest, position = self.__get_which_position_to_suggest(other_pos)
        index = 0 if suggest == "row" else 1
        
        # select a random card from row/column of the other location of the card currently open
        available_cards = Card.get_available_cards_by_suggest(suggest, position[index], game_board)
        
        # remove the other location if it is present: it must provide a wrong position
        if open_card_name in available_cards and len(available_cards) > 1:
            del available_cards[open_card_name]
        
        # now choose one (wrong) card from available
        card_name, position, _ = Card.get_random_card(available_cards)
        
        # in this case the agent can't provide anymore a wrong card: there is only one available who's also a match
        # (this because the card was not removed from available)
        if open_card_name == card_name:
            return card_name, other_pos

        return (card_name, position)

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
        clicks_until_match = self.env.get_flip_number()
        num_pairs_found = self.env.get_pairs_found()
        has_found_pair = self.env.was_last_move_a_match()
        is_turn_even = (self.env.get_turn() - 1) % 2 == 0

        # for the first six turns the agent can't provide any suggestion, thus the reward is 0
        # n.b the turn is not the current turn, but the next one
        if self.env.get_turn() < 7 and num_pairs_found == 0:
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
        if action == constants.SUGGEST_COL:
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

    ##################################################################################################################
    #                                              Theory of mind                                                    #
    ##################################################################################################################

    def get_flag_for_ToM(self, suggestion, card, position):
        """
        This function will return 2 flag in order to understand what robot should say in theory of mind case.

        Parameters:
        ----------
        suggestion (str): the type of suggestion ("card", "row" or "column")
        card (str): the name of the card suggested
        position (tuple): the coordinates of suggested card. Both positive if suggestion is card, negative for the row or the column.
        
        Returns:
        --------
        flag_ToM: int
            - -1 if the robot should not use Theory of Mind
            - 1 if the robot should use ToM but there's no player's history (for example at the beginning)
            - 1: if the card to open has been clicked only once
            - 2: it the card to open has never been clicked while the other one has been clicked multiple times
            - 3: if both had been clicked multiple times
            - 4: if the clicked card has been clicked multiple times while the other one has been clicked 0 times
            - 5: if the clicked card has been clicked only once while the other one multiple times
            - 6: if the clicked card has been clicked for the first time 
            - 0 otherwise

        flag_suggestion: int
            - 1 if the suggestion is provided for the first card
            - 2 it the suggestion is provided for the second card
            - 0 otherwise (i.e no ToM)
        """

        player_history = self.env.get_history()
        open_card = self.env.get_current_open_card()
        open_position = self.env.get_current_open_card_pos()

        flag_ToM = - 1
        flag_suggestion = 0

        if suggestion == "none":
            return flag_ToM, flag_suggestion

        # if there is an open card 
        if open_card != '': 
            # get which position to suggest in order to check how many times the card was clicked
            which_to_open = Card.get_which_to_open(open_card, open_position, player_history)
            # check if user has already seen the other location
            flag_ToM = self.env.check_if_user_has_seen_a_card(card, which_to_open)
            flag_suggestion = 2
        else:
            # there is no open card, so the suggestion is on the first card
            flag_suggestion = 1
            if suggestion == "card":
                which_to_open = Card.get_which_to_open(card, position, player_history)
                # check if user has already seen the other location
                flag_ToM = self.env.check_if_user_has_seen_a_card(card, which_to_open)
            else:
                # row or column
                index = 0 if suggestion == "row" else 1
                # check for first position
                if player_history[card]['first_pos'][index] == position[index] - 1:
                    flag_ToM = self.env.check_if_user_has_seen_a_card(card, "is_first_opened")
                # otherwise check for the second position
                if player_history[card]['second_pos'][index] == position[index] - 1: 
                    flag_ToM = self.env.check_if_user_has_seen_a_card(card, "is_second_opened")  

        print("flag ToM, flag_sugg", flag_ToM, flag_suggestion)

        return flag_ToM, flag_suggestion 

   