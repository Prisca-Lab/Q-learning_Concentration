# Q-learning_Concentration

## Project structure

  - ``Concentration_1_suggest`` is the folder that contains the agorithm that provides only one suggestion (the one after turning up the first card)
  - ``Concentration_2_suggest``, on the other hand, is the folder that contains the algorithm that provides two suggestions (before and after turning up the first card)
     - ``robot`` is the directory that contains all the files necessary for the agent to play by itself for training
        - ``plot`` is the directory which includes several plot images. If it is empty, the main script will automatically create the necessary folders, including a png and tex folders. The following folders will be created for both of them:
            - **Avg_of_moves_until_match**, the average number of moves it takes the agent to find each pair over time
            - **Avg_of_suggests_after_some_episode**, the average of suggestions provided by the agent for each pair over time
            - **avg_of_suggests_in_specific_episode**, the average of suggestions provided by the agent for each pair in a single episode
            - **Episode_Click_until_match**, i.e. how many moves it takes the agent to find a couple in an episode.
            - **Episode_length**, i.e how many moves it takes the agent to finish an episode
            - **Rewards**, which includes the plot of the episode's reward over time.
        - ``card`` is the class which includes all the utility functions for the card such as get a random card, get all cards that can be clicked, and so on
        - ``game`` is the class which includes the game board and the functions necessary to play such as make a move following the suggestions given by the agent
        - ``agent`` is the class that includes all the utility functions for the Q-learning algorithm, such as getting the next state, getting the reward or which suggestion to provide.
        - ``learning`` is the main file which includes the Q-learning algorithm
     - ``human`` is the directory that contains all the files necessary for human-robot interaction like the memory game interface
        - ``animal game`` is the directory that contains all the files which are necessary for the memory game, such as the html file, the js file and so on. the js file and so on
        - ``app.py`` is the *Flask server*, used to create a bridge between javascript and python. Whenever the user clicks on a card, data is sent to Flask and this data is sent to the Q-learning script via socket
        - the other files are similar to those in the 'robot' directory 
     - ``util`` is the directory that contains some utility files
        - ``constants.py``: it contains the state-action pair and reward values.
        - ``greedy.json``: the epsilon value after 100.000 games done by the agent. This value will be read into the human player file
        - ``matrix.npy``: the Q-table after 100,000 games played by the agent. This will be the matrix that will be used in the human player file.
        - ``plotting.py``: a file which includes utility functions to plot data. 
        - ``config.py``: the configuration file which include ip and server port
        - ``hints.txt``: a file that contains all the suggestions provided by the agent during all the episodes in the training phase
        - ``hints_with_human.txt``: a file that contains all the suggestion provided by the agent while the human player was playing
        - ``user_number.txt``: a counter used to create a different directory for each user who's gonna play the game
     - ``test``, which includes some unit test

## How to train the agent
In the robot folder: just run "learning.py".

## Game with 1 suggestion (suggestion for the second card)

### Q-table

Our state include cartesian product between:
  - the *last action* provided by the agent in the previous turn
  - the *game state* i.e. how many pairs the player has found (a game state includes 4 pairs)
  - the *user state* i.e. whether the player made match or not

Each action has a value in order to assign a reward:
  - none: 10
  - row or column: 5
  - card: 0.1

| State\Action | None | Suggest row or column | Suggest card |
| :---         |     :---:      |          ---: | ---: |
| `init_state`| | | 
| | | 
| `none_begin_correct`| | | 
| `none_begin_wrong`| | | 
| `rc_begin_correct`| | | 
| `rc_begin_wrong`| | | 
| `card_begin_correct`| | | 
| `card_begin_wrong`| | | 
| | | 
| `none_middle_correct`| | | 
| `none_middle_wrong`| | | 
| `rc_middle_correct`| | | 
| `rc_middle_wrong`| | | 
| `card_middle_correct`| | | 
| `card_middle_wrong`| | | 
| | | 
| `none_end_correct`| | | 
| `none_end_wrong`| | | 
| `rc_end_correct`| | | 
| `rc_end_wrong`| | | 
| `card_end_correct`| | | 
| `card_end_wrong`| | |  
| | | 

### Reward
Each time a pair has been found then a positive reward is assigned as follow: we divide the number of clicks it took to find a pair by the state of the game(beginning, middle, end) and the result will divide the constant assigned to the suggestion type.
For example, if at the beginning the number of clicks to find a pair was 8 then this number is divided by the state of the game(beginning in this case) which is worth 3. At this point if the suggested action was "nothing" then there will be a reward equal to 10/3

### How the agent provide a suggestion
For both row/column suggestion and card suggestion the agent will suggest the other face up card location in the current turn:
  - if the suggestion is "row or column" then it will check the number of face up cards in the row and column of the card to be suggested. If the number of face up cards in the row is greater than the number of face up cards in the column then it will suggest the column, row otherwise. If both the row and the column have few or no face up cards then it will choose randomly
  - if the suggestion is "card" it will simpy suggest the other location 
  
## Game with 2 suggestions (suggestion for both first and second card)

### Q-table

Our state include cartesian product between:
  - the *last action* provided by the agent in the previous turn
  - the *game state* i.e. how many pairs the player has found (a game state includes 4 pairs)
  - the *user state* i.e. whether the player made match or not and the suggestion they received on both the first and second card 

The actions have the same values as already said above.

| State\Action | None | Suggest row or column | Suggest card |
| :---         |     :---:      |          ---: | ---: |
| `init_state`| | | 
| | | 
| `FIRST_FLIPPING_NONE_BEGIN_CORRECT`| | | 
| `FIRST_FLIPPING_NONE_BEGIN_WRONG`| | | 
| `FIRST_FLIPPING_NONE_MIDDLE_CORRECT`| | | 
| `FIRST_FLIPPING_NONE_MIDDLE_WRONG`| | | 
| `FIRST_FLIPPING_NONE_END_CORRECT`| | | 
| `FIRST_FLIPPING_NONE_END_WRONG`| | | 
| | | 
| `FIRST_FLIPPING_RC_BEGIN_CORRECT`| | | 
| `FIRST_FLIPPING_RC_BEGIN_WRONG`| | | 
| `FIRST_FLIPPING_RC_MIDDLE_CORRECT`| | | 
| `FIRST_FLIPPING_RC_MIDDLE_WRONG`| | | 
| `FIRST_FLIPPING_RC_END_CORRECT`| | | 
| `FIRST_FLIPPING_RC_END_WRONG`| | | 
| | | 
| `FIRST_FLIPPING_CARD_BEGIN_CORRECT`| | | 
| `FIRST_FLIPPING_CARD_BEGIN_WRONG`| | | 
| `FIRST_FLIPPING_CARD_MIDDLE_CORRECT`| | | 
| `FIRST_FLIPPING_CARD_MIDDLE_WRONG`| | | 
| `FIRST_FLIPPING_CARD_END_CORRECT`| | | 
| `FIRST_FLIPPING_CARD_END_WRONG`| | | 
| | | 
| `SECOND_FLIPPING_NONE_BEGIN_CORRECT`| | | 
| `SECOND_FLIPPING_NONE_BEGIN_WRONG`| | | 
| `SECOND_FLIPPING_NONE_MIDDLE_CORRECT`| | | 
| `SECOND_FLIPPING_NONE_MIDDLE_WRONG`| | | 
| `SECOND_FLIPPING_NONE_END_CORRECT`| | | 
| `SECOND_FLIPPING_NONE_END_WRONG`| | | 
| | | 
| `SECOND_FLIPPING_RC_BEGIN_CORRECT`| | | 
| `SECOND_FLIPPING_RC_BEGIN_WRONG`| | | 
| `SECOND_FLIPPING_RC_MIDDLE_CORRECT`| | | 
| `SECOND_FLIPPING_RC_MIDDLE_WRONG`| | | 
| `SECOND_FLIPPING_RC_END_CORRECT`| | | 
| `SECOND_FLIPPING_RC_END_WRONG`| | | 
| | | 
| `SECOND_FLIPPING_CARD_BEGIN_CORRECT`| | | 
| `SECOND_FLIPPING_CARD_BEGIN_WRONG`| | | 
| `SECOND_FLIPPING_CARD_MIDDLE_CORRECT`| | | 
| `SECOND_FLIPPING_CARD_MIDDLE_WRONG`| | | 
| `SECOND_FLIPPING_CARD_END_CORRECT`| | | 
| `SECOND_FLIPPING_CARD_END_WRONG`| | | 
| | | 

### Reward
In this case we also need to considerate the action provided in the previous turn, so the reward is assigned as follow:
(last_action * current_action)/(number_of_clicks_before_match/game_state).
Some pairs are not symmetrical, for example the pair (nothing, card) is different from the pair (card, nothing) since with the first one we have a 100% match while with the second one we cannot say the same. Depending on the pair we will add or remove a bonus from the reward.
We only have two asymmetrical pairs: 
  - (card, none) where a 25% bonus is added since we rely on the user's memory because the suggested position is opposite to the most clicked position (of the same card)
  - (row/column, none) where a 25% bonus is removed because the user might get confused if he finds out a card that he has never seen whereas this is not true for (none, row/column) because the user understands that the card that allows him to match is in a certain row or column

### How the agent provide a suggestion
The suggestions on the second card work as written above.
When the agent suggests the first card, he will choose one of the most clicked cards. Finally, it will suggest the least clicked location of the chosen card.

## How the agent play
The robot player will make a move following one of the suggestion provided by the agent as follow:
  - when the suggestion is "card" then it will simply open the position suggested by the agent. If the suggestion is provided for the second card then it will be a 100% match.
  - when the suggestion is "row or column" it will open a card of row or column suggested. Considering that the board is 6x4 then the probability of a match when the suggestion is "row" is 1/6, 1/4 otherwise.
  - when the suggestion is "none", at the beginning it will choose randomly but as the game progresses the probability of making matches will increase. When that probability is greater than or equal to 50% then it will be randomly chosen whether to provide to the robot player the correct card to make match.
  The probability is calculated as follows:
  
  N = number of pairs to find

2N = number of cards to find

T = number of tries

Probability of a match:
<p align="center">
  $\mathbb{P}(E) = \frac{1}{2N - 1}$
</p>

Probability of not making match
<p align="center">
  $1 - \mathbb{P}(E)$
</p>

Probability of not making match after t attempts
<p align="center">
  $(1 - \mathbb{P}(E))^T$
</p>

## How to play with agent's suggestions
In the human directory:
  - "ipconfig" on terminal/powershell  
  ![Immagine](https://user-images.githubusercontent.com/64232060/199301970-505946f8-2451-4d2a-ba05-6c53db737599.png)
  - write your ip into "config.json" and into js file (human\animal_game\static\js)
  - ![Immagine](https://user-images.githubusercontent.com/64232060/199302552-63c34f4d-1937-4d65-9cdc-f27a7577fcd7.png)
  - run **app.py**
  - then, run **learning.py**
  - go to "http://192.168.X.Y:5000/"
  
 N.B.: you need to install flask, flask-socketio, pandas, matplotlib, numpy

## UI
credit: https://github.com/yunkii/animal-memory-game
