# Matching tags in Trello with tags in Planka
TRELLO_TO_PLANKA_COLORS = {
    "green": "tank-green",
    "yellow": "egg-yellow",
    "orange": "pumpkin-orange",
    "red": "berry-red",
    "purple": "midnight-blue",
    "blue": "lagoon-blue",
    "sky": "morning-sky",
    "pink": "pink-tulip",
    "black": "dark-granite",
    "lime": "bright-moss"
}

# The function matches the colour of a label in Planka to a label from Trello
def get_planka_label_color(trello_color):
    return TRELLO_TO_PLANKA_COLORS.get(trello_color, "desert-sand")  # Default: neutral colour