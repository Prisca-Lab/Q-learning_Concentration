import random
import logging

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

import constants
from util import Util

from card import Card


class Agent:
    def get_next_state(self, action, face_up_cards, pairs, last_match):
        # init state
        if pairs == 0:
            return constants.INIT_STATE
        
        if pairs < 4:
            if last_match:     
                return self.__which_state([
                    constants.NONE_BEGIN_CORRECT,
                    constants.RC_BEGIN_CORRECT,
                    constants.CARD_BEGIN_CORRECT],
                    action)
            else:
                return self.__which_state([
                    constants.NONE_BEGIN_WRONG,
                    constants.RC_BEGIN_WRONG,
                    constants.CARD_BEGIN_WRONG],
                    action)

        elif 3 < pairs < 8:
            if last_match:
                return self.__which_state([
                    constants.NONE_MIDDLE_CORRECT,
                    constants.RC_MIDDLE_CORRECT,
                    constants.CARD_MIDDLE_CORRECT],
                    action)
            else:
                return self.__which_state([
                    constants.NONE_MIDDLE_WRONG,
                    constants.RC_MIDDLE_WRONG,
                    constants.CARD_MIDDLE_WRONG],
                    action)

        else:
            if last_match:
                return self.__which_state([
                    constants.NONE_END_CORRECT,
                    constants.RC_END_CORRECT,
                    constants.CARD_END_CORRECT],
                    action)
            else:
                return self.__which_state([
                    constants.NONE_END_WRONG,
                    constants.RC_END_WRONG,
                    constants.CARD_END_WRONG],
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

    def take_action(self, action, player, game):
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

        Return
        ------
        card: string
            which card should be clicked if suggest is 'card', none otherwise
        position: array of int
            coordinates of suggested card. 
                - Both >= 0 if suggest is a card.
                - First one = -1 if suggest is column
                - Second one = -1 if suggest is row
        """

        if action == constants.SUGGEST_ROW_COLUMN:
            suggest, card, position = self.__suggest_row_or_col(player, game)
            index = position[0] if position[1] == -1 else position[1]
            logging.debug("Try with ", suggest, index)

        elif action == constants.SUGGEST_CARD:
            suggest, card, position = self.__suggest_card(player, game)
            logging.debug("Try with ", suggest, " in position: ", position)

        else:
            suggest = 'none'
            card = 'none'
            position = []

        return suggest, card, position

    def __suggest_card(self, player, game):
        """
        This function will show the card and its position based on the last card clicked.

        If the user has no clicked yet a card then choose the first/second position of the most clicked one. 
        Then return the other position.
        """

        card_name = ''
        other_pos = []

        history = player.get_history
        open_card_name = game.get_current_open_card_name
        game_board = game.get_board

        if open_card_name == '':
            # choose randomly a card from the list of available card
            card = Card()
            available_cards = card.get_most_clicked_cards(history)
            card_name, other_pos, which_is_clicked = Card.get_random_card(available_cards)
            # get position with less click of chosen card
            if which_is_clicked == 'is_first_opened':
                other_pos = history[card_name]['second_pos']
            else:
                other_pos = history[card_name]['first_pos']
        else:
            # suggest the other position
            other_pos = Card.get_other_location_of_open_card(open_card_name, game_board)
            card_name = open_card_name

        return 'card', card_name, other_pos

    def __suggest_row_or_col(self, player, game):
        """
        Suggest the row or column of clicked card.
            - If there is no open card yet then it will suggest the other position of one of most clicked cards.
            - It will suggest the other position of a face up card otherwise.
        """

        card_name = ''
        suggest = ''
        other_pos = []

        history = player.get_history
        open_card_name = game.get_current_open_card_name
        game_board = game.get_board

        if open_card_name == '':
            # choose randomly a card from the list of available card
            card = Card()
            available_cards = card.get_most_clicked_cards(history)
            card_name, _, which_is_clicked = Card.get_random_card(available_cards)
            # get position with less click of chosen card
            if which_is_clicked == 'is_first_opened':
                other_pos = history[card_name]['second_pos']
            else:
                other_pos = history[card_name]['first_pos']

            suggest, position = self.__get_which_position_to_suggest(other_pos, game_board)
        else:
            # suggest the other position
            other_pos = Card.get_other_location_of_open_card(open_card_name, history)
            suggest, position = self.__get_which_position_to_suggest(other_pos, game_board)
            card_name = open_card_name

        return suggest, card_name, position

    @staticmethod
    def __get_which_position_to_suggest(position, game_board):
        """
        Returns the type of suggestion (row or column) to provide.
        It will suggest:
            - row, if there are more than 2 face up cards in a column and less than 4 in a row
            - column, if there are more than 3 face up cards in a row and less than 3 in a column
            - random between row and column otherwise
        """

        row = position[0]
        column = position[1]

        face_up_card_rows = Card.get_face_up_cards_by_index("row", row, game_board)
        face_up_card_cols = Card.get_face_up_cards_by_index("column", column, game_board)

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

    def get_reward(self, state, action, player, game):
        # if there is only one face up card than it's the first turn of a move
        if game.get_face_up_cards == 1:
            return 0

        if player.get_last_pair_was_correct:
            pairs = player.get_pairs
            clicks_until_match = player.get_number_of_clicks_for_current_pair
            
            n = self.__get_divide_correct_state_for_clicks(pairs, clicks_until_match)

            return self.__get_reward_by_state_action_pair(action, n)
        else:
            return 0

    @staticmethod
    def __get_divide_correct_state_for_clicks(pairs, clicks):
        if pairs < 4:
            return clicks / constants.BEGIN_STATE
        elif 3 < pairs < 8:
            return clicks / constants.MIDDLE_STATE
        else:
            return clicks / constants.END_STATE

    @staticmethod
    def __get_reward_by_state_action_pair(action, state_click):
        match action:
            case constants.SUGGEST_NONE:
                return constants.REWARD_SUGGEST_NONE / state_click

            case constants.SUGGEST_ROW_COLUMN:
                return constants.REWARD_SUGGEST_RC / state_click

            case constants.SUGGEST_CARD:
                return constants.REWARD_SUGGEST_CARD / state_click
