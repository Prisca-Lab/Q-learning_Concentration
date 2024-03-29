import random
import logging

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))
import constants

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

    def take_action(self, action, game):
        """
        This function will return the suggest provided by the robot.
        
        Parameters
        ----------
        action: int
            robot will choose a suggest based on action (which can be 0, 1 or 2)
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
            suggest, card, position = self.__suggest_row_or_col(game)
            index = position[0] if position[1] == -1 else position[1]
            logging.debug("Try with ", suggest, index)

        elif action == constants.SUGGEST_CARD:
            suggest, card, position = self.__suggest_card(game)
            logging.debug("Try with ", suggest, " in position: ", position)

        else:
            suggest = 'none'
            card = 'none'
            position = []

        return suggest, card, position

    def __suggest_card(self, game):
        """
        This function will show the card and its position based on the last card clicked.
 
        Then return the other position.
        """

        game_board = game.get_board
        open_card_name = game.get_current_open_card_name

        # suggest the other position
        other_pos = Card.get_other_location_of_open_card(open_card_name, game_board)

        return 'card', open_card_name, other_pos

    def __suggest_row_or_col(self, board):
        """
        This function will get the row/column of the card to suggest.

        Return
        ------
        suggest: String
            The index to suggest: row or column
        position: array of int
            coordinates of suggested card. 
                - Both >= 0 if suggest is a card.
                - First one = -1 if suggest is column
                - Second one = -1 if suggest is row
        """

        card_name = board.get_current_open_card_name
        game_board = board.get_board

        # suggest the other position
        other_pos = Card.get_other_location_of_open_card(card_name, game_board)

        suggest, position = self.__get_which_position_to_suggest(other_pos, game_board)

        return suggest, None, position

    @staticmethod
    def __get_which_position_to_suggest(position, player_board):
        """
        Returns the type of suggestion (row or column) to provide.
        It will suggest:
            - row, if there are more than 2 face up cards in a column and less than 4 in a row
            - column, if there are more than 3 face up cards in a row and less than 3 in a column
            - random between row and column otherwise
        """

        row = position[0]
        column = position[1]

        face_up_card_rows = Card.get_face_up_cards_by_index("row", row, player_board)
        face_up_card_cols = Card.get_face_up_cards_by_index("column", column, player_board)

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
