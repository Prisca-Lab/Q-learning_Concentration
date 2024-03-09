import requests
import socket
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

from util import constants
from util import Util

from learning.qlearning_elements import actions, states, epsilon, alpha, gamma
from learning.learning import Qlearning
from game.environment import Environment

# get param received from server, if any
ID_PLAYER, EXPERIMENTAL_CONDITION = Util.get_argv_param(sys.argv)

# read ip and port from config file
SERVER_IP = Util.get_from_json_file("config")['ip'] 
SERVER_PORT = int(Util.get_from_json_file("config")['port'])

# send to Flask the first HTTP request to start the game
requests.post("http://" + SERVER_IP + ":5000/id_player", json={'id_player': ID_PLAYER})

#create TCP socket and connection to remote server
client_socket = Util.connect_to_server(SERVER_IP, SERVER_PORT)

# define the number of games that the agent will plays
EPISODES = constants.EPISODES_WITH_HUMAN

# Read from file the Q-table of robot training
Q_table = Util.get_Q_table_from_file()

# init environment
env = Environment(client_socket, SERVER_IP, ID_PLAYER)

# chose robot mode
if EXPERIMENTAL_CONDITION is None:
    # Choose one of the following experimental conditions:
    # - TOM
    # - NO_TOM
    # - DECEPTION
    experimental_condition = constants.TOM
else:
    experimental_condition = EXPERIMENTAL_CONDITION

# get string and send it to server
experimental_condition_str = Util.get_experimental_condition(experimental_condition)
json_data = { "experimental_condition": experimental_condition_str }
# send to Flask the experimental condition in string format
requests.post("http://" + SERVER_IP + ":5000/experimental_condition/" + str(ID_PLAYER), json=json_data)

# play
Q = Qlearning(Q_table, env, experimental_condition, len(states), len(actions), states, actions, epsilon, alpha, gamma)
Q.training(EPISODES)

# send msg to server in order to close the connection for both server and client
client_socket.shutdown(socket.SHUT_WR)
Util.close_connection(SERVER_IP, client_socket, ID_PLAYER)
env.get_socket().close()