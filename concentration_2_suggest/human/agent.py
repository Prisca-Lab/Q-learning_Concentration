import random
import logging

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

import constants
from util import Util

from card import Card


class Agent:

    __reward_first_card = 0.4
    __has_suggests_for_the_first_card = False
    
    def get_next_state(self, action, face_up_cards, turn, pairs, last_match):
        # init state
        if turn < 7 and pairs == 0:
            return constants.INIT_STATE

        if pairs <= 3:
            if face_up_cards == 1 and last_match:
                return self.__which_state([
                    constants.SECOND_FLIPPING_NONE_BEGIN_CORRECT,
                    constants.SECOND_FLIPPING_SUGGEST_RC_BEGIN_CORRECT,
                    constants.SECOND_FLIPPING_SUGGEST_CARD_BEGIN_CORRECT],
                    action)
            elif face_up_cards == 2 and last_match:
                return self.__which_state([
                    constants.FIRST_FLIPPING_NONE_BEGIN_CORRECT,
                    constants.FIRST_FLIPPING_SUGGEST_RC_BEGIN_CORRECT,
                    constants.FIRST_FLIPPING_SUGGEST_CARD_BEGIN_CORRECT],
                    action)
            elif face_up_cards == 1 and last_match is False:
                return self.__which_state([
                    constants.SECOND_FLIPPING_NONE_BEGIN_WRONG,
                    constants.SECOND_FLIPPING_SUGGEST_RC_BEGIN_WRONG,
                    constants.SECOND_FLIPPING_SUGGEST_CARD_BEGIN_WRONG],
                    action)
            else:
                return self.__which_state([
                    constants.FIRST_FLIPPING_NONE_BEGIN_WRONG,
                    constants.FIRST_FLIPPING_SUGGEST_RC_BEGIN_WRONG,
                    constants.FIRST_FLIPPING_SUGGEST_CARD_BEGIN_WRONG],
                    action)

        elif 3 < pairs < 8:
            if face_up_cards == 1 and last_match:
                return self.__which_state([
                    constants.SECOND_FLIPPING_NONE_MIDDLE_CORRECT,
                    constants.SECOND_FLIPPING_SUGGEST_RC_MIDDLE_CORRECT,
                    constants.SECOND_FLIPPING_SUGGEST_CARD_MIDDLE_CORRECT],
                    action)
            elif face_up_cards == 2 and last_match:
                return self.__which_state([
                    constants.FIRST_FLIPPING_NONE_MIDDLE_CORRECT,
                    constants.FIRST_FLIPPING_SUGGEST_RC_MIDDLE_CORRECT,
                    constants.FIRST_FLIPPING_SUGGEST_CARD_MIDDLE_CORRECT],
                    action)
            elif face_up_cards == 1 and last_match is False:
                return self.__which_state([
                    constants.SECOND_FLIPPING_NONE_MIDDLE_WRONG,
                    constants.SECOND_FLIPPING_SUGGEST_RC_MIDDLE_WRONG,
                    constants.SECOND_FLIPPING_SUGGEST_CARD_MIDDLE_WRONG],
                    action)
            else:
                return self.__which_state([
                    constants.FIRST_FLIPPING_NONE_MIDDLE_WRONG,
                    constants.FIRST_FLIPPING_SUGGEST_RC_MIDDLE_WRONG,
                    constants.FIRST_FLIPPING_SUGGEST_CARD_MIDDLE_WRONG],
                    action)

        else:
            if face_up_cards == 1 and last_match:
                return self.__which_state([
                    constants.SECOND_FLIPPING_NONE_END_CORRECT,
                    constants.SECOND_FLIPPING_SUGGEST_RC_END_CORRECT,
                    constants.SECOND_FLIPPING_SUGGEST_CARD_END_CORRECT],
                    action)
            elif face_up_cards == 2 and last_match:
                return self.__which_state([
                    constants.FIRST_FLIPPING_NONE_END_CORRECT,
                    constants.FIRST_FLIPPING_SUGGEST_RC_END_CORRECT,
                    constants.FIRST_FLIPPING_SUGGEST_CARD_END_CORRECT],
                    action)
            elif face_up_cards == 1 and last_match is False:
                return self.__which_state([
                    constants.SECOND_FLIPPING_NONE_END_WRONG,
                    constants.SECOND_FLIPPING_SUGGEST_RC_END_WRONG,
                    constants.SECOND_FLIPPING_SUGGEST_CARD_END_WRONG],
                    action)
            else:
                return self.__which_state([
                    constants.FIRST_FLIPPING_NONE_END_WRONG,
                    constants.FIRST_FLIPPING_SUGGEST_RC_END_WRONG,
                    constants.FIRST_FLIPPING_SUGGEST_CARD_END_WRONG],
                    action)

    @staticmethod
    def __which_state(states, action):
        """
        Based on the last action return the correct state
        """

        if action == constants.SUGGEST_NONE:
            return states[0]
        elif action == constants.SUGGEST_ROW_COLUMN:
            return states[1]
        else:
            return states[2]

    ##################################################################################################################
    #                                                 ACTION                                                         #
    ##################################################################################################################

    def take_action(self, action, player, game, robot_type):
        """
        This function will return the suggest provided by the robot.
        
        Parameters
        ----------
        action: int
            robot will choose a suggest based on action (which can be 0, 1 or 2)
        player: Player object
            The current player. The agent must now the player's history when it suggests for the first card
        game: Game object
            The current game, which include the board from which the agent retrieves information for suggestions
        robot_type: String
            A flag which can be 'ToM', 'noToM' or 'faulty'. The suggestion will be different if flag is 'faulty'

        Return
        ------
        suggest: string
            "card", "row" or "column" suggestion
        card: string
            which card should be clicked if suggest is 'card', none otherwise
        position: array of int
            coordinates of suggested card. 
                - Both >= 0 if suggest is a card.
                - First one = -1 if suggest is column
                - Second one = -1 if suggest is row
        """

        if action == constants.SUGGEST_ROW_COLUMN:
            suggest, card, position = self.__suggest_row_or_col(player, game, robot_type)
            index = position[0] if position[1] == -1 else position[1]
            print("Try with ", suggest, index)

        elif action == constants.SUGGEST_CARD:
            suggest, card, position = self.__suggest_card(player, game, robot_type)
            print("Try with ", suggest, " in position: ", position)

        else:
            suggest = 'none'
            card = 'none'
            position = []

        return suggest, card, position

    def __suggest_card(self, player, game, robot_type):
        """
        This function will show the card and its position based on the last card clicked.

        If the user has no clicked yet a card then choose the first/second position of the most clicked one. 
        Then return the other position.
        """

        history = player.get_history
        open_card_name = game.get_current_open_card_name
        open_card_position = game.get_current_open_card_position
        game_board = game.get_board

        if open_card_name == '' and robot_type == 'ToM':
            # choose randomly a card from the list of most clicked cards
            card_name, other_pos = self.__get_other_location_of_most_clicked_card(history, game_board)
        elif open_card_name == '' and robot_type == 'noToM':
            # choose randomly a card from set of available cards
            card_name, other_pos = self.__get_random_card_from_available(game_board)
        elif open_card_name == '' and robot_type == 'faulty':
            # choose less clicked card from set of visitated card
            card_name, other_pos = self.__get_less_clicked_card(history)
        elif open_card_name != '' and robot_type == 'faulty' and random.choice([0, 1]) == 0:
            card_name, other_pos = self.__get_wrong_card(open_card_name, open_card_position, history, game_board)
        else:
            # suggest the other position
            other_pos = Card.get_other_location_of_open_card(open_card_name, open_card_position, game_board)
            card_name = open_card_name
            first = history[card_name]["times_that_first_was_clicked"]
            second = history[card_name]["times_that_second_was_clicked"]
            print("Chosen card to suggest:", card_name, first, second)

        # update position in order to make it readable for human user
        card_to_open = [0, 0]
        card_to_open[0] = other_pos[0] + 1
        card_to_open[1] = other_pos[1] + 1

        return 'card', card_name, card_to_open

    def __suggest_row_or_col(self, player, game, robot_type):
        """
        Suggest the row or column of a card.
            - If there is no open card yet then it will suggest the other position of one of most clicked cards.
            - It will suggest the other position of a face up card otherwise.
        
        Returns:
        --------
        suggest: String
            the type of the suggestion: row or column
        card_name: String
            the name of the card from which the suggestion originated
        position: array of int
            coordinates of suggested card. 
                - [-1, n + 1] if the suggestion is column
                - [n + 1, -1] otherwise
        """

        history = player.get_history
        open_card_name = game.get_current_open_card_name
        open_card_position = game.get_current_open_card_position
        game_board = game.get_board

        if open_card_name == '' and robot_type == "ToM":
            # choose randomly a card from the list of most clicked cards
            card_name, other_pos = self.__get_other_location_of_most_clicked_card(history, game_board)
            # choose what suggest: row or column
            suggest, position = self.__get_which_position_to_suggest(other_pos, open_card_position, game_board)
        elif open_card_name == '' and robot_type == 'noToM':
            # choose randomly a card from set of available cards
            card_name, other_pos = self.__get_random_card_from_available(game_board)
            # get which index(row or column) to suggest
            suggest, position = self.__get_which_position_to_suggest(other_pos, open_card_position, game_board)
        elif open_card_name == '' and robot_type == 'faulty':
            # choose less clicked card from set of visitated card
            card_name, position = self.__get_less_clicked_card(history)
            # get which index(row or column) to suggest
            suggest, position = self.__get_which_position_to_suggest(position, open_card_position, game_board)
            print(suggest, position)
        else:
            # suggest the other position
            other_pos = Card.get_other_location_of_open_card(open_card_name, open_card_position, history)
            suggest, position = self.__get_which_position_to_suggest(other_pos, open_card_position, game_board)
            card_name = open_card_name
            first = history[card_name]["times_that_first_was_clicked"]
            second = history[card_name]["times_that_second_was_clicked"]
            print("Chosen card row/col to suggest:", card_name, first, second)

        return suggest, card_name, position

    ##################################################################################################################
    #                                                   UTIL                                                         #
    ##################################################################################################################

    @staticmethod
    def __get_which_position_to_suggest(position, open_card_position, game_board):
        """
        Returns the type of suggestion (row or column) and number of selected row/column + 1 to provide.
        It will suggest:
            - row, if there are more than 2 face up cards in a column and less than 4 in a row
            - column, if there are more than 3 face up cards in a row and less than 3 in a column
            - random between row and column otherwise
        """

        row = position[0] + 1
        column = position[1] + 1

        face_up_card_rows = Card.get_face_up_cards_by_index("row", row - 1, game_board, open_card_position)
        face_up_card_cols = Card.get_face_up_cards_by_index("column", column - 1, game_board, open_card_position)

        if face_up_card_cols > 2 and face_up_card_rows < 5:
            # suggest the row cause the column has already 2/4 face up card
            return 'row', [row, -1]
        elif face_up_card_cols <= 2 and face_up_card_rows > 3:
            # suggest the column cause the row has already 4/6 face up card
            return 'column', [-1, column]
        else:
            # the suggest can be random
            choice = random.randint(0, 1)  # 0: suggest row, 1: suggest column
            if choice == 0:
                return 'row', [row, -1]
            else:
                return 'column', [-1, column]

    def __get_other_location_of_most_clicked_card(self, history, game_board):
        """
        This function will return the name of the most clicked card and its other location(i.e the less clicked)

        Parameters:
        ----------
        history: dictionary
            the player's history which contains the number of clicks for each card.
        game_board: dictionary
            the board game

        Returns:
        -------
        card_name: String
            The name of the most clicked card
        other_pos: array of int
            the other location of most clicked card
        """

        card = Card()
        available_cards = card.get_most_clicked_cards(history)
        card_name, position, which_is_clicked = Card.get_random_card(available_cards)
        # get position with less click of chosen card
        other_pos = Card.get_other_location_of_open_card(card_name, position, game_board)

        first = history[card_name]["times_that_first_was_clicked"]
        second = history[card_name]["times_that_second_was_clicked"]
        print("Chosen card to suggest:", card_name, which_is_clicked, first, second)

        return card_name, other_pos

    def __get_random_card_from_available(self, game_board):
        """
        This function will return a random card and its position  

        Parameters:
        ----------
        game_board: dictionary
        
        Returns:
        --------
        card_name: String
        position: array of int
        """

        print("noToM first card")
        available_cards = Card.get_available_cards_and_position(game_board)
        # suggest one randomly
        card_name, position, _ = Card.get_random_card(available_cards)

        return card_name, position

    def __get_less_clicked_card(self, history):
        """
        This function will return the card with less clicks.

        Parameters:
        ----------
        history: dictionary
            the player's history
        
        Returns:
        --------
        card_name: String
            the name of the card with less clicks
        position: array of int
            the position of selected card
        """

        print("less clicked")
        card = Card()
        available_cards = card.get_less_clicked_cards(history)
        print("available is", available_cards)
        card_name, position, _ = Card.get_random_card(available_cards)
        # suggest the other location of less clicked
        #other_pos = Card.get_other_location_of_open_card(card_name, position, game_board)
        print(card_name, position)

        return card_name, position

    def __get_wrong_card(self, open_card_name, open_card_position, history, game_board):
        """
        With this function tha agent suggests the wrong card based on the card currently open.

        Parameters:
        ----------
        open_card_name: String
            the name of card currently open
        open_card_position: array of int
            the position of the card currently open
        history: dictionary
            the player's history of the game
        game_board: dictionary
        
        Returns:
        -------
        card_name: String
            the name of the selected card to suggest
        other_pos: array of int
            the position of selected card
        """
        
        print("wrong card")
        # choose neighbour card
        # get other location of current open card
        other_pos = Card.get_other_location_of_open_card(open_card_name, open_card_position, history)
        # choose what suggest (row or column)
        suggest, position = self.__get_which_position_to_suggest(other_pos, open_card_position, game_board)
        index = 0 if suggest == "row" else 1
        # select a random card from row/column of the other location of the card currently open
        available_cards = Card.get_available_cards_by_suggest(suggest, position[index] - 1, game_board)
        # remove the other location if it is present: it must provide a wrong position
        if open_card_name in available_cards and len(available_cards) > 1:
            del available_cards[open_card_name]
        card_name, position, _ = Card.get_random_card(available_cards)
        # in this case the agent can't provide anymore a wrong card: there is only one available who's also a match
        if open_card_name == card_name:
            return card_name, other_pos

        return card_name, position

    ##################################################################################################################
    #                                              Theory of mind                                                    #
    ##################################################################################################################

    def get_flag_for_ToM(self, suggestion, card, position, player, game):
        """
        This function will return 2 flag in order to understand what robot should say in theory of mind case.

        Parameters:
        ----------
        suggestion: String
            the type of suggestion ("card", "row" or "column")
        card: String
            the name of the card suggested
        position: array of int
            the coordinates of suggested card. Both positive if suggestion is card, negative for the row or the column.
        player: Player object
            the current player
        game: Game object
            the current game
        
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

        player_history = player.get_history
        open_card = game.get_current_open_card_name
        open_position = game.get_current_open_card_position

        flag_ToM = - 1
        flag_suggestion = 0

        if suggestion == "none":
            return flag_ToM, flag_suggestion

        # if there is an open card 
        if open_card != '': 
            # get which position to suggest in order to check how many times the card was clicked
            which_to_open = Card.get_which_to_open(open_card, open_position, player_history)
            # check if user has already seen the other location
            flag_ToM = player.check_if_user_has_seen_a_card(card, which_to_open)
            flag_suggestion = 2
        else:
            # there is no open card, so the suggestion is on the first card
            flag_suggestion = 1
            if suggestion == "card":
                which_to_open = Card.get_which_to_open(card, position, player_history)
                # check if user has already seen the other location
                flag_ToM = player.check_if_user_has_seen_a_card(card, which_to_open)
            else:
                # row or column
                index = 0 if suggestion == "row" else 1
                # check for first position
                if player_history[card]['first_pos'][index] == position[index] - 1:
                    flag_ToM = player.check_if_user_has_seen_a_card(card, "is_first_opened")
                # otherwise check for the second position
                if player_history[card]['second_pos'][index] == position[index] - 1: 
                    flag_ToM = player.check_if_user_has_seen_a_card(card, "is_second_opened")  

        print("flag ToM, flag_sugg", flag_ToM, flag_suggestion)

        return flag_ToM, flag_suggestion 

    ##################################################################################################################
    #                                                 REWARD                                                         #
    ##################################################################################################################

    def get_reward(self, state, action, player, game):
        clicks_until_match = player.get_number_of_clicks_for_current_pair
        pairs = player.get_pairs
        has_found_pair = player.get_last_pair_was_correct
        is_turn_even = (game.get_turn - 1) % 2 == 0

        # it it's the first pair then the agent can not suggests, so the reward is 0
        if game.get_turn < 7 and pairs == 0:
            return 0

        # suggestion for the first card
        if game.get_face_up_cards == 1 and \
            ((clicks_until_match > 4 and pairs > 0 ) or (clicks_until_match > 9 and pairs == 0)):
            if action != 0:
                self.__has_suggests_for_the_first_card = True
            else:
                self.__has_suggests_for_the_first_card = False
            self.__reward_first_card += 0.4
            return self.__reward_first_card

        # if the suggestion on the first was usless then reset the reward
        if is_turn_even and has_found_pair is False and self.__has_suggests_for_the_first_card:
            self.__reward_first_card = 0.4

        # if the player has found a pair
        if has_found_pair and is_turn_even:
            self.__reward_first_card = 0.4  # reset the reward for the first card
            n = self.__get_divide_correct_state_for_clicks(pairs, clicks_until_match)
            return self.__get_reward_by_state_action_pair(action, n)
        
        return 0

    @staticmethod
    def __get_divide_correct_state_for_clicks(pairs, clicks):
        if pairs <= 3:
            return clicks * constants.BEGIN_STATE
        elif 3 < pairs < 8:
            return clicks * constants.MIDDLE_STATE
        else:
            return clicks * constants.END_STATE

    @staticmethod
    def __get_reward_by_state_action_pair(action, state_click):
        match action:
            case constants.SUGGEST_NONE:
                return constants.REWARD_SUGGEST_NONE / state_click

            case constants.SUGGEST_ROW_COLUMN:
                return constants.REWARD_SUGGEST_RC * state_click

            case constants.SUGGEST_CARD:
                return constants.REWARD_SUGGEST_CARD * state_click