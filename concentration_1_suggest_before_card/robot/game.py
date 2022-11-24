import numpy as np
import random
import logging

from card import Card


class Game:
    __cards = ['goose', 'koala', 'bird', 'tiger', 'panda', 'pelican',
               'penguin', 'walrus', 'flamingo', 'shark', 'horse', 'duck',
               'goose', 'koala', 'bird', 'tiger', 'panda', 'pelican',
               'penguin', 'walrus', 'flamingo', 'shark', 'horse', 'duck']

    def __init__(self):
        self.__reset()

    def __reset(self):
        self._face_up_cards = 0
        self._current_open_card_name = ''
        self._current_open_card_position = []
        self._board = {}
        self._turn = 1
        self._pairs_found = 0

    ##################################################################################################################
    #                                             GETTER/SETTER                                                      #
    ##################################################################################################################

    @property
    def get_face_up_cards(self):
        return self._face_up_cards

    @get_face_up_cards.setter
    def set_face_up_cards(self, value):
        self._face_up_cards = value

    @property
    def get_board(self):
        return self._board

    @get_board.setter
    def set_board(self, value):
        self._board = value

    @property
    def get_current_open_card_name(self):
        return self._current_open_card_name

    @get_current_open_card_name.setter
    def set_current_open_card_name(self, value):
        self._current_open_card_name = value

    @property
    def get_current_open_card_position(self):
        return self._current_open_card_position

    @get_current_open_card_position.setter
    def set_current_open_card_position(self, value):
        self._current_open_card_position = value

    @property
    def get_turn(self):
        return self._turn

    @get_turn.setter
    def set_turn(self, value):
        self._turn = value

    ##################################################################################################################
    #                                                 GAME                                                          #
    ##################################################################################################################

    def init_game(self, player):
        """
        This function will create the game board and reinitialize data in order to reuse the same object.
        """

        # in order to to play mulitple times reset player and game
        if player.get_pairs == 12:
            self.__reset()
            player.reset()

        shuffle_cards = random.sample(self.__cards, len(self.__cards))

        self.__create_board(shuffle_cards)

        player.create_history(shuffle_cards)

    def __create_board(self, shuffle_cards):
        """
        Create a new dictionary which contains the board data.
        """
        
        k = 0
        for i in range(4):
            for j in range(6):
                card = shuffle_cards[k]
                if card in self._board:
                    self._board[card]['second_pos'] = [i, j]
                else:
                    self._board[card] = {
                        'first_pos': [i, j],        # the first location of a card
                        'is_first_opened': False,   # is the card currently face up?
                        'second_pos': [-1, -1],
                        'is_second_opened': False,
                        'founded': False            # true if the pair has been found    
                    }
                k += 1

    def __update_game(self, clicked_card_name, clicked_card_position, match, which_is_clicked):
        is_turn_even = self._turn % 2 == 0

        if is_turn_even:
            # click second card
            previous_card = self._current_open_card_name  # it still contain the card's name opened in the previous turn
            which_flag = Card.get_which_is_open(previous_card, self._board)
            self._board[previous_card][which_flag] = False
            self._face_up_cards = 2
            self._current_open_card_name = ''
            self._current_open_card_position = []
        else:
            # click first card
            self._face_up_cards = 1
            self._current_open_card_name = clicked_card_name
            self._current_open_card_position = clicked_card_position
            self._board[clicked_card_name][which_is_clicked] = True

        if is_turn_even and match:
            self._board[clicked_card_name]['founded'] = True
            self._pairs_found += 1

        self._turn += 1
    
    ##################################################################################################################
    #                                                 MOVES                                                          #
    ##################################################################################################################
    
    def make_move(self, player):
        """
        This function will choose randomly a card from board.

        Parameters:
        ----------
        player: Player object
            the current player who's playing

        Returns:
        --------
        random_card: String
            name of chosen card
        position: array of int
            the coordinates of clicked card
        which_is_clicked: String
            'is_first_opened' if the card in first location has been clicked, 'is_second_opened' otherwise.
        match: boolean
            true if a pair was found, false otherwise.
        """

        game_board = self._board
        open_card_name = self._current_open_card_name

        available_cards = Card.get_available_cards_and_position(game_board)
        random_card, position, which_is_clicked = self.__select_card(available_cards, player)

        # if it's second turn check if a pair has been found
        match = self.__check_if_match(random_card, open_card_name)

        # update game data
        self.__update_game(random_card, position, match, which_is_clicked)

        return random_card, position, which_is_clicked, match

    def make_move_by_card(self, card, position):
        """
        This function will select the card suggested by the robot.

        Parameters
        ----------
        card: String
            the name of the card suggested which is also the card that will be clicked.
        position: array of int
            the coordinates of the card that should be clicked

        Returns:
        -------
        card: String
            name of chosen card
        position: array of int
            the coordinates of clicked card
        which_is_clicked: String
            which position was chosen: 'is_first_opened' for the first one, 'is_second_opened' otherwise
        match: boolean
            true if a pair has been found, false otherwise. 
            Given that the card suggested is based on the card clicked in previous turn 
            then it will be a certain match
        """

        game_board = self._board
        open_card_name = self._current_open_card_name

        # in order to figure out which card's location has been face up
        which_is_clicked = Card.get_which_to_open(card, position, game_board)

        # if the agent suggests when there is already a face up card then it's 100% a match
        match = False if  open_card_name == '' else True

        # update game data
        self.__update_game(card, position, match, which_is_clicked)

        return card, position, which_is_clicked, match

    def make_move_by_grid(self, suggest, number_suggested):
        """
        This function will select randomly a card based on row or column suggest.

        Parameters
        ----------
        type_of_suggest: String
            'row' or 'column' suggest.
        number_suggested: int
            The number of the row or column in which a card should be clicked

        Returns:
        -------
        card: String
            name of chosen card
        position: array of int
            the coordinates of clicked card
        which_is_clicked: String
            which position was chosen: 'is_first_opened' for the first one, 'is_second_opened' otherwise
        match: boolean
            true if a pair has been found, false otherwise. 
            Given that the card suggested is based on the card clicked in previous turn 
            then it will be a certain match
        """

        game_board = self._board
        open_card_name = self._current_open_card_name

        available_cards = Card.get_available_cards_by_suggest(suggest, number_suggested, game_board)
        random_card, position, which_is_clicked = Card.get_random_card(available_cards)

        # if there is already an open card then check if it is a match, false otherwise
        if open_card_name != '':
            match = self.__check_if_match(random_card, open_card_name)
        else:
            match = False

        # update game data
        self.__update_game(random_card, position, match, which_is_clicked)

        return random_card, position, which_is_clicked, match

    ##################################################################################################################
    #                                                   UTIL                                                         #
    ##################################################################################################################

    def __select_card(self, available_cards, player):
        """
        This function will choose a card based on probability condition.

        Parameters:
        ----------
        available_cards: dictionary
            the set of cards
        player: Player 
            the current player who's playing the game

        Returns:
        --------
        random_card: String
            name of chosen card
        position: array of int
            the coordinates of clicked card
        which_is_clicked: String
            'is_first_opened' if the card in first location has been clicked, 'is_second_opened' otherwise.
        """

        # get player's data 
        face_up_cards = self._face_up_cards
        founded_pairs = player.get_pairs
        number_of_click_for_pair = player.get_number_of_clicks_for_current_pair # it considers turns, not moves
        pairs_to_found = 12 - founded_pairs

        # get probability
        probability_of_no_match = (1 - 1 / (2 * pairs_to_found - 1))
        probability_of_no_match_after_n_clicks = pow(probability_of_no_match, number_of_click_for_pair)
        probability_of_match = (1 - probability_of_no_match_after_n_clicks) * 100

        # if probability is increase then robot will choose correct card, otherwise the card will be choose randomly.
        if face_up_cards == 1 and probability_of_match > 50:
            
            if random.randint(0, 1) == 1:
                random_card = self._current_open_card_name
                position = Card.get_other_location_of_open_card(random_card, self._board)
                if self._board[random_card]['is_first_opened']:
                    which_is_clicked = 'is_second_opened'
                else:
                    which_is_clicked = 'is_first_opened'
                return random_card, position, which_is_clicked

        # if result of random.randint is not 1 then choose randomly a card
        random_card, position, which_is_clicked = Card.get_random_card(available_cards)

        return random_card, position, which_is_clicked

    def is_game_ended(self):
        return self._pairs_found == 12

    @staticmethod
    def __check_if_match(first_card, second_card):
        return True if first_card == second_card else False
