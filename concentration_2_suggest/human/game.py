import json
import numpy as np
from socket import *

from card import Card

class Game:

	def __init__(self):
		"""
        It initializes the game object object.

		Attributes:
		-----------
			board - a dictionary with card name as key and positions and flags as value
			turns - the number of turns played in the game
			pairs_left - the number of pairs of cards remaining to be found
			finished - a boolean indicating if the game has finished
			current_open_card_name - the current open card in the game
			current_open_card_position - the position of the current open card in the game
			num_cols - the number of columns in the game board
			num_rows - the number of rows in the game board
        """
		self.shuffled = []
		self.board = {}
		self.turns = 1
		self.pairs_left = 12
		self.finished = False
		self.current_open_card_name = ''
		self.current_open_card_position = []
		self.num_cols = 6
		self.num_rows = 4

	def reset(self, shuffled):
		self.shuffled = shuffled
		self.board = {}
		self.turns = 1
		self.pairs_left = 12
		self.finished = False
		self.current_open_card_name = ''
		self.current_open_card_position = []
		self.num_cols = 6
		self.num_rows = 4
		self.__create_board()

	def __create_board(self):
		"""
		Create a new dictionary which contains the board data.
        """

		# for debug: print as matrix the board
		Game.__print_board_as_matrix(self.shuffled)

		k = 0
		for i in range(self.num_rows):
			for j in range(self.num_cols):
				card = self.shuffled[k]
				if card in self.board:
					self.board[card]['second_pos'] = [i, j]
				else:
					self.board[card] = {
                        'first_pos': [i, j],        # the first location of a card
                        'is_first_opened': False,   # is the card currently face up?
                        'second_pos': [-1, -1],
                        'is_second_opened': False,
                        'founded': False            # true if the pair has been found    
                    }
				k += 1

	def update_state_of_game(self, card_name, card_position, match):
		"""
		Update the state of the game after a player's turn.

		Parameters:
		----------
		card_name (str): the name of the card that was flipped over
		card_position (tuple of int): the position of the card that was flipped over
		match (bool): indicates if the card flipped over matches another card on the board
			
		Returns:
		-------
		None
		
		Side Effects:
		-------------
		- Sets the name and position of the current open card.
		- Decreases the pairs_left counter if there was a match.
		- Sets the "founded" flag of the card to True if there was a match.
		- Increases the turns counter.
		"""

		self.current_open_card_name = card_name
		self.current_open_card_position = card_position

		row = card_position[0] + 1
		col = card_position[1] + 1

		print("Clicked card:", card_name, row, col, "\n")

		is_turn_even = self.turns % 2 == 0

		if match:
			self.pairs_left -= 1
			self.board[card_name]['founded'] = True

		# turn down the card
		if is_turn_even:
			self.current_open_card_name = ''
			self.current_open_card_position = []

		self.turns += 1

	def print_board(self):
		print(json.dumps(self._board, indent=4))

	def is_game_ended(self):
		return self.pairs_left == 0

	@staticmethod
	def __print_board_as_matrix(shuffle_cards):
		board = np.zeros((6, 4))
		board = np.reshape(shuffle_cards, (4, 6))
		mx = len(max((sub[0] for sub in board), key=len))
		print("\n")
		for row in board:
			print(" ".join(["{:<{mx}}".format(ele, mx=mx) for ele in row]))
		print("\n")

	def get_least_clicked_location_of_most_clicked_pair(self, history):
		"""
        This function will find the most clicked card. Then it will returns the least clicked location of that card.

        Parameters:
        ----------
            history (dict): the player's history which contains the card name as key, and the 
            locations and how many times they have clicked as values.

        Returns:
        ---------
            tuple: a tuple containing the name of the card and another tuple which contains the coordinates of the least clicked location
        """

		print("Suggest other location of most clicked card - ToM")

		card = Card()
		available_cards = card.get_most_clicked_cards(history)
		card_name, position, _ = Card.get_random_card(available_cards)
		# get position with less click of chosen card
		other_pos = Card.get_other_location_of_open_card(card_name, position, self.board)

		return (card_name, other_pos)
	
	def get_random_card(self):
		"""
		This function return a random card from all available cards.

		Returns:
        ---------
            tuple: a tuple containing the name of the card and another tuple which contains the coordinates of the least clicked location
		"""

		print("Suggest random location - noToM")

		available_cards = Card.get_available_cards_and_position(self.board)
        # suggest one randomly
		card_name, position, _ = Card.get_random_card(available_cards)

		return (card_name, position)
	
	def get_least_clicked_location_from_visitated(self, history):
		"""
        This function will return the less clicked location based on the cards that the user has already saw.

        Parameters:
        ----------
            history (dict): the player's history which contains the card name as key, and the 
            locations and how many times they have clicked as values.

        Returns:
        ---------
            tuple: a tuple containing the name of the card and another tuple which contains the coordinates of the least clicked location
        """

		print("Suggest least clicked location from all visitated cards - deception")

		card = Card()
		available_cards = card.get_less_clicked_cards(history)
		print("available is", available_cards)
		card_name, position, _ = Card.get_random_card(available_cards)
        
		return (card_name, position)
	