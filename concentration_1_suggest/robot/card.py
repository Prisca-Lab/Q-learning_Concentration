import random

class Card:

    @staticmethod
    def get_random_card(available_cards):
        """
        This function return a random card chosen from available cards dictionary.

        Parameters
        ----------
        available_cards: dictionary
            includes the name of the card and its available positions

        Returns
        -------
        card: string
            the card name randomly chosen
        position: array of int
            coordinates of chosen card
        which_one: string
            which position was chosen: 'is_first_opened' for the first one, 'is_second_opened' otherwise
        """
        # choose randomly a card from the list of available card
        card, position = random.choice(list(available_cards.items()))

        # check which position is chosen
        if position['first_pos'] is None:
            position = available_cards[card]['second_pos']
            which_is_clicked = 'is_second_opened'
        elif position['second_pos'] is None:
            position = available_cards[card]['first_pos']
            which_is_clicked = 'is_first_opened'
        else:
            # both position are available, so we can choose a random position
            if random.randint(0, 1) == 0:
                # get first
                position = available_cards[card]['first_pos']
                which_is_clicked = 'is_first_opened'
            else:
                # get second
                position = available_cards[card]['second_pos']
                which_is_clicked = 'is_second_opened'

        return card, position, which_is_clicked

    @staticmethod
    def get_available_cards_and_position(board):
        """
        This function will return all the cards which can be clicked.

        Parameters
        ----------
        board: dictionary
            The board of the game.

        Returns
        -------
        available_cards: dictionary
            All name and coordinates of cards that can be clicked

        """

        available_cards = {}
        for k, v in board.items():
            if board[k]['founded'] is False:
                is_first_clicked = board[k]['is_first_opened']
                is_second_clicked = board[k]['is_second_opened']

                if is_first_clicked:
                    available_cards[k] = {'first_pos': None, 'second_pos': v['second_pos']}
                elif is_second_clicked:
                    available_cards[k] = {'first_pos': v['first_pos'], 'second_pos': None}
                else:  # both position can be clicked
                    available_cards[k] = {'first_pos': v['first_pos'], 'second_pos': v['second_pos']}

        return available_cards

    @staticmethod
    def get_available_cards_by_suggest(suggest, number_suggested, board):
        """
        This function will return all cards that robot can click based on row or column suggested.

        Parameters
        ----------
        suggest: string
            The robot suggest: row or column
        number_suggested: int
            The number of row/column suggested
        history: dictionary
            The history of game used to get all available cards of specific row/column 

        Returns
        -------
        available_cards: dictionary
            A dictionary which contains all name and position that can be clicked
        """

        hint = 0 if suggest == 'row' else 1

        available_cards = {}
        for k, v in board.items():
            if board[k]['founded'] is False:
                is_first_clicked = board[k]['is_first_opened']
                is_second_clicked = board[k]['is_second_opened']
                is_first_valid = board[k]['first_pos'][hint] == number_suggested
                is_second_valid = board[k]['second_pos'][hint] == number_suggested

                if is_first_clicked and is_second_valid:
                    available_cards[k] = {'first_pos': None, 'second_pos': v['second_pos']}

                elif is_second_clicked and is_first_valid:
                    available_cards[k] = {'first_pos': v['first_pos'], 'second_pos': None}

                elif is_first_valid and is_second_valid:
                    available_cards[k] = {'first_pos': v['first_pos'], 'second_pos': v['second_pos']}

                else:
                    if is_first_valid:
                        available_cards[k] = {'first_pos': v['first_pos'], 'second_pos': None}
                    elif is_second_valid:
                        available_cards[k] = {'first_pos': None, 'second_pos': v['second_pos']}

        return available_cards

    @staticmethod
    def get_other_location_of_open_card(card, board):
        """
        Return the other position of a face up card
        """
        is_first_clicked = board[card]['is_first_opened']

        first_pos = board[card]['first_pos']
        second_pos = board[card]['second_pos']

        return second_pos if is_first_clicked else first_pos

    @staticmethod
    def get_face_up_cards_by_index(index_type, index, board):
        """
        This function returns the number of face up cards in specific index.

        Parameters
        ---------- 
        index_type: string
            the row or the column
        index: int
            the index of the row / column for which you want to know the number of face up cards
        board: dictionary
            the board of the game

        Returns
        -------
        n: int
            the number of face up cards 
        """
        n = 0

        which_one = 0 if index_type == "row" else 1

        for k in board:
            is_founded = board[k]['founded']

            index_first_card = board[k]['first_pos'][which_one]
            index_second_card = board[k]['second_pos'][which_one]

            is_first_open = board[k]['is_first_opened']
            is_second_open = board[k]['is_second_opened']

            if is_founded and (index_first_card == index and index_second_card == index):
                # both cards are on the same row/column 
                n += 2
            elif is_founded and (index_first_card == index or index_second_card == index):
                n += 1

            # if the current open card has the same index then increment the counter
            if is_first_open or is_second_open:
                if index_first_card == index or index_second_card == index:
                    n += 1

        return n

    @staticmethod
    def get_which_is_open(card, board):
        """
        Returns a flag to figure out which card location is face up
        """

        return 'is_first_opened' if board[card]['is_first_opened'] is True else 'is_second_opened'