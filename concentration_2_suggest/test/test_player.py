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
            "times_that_first_was_clicked": 10,
            "is_first_opened": False,
            "second_pos": [
                2,
                2
            ],
            "times_that_second_was_clicked": 5,
            "is_second_opened": False,
            "founded": True
        },
        "tiger": {
            "first_pos": [
                0,
                0
            ],
            "times_that_first_was_clicked": 1,
            "is_first_opened": False,
            "second_pos": [
                0,
                3
            ],
            "times_that_second_was_clicked": 1,
            "is_second_opened": False,
            "founded": True
        },
        "horse": {
            "first_pos": [
                0,
                4
            ],
            "times_that_first_was_clicked": 7,
            "is_first_opened": False,
            "second_pos": [
                1,
                1
            ],
            "times_that_second_was_clicked": 3,
            "is_second_opened": False,
            "founded": False
        },
        "duck": {
            "first_pos": [
                2,
                0
            ],
            "times_that_first_was_clicked": 2,
            "is_first_opened": False,
            "second_pos": [
                2,
                3
            ],
            "times_that_second_was_clicked": 3,
            "is_second_opened": False,
            "founded": True
        },
        "penguin": {
            "first_pos": [
                2,
                5
            ],
            "times_that_first_was_clicked": 4,
            "is_first_opened": False,
            "second_pos": [
                3,
                1
            ],
            "times_that_second_was_clicked": 0,
            "is_second_opened": False,
            "founded": False
        },
        "koala": {
            "first_pos": [
                0,
                5
            ],
            "times_that_first_was_clicked": 7,
            "is_first_opened": False,
            "second_pos": [
                3,
                3
            ],
            "times_that_second_was_clicked": 7,
            "is_second_opened": False,
            "founded": False
        },
        "bird": {
            "first_pos": [
                1,
                4
            ],
            "times_that_first_was_clicked": 1,
            "is_first_opened": False,
            "second_pos": [
                3,
                2
            ],
            "times_that_second_was_clicked": 7,
            "is_second_opened": False,
            "founded": True
        },
        "shark": {
            "first_pos": [
                0,
                1
            ],
            "times_that_first_was_clicked": 4,
            "is_first_opened": False,
            "second_pos": [
                3,
                5
            ],
            "times_that_second_was_clicked": 2,
            "is_second_opened": False,
            "founded": False
        },
        "flamingo": {
            "first_pos": [
                1,
                0
            ],
            "times_that_first_was_clicked": 7,
            "is_first_opened": False,
            "second_pos": [
                1,
                3
            ],
            "times_that_second_was_clicked": 1,
            "is_second_opened": False,
            "founded": False
        },
        "goose": {
            "first_pos": [
                1,
                5
            ],
            "times_that_first_was_clicked": 0,
            "is_first_opened": False,
            "second_pos": [
                2,
                4
            ],
            "times_that_second_was_clicked": 0,
            "is_second_opened": False,
            "founded": False
        },
        "walrus": {
            "first_pos": [
                0,
                2
            ],
            "times_that_first_was_clicked": 0,
            "is_first_opened": False,
            "second_pos": [
                2,
                1
            ],
            "times_that_second_was_clicked": 0,
            "is_second_opened": False,
            "founded": False
        },
        "pelican": {
            "first_pos": [
                3,
                0
            ],
            "times_that_first_was_clicked": 0,
            "is_first_opened": False,
            "second_pos": [
                3,
                4
            ],
            "times_that_second_was_clicked": 0,
            "is_second_opened": False,
            "founded": False
        }
    }
    

    def setUp(self):
        self.player = Player()
        self.game = Game()
        self.game.set_board = self.game_board
        self.game.set_turn = 7
        self.player.set_click_for_pair = 5
        self.player.set_pairs = 1
        self.player.set_history = self.game_board


    def test_check_if_the_player_data_are_updated_correctly(self):
        # first turn of a move
        suggest = "card"
        card_suggested = "flamingo"
        position_suggested = [1, 0]

        clicked_card_name, clicked_card_pos, match = self.player.play(suggest, card_suggested, position_suggested,
                                                                      self.game)
        self.assertEqual(card_suggested, clicked_card_name)
        self.assertEqual(position_suggested, clicked_card_pos)
        self.assertFalse(match)
        self.assertEqual(self.player.get_number_of_clicks_for_current_pair, 1)

        # suggest again a card
        suggest = "card"
        card_suggested = "flamingo"
        position_suggested = [1, 3]

        clicked_card_name, clicked_card_pos, match = self.player.play(suggest, card_suggested, position_suggested,
                                                                      self.game)
        self.assertEqual(card_suggested, clicked_card_name)
        self.assertEqual(position_suggested, clicked_card_pos)
        self.assertTrue(match)
        self.assertEqual(self.player.get_number_of_clicks_for_current_pair, 2)  # 2 click for match
        self.assertEqual(self.player.get_pairs, 2)                              # from 1 pair to 2 pairs
        self.assertTrue(self.player.get_last_pair_was_correct)                  # the player has found a new pair

        # get random card and check if click counter has been reset
        clicked_card_name, clicked_card_pos, match = self.player.play("none", "", [], self.game)
        self.assertEqual(self.player.get_number_of_clicks_for_current_pair, 1)  # reset for the new card 

        
if __name__ == '__main__':
    unittest.main()