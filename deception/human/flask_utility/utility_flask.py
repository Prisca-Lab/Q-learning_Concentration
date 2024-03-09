from flask import jsonify
from flask_socketio import SocketIO, emit

import subprocess
import time
import webbrowser
import socket
import threading
import json
import numpy as np

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'util'))

from util import Util

class UtilityFlask:
    """
    Utility class for Flask application management.

    Attributes:
        MULTITHREADING (bool): Flag indicating whether multithreading is enabled.
        ONE_TERMINAL (bool): Flag indicating whether the application runs in a single terminal.
        IP_ADDRESS (str): IP address of the server.
        POP_UP (bool): Flag indicating whether pop-up windows are enabled (used before start the game).
        LEARNING_PORT (int): Port number for the learning socket.
        ROBOT_PORT (int): Port number for the robot socket.
        robot_socket (int): Socket object for the robot connection.
    """

    # Constants
    MULTITHREADING = Util.get_from_json_file("config")['multithreading'] 
    ONE_TERMINAL = Util.get_from_json_file("config")["one_terminal"]
    IP_ADDRESS = Util.get_from_json_file("config")['ip'] 
    POP_UP = Util.get_from_json_file("config")['pop_up'] 
    AUTO_OPEN_WEBPAGE = Util.get_from_json_file("config")['auto_open_webpage'] 
    LEARNING_PORT = 6000
    ROBOT_PORT = 7000
    robot_socket = 0

    def __init__(self):
        """
        Initializes a UtilityFlask object.

        Attributes:
        ----------
            CSV_FIELDS (list): List of field names for the CSV data.
            id_player (int): ID of the player.
            experiment_condition (str): Current experimental condition.
            learning_socket (int): Socket object for the learning connection.
            isRobotConnected (bool): Flag indicating if the robot is connected: 
                                     if false the client will not show a pop-up before highlight the position suggested.
            exit_pressed (bool): Flag indicating if the exit command was pressed.
            first_start (bool): Flag indicating if it's the first start of the application.
            received_hint (dict): Dictionary containing received hints.
            csv_data (dict): Dictionary to store CSV data fields.
        """
        self.CSV_FIELDS = ['id_player', 'turn_number', 'position_clicked', 'time_game',
                           'time_until_match', 'suggestion_type', 'position_suggested', 
                           'experiment_condition', 'match', 'game_ended', 'wrong_hint']
        self.id_player = -1
        self.experiment_condition = ''
        self.learning_socket = 0
        self.isRobotConnected = False
        self.exit_pressed = False
        self.first_start = True
        self.received_hint = {}
        self.csv_data = {field: [] for field in self.CSV_FIELDS}

    @staticmethod
    def clean_shell():
        """
        Clears the terminal shell.
        """
        os.system('clear' if os.name == 'posix' else 'cls')

    @staticmethod
    def create_socket(port):
        """
        Function to create a socket on a specific port.
        Accepts incoming connections and starts a thread to handle each client.
        Used to create connection with robot!

        Args:
            port (int): Port number for the socket.
        """
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind((UtilityFlask.IP_ADDRESS, port))
        serversocket.listen(5)
        while True:
            (clientsocket, address) = serversocket.accept()
            client_handler = threading.Thread(target=UtilityFlask.handle_client, args=(clientsocket, port))
            client_handler.start()   

    @staticmethod
    def start_algorithm(IP_ADDRESS, first_start, experimental_condition):
        """
        Executes the Q-learning algorithm as a separate process.
        Is should use only when ONE_TERMINAL=True
        
        Args:
            IP_ADDRESS (str): IP address of the server.
            first_start (bool): Flag indicating if it's the first start.
            experimental_condition (str): Experimental condition for the algorithm.
        """
        Util.formatted_debug_message("Running Q-learning script...", level='')
        
        if first_start:
            if not UtilityFlask.MULTITHREADING:
                subprocess.Popen(["python", "play.py"])
                UtilityFlask.open_web_page(IP_ADDRESS)
            else:
                # if is multithreading the server will create the directory for clients, not the Q-learning program 
                subprocess.Popen(["python", "play.py", "true"])
        else:
            if experimental_condition:
                # send the new experimental condition
                subprocess.Popen(["python", "play.py", str(experimental_condition)])
            else:
                subprocess.Popen(["python", "play.py"])

            if UtilityFlask.POP_UP:
                UtilityFlask.open_web_page(IP_ADDRESS)
            else:
                Util.formatted_debug_message("Refresh page to initialize Q-learning data!")
        
    @staticmethod
    def open_web_page(IP_ADDRESS):
        """
        Opens a web page in a browser.
        
        Args:
            IP_ADDRESS (str): IP address of the server.
        """
        if UtilityFlask.AUTO_OPEN_WEBPAGE:
            Util.formatted_debug_message("Server started. Opening URL http://" + IP_ADDRESS + ":5000 ...", level='INFO')
            time.sleep(1)
            webbrowser.open(f"http://{IP_ADDRESS}:5000", autoraise=True)
        else:
            Util.formatted_debug_message("Server started. Open URL http://" + IP_ADDRESS + ":5000", level='INFO')

    @staticmethod
    def debug_print(message):
        """
        Prints a debug message if multithreading is enabled.
        
        Args:
            message (str): Debug message to print.
        """
        if UtilityFlask.MULTITHREADING: print(message)

    ##################################################################################################################
    #                                             connection and menu                                                #
    ##################################################################################################################

    def handle_exit_signal(self, signal, frame):
        """
        Function to handle the exit signal (CTRL-C) of the server.
        Closes the connections of the learning and Furhat sockets if they are open.
        """
        Util.formatted_debug_message('(Server) CTRL-C pressed!', level='INFO')
        if UtilityFlask.robot_socket:
            UtilityFlask.robot_socket.close()
        if self.learning_socket:
            self.learning_socket.send(json.dumps({"connection": "close"}).encode())
            self.learning_socket.close()
            UtilityFlask.clean_shell()
            if not UtilityFlask.ONE_TERMINAL:
                Util.formatted_debug_message("Waiting for new client...", level='INFO')
            else:
                Util.formatted_debug_message("Server closed!", level='INFO')
        else:
            Util.formatted_debug_message("Exit...", level='INFO')
        os._exit(0)

    def _wait_for_client(self):
        """
        Function to wait for client connection.
        This function runs in a separate thread.
        """
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind((UtilityFlask.IP_ADDRESS, UtilityFlask.LEARNING_PORT))
        serversocket.listen(1)  # Listen for one connection only

        Util.formatted_debug_message("Waiting for client connection...", level='INFO')
        clientsocket, address = serversocket.accept()
        self.learning_socket = clientsocket
        if not UtilityFlask.ONE_TERMINAL:
            Util.formatted_debug_message("Client connected from" + str(address), level='INFO')

    def _handle_admin_menu(self):
        """
        Handle the admin menu options.

        This function displays a menu to the administrator, allowing them to restart the Q-learning script
        or close the server. The administrator can input 'ok' to restart the Q-learning script or 'exit' to 
        close the server. If 'ok' is entered it also displays a menu to change experimental condition.
        """
        Util.formatted_debug_message("Write 'ok' to restart Q-learning script or 'exit' to close the server...", level='INFO')
        
        while True:
            user_input = input("Choice:").lower()
            
            if user_input == "ok":
                self.first_start = False
                return self._handle_admin_menu_experimental_condition()
            elif user_input == "exit":
                self.exit_pressed = True
                return jsonify({'message': 'Closing after user input'}), 200

    def _handle_admin_menu_experimental_condition(self):
        """
        Handle the experimental conditions in the admin menu.

        This function prompts the administrator to change the experimental condition. It displays the available
        experimental conditions and allows the administrator to choose one. If the administrator chooses to change 
        the experimental condition, the program is restarted with the new condition. Otherwise, the program restarts 
        with the same experimental condition.
        """
        Util.formatted_debug_message("Do you want to change the experimental condition?", level='INFO')
        new_experimental_condition = input("Y/n? ").lower()
        
        if new_experimental_condition in ['yes', 'y']:
            Util.formatted_debug_message("Experimental conditions:\n" +
                                        "0: Theory of Mind\n" +
                                        "1: No-Theory of Mind\n" +
                                        "2: Deception\n" +
                                        "3: External\n" +
                                        "4: Superficial\n" +
                                        "5: Hidden\n" +
                                        "Other: you will restart with the same experimental condition setted at the beginning",
                                        level='INFO')
            experimental_condition = input("Choose mode: ")
            
            if experimental_condition == '' or (not experimental_condition.isdigit() or int(experimental_condition) not in range(6)):
                experimental_condition = None
                UtilityFlask.clean_shell()
            
            # start new program with new experimental condition (if available)
            threading.Thread(target=self.start_algorithm, args=(self.IP_ADDRESS, self.first_start, experimental_condition, )).start()
        else:
            # start new program with same experimental condition
            threading.Thread(target=self.start_algorithm, args=(self.IP_ADDRESS, self.first_start, None, )).start()

        return jsonify({'message': 'Finished game, closing...'}), 200

    ##################################################################################################################
    #                                                     CSV                                                        #
    ##################################################################################################################

    def _write_hint_data_on_file(self, data):
        """
        Write on file the hint provided by the agent.
        If the experimental condition is deception or hidden, it will also indicate whether the provided hint is correct or not.
        """
        state = data['action']['state']
        hint_type = data['action']['suggestion']
        hint_position = data['action']['position']
        hint_card = data['action']['card']

        wrong_hint = f"Has provided wrong card? {data['action']['wrong_hint']}"

        hint_info = ''
        if hint_type == 'none':
            hint_info = 'none, None, None'
        elif hint_type == 'row':
            hint_info = f'{hint_type}, {hint_card}, ({hint_position[0] - 1}, -1)'
        elif hint_type == 'column':
            hint_info = f'{hint_type}, {hint_card}, (-1, {hint_position[1] - 1})'
        else:
            hint_info = f'{hint_type}, {hint_card}, ({hint_position[0] - 1}, {hint_position[1] - 1})'
        
        self._update_csv_data(data)
        deception_conditions = ['deception', 'superficial_deception']
        if self.experiment_condition in deception_conditions: 
            Util.update_log_file(f"\n\nHint: ({hint_info})\n{state}\n{wrong_hint}", self.id_player)
        else:
            Util.update_log_file(f"\n\nHint: ({hint_info})\n{state}", self.id_player)

    def _write_game_data_on_file(self, data):
        """
        Write on file the user's info and update the structure for csv data.
        """
        self._update_csv_data(data)
        self._update_log_file_by_game_data(data)

    def _update_log_file_by_game_data(self, data):
        """
        Write on log file the user's info.
        """
        game_data = data["game"]
        Util.update_log_file(f"\nTurn: {game_data['turn']}\nPosition_clicked: {game_data['position']}\nCard_clicked: {game_data['open_card_name']}\nTime_game: {game_data['time_game']}\nTime_before_match: {game_data['time_until_match']}\nMatch: {game_data['match']}", self.id_player)

    def _write_board_on_file(self, shuffle_cards):
        """
        Print game board as matrix and write it on log-file.

        Args:
            shuffle_cards (list): List of cards.
        """
        output_lines = []
        board = np.zeros((6, 4))
        board = np.reshape(shuffle_cards, (4, 6))
        mx = len(max((sub[0] for sub in board), key=len))
        #print("\n")
        for row in board:
            if not self.ONE_TERMINAL: print(" ".join(["{:<{mx}}".format(ele, mx=mx) for ele in row]))
            output_lines.append(" ".join(["{:<{mx}}".format(ele, mx=mx) for ele in row]))
        print("\n")

        # write board on file
        if self.id_player != -1: Util.update_log_file("\n".join(output_lines) + "\n", self.id_player)

    def _clear_csv_struct(self):
        """
        Clear csv structure for other users.
        """
        for field in self.CSV_FIELDS:
            self.csv_data[field].clear()
    
    def _update_csv_data(self, data):
        """
        Update structure for csv data.
        """
        if 'game' in data:
            self.csv_data["id_player"].append(self.id_player)
            self.csv_data["experiment_condition"].append(self.experiment_condition)

            self.csv_data["turn_number"].append(data["game"]["turn"])
            self.csv_data["position_clicked"].append(data["game"]["position"])
            self.csv_data["time_game"].append(data["game"]["time_game"])
            self.csv_data["time_until_match"].append(data["game"]["time_until_match"])
            self.csv_data["match"].append(data["game"]["match"])
            self.csv_data["game_ended"].append(data["game"]["pairs"] == 12)

            # if game is finished, write the csv file and clear the csv structure for other users
            if data["game"]["pairs"] == 12:
                Util.formatted_debug_message("Saving csv...", level='INFO')
                Util.put_data_in_csv(self.csv_data, self.id_player)
                Util.formatted_debug_message("Data saved on csv file. Clear csv struct...", level='INFO')
                self._clear_csv_struct()

        if 'action' in data:
            action_data = data["action"]
            suggestion_type = action_data["suggestion"]
            
            self.csv_data["suggestion_type"].append(suggestion_type)
            self.csv_data["wrong_hint"].append(action_data["wrong_hint"])

            if suggestion_type == "none":
                self.csv_data["position_suggested"].append("none")
            else:
                if suggestion_type in ["row", "column"]:
                    position_index = 0 if suggestion_type == "row" else 1
                    suggested_position = action_data["position"][position_index] - 1
                else:
                    suggested_position = [pos - 1 for pos in action_data["position"]]

                self.csv_data["position_suggested"].append(suggested_position)

    ##################################################################################################################
    #                                                  handler                                                       #
    ##################################################################################################################

    def handle_client(client_socket, port):
        """
        Function to handle the client connecting to the socket.
        If the port matches the learning port, sets the learning (q-learning algorithm) socket.
        If the port matches the robot port, sets the robot socket and indicates that the robot is connected.
        """
        if port == UtilityFlask.ROBOT_PORT:
            UtilityFlask.robot_socket = client_socket 
            Util.formatted_debug_message("Handle robot client" + str(UtilityFlask.robot_socket.getsockname()), level='INFO')

    def handle_id_player(self, request):
        """
        Handle the player ID received in the request.

        Args:
        - request: The request object containing player ID information.

        Returns:
        - Response indicating success or failure.
        """
        data = request.get_json()
        # get experimental_condition  from json
        self.id_player = data.get('id_player')

        if self.id_player is not None:
            # update log file
            Util.update_log_file(f"id_player: {self.id_player}", self.id_player)
            Util.formatted_debug_message("Init for player with ID " + str(self.id_player), level='INFO')
            # create connection with Q-learning algo using socket
            client_thread = threading.Thread(target=self._wait_for_client)
            client_thread.start()
            return jsonify({'message': 'ID player updated correctly'}), 200
        else:
            return jsonify({'error': 'ID player not provided in the request'}), 400
        
    def handle_experiment_condition(self, request):
        """
        Handle the experimental condition received in the request.

        Args:
        - request: The request object containing experimental condition information.

        Returns:
        - Response indicating success or failure.
        """
        data = request.get_json()
        # get id from json data
        self.experiment_condition = data.get('experimental_condition')

        if self.experiment_condition is not None:
            # update log file
            Util.update_log_file("\nExperimental condition:" + self.experiment_condition + "\n\n", self.id_player)
            Util.formatted_debug_message("Experiment condition:" + self.experiment_condition, level='INFO')
            return jsonify({'message': 'Experiment condition updated correctly'}), 200
        else:
            return jsonify({'error': 'Experiment condition not provided in the request'}), 400
        
    def handle_game_board(self, request):
        """
        Receive and handle the game board sent in the request.

        Args:
        - request: The request object containing the game board matrix.

        Returns:
        - Response indicating success or failure.
        """
        data = request.get_json()
        # get id from json data
        game_board = data.get('matrix')

        # handle game board (received from js and send it to python program)
        if game_board is not None:
            # send game board to Q-learning algorithm
            if self.learning_socket: self.learning_socket.send(json.dumps(data).encode())
            # print game board (if not local) and write it on log file
            self._write_board_on_file(data['matrix'])
            return jsonify({'message': 'Game board received'}), 200
        else:
            return jsonify({'error': 'Game board not passed not provided in the request'}), 400
        
    def handle_player_move(self, request):
        """
        Receive and handle the player's move (card clicket, position, ...) sent in the request.

        Args:
        - request: The request object containing the game data.

        Returns:
        - Response indicating success or failure.
        """
        # get json data
        data = request.get_json()
        string = json.dumps(data)
        dictionary = json.loads(string)
        # get id from json data
        player_move = data.get('game')

        # received user's info (js)
        if player_move is not None:
            # send to robot 
            if UtilityFlask.robot_socket != 0:
                UtilityFlask.robot_socket.send(json.dumps(data).encode())
                Util.formatted_debug_message("Player's move sended to robot socket", level='INFO')

            # send data to Q-learning script
            if self.learning_socket: self.learning_socket.send(json.dumps(data).encode())
            else: print("Error socket")

            # write log file and update csv file
            self._write_game_data_on_file(dictionary)
                    
            if player_move["pairs"] == 12 and self.ONE_TERMINAL and not self.MULTITHREADING:
                return self._handle_admin_menu()
            return jsonify({'message': 'User move received'}), 200
        else:
            return jsonify({'error': 'User move not passed not provided in the request'}), 400
        
    def handle_robot_hint(self, request, socketio):
        """
        Handle the hint received from the robot.

        Args:
        - request: The request object containing the hint data.
        - socketio: The SocketIO instance for emitting events.

        Returns:
        - Response indicating success or failure.
        """
        # get json data
        data = request.get_json()
        string = json.dumps(data)
        dictionary = json.loads(string)
        # get id from json data
        agent_hint = data.get('action')

        # received user's info (js)
        if agent_hint is not None:
            # send to robot 
            if UtilityFlask.robot_socket != 0:
                UtilityFlask.robot_socket.send(json.dumps(data).encode())
                Util.formatted_debug_message("Hint sended to robot socket", level='INFO')
                self.isRobotConnected = True

            # if not none send to js in order to highlight the card/row/col and send it to robot app     
            if agent_hint["suggestion"] != "none":
                agent_hint["isRobotConnected"] = self.isRobotConnected
                if not self.ONE_TERMINAL: print(json.dumps(data, indent=4))
                socket_address = "robot_hint_" + str(self.id_player)
                #print("address", socket_address)
                socketio.emit(socket_address, json.dumps(data))
                Util.formatted_debug_message("Hint received by Q-learning agent.", level='INFO')
                Util.formatted_debug_message("Hint sended to javascript.", level='INFO')
            # write hint on log file and csv
            self._write_hint_data_on_file(dictionary)
            # save hint object (could be used in order to avoid websocket)
            self.received_hint = agent_hint
            return jsonify({'message': 'Hint agent received'}), 200
        else:
            return jsonify({'error': 'Hint agent not passed not provided in the request'}), 400
        
    def handle_exit_client(self, request):
        """
        Handle the client exit request.

        Args:
        - request: The request object containing the exit data.

        Returns:
        - Response indicating success or failure.
        """
        data = request.get_json()
        # get id from json data
        exit_data = data.get('connection')

        if exit_data is not None:
            Util.formatted_debug_message("Socket of Q-learning agent closed!", level='INFO')
            self.learning_socket.close()
            self.learning_socket = 0
            UtilityFlask.clean_shell()
            Util.formatted_debug_message("Waiting for new client...", level='INFO')
            if UtilityFlask.robot_socket != 0:
                Util.formatted_debug_message("Socket of robot closed!", level='INFO')
                UtilityFlask.robot_socket.close()
                UtilityFlask.robot_socket = 0
                # if you want to play without robot then remove pop-up
                self.isRobotConnected = False
            return jsonify({'connection': 'Closing socket'}), 200
        else:
            return jsonify({'error': 'Connection info not passed not provided in the request'}), 400