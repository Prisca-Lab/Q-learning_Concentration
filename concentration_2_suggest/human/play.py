import requests
import signal
import numpy as np
import pandas as pd

from socket import *

from player import Player
from agent import Agent
from game import Game
from quser import Q_User

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

from util import Util

# in order to have a different directory of plots for each user who's gonna play
user_number = Util.get_user_number()
Util.create_directory_for_plots(1, user_number)

# init instances
player = Player()
agent = Agent()
game = Game()

# read ip and port from config file
data_file = Util.get_from_json_file("config")
serverName = data_file['ip'] 
serverPort = int(data_file['port'])

# read final epsilon from robot training file
epsilon_param = Util.get_from_json_file("greedy")

# create TCP socket
client_socket = socket(AF_INET, SOCK_STREAM)

# connect socket to remote server at (serverName, serverPort)
client_socket.connect((serverName, serverPort))

# send to Flask user id for csv file
requests.post("http://" + serverName + ":5000", json={'id_player': user_number})

# signal handler
def handler(signal, frame):
    print('CTRL-C pressed!')
    close_connection()
    os._exit(0)
signal.signal(signal.SIGINT, handler)

def close_connection(self):
    json_data = { "connection": "close" }
    requests.post("http://" + serverName + ":5000", json=json_data)
    client_socket.close()

# Read from file the Q-table of robot training
Q = Util.get_Q_table_from_file()

# get epsilon from file
epsilon = epsilon_param['epsilon']  # get last epsilon value (after 100k episodes done by agent) from file

# init instance
q_user = Q_User(client_socket, player, game, agent, serverName)

# launch
q_user.user_play(Q, epsilon)