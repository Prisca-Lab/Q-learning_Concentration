import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# define robot's action
actions = ['none', 'rc', 'card']

# define states: {user_state X robot_last_action X game_state}
states = [
    'INIT_STATE',

    'FIRST_FLIP_NONE_BEGIN_CORRECT',
    'FIRST_FLIP_NONE_BEGIN_WRONG',
    'FIRST_FLIP_NONE_MIDDLE_CORRECT',
    'FIRST_FLIP_NONE_MIDDLE_WRONG',
    'FIRST_FLIP_NONE_END_CORRECT',
    'FIRST_FLIP_NONE_END_WRONG',

    'FIRST_FLIP_SUGGEST_RC_BEGIN_CORRECT',
    'FIRST_FLIP_SUGGEST_RC_BEGIN_WRONG',
    'FIRST_FLIP_SUGGEST_RC_MIDDLE_CORRECT',
    'FIRST_FLIP_SUGGEST_RC_MIDDLE_WRONG',
    'FIRST_FLIP_SUGGEST_RC_END_CORRECT',
    'FIRST_FLIP_SUGGEST_RC_END_WRONG',

    'FIRST_FLIP_SUGGEST_CARD_BEGIN_CORRECT',
    'FIRST_FLIP_SUGGEST_CARD_BEGIN_WRONG',
    'FIRST_FLIP_SUGGEST_CARD_MIDDLE_CORRECT',
    'FIRST_FLIP_SUGGEST_CARD_MIDDLE_WRONG',
    'FIRST_FLIP_SUGGEST_CARD_END_CORRECT',
    'FIRST_FLIP_SUGGEST_CARD_END_WRONG',

    'SECOND_FLIP_NONE_BEGIN_CORRECT',
    'SECOND_FLIP_NONE_BEGIN_WRONG',
    'SECOND_FLIP_NONE_MIDDLE_CORRECT',
    'SECOND_FLIP_NONE_MIDDLE_WRONG',
    'SECOND_FLIP_NONE_END_CORRECT',
    'SECOND_FLIP_NONE_END_WRONG',

    'SECOND_FLIP_SUGGEST_RC_BEGIN_CORRECT',
    'SECOND_FLIP_SUGGEST_RC_BEGIN_WRONG',
    'SECOND_FLIP_SUGGEST_RC_MIDDLE_CORRECT',
    'SECOND_FLIP_SUGGEST_RC_MIDDLE_WRONG',
    'SECOND_FLIP_SUGGEST_RC_END_CORRECT',
    'SECOND_FLIP_SUGGEST_RC_END_WRONG',

    'SECOND_FLIP_SUGGEST_CARD_BEGIN_CORRECT',
    'SECOND_FLIP_SUGGEST_CARD_BEGIN_WRONG',
    'SECOND_FLIP_SUGGEST_CARD_MIDDLE_CORRECT',
    'SECOND_FLIP_SUGGEST_CARD_MIDDLE_WRONG',
    'SECOND_FLIP_SUGGEST_CARD_END_CORRECT',
    'SECOND_FLIP_SUGGEST_CARD_END_WRONG'
]


Q = np.load('matrix.npy')
print(Q)

# create heatmap with Seaborn
"""fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(Q, annot=True, fmt='.2f', xticklabels=actions, yticklabels=states, ax=ax, 
            square=True, cbar=False,
            cbar_kws={"orientation": "horizontal", "pad": 0.15, "aspect": 50, "shrink": 0.8},
            annot_kws={"size": 14})
ax.tick_params(axis="x", bottom=True, top=False, labelbottom=True, labeltop=False, labelsize=14)
ax.tick_params(axis="y", left=True, right=False, labelleft=True, labelright=False, labelsize=14)

# adjust cell sizes and spacing
sns.set(font_scale=1.8)
sns.set_style({"font.family": "serif", "font.serif": ["Times", "Palatino", "serif"]})
sns.set_context("notebook", rc={"lines.linewidth": 2.5})
sns.set_palette("pastel")
sns.despine(left=True, bottom=True)
ax.set_aspect("equal")
ax.set_title("Final Q-table", fontsize=18, pad=15)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0, ha="center", fontsize=11)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, va="center", fontsize=8)

plt.tight_layout()
plt.show()
#plt.savefig('heatmap.svg', format='svg')"""


sns.set(font_scale=0.7)
fig, ax = plt.subplots(figsize=(6, 10))

sns.heatmap(Q, xticklabels=actions, yticklabels=states, annot=True, fmt=".2f", cbar=False,
            linewidths=0.5, annot_kws={'fontsize':12}
            )
ax.tick_params(axis="x", bottom=True, top=False, labelbottom=True, labeltop=False, labelsize=10)
ax.tick_params(axis="y", left=True, right=False, labelleft=True, labelright=False, labelsize=10)
ax.set_title("Final Q-table", fontsize=18, pad=15)
ax.set_xlabel('Action')
ax.set_ylabel('State')


plt.tight_layout()

"""fontsize_pt = plt.rcParams['ytick.labelsize']
dpi = 72.27

# comput the matrix height in points and inches
matrix_height_pt = fontsize_pt * Q.shape[0]
#matrix_height_in = matrix_height_pt / dpi

# compute the required figure height 
top_margin = 0.04  # in percentage of the figure height
bottom_margin = 0.04 # in percentage of the figure height
#figure_height = matrix_height_in / (1 - top_margin - bottom_margin)


# build the figure instance with the desired height
fig, ax = plt.subplots(
        figsize=(6,10), 
        gridspec_kw=dict(top=1-top_margin, bottom=bottom_margin))

# let seaborn do it's thing
ax = sns.heatmap(Q, ax=ax, xticklabels=actions, yticklabels=states, cbar=False)
ax.tick_params(axis="x", bottom=True, top=False, labelbottom=True, labeltop=False, labelsize=10)
ax.tick_params(axis="y", left=True, right=False, labelleft=True, labelright=False, labelsize=10)
ax.set_title("Final Q-table", fontsize=18, pad=15)
ax.set_xlabel('Action')
ax.set_ylabel('State')"""

plt.savefig('heatmap.svg', format='svg')