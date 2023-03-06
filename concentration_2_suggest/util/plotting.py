from collections import namedtuple

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import constants

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
            "avg_of_suggests_first_card_over_time" # Average of suggestions provided by the agent for the first card for each pair
        ]
    )

    # constants used to plot data
    AVERAGE_EPISODE_REWARDS = 0
    AVERAGE_EPISODE_LENGTH = 1
    AVERAGE_OF_TURNS_FOR_MATCH = 2
    NUMBER_OF_CLICK_UNTIL_MATCH = 3
    ACTION_TAKEN_IN_SPECIFIC_EPISODE = 4
    AVERAGE_OF_ACTIONS_TAKEN = 5
    AVERAGE_OF_ACTIONS_FIRST_CARD = 6
    PERCENTAGE_MOVES = 7
    MISTAKES = 8

    __array_of_suggests = [] # It is used in order to do the avg of all suggests provided by the robot for every pair.
    __array_of_suggests_on_first_card = []  # idem, but only for the first card
    action_counts_first = {'none': 0, 'row': 0, 'col': 0, 'card': 0}      # to plot the percentage of suggestions provided for the first flip
    action_counts_second = {'none': 0, 'row': 0, 'col': 0, 'card': 0}     # idem, but for the second flip
    mistakes = np.zeros(100000)                                 # to count all the moves that doesn't end in a match

    @staticmethod
    def save_stats(stats, flag, episode, smoothing_window=10):
        """
        This function will create plot and it will save them in specific directory.
        It will save them as png and pdf extensions.

        Parameters
        ----------
            stats (array): The array which contains the data to plot
            flag (int): In order to save the data in the correct path and with the correct name
            episode (int): The current number of episode
        """

        if flag == Plotting.PERCENTAGE_MOVES:
            figure = plt.figure(figsize=(5,5))
        else:
            figure = plt.figure(figsize=(12,5))

        match flag:
            case Plotting.AVERAGE_EPISODE_REWARDS:
                plt.plot(stats[0:episode])
                plt.xlabel("Episode")
                plt.ylabel("Episode Reward")
                plt.title("Episode Reward over Time".format(smoothing_window))
                
                plt.savefig('plot/png/Rewards/Rewards_after_' + str(episode) + '.png')
                plt.savefig('plot/pdf/Rewards/Rewards_after_' + str(episode) + '.pdf')

            case Plotting.AVERAGE_EPISODE_LENGTH:
                plt.plot(stats[0:episode])

                plt.xlabel("Episode")
                plt.ylabel("Moves number")
                plt.title("Game Length over Time".format(smoothing_window))
                
                plt.savefig('plot/png/Episode_length/Number_of_moves_after_' + str(episode) + '.png')
                plt.savefig('plot/pdf/Episode_length/Number_of_moves_after_' + str(episode) + '.pdf')

            case Plotting.AVERAGE_OF_TURNS_FOR_MATCH:
                plt.plot(stats, 'o-')
                plt.xlabel("Pairs", fontsize = 14)
                plt.ylabel("Number of clicks", fontsize = 14)
                plt.title("Average click for each card (for episode)".format(smoothing_window))
                
                plt.savefig('plot/png/Avg_of_moves_until_match/AVG_of_moves_episode_after_' + str(episode) + '.png')
                plt.savefig('plot/pdf/Avg_of_moves_until_match/AVG_of_moves_episode_after_' + str(episode) + '.pdf')

            case Plotting.NUMBER_OF_CLICK_UNTIL_MATCH:
                plt.plot(stats, 'o-')
                plt.xlabel("Pairs")
                plt.ylabel("Click")
                plt.title("Click until match".format(smoothing_window))
                
                plt.savefig('plot/png/Episode_Click_until_match/Click_until_match_of_' + str(episode) + '.png')
                plt.savefig('plot/pdf/Episode_Click_until_match/Click_until_match_of_' + str(episode) + '.pdf')

            case Plotting.ACTION_TAKEN_IN_SPECIFIC_EPISODE:
                plt.plot(stats, 'o-')
                plt.xlabel("Pairs")
                plt.ylabel("Most suggested action")
                plt.title("Average action provided by robot of " + str(episode) + " episode".format(smoothing_window))
                
                plt.savefig('plot/png/Avg_of_suggests_in_specific_episode/AVG_suggest_of_' + str(episode) + '.png')
                plt.savefig('plot/pdf/Avg_of_suggests_in_specific_episode/AVG_suggest_of_' + str(episode) + '.pdf')

            case Plotting.AVERAGE_OF_ACTIONS_TAKEN:
                plt.plot(stats)
                plt.xlabel("Pairs")
                plt.ylabel("Most suggested action")
                plt.title("Average action provided by robot after " + str(episode) + " episode".format(smoothing_window))
                
                plt.savefig('plot/png/Avg_of_suggests_after_some_episode/AVG_suggest_after_' + str(episode) + '.png')
                plt.savefig('plot/pdf/Avg_of_suggests_after_some_episode/AVG_suggest_after_' + str(episode) + '.pdf')

            case Plotting.AVERAGE_OF_ACTIONS_FIRST_CARD:
                plt.plot(stats)
                plt.xlabel("Pairs")
                plt.ylabel("Most suggested action")
                plt.title("Average action for the first card provided by robot after " + str(episode) + " episode".format(smoothing_window))
                
                plt.savefig('plot/png/Avg_of_suggests_on_first_card/AVG_suggest_after_' + str(episode) + '.png')
                plt.savefig('plot/pdf/Avg_of_suggests_on_first_card/AVG_suggest_after_' + str(episode) + '.pdf')

            case Plotting.PERCENTAGE_MOVES:
                # case for percent
                total_actions1 = sum(Plotting.action_counts_first.values())
                percent_actions1 = {action: count / total_actions1 * 100 for action, count in Plotting.action_counts_first.items()}

                total_actions2 = sum(Plotting.action_counts_second.values())
                percent_actions2 = {action: count / total_actions2 * 100 for action, count in Plotting.action_counts_second.items()}

                # Crea il grafico a barre per la percentuale di azioni
                df = pd.DataFrame([percent_actions1, percent_actions2], index=['1th flip','2nd flip']).transpose()
                fig, ax= plt.subplots(1,1, figsize=(4,5))
                df.plot.bar(ax=ax)

                for container in ax.containers:
                    ax.bar_label(container, labels=[f'%.1f%%' % v for v in container.datavalues], label_type='edge', padding=2.5, fontsize=7)
                ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
                
                # Aggiungi una legenda e etichetta gli assi
                plt.xlabel("Actions")
                plt.ylabel("Percentage of times selected (%)")
                plt.title("Percentage of hint provided")

                # Salva il grafico
                fig.tight_layout()
                fig.savefig('plot/png/Percent/Percent_after_' + str(episode) + '.png')
                fig.savefig('plot/pdf/Percent/Percent_after_' + str(episode) + '.pdf')

            case Plotting.MISTAKES:
                cumulative_mistakes = Util.get_cumulative_avg(Plotting.mistakes, episode)

                plt.plot(cumulative_mistakes)
                
                plt.xlabel("Episode", fontsize = 14)
                plt.ylabel("Mistakes number", fontsize = 14)
                plt.title("Number of mistakes over Time".format(smoothing_window))
                plt.savefig('plot/png/Mistakes/Mistakes_after_' + str(episode) + '.png')
                plt.savefig('plot/pdf/Mistakes/Mistakes_after_' + str(episode) + '.pdf')

        plt.close(figure)

    @staticmethod
    def update_stats(stats, episode, reward, action, env):
        is_turn_even = (env.get_turn() - 1) % 2 == 0     # turn - 1 because the turn has already been increased
        is_game_ended = env.get_pairs_found() == 12          # the turn doesn't increase when game is ended
        moves_until_match = env.get_flip_number()/2

        # every even turn append robot's suggestion into the array in order to get the average of suggestions for both card
        Plotting.__array_of_suggests.append(action)

        # percentage of suggestions
        if is_turn_even is False:
            Plotting.__array_of_suggests_on_first_card.append(action)

            if action == constants.SUGGEST_NONE:
                Plotting.action_counts_first['none'] += 1
            elif action == constants.SUGGEST_ROW:
                Plotting.action_counts_first['row'] += 1
            elif action == constants.SUGGEST_COL:
                Plotting.action_counts_first['col'] += 1
            else:
                Plotting.action_counts_first['card'] += 1
        else:
            if action == constants.SUGGEST_NONE:
                Plotting.action_counts_second['none'] += 1
            elif action == constants.SUGGEST_ROW:
                Plotting.action_counts_second['row'] += 1
            elif action == constants.SUGGEST_COL:
                Plotting.action_counts_second['col'] += 1
            else:
                Plotting.action_counts_second['card'] += 1

            if env.was_last_move_a_match() is False:
                Plotting.mistakes[episode] += 1

        # if a new pair has been found
        if (is_turn_even and env.was_last_move_a_match()) or is_game_ended:
            pair = env.get_pairs_found() - 1
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
            Util.save_suggests_into_file(Plotting.__array_of_suggests, episode, is_game_ended)

            Plotting.__array_of_suggests.clear()
            Plotting.__array_of_suggests_on_first_card.clear()

        # cumulative reward 
        stats.episode_rewards[episode] += reward
        # cumulative moves
        stats.episode_lengths[episode] = (env.get_turn() - 1)/2  # 2 turns = 1 move
        