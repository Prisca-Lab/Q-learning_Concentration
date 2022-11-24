import json
import socket
import threading
import signal

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

from util import Util

# global var
is_game_ended = False
id_player = 0
robot_type = ''

# read ip from config file
data_file = Util.get_from_json_file("config")
ip_address = data_file['ip']   

# global socket variable
learning_socket = 0
furhat_socket = 0

# game data for csv file
csv_data = {
        'id_player': [],
        'turn_number': [],
        'position_clicked': [],
        'time_until_match': [],
        'suggestion_type': [],
        'position_suggested': [],
        'robot_type': [],
        'match': [],
        'game_ended': []
}

# create flask app
app = Flask(__name__, template_folder="./animal_game/template", static_folder="./animal_game/static")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# @route decorator to tell Flask what URL should trigger our function
@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        global is_game_ended, id_player, robot_type

        data = request.get_json()
        str = json.dumps(data)
        dictionary = json.loads(str)
        
        # game board
        if("matrix" in dictionary): 
            is_game_ended = False
            if learning_socket != 0:
                learning_socket.send(json.dumps(data).encode())
            print(json.dumps(data).encode())
            return jsonify(200)


        # id_player received from python client
        if("id_player" in dictionary):
            id_player = dictionary['id_player']
            print("id_player:", id_player)

        if("robot_type" in dictionary):
            robot_type = dictionary["robot_type"]
            print("robot_type:", robot_type)


        # action: suggestion provided by agent (python script)
        # game: game's data (js)
        if("action" in dictionary or "game" in dictionary):

            if furhat_socket != 0:
                furhat_socket.send(json.dumps(data).encode())
                print("Sended data to furhat socket:", furhat_socket)

            if "action" in dictionary:
                print("received suggestion")
                # Sends suggestion to js so that cards are highlighted 
                if dictionary["action"]["suggestion"] != "none":
                    socketio.emit('robot_hint', json.dumps(data))
                    print("suggestion sended to javascript")
                # update data for csv
                update_csv_data_by_suggestion(dictionary)

            if "game" in dictionary:
                # send data to Q-learning script
                if learning_socket != 0:
                    learning_socket.send(json.dumps(data).encode())
                # update data for csv
                print(csv_data)
                update_csv_data_by_game_data(dictionary, id_player)
                
                print(json.dumps(csv_data, indent=4))
                is_game_ended = dictionary["game"]["pairs"] == 12
                if is_game_ended:
                    print("save csv")
                    Util.put_data_in_csv(csv_data, id_player)
                    clear_csv_struct()


        if("refreshed" in dictionary):
            print("Refreshed! Clear csv's structure.")
            clear_csv_struct()


        if("connection" in dictionary):
            # game ended
            learning_socket.close()


        if "furhat_game" in dictionary:
            if furhat_socket != 0:
                furhat_socket.send(json.dumps(data).encode())

    return render_template('index.html')


# define socket connection
def create_learning_socket():
    global learning_socket

   # create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the socket to a public host, and a well-known port
    serversocket.bind((ip_address, 6000))
    # become a server socket
    serversocket.listen(5)
    while True:
        # accept connections from outside
        (clientsocket, address) = serversocket.accept()
        print("Handle learning client", clientsocket)
        learning_socket = clientsocket 


def create_furhat_socket():
    global furhat_socket

   # create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the socket to a public host, and a well-known port
    serversocket.bind((ip_address, 7000))
    # become a server socket
    serversocket.listen(5)
    while True:
        # accept connections from outside
        (clientsocket, address) = serversocket.accept()
        print("Handle furhat client", clientsocket)
        furhat_socket = clientsocket 


# signal handler
def handler(signal, frame):
    print('CTRL-C pressed!')
    if learning_socket != 0:
        learning_socket.close()
    if furhat_socket != 0:
        furhat_socket.close()
    os._exit(0)


def update_csv_data_by_game_data(dictionary, id_player):
    csv_data["id_player"].append(id_player)
    csv_data["turn_number"].append(dictionary["game"]["turn"])
    if dictionary["game"]["turn"] == 1:
        csv_data["suggestion_type"].append("none")
        csv_data["position_suggested"].append("none")
        csv_data["robot_type"].append(robot_type)
    csv_data["position_clicked"].append(dictionary["game"]["position"])
    csv_data["time_until_match"].append(dictionary["game"]["time_until_match"])
    csv_data["match"].append(dictionary["game"]["match"])
    is_game_ended = dictionary["game"]["pairs"] == 12
    csv_data["game_ended"].append(is_game_ended)


def update_csv_data_by_suggestion(dictionary):
    csv_data["suggestion_type"].append(dictionary["action"]["suggestion"])
    if dictionary["action"]["suggestion"] == "none":
        csv_data["position_suggested"].append("none")
    else:
        if dictionary["action"]["suggestion"] == "row":
            csv_data["position_suggested"].append(dictionary["action"]["position"][0] - 1)
        elif dictionary["action"]["suggestion"] == "column":
            csv_data["position_suggested"].append(dictionary["action"]["position"][1] - 1)
        else:
            position = [dictionary["action"]["position"][0] - 1, dictionary["action"]["position"][1] - 1]
            csv_data["position_suggested"].append(position)
    csv_data["robot_type"].append(dictionary["action"]["robot_type"])


def clear_csv_struct():
    csv_data["id_player"].clear()
    csv_data["turn_number"].clear()
    csv_data["position_clicked"].clear()
    csv_data["time_until_match"].clear()
    csv_data["suggestion_type"].clear()
    csv_data["position_suggested"].clear()
    csv_data["robot_type"].clear()
    csv_data["match"].clear()
    csv_data["game_ended"].clear()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    threading.Thread(target = create_learning_socket).start()
    threading.Thread(target = create_furhat_socket).start()
    socketio.run(app, host=ip_address, port=5000, debug=True, use_reloader=False)