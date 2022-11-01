
import json
import os
import numpy as np
import pandas as pd

import constants

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
        file_name = "hints" if player_type == "robot" else "hints_with_human"
        # if it's the first run then clean the file
        if episode == 0:
            open('../util/' + file_name + '.txt', 'w').close()

        # write the contents of list in a file every 4000 episode
        if (player_type == "robot" and episode % 4000 == 0 and is_game_ended and episode != 0) or \
            (episode == 99999 and is_game_ended):
            Util.__write_on_file(file_name)

        # write all suggestions provided in all episodes when the player is human
        if player_type == "human" and episode == constants.EPISODES_WITH_HUMAN - 1 and is_game_ended:
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
        
        else:
            # create parent directory
            user_path_png_plot = "../human/plot"
            if os.path.exists(user_path_png_plot) is False:
                os.mkdir(user_path_png_plot)

            user_path_png_parent = "../human/plot/png"
            if os.path.exists(user_path_png_parent) is False:
                os.mkdir(user_path_png_parent)
            # create in parent directory a folder for plots
            user_path_png_child = "../human/plot/png/user_" + str(user_number)
            os.mkdir(user_path_png_child)
            os.mkdir(user_path_png_child + "/Avg_of_suggests_in_specific_episode")
            os.mkdir(user_path_png_child + "/Avg_of_moves_until_match")
            os.mkdir(user_path_png_child + "/Avg_of_suggests_after_some_episode")
            os.mkdir(user_path_png_child + "/Episode_Click_until_match")
            os.mkdir(user_path_png_child + "/Rewards")
            os.mkdir(user_path_png_child + "/Episode_length")
            # for tex file
            user_path_tex_parent = "../human/plot/tex"
            if os.path.exists(user_path_tex_parent) is False:
                os.mkdir(user_path_tex_parent)
            user_path_tex_child = "../human/plot/tex/user_" + str(user_number)
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

