#########################################     REWARDS     ######################################### 
REWARD_SUGGEST_NONE = 10
REWARD_SUGGEST_RC = 5
REWARD_SUGGEST_CARD = 0.01

BEGIN_STATE = 3
MIDDLE_STATE = 1.5
END_STATE = 0.75
###################################################################################################


######################################         STATES     ######################################### 
#last_action_x_state_game_x_user_state

INIT_STATE = 0

NONE_BEGIN_CORRECT = 1
NONE_BEGIN_WRONG = 2
RC_BEGIN_CORRECT = 3
RC_BEGIN_WRONG = 4
CARD_BEGIN_CORRECT = 5
CARD_BEGIN_WRONG = 6    

NONE_MIDDLE_CORRECT = 7
NONE_MIDDLE_WRONG = 8
RC_MIDDLE_CORRECT = 9
RC_MIDDLE_WRONG = 10
CARD_MIDDLE_CORRECT = 11
CARD_MIDDLE_WRONG = 12

NONE_END_CORRECT = 13
NONE_END_WRONG = 14
RC_END_CORRECT = 15
RC_END_WRONG = 16
CARD_END_CORRECT = 17
CARD_END_WRONG = 18
###################################################################################################


######################################         ACTION     ######################################### 
SUGGEST_NONE = 0
SUGGEST_ROW_COLUMN = 1
SUGGEST_CARD = 2
###################################################################################################

# ENV

EPISODES_WITH_HUMAN = 5
EPISODES_WITH_AGENT = 100000