import json

from card import Card
from player import Player
from game import Game

class Environment:
    def __init__(self, socket, server_name):
        self.socket = socket
        self.__game = Game()
        self.__player = Player(self.__game)
        self.server_name = server_name

    def __reset(self):
        json_board = self.socket.recv(1024)
        game_board = json.loads(json_board.decode())['matrix']

        self.__game.reset(game_board)
        self.__player.reset()
        self.__player.game = self.__game
        # in order to create the player history game must be initialized first
        self.__player.create_history()
        self.__player.print_history()

    def start(self):
        self.__reset()

    def update_environment(self):
        data = json.loads(self.socket.recv(1024).decode())

        clicked_card_name = data['game']['open_card_name']
        clicked_card_position = data['game']['position']
        match = data['game']['match']

        self.__game.update_state_of_game(clicked_card_name, clicked_card_position, match)
        self.__player.update_data_player(clicked_card_name, clicked_card_position, match)

    def get_server_name(self):
        return self.server_name
    
    def get_socket(self):
        return self.socket

    def get_turn(self):
        return self.__game.turns
    
    def get_pairs_found(self):
        return self.__player.pairs_found
    
    def get_flip_number(self):
        return self.__player.flip_number
    
    def play(self, suggestion):
        return self.__player.play(suggestion)
    
    def get_current_open_card(self):
        return self.__game.current_open_card_name
    
    def get_current_open_card_pos(self):
        return self.__game.current_open_card_position
    
    def get_board(self):
        return self.__game.board
    
    def get_other_location(self, card, pos):
        game_board = self.__game.board
        return Card.get_other_location_of_open_card(card, pos, game_board)
    
    def get_cards_by_index(self, type, index):
        game_board = self.__game.board
        current_open_pos = self.__game.current_open_card_position
        return Card.get_face_up_cards_by_index(type, index, game_board, current_open_pos)
    
    def was_last_move_a_match(self):
        return self.__player.last_match
    
    def is_game_finished(self):
        return self.__game.is_game_ended()
    
    def get_history(self):
        return self.__player.history
    
    def print_player_history(self):
        self.__player.print_history()
    
    def get_least_clicked_location_of_most_clicked_card(self):
        history = self.__player.history
        return self.__game.get_least_clicked_location_of_most_clicked_pair(history)
    
    def check_if_user_has_seen_a_card(self, card, which_to_open):
        return self.__player.check_if_user_has_seen_a_card(card, which_to_open)
    
    def get_least_clicked_location_of_most_clicked_card(self):
        history = self.__player.history
        return self.__game.get_least_clicked_location_of_most_clicked_pair(history)
    
    def get_random_card(self):
        return self.__game.get_random_card()
        
    def get_least_clicked_location_from_visitated(self):
        return self.__game.get_least_clicked_location_from_visitated(self.__player.history)