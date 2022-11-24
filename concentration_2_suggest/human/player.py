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

    
    def check_if_user_has_seen_a_card(self, suggested_card, suggested_position):
        """
        Returns an integer in order to understand if the user has already seen a card.

        Returns
            - 1: if it has been clicked only once
            - 2: it the card to open has never been clicked while the other one has been clicked multiple times
            - 3: if both had been clicked multiple times
            - 4: if the clicked card has been clicked multiple times while the other one has been clicked 0 times
            - 5: if the clicked card has been clicked only once while the other one multiple times
            - 6: if the clicked card has been clicked for the first time 
            - 0 otherwise
        """

        history = self._history
        # clicks of location to suggest
        clicks_of_card_to_open = 'times_that_second_was_clicked' if suggested_position == "is_first_opened" else "times_that_first_was_clicked"
        # clicks of location not suggested (regardless of whether it is face up or not)
        clicks_of_other_location = "times_that_second_was_clicked" if clicks_of_card_to_open == "times_that_first_was_clicked" else "times_that_first_was_clicked" 

        print("card suggested", clicks_of_card_to_open, history[suggested_card][clicks_of_card_to_open])
        print("other location", clicks_of_other_location, history[suggested_card][clicks_of_other_location])

        if history[suggested_card][clicks_of_card_to_open] == 1 and history[suggested_card][clicks_of_other_location] == 1:
            print("Hai visto entrambe le locazioni 1 volta")
            return 1

        if history[suggested_card][clicks_of_card_to_open] == 0 and history[suggested_card][clicks_of_other_location] > 1:
            print("Hai cliccato spesso l'altra locazione", clicks_of_other_location, "quindi clicca", clicks_of_card_to_open)
            return 2

        if history[suggested_card][clicks_of_card_to_open] > 1 and history[suggested_card][clicks_of_other_location] > 1:
            print("Hai cliccato entrambe spesso")
            return 3

        if history[suggested_card][clicks_of_card_to_open] > 1 and history[suggested_card][clicks_of_other_location] == 0:
            print("Hai cliccato spesso la locazione corrente", clicks_of_card_to_open, "quindi clicca l'altra", clicks_of_other_location)
            return 4

        if history[suggested_card][clicks_of_card_to_open] == 1 and history[suggested_card][clicks_of_other_location] > 1:
            print("L'altra l'hai vista spesso mentre questa una volta sola")
            return 5

        if history[suggested_card][clicks_of_card_to_open] > 1 and history[suggested_card][clicks_of_other_location] == 1:
            print("è la prima volta che scopri questa, ricordi l'altra?")
            return 6

        print("First time")
        return 0
