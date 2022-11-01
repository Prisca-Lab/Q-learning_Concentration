class Card:
    
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

        # if the row of the current open card is equal to the index suggested then increment the counter
        if current_open_card_position[row] == index_number and which_one == 0:
            n += 1

        # idem for the column
        if current_open_card_position[column] == index_number and which_one == 1:
            n += 1
                    
        return n 