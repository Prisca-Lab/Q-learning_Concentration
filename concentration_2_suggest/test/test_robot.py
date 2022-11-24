import unittest

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'robot'))

from agent import Agent
from player import Player
from game import Game

class RobotTestCase(unittest.TestCase):

    def setUp(self):
        self.agent = Agent()
        self.cards = {
            'flamingo': 
            {
                'times_that_first_was_clicked': 10, 'first_pos': [1, 0], 'is_first_opened': False,
                'times_that_second_was_clicked': 0, 'second_pos': [1, 3], 'is_second_opened': False,
                'founded': False
            },
            'panda': 
            {
                'times_that_first_was_clicked': 0, 'first_pos': [1, 2], 'is_first_opened': False, 
                'times_that_second_was_clicked': 0, 'second_pos': [2, 2], 'is_second_opened': False, 
                'founded': True
            },
            'tiger': 
            {
                'times_that_first_was_clicked': 0, 'first_pos': [0, 0], 'is_first_opened': False, 
                'times_that_second_was_clicked': 0, 'second_pos': [0, 3], 'is_second_opened': False, 
                'founded': True
            },
            'pelican': 
            {
                'times_that_first_was_clicked': 0, 'first_pos': [3, 0], 'is_first_opened': False, 
                'times_that_second_was_clicked': 0, 'second_pos': [3, 4], 'is_second_opened': False, 
                'founded': False
            }
        }
        self.game = Game()
        self.game.set_current_open_card_name = ''
        self.game.set_board = self.cards    
        self.player = Player()
        self.player.set_last_pair_was_correct = True
        self.player.set_number_of_clicks_for_current_pair = 6
        self.player.set_history = self.cards


    def test_if_return_next_state_correctly(self):
        SUGGEST_CARD = 2
        SECOND_FLIPPING_SUGGEST_CARD_BEGIN_CORRECT = 31
        face_up_cards = 1 
        founded_pairs = 3 # begin
        turn = 8
        last_match = True 
        next_state = self.agent.get_next_state(SUGGEST_CARD, face_up_cards, turn,
                                               founded_pairs, last_match)
        self.assertEqual(next_state, SECOND_FLIPPING_SUGGEST_CARD_BEGIN_CORRECT)


    
    def test_checks_if_the_suggestion_provided_is_the_same_as_the_action_passed_as_the_argument(self):
        ACTION_SUGGEST_CARD = 2
        suggest, _, _ = self.agent.take_action(ACTION_SUGGEST_CARD, self.player, self.game)
        self.assertEqual("card", suggest)

    
    def test_check_if_agent_suggest_other_position_of_most_clicked_card(self):
        # this is the suggestion on the first card
        ACTION_SUGGEST_CARD = 2
        suggest, card, position = self.agent.take_action(ACTION_SUGGEST_CARD, self.player, self.game)
        self.assertEqual(position, [1, 3])


    def test_if_reward_is_correct(self):
        clicks_until_match = self.player.get_number_of_clicks_for_current_pair
        self.game.set_face_up_cards = 2
        self.player.set_pairs = 4                       # middle state
        SECOND_FLIPPING_SUGGEST_RC_MIDDLE_WRONG  = 28   # current state with last action RC
        SUGGEST_ROW_COLUMN = 1                          # current action
        REWARD_RC = 0.1
        MIDDLE_STATE = 2

        result = REWARD_RC * clicks_until_match * MIDDLE_STATE
        

        reward = self.agent.get_reward(SECOND_FLIPPING_SUGGEST_RC_MIDDLE_WRONG, SUGGEST_ROW_COLUMN, 
                                       self.player, self.game)
        
        self.assertEqual(reward, result)

if __name__ == '__main__':
    unittest.main()