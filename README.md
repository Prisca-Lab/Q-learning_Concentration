# Q-learning_Concentration
The project consists of a memory game in which the agent, using the Q-learning algorithm, learns how to provide assistance to the user. Once it learns the optimal policy it uses Theory of Mind to provide more targeted and useful assistance.

This work is described in the following pubblication:
**A.Andriella, G.Falcone, S. Rossi, "Enhancing Robot Assistive Behaviour with Reinforcement Learning and Theory of Mind", Submitted to IROS 2023**
## Project structure
- ``concentration_1_suggest`` is the folder which contains a first approach to the problem. In this case the agent can help only on the second flip.
- ``concentration_2_suggest`` is the folder in which the agent can suggest before and after the first flip. It's the main folder, which contains the Theory of Mind agent.
### Folders structure
- ``human``: Contains the Flask application and web interface for the human player and the files to receive assistance by the agent. The ToM files are ``agent`` and ``player``.
- ``robot``: Contains files for the agent to learn how to provide assistance
	- ``agent``: contains the functions for the Q-learning agent
	- ``environment``: contains the definition of the game environment
	- ``game``: contains the functions needed to play the memory game
	- ``card``: contains the utility functions for the game and the player (card available, most clicked card, ...)
	- ``player``: contains the definition of the player
	- ``q-learning``: contains the Q-learning algorithm
	- ``main``: contains the main code to run the game
- ``test``: contains files for running unit tests
- ``util``: contains the utility functions for the project (plot, storing data, ...)
## Installation instructions
```bash
pip install -r requirements.txt
```
### How to train the agent
```bash
# in the robot folder
py main.py
```

### How to play with agent's suggestions
In the human directory:
  1. "ipconfig" on terminal/powershell 
  ![Immagine](https://user-images.githubusercontent.com/64232060/199301970-505946f8-2451-4d2a-ba05-6c53db737599.png)
  
  2. write your ip into "**config.json**" and into js file (human\animal_game\static\js)
    - ![Immagine](https://user-images.githubusercontent.com/64232060/199302552-63c34f4d-1937-4d65-9cdc-f27a7577fcd7.png)
    - ![ipflask](https://user-images.githubusercontent.com/64232060/222992692-8cc3b8c2-3bac-4291-b6c0-74f2e447f470.png)

  3. run the Flask application
  
  ```bash
  py app.py
  ```

  4. run the agent 
  
  ```bash
  py play.py
  ```
  5. Access to the following address to play the game with UI helped by the robot
  
  ```javascript
  http://192.168.X.Y:5000/
  ```

## Robot folder
The agent will provide suggestions using the Furhat SDK. You can see the repo here: https://github.com/GiovanniFalcone/Concentration_furhat

## UI
credit: https://github.com/yunkii/animal-memory-game
