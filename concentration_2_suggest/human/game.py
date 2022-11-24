import json
import numpy as np
from socket import *


class Game:

	def __init__(self):	
		self.__reset()

	def __reset(self):
		self._face_up_cards = 0
		self._current_open_card_name = ''
		self._current_open_card_position = []
		self._board = {}
		self._turn = 1
		self._found_pairs = 0

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

	def start_game(self, player, clientSocket):
		"""
		This function will wait until new board is available.
		This function will create the game board and reinitialize data in order to reuse the same object.
		"""

		data_board = clientSocket.recv(1024)
		shuffle_cards = json.loads(data_board.decode())['matrix']

		# for debug: print as matrix the board
		Game.__print_board_as_matrix(shuffle_cards)
		
		# in order to to play mulitple times reset player and game
		if player.get_pairs == 12:
			self.__reset()
			player.reset()

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

	def update_state_of_game(self, player, clientSocket):
		"""	
		This function will wait for data from the tcp socket and it will update the game and player information 
		
		Example
		-------
		json data: {
			"open_card_name": clicked_card_name,
    		"position": clicked_card_position,
        	"pairs": pairs_found,
        	"turn": turns,
        	"match": is_match,
        	"n_face_up": face_up_cards,
        	"time_until_match": time_until_match,
			}
		"""

		data = json.loads(clientSocket.recv(1024).decode())

		clicked_card_name = data['game']['open_card_name']
		clicked_card_position = data['game']['position']
		face_up_cards = data['game']['n_face_up']
		match = data['game']['match']

		self._current_open_card_name = clicked_card_name
		self._current_open_card_position = clicked_card_position
		self._face_up_cards = face_up_cards

		row = clicked_card_position[0] + 1
		col = clicked_card_position[1] + 1

		print("Clicked card:", clicked_card_name, row, col, "\n")

		is_turn_even = self._turn % 2 == 0
		# reset clicks for the pair if a pair was found in the previous turn
		if player.get_last_pair_was_correct and is_turn_even is False:
			player.set_number_of_clicks_for_current_pair = 1
		else:
			player.set_number_of_clicks_for_current_pair += 1

		if self._face_up_cards == 2:
			player.set_last_pair_was_correct = True if match else False

			if player.get_last_pair_was_correct:
				self._board[clicked_card_name]['founded'] = True
				self._found_pairs += 1
				player.set_pairs = data['game']['pairs']

			# now there is no face up card so current_open is empty
			self._current_open_card_name = ''
			self._current_open_card_position = []

		self._turn += 1

		# update history of player
		player.update_history(clicked_card_name, clicked_card_position, match, self)

	##################################################################################################################
    #                                                   UTIL                                                         #
    ##################################################################################################################

	def print_board(self):
		print(json.dumps(self._board, indent=4))

	def is_game_ended(self):
		return self._found_pairs == 12

	@staticmethod
	def __print_board_as_matrix(shuffle_cards):
		board = np.zeros((6, 4))
		board = np.reshape(shuffle_cards, (4, 6))
		mx = len(max((sub[0] for sub in board), key=len))
		print("\n")
		for row in board:
			print(" ".join(["{:<{mx}}".format(ele, mx=mx) for ele in row]))
		print("\n")
