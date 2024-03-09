import random

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

from util import constants
from util import Util
from game.card import Card
from sentences.sentences import SuggestionGenerator

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
        self.type = type
        # handle speech generator
        tom_mode = Util.get_experimental_condition(constants.TOM)
        language = Util.get_from_json_file("config")["language"]
        if type == constants.DECEPTION:
            self.sentence_generator = SuggestionGenerator(tom_mode, language)
        else:
            self.sentence_generator = SuggestionGenerator(Util.get_experimental_condition(type), language)

    def take_action(self, action):
        """
        Executes an action based on the current game state and returns a tuple with the suggested action.

        Parameters
        ----------
            action (int): The action to be taken.

        Returns
        ----------
            Tuple of strings and integers:
                - The first element indicates the type of the suggested action ('row'/'col' for suggesting row and column,
                  'card' for suggesting a card and 'none' for not suggesting).
                - The second element is a string rapresenting the name of the card suggested.
                - The third element is an integer representing coordinates of suggested card. 
                  The agent returns the coordinates of the position increased by 1 to facilitate the human.
        """
        if action != constants.SUGGEST_NONE:
            current_open, _ = self.env.get_current_open_card()

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

        # allowed modes for ToM type behavior for the first flip 
        tom_modes = [constants.TOM]
        
        if self.type in tom_modes:
            # choose randomly a card from the list of most clicked cards
            card_name, other_pos = self.env.get_least_clicked_location_of_most_clicked_card()
        elif self.type == constants.NO_TOM:
            # choose randomly a card from set of available cards
            print("Choose random card")
            card_name, other_pos = self.env.get_random_card()
        else:
            # choose less clicked card from set of visitated card (deception mode)
            card_name, other_pos = self.env.get_least_clicked_location_from_visitated()

        return (card_name, other_pos)
    
    def __handle_second_flip(self, action):
        """
        Choose a card and its other location to flip.

        Parameters:
        ----------
        action: str
            The agent's chosen action for the current turn.

        Returns:
        -------
        Tuple of (str, Tuple of (int, int))
            The name of the card chosen and its other location on the game board.
        """
        current_open, current_pos = self.env.get_current_open_card()
        
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

    ##################################################################################################################
    #                                                    Speech                                                      #
    ##################################################################################################################

    def generate_sentence(self, hint_type, flip_type, flag_ToM, card, position):
        """
        Generate a sentence based on the provided hint.
        """
        
        # if none then say nothing
        if hint_type == 'none': return None

        return self.sentence_generator.get_sentence(hint_type, flip_type, flag_ToM, card, position)
    

    ##################################################################################################################
    #                                                   Deception                                                    #
    ##################################################################################################################

    def handle_deceptive_behavior(self, robot_type, card_name, position, action):
        """
        This function returns a different card from the one passed as parameter
        (e.g if card_name = 'pelican' the function will return any other available card but 'pelican')

        Parameters:
        ----------
            robot_type (int): The robot's deceptive behavior chosen.
            card_name (string): The card name that the robot chosen to suggests.

        Returns:
        ---------
            string: The card's name chosen randomly.
        """
        open_card, _ = self.env.get_current_open_card()
        is_card_open = open_card != ''

        deception_modes = [constants.DECEPTION]

        if robot_type in deception_modes and is_card_open:
            if robot_type == constants.DECEPTION and action == constants.SUGGEST_CARD:
                if random.choice([0, 1]) == 0:
                    _, position = self.__get_wrong_card()
                    row, col = position
                    return card_name, (row + 1, col + 1)
            
        return card_name, position
    
    def has_provided_wrong_card(self, action, suggested_position):
        """
        This function returns a boolean if the position provided by the agent is not the position that makes match with card currently open.

        Parameters:
        ---------
            suggested_position (tuple): the card position provided by the agent

        Returns:
        -------
            True if the position suggested and position that make a match are different, False otherwise
        """
        open_card_name, open_card_pos = self.env.get_current_open_card()

        # if there is no open card then return (since the wrong card is provived only in even turns)
        if open_card_name == '':
            return False
        
        # get other location of current open card
        other_pos = self.env.get_other_location(open_card_name, open_card_pos)
        # increment by 1 both coordinates
        other_pos = tuple([x + 1 for x in other_pos])

        wrong_hint = ''
        if action == 'card':
            wrong_hint = suggested_position != other_pos
        elif action == 'row':
            wrong_hint = suggested_position[0] != other_pos[0]
        else:
            wrong_hint = suggested_position[1] != other_pos[1]

        return  wrong_hint

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
        
        print("Choosing wrong card (if possible)...") # choose neighbour card

        open_card_name, open_card_pos = self.env.get_current_open_card()
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

