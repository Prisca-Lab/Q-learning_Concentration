from card import Card
from player import Player
from game import Game

class Environment:
    def __init__(self):
        self.__game = Game()
        self.__player = Player(self.__game)

    def __reset(self):
        self.__game.reset()
        self.__player.reset()
        self.__player.game = self.__game
        # in order to create the player history game must be initialized first
        self.__player.create_history()

    def start(self):
        self.__reset()

    def get_player(self):
        return self.__player
    
    def get_game(self):
        return self.__game

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
    
    def get_other_location(self, card):
        game_board = self.__game.board
        return Card.get_other_location_of_open_card(card, game_board)
    
    def get_cards_by_index(self, type, index):
        game_board = self.__game.board
        return Card.get_face_up_cards_by_index(type, index, game_board)
    
    def was_last_move_a_match(self):
        return self.__player.last_match
    
    def is_game_finished(self):
        return self.__game.is_game_ended()
    
    def print_player_history(self):
        self.__player.print_history()
    
    def get_least_clicked_location_of_most_clicked_card(self):
        history = self.__player.history

        return self.__game.get_least_clicked_location_of_most_clicked_pair(history)