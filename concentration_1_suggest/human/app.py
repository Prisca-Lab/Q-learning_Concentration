import json
import socket
import threading

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

from util import Util

# read ip from config file
data_file = Util.get_from_json_file("config")
ip_address = data_file['ip']   

# global socket variable
learning_socket = 0
furhat_socket = 0

# create flask app
app = Flask(__name__, template_folder="./animal_game/template", static_folder="./animal_game/static")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# @route decorator to tell Flask what URL should trigger our function
@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.get_json()
        str = json.dumps(data)
        dictionary = json.loads(str)
        
        # board game
        if("matrix" in dictionary): 
            if learning_socket != 0:
                learning_socket.send(json.dumps(data).encode())
            print(json.dumps(data).encode())
            return jsonify(200)

        # clicked card, its position, ...
        if("data" in dictionary):
            if learning_socket != 0:
                learning_socket.send(json.dumps(data).encode())
            print(json.dumps(data).encode())
            return jsonify(200)

        # send suggestion provided by agent and player's info to furhat
        if("action" in dictionary or "game" in dictionary):
            if furhat_socket != 0:
                furhat_socket.send(json.dumps(data).encode())
                print("sended to", furhat_socket)

        if("connection" in dictionary):
            learning_socket.close()

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
    serversocket.listen(10)
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
    serversocket.listen(10)
    while True:
        # accept connections from outside
        (clientsocket, address) = serversocket.accept()
        print("Handle furhat client", clientsocket)
        furhat_socket = clientsocket 



if __name__ == '__main__':
    threading.Thread(target = create_learning_socket).start()
    threading.Thread(target = create_furhat_socket).start()
    socketio.run(app, host=ip_address, port=5000, debug=True, use_reloader=False)
