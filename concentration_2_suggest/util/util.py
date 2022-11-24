
import json
import os
import numpy as np
import pandas as pd
import csv

import constants

from pathlib import Path

class Util:
    __list_of_suggests_in_episode = []  # in order to write the suggestions in a file
    __episode = 0                       # util for file
    __counter = 0                       # in order to print the Q-table only n times

    @staticmethod
    def get_avarage(array, index, episode):
        tmp = np.zeros(index)
        for i in range(index):
            tmp[i] = array[i] / episode

        return tmp

    @staticmethod
    def get_cumulative_avg(array, index):
        return np.cumsum(array[0:index]) / (np.arange(index) + 1)

    @staticmethod
    def get_percentage(percent, number):
        return (percent * number) / 100

    @staticmethod
    def save_epsilon_into_file(epsilon):
        with open('../util/greedy.json', 'w') as greedy_file:
            greedy_file.write(json.dumps({'epsilon': epsilon}))

    @staticmethod
    def save_Q_table_into_file(Q):
        with open('../util/matrix.npy', 'wb') as matrix_file:
            np.save(matrix_file, Q)

    @staticmethod
    def save_suggests_into_file(array_suggest, player_type, episode, is_game_ended):
        Util.__list_of_suggests_in_episode.append(list(array_suggest))
        if player_type == "robot":
            file_name = "hints" 
        else: 
            return
            
        # if it's the first run then clean the file
        if episode == 0:
            open('../util/' + file_name + '.txt', 'w').close()

        # write the contents of list in a file every 4000 episode
        if (player_type == "robot" and episode % 4000 == 0 and is_game_ended and episode != 0) or \
            (episode == 99999 and is_game_ended):
            Util.__write_on_file(file_name)

    @staticmethod
    def __write_on_file(file_name):
        pairs = 0
        with open('../util/' + file_name + '.txt', 'a+') as file:
            for i in range(len(Util.__list_of_suggests_in_episode)):
                pair = "pair: " + str(pairs + 1)
                file.write("\n%s \n" % pair)
                file.writelines("%s " % item for item in Util.__list_of_suggests_in_episode[i])
                pairs += 1
                if pairs == 12:
                    e = "end of episode: " + str(Util.__episode)
                    file.write("\n%s\n\n" % e)
                    pairs = 0
                    Util.__episode += 1
        Util.__list_of_suggests_in_episode.clear()      
            

    @staticmethod
    def get_from_json_file(filename):
        with open("../util/" + filename + ".json", "r") as configfile:
            data_file = json.load(configfile)

        return data_file

    @staticmethod
    def get_Q_table_from_file():
        with open('../util/matrix.npy', 'rb') as matrix_file:
            Q = np.load(matrix_file)

        return Q

    @staticmethod
    def get_user_number():
        """
        This function will return the number of user who have played.
        It will update the number and it will write on the file.
        """
        with open('../util/user_number.txt', 'r+') as f:
            n = int(f.read()) + 1
            f.seek(0)
            f.write(str(n))
            f.truncate()

        return n

    @staticmethod
    def create_directory_for_plots(user_type, user_number):
        """
        This function will create a directory for each stats to plot.
        For each run, It will create a new directory for each user (only if user_type is the human player).
        
        Parameters:
        ----------
        user_type: int
            0 it will create a directory for agent, it will create a directory for human otherwise
        user_number: int
            the number of the current player who will play for the first time.
            This number will be the suffix of the folder, 
            for example if it is 1 it will create the folder "user_1" in which the other folders for plots will be placed
            It can be any number when user_type is 0.
        """

        if user_type == 0:
            # create directory if it doesn't exists
            robot_path_plot = "../robot/plot"
            if os.path.exists(robot_path_plot) is False:
                os.mkdir(robot_path_plot)

            robot_path_png = "../robot/plot/png"
            if os.path.exists(robot_path_png):
                return
            os.mkdir(robot_path_png)
            os.mkdir(robot_path_png + "/avg_of_suggests_in_specific_episode")
            os.mkdir(robot_path_png + "/Avg_of_moves_until_match")
            os.mkdir(robot_path_png + "/Avg_of_suggests_after_some_episode")
            os.mkdir(robot_path_png + "/Episode_Click_until_match")
            os.mkdir(robot_path_png + "/Rewards")
            os.mkdir(robot_path_png + "/Episode_length")
            os.mkdir(robot_path_png + "/Avg_of_suggests_on_first_card")
            # tex file
            robot_path_tex = "../robot/plot/tex"
            if os.path.exists(robot_path_tex):
                return
            os.mkdir(robot_path_tex)
            os.mkdir(robot_path_tex + "/avg_of_suggests_in_specific_episode")
            os.mkdir(robot_path_tex + "/Avg_of_moves_until_match")
            os.mkdir(robot_path_tex + "/Avg_of_suggests_after_some_episode")
            os.mkdir(robot_path_tex + "/Episode_Click_until_match")
            os.mkdir(robot_path_tex + "/Rewards")
            os.mkdir(robot_path_tex + "/Episode_length")
            os.mkdir(robot_path_tex + "/Avg_of_suggests_on_first_card")
        
        else:
            # create parent directory
            user_path_png_plot = "../human/plot"
            if os.path.exists(user_path_png_plot) is False:
                os.mkdir(user_path_png_plot)

            user_path_png_parent = "../human/plot/user_" + str(user_number)
            os.mkdir(user_path_png_parent)
            user_path_png_child = "../human/plot/user_" + str(user_number) + "/png"
            os.mkdir(user_path_png_child)
            # create in parent directory a folder for plots
            os.mkdir(user_path_png_child + "/Avg_of_suggests_in_specific_episode")
            os.mkdir(user_path_png_child + "/Avg_of_moves_until_match")
            os.mkdir(user_path_png_child + "/Avg_of_suggests_after_some_episode")
            os.mkdir(user_path_png_child + "/Episode_Click_until_match")
            os.mkdir(user_path_png_child + "/Rewards")
            os.mkdir(user_path_png_child + "/Episode_length")
            # for tex file
            user_path_tex_child = "../human/plot/user_" + str(user_number) + "/tex"
            os.mkdir(user_path_tex_child)
            os.mkdir(user_path_tex_child + "/avg_of_suggests_in_specific_episode")
            os.mkdir(user_path_tex_child + "/Avg_of_moves_until_match")
            os.mkdir(user_path_tex_child + "/Avg_of_suggests_after_some_episode")
            os.mkdir(user_path_tex_child + "/Episode_Click_until_match")
            os.mkdir(user_path_tex_child + "/Rewards")
            os.mkdir(user_path_tex_child + "/Episode_length")
    
    @staticmethod
    def print_Q_table(Q, states, actions, module):
        if Util.__counter % module == 0:
            print("\n", pd.DataFrame(Q, states, actions))
            print("end of episode", Util.__counter)
        Util.__counter += 1

    @staticmethod
    def put_data_in_csv(csv_data, id_player):
        file_path = Path("../human/plot/user_" + str(id_player) + "/game_data.csv")
        keys = csv_data.keys()
        print("keys:", keys)

        if file_path.is_file() is False:
            # add header
            with open(file_path, "a+", newline='') as outfile:
                writer = csv.writer(outfile, delimiter = ";")
                # write header only if file doesn't exists
                writer.writerow(keys)
                writer.writerows(list(zip(*[csv_data[key] for key in keys])))
        else:
            # if it does exists do not add the header
            with open(file_path, "a+", newline='') as outfile:
                writer = csv.writer(outfile, delimiter = ";")
                writer.writerows(list(zip(*[csv_data[key] for key in keys])))