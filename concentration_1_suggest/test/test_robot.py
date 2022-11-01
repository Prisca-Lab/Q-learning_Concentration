import unittest

import sys 
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'robot'))

from agent import Agent
from game import Game
from player import Player

class RobotTestCase(unittest.TestCase):

    def setUp(self):
        self.agent = Agent()
        self.cards = {
            'flamingo': 
            {
                'first_pos': [1, 0], 'is_first_opened': True,
                'second_pos': [1, 3], 'is_second_opened': False,
                'founded': False
            },
            'panda': 
            {
                'first_pos': [1, 2], 'is_first_opened': False, 
                'second_pos': [2, 2], 'is_second_opened': False, 
                'founded': True
            },
            'tiger': 
            {
                'first_pos': [0, 0], 'is_first_opened': False, 
                'second_pos': [0, 3], 'is_second_opened': False, 
                'founded': True
            },
            'pelican': 
            {
                'first_pos': [3, 0], 'is_first_opened': False, 
                'second_pos': [3, 4], 'is_second_opened': False, 
                'founded': False
            }
        }
        self.game = Game()
        self.game.set_current_open_card_name = 'flamingo'
        self.game.set_board = self.cards
        self.player = Player()
        self.player.set_last_pair_was_correct = True
        self.player.set_number_of_clicks_for_current_pair = 6


    def test_if_return_next_state_correctly(self):
        ACTION_SUGGEST_ROW_COL = 1
        RC_BEGIN_CORRECT = 3
        face_up_cards = 1
        founded_pairs = 3
        last_match = True
        next_state = self.agent.get_next_state(ACTION_SUGGEST_ROW_COL, face_up_cards, founded_pairs, last_match)
        self.assertEqual(next_state, RC_BEGIN_CORRECT)

    
    def test_checks_if_the_suggestion_provided_is_the_same_as_the_action_passed_as_the_argument(self):
        ACTION_SUGGEST_CARD = 2
        suggest, card, position = self.agent.take_action(ACTION_SUGGEST_CARD, self.game)
        self.assertEqual("card", suggest)

    
    def test_check_if_agent_suggest_other_position_of_open_card(self):
        ACTION_SUGGEST_CARD = 2
        suggest, card, position = self.agent.take_action(ACTION_SUGGEST_CARD, self.game)
        self.assertEqual(position, [1, 3])

    
    def test_if_reward_is_correct(self):
        self.game.set_face_up_cards = 2
        NONE_MIDDLE_CORRECT = 7 # current state
        SUGGEST_ROW_COLUMN = 1

        reward = self.agent.get_reward(NONE_MIDDLE_CORRECT, SUGGEST_ROW_COLUMN, self.player, self.game)
        
        self.assertEqual(reward, 2.5)

if __name__ == '__main__':
    unittest.main()