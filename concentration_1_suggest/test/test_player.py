import unittest

import sys 
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'robot'))

from player import Player
from game import Game

class PlayerTestCase(unittest.TestCase):

    game_board = {
        "panda": {
            "first_pos": [
                1,
                2
            ],
            "is_first_opened": False,
            "second_pos": [
                2,
                2
            ],
            "is_second_opened": False,
            "founded": True
        },
        "tiger": {
            "first_pos": [
                0,
                0
            ],
            "is_first_opened": False,
            "second_pos": [
                0,
                3
            ],
            "is_second_opened": False,
            "founded": True
        },
        "horse": {
            "first_pos": [
                0,
                4
            ],
            "is_first_opened": False,
            "second_pos": [
                1,
                1
            ],
            "is_second_opened": False,
            "founded": False
        },
        "duck": {
            "first_pos": [
                2,
                0
            ],
            "is_first_opened": False,
            "second_pos": [
                2,
                3
            ],
            "is_second_opened": False,
            "founded": True
        },
        "penguin": {
            "first_pos": [
                2,
                5
            ],
            "is_first_opened": False,
            "second_pos": [
                3,
                1
            ],
            "is_second_opened": False,
            "founded": False
        },
        "koala": {
            "first_pos": [
                0,
                5
            ],
            "is_first_opened": False,
            "second_pos": [
                3,
                3
            ],
            "is_second_opened": False,
            "founded": False
        },
        "bird": {
            "first_pos": [
                1,
                4
            ],
            "is_first_opened": False,
            "second_pos": [
                3,
                2
            ],
            "is_second_opened": False,
            "founded": True
        },
        "shark": {
            "first_pos": [
                0,
                1
            ],
            "is_first_opened": False,
            "second_pos": [
                3,
                5
            ],
            "is_second_opened": False,
            "founded": False
        },
        "flamingo": {
            "first_pos": [
                1,
                0
            ],
            "is_first_opened": True,
            "second_pos": [
                1,
                3
            ],
            "is_second_opened": False,
            "founded": False
        },
        "goose": {
            "first_pos": [
                1,
                5
            ],
            "is_first_opened": False,
            "second_pos": [
                2,
                4
            ],
            "is_second_opened": False,
            "founded": False
        },
        "walrus": {
            "first_pos": [
                0,
                2
            ],
            "is_first_opened": False,
            "second_pos": [
                2,
                1
            ],
            "is_second_opened": False,
            "founded": False
        },
        "pelican": {
            "first_pos": [
                3,
                0
            ],
            "is_first_opened": False,
            "second_pos": [
                3,
                4
            ],
            "is_second_opened": False,
            "founded": False
        }
    }
    

    def setUp(self):
        self.player = Player()
        self.game = Game()
        self.game.set_board = self.game_board
        self.game.set_current_open_card_name = 'flamingo'
        self.game.set_current_open_card_position = [1, 0]
        self.game.set_turn = 8
        self.player.set_click_for_pair = 5
        self.player.set_pairs = 1

    def test_check_if_the_player_data_are_updated_correctly(self):
        suggest = "card"
        card_suggested = "flamingo"
        position_suggested = [1, 3]

        clicked_card_name, clicked_card_pos, match = self.player.play(suggest, card_suggested, position_suggested,
                                                                      self.game)

        self.assertEqual(card_suggested, clicked_card_name)
        self.assertEqual(position_suggested, clicked_card_pos)
        self.assertTrue(match)
        self.assertEqual(self.player.get_number_of_clicks_for_current_pair, 1)  # reset the counter
        self.assertEqual(self.player.get_pairs, 2)                              # from 1 pair to 2 pairs
        self.assertTrue(self.player.get_last_pair_was_correct)                  # the player has found a new pair

        
if __name__ == '__main__':
    unittest.main()