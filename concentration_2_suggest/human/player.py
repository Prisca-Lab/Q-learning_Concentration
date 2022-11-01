import json

from card import Card

class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self._pairs = 0
        self._last_pair_was_correct = False
        self._click_for_pair = 0
        self._history = {}
        self._previous_card_name = ''

    @property
    def get_pairs(self):
        return self._pairs

    @get_pairs.setter
    def set_pairs(self, value):
        self._pairs = value

    @property
    def get_last_pair_was_correct(self):
        return self._last_pair_was_correct

    @get_last_pair_was_correct.setter
    def set_last_pair_was_correct(self, value):
        self._last_pair_was_correct = value

    @property
    def get_number_of_clicks_for_current_pair(self):
        return self._click_for_pair

    @get_number_of_clicks_for_current_pair.setter
    def set_number_of_clicks_for_current_pair(self, value):
        self._click_for_pair = value

    @property
    def get_history(self):
        return self._history

    @get_history.setter
    def set_history(self, value):
        self._history = value


    def create_history(self, shuffle_cards):
        k = 0
        for i in range(4):
            for j in range(6):
                card = shuffle_cards[k]
                if card in self._history:
                    self._history[card]['second_pos'] = [i, j]
                else:
                    self._history[card] = {
                        'first_pos': [i, j],          
                        'is_first_opened': False,           
                        'times_that_first_was_clicked': 0,  
                        'second_pos': [-1, -1],
                        'is_second_opened': False,
                        'times_that_second_was_clicked': 0,
                        'founded': False                      
                    }
                k += 1


    def update_history(self, clicked_card_name, clicked_card_position, match, game):
        if self._history[clicked_card_name]['first_pos'] == clicked_card_position:
            # update first location
            self._history[clicked_card_name]['times_that_first_was_clicked'] += 1
            self._history[clicked_card_name]['is_first_opened'] = True
            which_is_open = 'is_first_opened'
        else:
            # update first location
            self._history[clicked_card_name]['times_that_second_was_clicked'] += 1
            self._history[clicked_card_name]['is_second_opened'] = True
            which_is_open = 'is_second_opened'

        is_turn_even = (game.get_turn - 1) % 2 == 0

        if match and is_turn_even:
            self._history[clicked_card_name]['founded'] = True

        # after a move turn down previous card
        if is_turn_even:
            which_flag = Card.get_which_is_open(self._previous_card_name, self._history)
            self._history[self._previous_card_name][which_flag] = False
            self._history[clicked_card_name][which_is_open] = False
            self._previous_card_name = ''

        self._previous_card_name = clicked_card_name

    def print_history(self):
        print(json.dumps(self._history, indent=4))
