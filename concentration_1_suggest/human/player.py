import random


class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self._pairs = 0
        self._last_pair_was_correct = False
        self._click_for_pair = 1
        
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
