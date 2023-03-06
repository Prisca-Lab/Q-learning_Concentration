import requests
import signal

from socket import *

from learning import Qlearning
from environment import Environment

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

import constants
from util import Util

# in order to have a different directory of plots for each user who's gonna play
user_number = Util.get_user_number()
user_path = "../human/plot/user_" + str(user_number)
os.mkdir(user_path)

# read ip and port from config file
data_file = Util.get_from_json_file("config")
server_name = data_file['ip'] 
serverPort = int(data_file['port'])

# create TCP socket
client_socket = socket(AF_INET, SOCK_STREAM)

# connect socket to remote server at (serverName, serverPort)
client_socket.connect((server_name, serverPort))

# send to Flask user id for csv file
requests.post("http://" + server_name + ":5000", json={'id_player': user_number})

# signal handler
def handler(signal, frame):
    print('CTRL-C pressed!')
    close_connection()
    os._exit(0)
signal.signal(signal.SIGINT, handler)

def close_connection():
    json_data = { "connection": "close" }
    requests.post("http://" + server_name + ":5000", json=json_data)
    client_socket.close()

# define robot's action
actions = ['none', 'suggest_row', 'suggest_col', 'suggest_card']

# define states: {robot_last_action X game_state X user_state}
states = [
    'INIT_STATE',

    '(no_help, beg, f_correct)',
    '(no_help, beg, f_wrong)',
    '(no_help, mid, f_correct)',
    '(no_help, mid, f_wrong)',
    '(no_help, end, f_correct)',
    '(no_help, end, f_wrong)',

    '(sugg_row, beg, f_correct)',
    '(sugg_row, beg, f_wrong)',
    '(sugg_row, mid, f_correct)',
    '(sugg_row, mid, f_wrong)',
    '(sugg_row, end, f_correct)',
    '(sugg_row, end, f_wrong)',

    '(sugg_col, beg, f_correct)',
    '(sugg_col, beg, f_wrong)',
    '(sugg_col, mid, f_correct)',
    '(sugg_col, mid, f_wrong)',
    '(sugg_col, end, f_correct)',
    '(sugg_col, end, f_wrong)',

    '(sugg_card, beg, f_correct)',
    '(sugg_card, beg, f_wrong)',
    '(sugg_card, mid, f_correct)',
    '(sugg_card, mid, f_wrong)',
    '(sugg_card, end, f_correct)',
    '(sugg_card, end, f_wrong)',

    '(no_help, beg, s_correct)',
    '(no_help, beg, s_wrong)',
    '(no_help, mid, s_correct)',
    '(no_help, mid, s_wrong)',
    '(no_help, end, s_correct)',
    '(no_help, end, s_wrong)',

    '(sugg_row, beg, s_correct)',
    '(sugg_row, beg, s_wrong)',
    '(sugg_row, mid, s_correct)',
    '(sugg_row, mid, s_wrong)',
    '(sugg_row, end, s_correct)',
    '(sugg_row, end, s_wrong)',

    '(sugg_col, beg, s_correct)',
    '(sugg_col, beg, s_wrong)',
    '(sugg_col, mid, s_correct)',
    '(sugg_col, mid, s_wrong)',
    '(sugg_col, end, s_correct)',
    '(sugg_col, end, s_wrong)',

    '(sugg_card, beg, s_correct)',
    '(sugg_card, beg, s_wrong)',
    '(sugg_card, mid, s_correct)',
    '(sugg_card, mid, s_wrong)',
    '(sugg_card, end, s_correct)',
    '(sugg_card, end, s_wrong)',
]

# define the number of games that the agent will plays
EPISODES = constants.EPISODES_WITH_HUMAN

# Read from file the Q-table of robot training
Q_table = Util.get_Q_table_from_file()

# init environment
env = Environment(client_socket, server_name)

# parameters setting
epsilon_param = Util.get_from_json_file("greedy")   # read final epsilon from robot training file
epsilon = epsilon_param['epsilon']                  # get last epsilon value (after 100k episodes done by agent) from file
alpha = 0.95
gamma = 0.8

# chose robot_type and send it to the server
type = constants.NO_TOM
robot_type = ''
if type == constants.TOM:
    robot_type ='ToM'
elif type == constants.NO_TOM:
    robot_type = 'noToM'
else:
    robot_type = 'deception'
json_data = { "robot_type": type }
requests.post("http://" + server_name + ":5000", json=json_data)

# play
Q = Qlearning(Q_table, env, type, len(states), len(actions), states, actions, epsilon, alpha, gamma)
Q.training(EPISODES)

# send msg to server in order to close the connection for both server and client
json_data = { "connection": "close" }
requests.post("http://" + env.get_server_name() + ":5000", json=json_data)
env.get_socket().close()