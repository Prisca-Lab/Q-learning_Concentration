import json
import threading
import signal
import time

from threading import Lock
from flask import Flask, render_template, request, session, jsonify
from flask_socketio import SocketIO

from flask_utility.utility_flask import UtilityFlask

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'util'))

from util import Util

# constants
ONE_TERMINAL = Util.get_from_json_file("config")["one_terminal"]
IP_ADDRESS = Util.get_from_json_file("config")['ip'] 
MULTITHREADING = Util.get_from_json_file("config")['multithreading'] 

# Creazione dell'app Flask
app = Flask(__name__, template_folder="./animal_game/template", static_folder="./animal_game/static")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# global
client_instances = {}
first_start = True
lock = Lock()

@app.route('/id_player', methods=["POST"])
def receive_id_player():

    client_id = request.get_json().get('id_player')
    # if player is not instanced yet
    client_instances[client_id] = UtilityFlask() 
    # handle CTRL+C
    signal.signal(signal.SIGINT, client_instances[client_id].handle_exit_signal)
    # handle player
    return client_instances[client_id].handle_id_player(request)
        
@app.route('/experimental_condition/<int:id>', methods=["POST"])
def receive_experiment_type(id):
    UtilityFlask.debug_print("in robot: " + str(id) + str(client_instances))

    utility_flask = client_instances.get(id)
    return utility_flask.handle_experiment_condition(request)
    
@app.route('/exit/<int:id>', methods=["POST"])
def receive_exit_clients(id):
    print(f"Closing socket with user {id}")
    utility_flask = client_instances.get(id)
    res = utility_flask.handle_exit_client(request)
    del client_instances[id]

    # If admin has written "exit" then start a thread to close server after closing learning socket
    def exit_thread():
        if utility_flask.exit_pressed:
            time.sleep(2)
            Util.formatted_debug_message("Socket of Q-learning agent closed!", level='INFO')
            os._exit(0)

    # Avvia il thread per eseguire os._exit
    exit_thread = threading.Thread(target=exit_thread)
    exit_thread.start()

    return res

@app.route('/game_board/<int:id>', methods=["POST"])
def receive_game_board(id):
    UtilityFlask.debug_print("Received game board for player: " + str(id))

    utility_flask = client_instances.get(id)
    if utility_flask is None:
        print("[Game Board] No client yet")
        return render_template('index.html') 
    
    return utility_flask.handle_game_board(request)
    
@app.route('/player_move/<int:id>', methods=["POST"])
def receive_player_move_data(id):
    UtilityFlask.debug_print("Action move received from player with id " + str(id))

    utility_flask = client_instances.get(id)
    if utility_flask is None:
        print("[Player move] No client yet")
        return render_template('index.html') 
    
    return utility_flask.handle_player_move(request)

@app.route('/hint_data/<int:id>', methods=["POST"])
def receive_hint_data(id):
    UtilityFlask.debug_print("Hint received from agent for player with id " + str(id))
    
    utility_flask = client_instances.get(id)
    if utility_flask is None:
        print("[Agent] No client yet")
        return render_template('index.html') 
    
    return utility_flask.handle_robot_hint(request, socketio)

@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.get_json()
        string = json.dumps(data)
        dictionary = json.loads(string)
        
        if "Speech" in dictionary:
            print("The robot has finished uttering the suggestion, sending to the browser: removal of pop-up!")
            print(json.dumps(data))
            socketio.emit('Speech', json.dumps(data))

        if "refreshed" in dictionary:
            print("Refreshed! Clear csv's structure.")
            #clear_csv_struct()           
        
    return render_template('index.html')

@app.route('/get_file_config/<id>')
def serve_frontend(id):
    pop_up = False
    language = 'ita'

    if MULTITHREADING:
        utility_flask = client_instances.get(id)
        if not utility_flask:
            lock.acquire()
            id = Util.create_dir_for_current_user() 
            lock.release()
            pop_up = Util.get_from_json_file("config")['pop_up']
            UtilityFlask.debug_print(f"js: New client connected with ID={id}, running Q-learning script!")

            threading.Thread(target=UtilityFlask.start_algorithm, args=(IP_ADDRESS, True, None, )).start()
    else:
        #print("Flask id request:", id)
        id = Util.get_user_number(False)
        pop_up = Util.get_from_json_file("config")['pop_up']
        language = Util.get_from_json_file("config")['language']

    return jsonify({'message': pop_up, 'id': id, "multithreading": MULTITHREADING, "language": language}), 200

if __name__ == '__main__':
    # create robot socket
    threading.Thread(target=UtilityFlask.create_socket, args=(UtilityFlask.ROBOT_PORT,)).start()
    # run q-learning program only if ONE_TERMINAL=True
    if ONE_TERMINAL and MULTITHREADING is False: 
        threading.Thread(target=UtilityFlask.start_algorithm, args=(IP_ADDRESS, True, None, )).start()
    socketio.run(app, host=IP_ADDRESS, port=5000, debug=True, use_reloader=False, log_output=False)