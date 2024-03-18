# Q-learning_Concentration
The project consists of a memory game in which the agent, using the Q-learning algorithm, learns how to provide assistance to the user. Once it learns the optimal policy it uses Theory of Mind to provide more targeted and useful assistance.

## Project structure
- ``concentration_1_suggest`` is the folder which contains a first approach to the problem. In this case the agent can help only on the second flip.
- ``concentration_2_suggest`` is the folder in which the agent can suggest before and after the first flip. It's the main folder, which contains the Theory of Mind agent.
## Installation instructions
```bash
pip install -r requirements.txt
```
### How to train the agent
N.B.: the agent is already trained!
```bash
# in the robot folder
py main.py
```

### How to play with agent's suggestions
If you want to play with agent's suggestions you can find a tutorial here: https://drive.google.com/file/d/1irXKeHzRwjW5KeJAQs-9mCeZEr_bzscU/view?usp=sharing

### Demo
A demo on how to start the program and how to play is available at this link: https://drive.google.com/file/d/1tr41x4EwkZHiFOsofJ6gxm_XytnNoaQO/view?usp=sharing
P.s it's a little be slow because of OBS.

## Robot folder
The agent will provide suggestions using the Furhat SDK. You can see the repo here: https://github.com/GiovanniFalcone/Concentration_furhat

## UI
credit: https://github.com/yunkii/animal-memory-game
