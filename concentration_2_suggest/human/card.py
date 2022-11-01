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
    def get_other_location_of_open_card(card, position, board):
        """
        Return the other position of a face up card
        """

        first_pos = board[card]['first_pos']
        second_pos = board[card]['second_pos']

        return second_pos if first_pos == position else first_pos

    @staticmethod
    def get_face_up_cards_by_index(index_type, index_number, board, current_open_card_position):
        """
        This function returns the number of face up cards in specific index.

        Parameters
        ---------- 
        index_type: string
            the row or the column
        index_number: int
            the index of the row / column for which you want to know the number of face up cards
        board: dictionary
            the history of player
        current_open_card_position: array of int
            the position of current open card

        Returns
        -------
        n: int
            the number of face up cards 
        """
        n = 0
        row = 0
        column = 1

        which_one = 0 if index_type == "row" else 1

        for k in board:
            is_founded = board[k]['founded']
            index_first_card = board[k]['first_pos'][which_one]
            index_second_card = board[k]['second_pos'][which_one]

            if is_founded and (index_first_card == index_number and index_second_card == index_number):
                # both cards are on the same row/column 
                n += 2
            elif is_founded and (index_first_card == index_number or index_second_card == index_number):
                n += 1

        if current_open_card_position != []:
            # if the row of the current open card is equal to the index suggested then increment the counter
            if current_open_card_position[row] == index_number and which_one == 0:
                n += 1

            # idem for the column
            if current_open_card_position[column] == index_number and which_one == 1:
                n += 1
                        
        return n 

    @staticmethod
    def get_max_clicks(history):
        """
        Returns the number of times of the most clicked card
        """

        # get first_location max
        # we check if it's open just for robustness
        max_first = max(k['times_that_first_was_clicked'] for k in history.values() if 
                        k['is_first_opened'] is False and k['founded'] is False)
        # get second_location_max
        max_second = max(k['times_that_second_was_clicked'] for k in history.values() if
                         k['is_second_opened'] is False and k['founded'] is False)

        return max_first if max_first > max_second else max_second

    def get_most_clicked_cards(self, history):
        """
        Returns a new dictionary containing cards and positions of the most clicked cards
        """
        max_click = self.get_max_clicks(history)

        cards = {}
        for key, v in history.items():
            is_founded = history[key]['founded']

            if is_founded is False:
                click_of_first = history[key]['times_that_first_was_clicked']
                click_of_second = history[key]['times_that_second_was_clicked']

                is_first_clicked = history[key]['is_first_opened']
                is_second_clicked = history[key]['is_second_opened']

                both_face_down = is_first_clicked is False and is_second_clicked is False

                if click_of_first == max_click and click_of_second == max_click and both_face_down:
                    cards[key] = {'first_pos': v['first_pos'], 'second_pos': v['second_pos']}

                elif click_of_first == max_click and (is_second_clicked or click_of_second < max_click):
                    cards[key] = {'first_pos': v['first_pos'], 'second_pos': None}

                elif click_of_second == max_click and (is_first_clicked or click_of_first < max_click):
                    cards[key] = {'first_pos': None, 'second_pos': v['second_pos']}

        return cards
    
    @staticmethod
    def get_which_is_open(card, board):
        """
        Returns a flag to figure out which card location is face up
        """

        return 'is_first_opened' if board[card]['is_first_opened'] is True else 'is_second_opened'

    @staticmethod
    def get_which_to_open(card, position, board):
        """
        Returns a flag to figure out which card's location to face up in the current turn
        """

        return 'is_first_opened' if board[card]['first_pos'] == position else 'is_second_opened'