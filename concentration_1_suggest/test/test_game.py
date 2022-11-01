import unittest

import sys 
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'robot'))

from card import Card
from player import Player
from game import Game

class GameTestCase(unittest.TestCase):

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
        self.game = Game()
        self.game.set_board = self.game_board
        self.game.set_current_open_card_name = 'flamingo'
        self.game.set_current_open_card_position = [1, 0]

    def test_move_with_card_suggestion(self):
        # card open is 'flamingo' in position [1, 0] so the agent will suggest [1, 3] 
        # in this way we have a match
        card_suggested = "flamingo"
        position_suggested = [1, 3]
        clicked_card, clicked_position, which_is_clicked, match = self.game.make_move_by_card(card_suggested, 
                                                                                              position_suggested)
        self.assertEqual(clicked_card, clicked_card)
        self.assertEqual(clicked_position, clicked_position)
        self.assertEqual(which_is_clicked, 'is_second_opened')
        self.assertTrue(match, True)

    def test_move_with_row_suggestion(self):
        # card open is 'flamingo' in position [1, 0], the second position is [1, 3] 
        # so, the agent will suggest row 1
        # then, only the cards in row 1 will be clickable
        type_of_suggest = "row"
        number_of_suggest = 1
        _, clicked_position, _, _ = self.game.make_move_by_grid(type_of_suggest, number_of_suggest)
        self.assertEqual(clicked_position[0], number_of_suggest)

if __name__ == '__main__':
    unittest.main()

