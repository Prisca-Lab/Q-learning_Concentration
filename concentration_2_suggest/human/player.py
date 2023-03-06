import json

from card import Card

class Player:
    def __init__(self, game):
        """
        Initialize the Player object.

        Parameters:
        ----------
        game (Game): a Game object to associate with the player.

        Attributes:
        history (dict): A dictionary that tracks the player's card history.
            The key is the name of the card, while the value is a dictionary with the following keys:
                - card (str): the name of the card.
                - first_pos (int): the number of times the first position of the card has been clicked.
                - second_pos (int): the number of times the second position of the card has been clicked.
        last_match (bool): True if the previous move was a match, False otherwise.
        flip_number (int): The number of flip made by the player before they find a pair.
        pairs_found (int): The number of pairs found by the player.
        previous_card_name (str): The name of the card selected in the previous move.
        """
        self.game = game
        self.history = {}
        self.last_match = False
        self.flip_number = 0
        self.pairs_found = 0
        self.previous_card_name = ''

    def reset(self):
        """
        Reset the player's attributes to their initial values.
        """
        self.game = None
        self.history = {}
        self.last_match = False
        self.flip_number = 0
        self.pairs_found = 0
        self.previous_card_name = ''

    def create_history(self):
        k = 0
        for i in range(self.game.num_rows):
            for j in range(self.game.num_cols):
                card = self.game.shuffled[k]

                if card in self.history:
                    self.history[card]['second_pos'] = [i, j]
                else:
                    self.history[card] = {
                        'first_pos': [i, j],          
                        'is_first_opened': False,           
                        'times_that_first_was_clicked': 0,  
                        'second_pos': [-1, -1],
                        'is_second_opened': False,
                        'times_that_second_was_clicked': 0,
                        'founded': False                      
                    }
                k += 1

    def update_data_player(self, card, position, match):
        """
        This function modifies the player's data by updating their pair-finding progress and click counter.

        Parameters:
        -----------
            card (str): The name of clicked card
            position (tuple): The coordinates of clicked card
            match (bool): A boolean value indicating whether the two flipped cards in the current turn form a matching pair.

        Returns:
        ----------
            None
        """

        is_turn_even = (self.game.turns - 1) % 2 == 0

        if self.last_match and is_turn_even is False:
             self.flip_number = 1
        else:
             self.flip_number += 1
        
        if is_turn_even:
            self.last_match = True if match else False

            if self.last_match:
                self.pairs_found += 1

        self.__update_history(card, position, match)

    def __update_history(self, clicked_card_name, clicked_card_position, match):
        """
        This method updates the history of the game with the information of the clicked card.

        Parameters:
        ----------
            clicked_card_name (str): The name of the card that was clicked.
            clicked_card_position (tuple): A tuple containing the row and column indices of the clicked card.
            match (bool): A boolean value indicating whether the two flipped cards in the current turn form a matching pair.
        """
        is_turn_even = (self.game.turns - 1) % 2 == 0

        if self.history[clicked_card_name]['first_pos'] == clicked_card_position:
            # update first location
            self.history[clicked_card_name]['times_that_first_was_clicked'] += 1
            self.history[clicked_card_name]['is_first_opened'] = True
            which_is_open = 'is_first_opened'
        else:
            # update first location
            self.history[clicked_card_name]['times_that_second_was_clicked'] += 1
            self.history[clicked_card_name]['is_second_opened'] = True
            which_is_open = 'is_second_opened'

        if match and is_turn_even:
            self.history[clicked_card_name]['founded'] = True

        # after a move turn down previous card
        if is_turn_even:
            which_flag = Card.get_which_is_open(self.previous_card_name, self.history)
            self.history[self.previous_card_name][which_flag] = False
            self.history[clicked_card_name][which_is_open] = False
            self.previous_card_name = ''

        self.previous_card_name = clicked_card_name

    def print_history(self):
        print(json.dumps(self.history, indent=4))

    
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

        history = self.history
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
