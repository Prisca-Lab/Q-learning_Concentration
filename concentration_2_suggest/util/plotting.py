from collections import namedtuple

import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

from util import Util

class Plotting:
    
    EpisodeStats = namedtuple(
        "Stats", [
            "episode_lengths",                     # How many steps it took to finish an episode
            "episode_rewards",                     # Reward of an episode
            "episode_click_until_match",           # How many clicks it took to find a pair in a specific episode
            "avg_of_moves_until_match",            # Average of number of moves it took to find a pair - after n episodes
            "avg_of_suggests_in_specific_episode", # Average of suggestions provided by the agent in a specific episode for each pair
            "avg_of_suggests_after_some_episode",  # Average of suggestions provided by the agent after n episodes for each pair
            "avg_of_suggests_first_card_over_time" # Average of suggestions provided by the agent for the first card 
        ]
    )

    AVERAGE_EPISODE_REWARDS = 0
    AVERAGE_EPISODE_LENGTH = 1
    AVERAGE_OF_TURNS_FOR_MATCH = 2
    NUMBER_OF_CLICK_UNTIL_MATCH = 3
    ACTION_TAKEN_IN_SPECIFIC_EPISODE = 4
    AVERAGE_OF_ACTIONS_TAKEN = 5
    AVERAGE_OF_ACTIONS_FIRST_CARD = 6
    LENGTH_GAMES = 7

    HUMAN_PLAYER = "human"
    ROBOT_PLAYER = "robot"

    __array_of_suggests = [] # It is used in order to do the avg of all suggests provided by the robot for every pair.
    __array_of_suggests_on_first_card = []

    @staticmethod
    def save_stats(stats, flag, episode, user_type, number_of_current_user, smoothing_window=10):
        """
        This function will create plot and it will save them in specific directory.
        It will save them as png and tex extensions.

        Parameters
        ----------

        stats: Array
            The array which contains the data to plot
        flag: int
            In order to save the data in the correct path and with the correct name
        episode: Array
            The array of episode for x-axis 
        user_type: String
            This flag is used in order to create new directory for each human player
        number_of_current_user: int
            In order to save the plot in the directory of the current user. It can be any value for ROBOT_PLAYER.
        """

        figure = plt.figure(figsize=(12,5))

        match flag:
            case Plotting.AVERAGE_EPISODE_REWARDS:
                plt.plot(stats[0:episode])
                plt.xlabel("Episode")
                plt.ylabel("Episode Reward")
                plt.title("Episode Reward over Time".format(smoothing_window))
                if user_type == Plotting.HUMAN_PLAYER:
                    plt.savefig('plot/user_' + str(number_of_current_user) + '/png/Rewards/Rewards_after_' + str(episode) + '.png')
                    tikzplotlib.save('plot/user_' + str(number_of_current_user) + '/tex/Rewards/Rewards_after_' + str(episode) + '.tex')
                else:
                    plt.savefig('plot/png/Rewards/Rewards_after_' + str(episode) + '.png')
                    tikzplotlib.save('plot/tex/Rewards/Rewards_after_' + str(episode) + '.tex')

            case Plotting.AVERAGE_EPISODE_LENGTH:
                # save bar plot for human user, standard plot otherwise
                plt.plot(stats[0:episode])

                plt.xlabel("Episode")
                plt.ylabel("Moves number")
                plt.title("Game Length over Time".format(smoothing_window))
                if user_type == Plotting.HUMAN_PLAYER:
                    plt.savefig('plot/user_' + str(number_of_current_user) + '/png/Episode_length/Number_of_moves_after_' + str(episode) + '.png')
                    tikzplotlib.save('plot/user_' + str(number_of_current_user) + '/tex/Episode_length/Number_of_moves_after_' + str(episode) + '.tex')
                else:
                    plt.savefig('plot/png/Episode_length/Number_of_moves_after_' + str(episode) + '.png')
                    tikzplotlib.save('plot/tex/Episode_length/Number_of_moves_after_' + str(episode) + '.tex')

            case Plotting.AVERAGE_OF_TURNS_FOR_MATCH:
                plt.plot(stats, 'o-')
                plt.xlabel("Pairs")
                plt.ylabel("Number of clicks")
                plt.title("Average click for each card (for episode)".format(smoothing_window))
                if user_type == Plotting.HUMAN_PLAYER:
                    plt.savefig('plot/user_' + str(number_of_current_user) + '/png/Avg_of_moves_until_match/AVG_of_moves_episode_after_' + str(episode) + '.png')
                    tikzplotlib.save('plot/user_' + str(number_of_current_user) + '/tex/Avg_of_moves_until_match/AVG_of_moves_episode_after_' + str(episode) + '.tex')
                else:
                    plt.savefig('plot/png/Avg_of_moves_until_match/AVG_of_moves_episode_after_' + str(episode) + '.png')
                    tikzplotlib.save('plot/tex/Avg_of_moves_until_match/AVG_of_moves_episode_after_' + str(episode) + '.tex')

            case Plotting.NUMBER_OF_CLICK_UNTIL_MATCH:
                plt.plot(stats, 'o-')
                plt.xlabel("Pairs")
                plt.ylabel("Click")
                plt.title("Click until match".format(smoothing_window))
                if user_type == Plotting.HUMAN_PLAYER:
                    plt.savefig('plot/user_' + str(number_of_current_user) + '/png/Episode_Click_until_match/Click_until_match_of_' + str(episode) + '.png')
                    tikzplotlib.save('plot/user_' + str(number_of_current_user) + '/tex/Episode_Click_until_match/Click_until_match_of_' + str(episode) + '.tex')
                else:
                    plt.savefig('plot/png/Episode_Click_until_match/Click_until_match_of_' + str(episode) + '.png')
                    tikzplotlib.save('plot/tex/Episode_Click_until_match/Click_until_match_of_' + str(episode) + '.tex')

            case Plotting.ACTION_TAKEN_IN_SPECIFIC_EPISODE:
                plt.plot(stats, 'o-')
                plt.xlabel("Pairs")
                plt.ylabel("Most suggested action")
                plt.title("Average action provided by robot of " + str(episode) + " episode".format(smoothing_window))
                if user_type == Plotting.HUMAN_PLAYER:
                    plt.savefig('plot/user_' + str(number_of_current_user) + '/png/Avg_of_suggests_in_specific_episode/AVG_suggest_of_' + str(episode) + '.png')
                    tikzplotlib.save('plot/user_' + str(number_of_current_user) + '/tex/Avg_of_suggests_in_specific_episode/AVG_suggest_of_' + str(episode) + '.tex')
                else:
                    plt.savefig('plot/png/Avg_of_suggests_in_specific_episode/AVG_suggest_of_' + str(episode) + '.png')
                    tikzplotlib.save('plot/tex/Avg_of_suggests_in_specific_episode/AVG_suggest_of_' + str(episode) + '.tex')

            case Plotting.AVERAGE_OF_ACTIONS_TAKEN:
                plt.plot(stats)
                plt.xlabel("Pairs")
                plt.ylabel("Most suggested action")
                plt.title("Average action provided by robot after " + str(episode) + " episode".format(smoothing_window))
                if user_type == Plotting.HUMAN_PLAYER:
                    plt.savefig('plot/user_' + str(number_of_current_user) + '/png/Avg_of_suggests_after_some_episode/AVG_suggest_after_' + str(episode) + '.png')
                    tikzplotlib.save('plot/user_' + str(number_of_current_user) + '/tex/Avg_of_suggests_after_some_episode/AVG_suggest_after_' + str(episode) + '.tex')
                else:
                    plt.savefig('plot/png/Avg_of_suggests_after_some_episode/AVG_suggest_after_' + str(episode) + '.png')
                    tikzplotlib.save('plot/tex/Avg_of_suggests_after_some_episode/AVG_suggest_after_' + str(episode) + '.tex')

            case Plotting.AVERAGE_OF_ACTIONS_FIRST_CARD:
                plt.plot(stats)
                plt.xlabel("Pairs")
                plt.ylabel("Most suggested action")
                plt.title("Average action for the first card provided by robot after " + str(episode) + " episode".format(smoothing_window))
                if user_type == Plotting.HUMAN_PLAYER:
                    plt.savefig('plot/user_' + str(number_of_current_user) + '/png/Avg_of_suggests_on_first_card/AVG_suggest_after_' + str(episode) + '.png')
                    tikzplotlib.save('plot/user_' + str(number_of_current_user) + '/tex/Avg_of_suggests_on_first_card/AVG_suggest_after_' + str(episode) + '.tex')
                else:
                    plt.savefig('plot/png/Avg_of_suggests_on_first_card/AVG_suggest_after_' + str(episode) + '.png')
                    tikzplotlib.save('plot/tex/Avg_of_suggests_on_first_card/AVG_suggest_after_' + str(episode) + '.tex')

            case Plotting.LENGTH_GAMES:
                games = np.arange(1, 6)
                # creating the bar plot
                plt.bar(games, stats, width = 0.4)


        plt.close(figure)

    @staticmethod
    def update_stats(stats, episode, reward, action, player, game, player_type):
        is_turn_even = (game.get_turn - 1) % 2 == 0     # turn - 1 because the turn has already been increased
        is_game_ended = player.get_pairs == 12          # the turn doesn't increase when game is ended
        moves_until_match = player.get_number_of_clicks_for_current_pair/2

        # every even turn append robot's suggestion into the array in order to get the average of suggestions for both card
        Plotting.__array_of_suggests.append(action)

        # in order to get the average of suggestions for the first card only
        if is_turn_even is False:
            Plotting.__array_of_suggests_on_first_card.append(action)

        # if a new pair has been found
        if (is_turn_even and player.get_last_pair_was_correct) or is_game_ended:
            pair = player.get_pairs - 1
            # number of moves until pair is found, only of one specific episode
            stats.episode_click_until_match[pair] = moves_until_match
            # average number of moves until pair is found, considering n episodes
            stats.avg_of_moves_until_match[pair] += moves_until_match
            # average hint for each turn of each episode
            stats.avg_of_suggests_in_specific_episode[pair] = sum(Plotting.__array_of_suggests) / len(Plotting.__array_of_suggests)
            # add up all the suggestions given by the robot to make the average later
            stats.avg_of_suggests_after_some_episode[pair] += stats.avg_of_suggests_in_specific_episode[pair]
            # add up all the suggestions for the first card in order to plot the average
            stats.avg_of_suggests_first_card_over_time[pair] += sum(Plotting.__array_of_suggests_on_first_card) / len(Plotting.__array_of_suggests_on_first_card)
            
            # just for debug: create a file with all suggests provided by the agent
            # it will save every 4000 times when the player is the robot
            Util.save_suggests_into_file(Plotting.__array_of_suggests, player_type, episode, is_game_ended)

            #print("total first suggestions: ", Plotting.__array_of_suggests_on_first_card)
            #print("total suggestions for both cards:", Plotting.__array_of_suggests)
            Plotting.__array_of_suggests.clear()
            Plotting.__array_of_suggests_on_first_card.clear()

        # cumulative reward 
        stats.episode_rewards[episode] += reward
        # cumulative moves
        stats.episode_lengths[episode] = (game.get_turn - 1)/2  # 2 turns = 1 move